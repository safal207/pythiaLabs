defmodule Pythia.Mcp.JsonEvaluator do
  @moduledoc """
  JSON bridge for IDE / MCP clients: decodes a proposal plus context maps,
  runs the matching deterministic showcase gate, returns JSON-friendly maps.

  Input uses string keys. Required top-level key `"gate"`:

  - `"agent_infra_action"` — requires `"action"` and `"safety_context"` (see infra showcase).
  - `"banking_risk_action"` — requires `"action"` and `"governance"` (see banking showcase).
  - `"web3_treasury_action"` — requires `"action"` and `"governance"` (see treasury showcase).
  """

  alias Pythia.Showcase.{
    AgentInfraAction,
    BankingRiskAction,
    Web3TreasuryAction
  }

  @supported_gates ~w(agent_infra_action banking_risk_action web3_treasury_action)

  @doc """
  Parses `json_string` and returns `{:ok, response_map}` or `{:error, error_map}`.
  Both maps are safe to pass to `Jason.encode!/1`.
  """
  @spec run(String.t()) :: {:ok, map()} | {:error, map()}
  def run(json_string) when is_binary(json_string) do
    with {:ok, decoded} <- Jason.decode(json_string),
         {:ok, response} <- evaluate_decoded(decoded) do
      {:ok, response}
    else
      {:error, %Jason.DecodeError{} = e} ->
        {:error, %{ok: false, error: "invalid_json", message: Exception.message(e)}}

      {:error, reason} when is_map(reason) ->
        {:error, Map.put(reason, :ok, false)}
    end
  end

  defp evaluate_decoded(decoded) when is_map(decoded) do
    gate = Map.get(decoded, "gate")

    case gate do
      "agent_infra_action" ->
        with {:ok, action} <- decode_infra_action(Map.get(decoded, "action", %{})),
             {:ok, ctx} <- decode_safety_context(Map.get(decoded, "safety_context", %{})) do
          raw = AgentInfraAction.evaluate(action, ctx)
          evidence = AgentInfraAction.export_evidence(raw)
          {:ok, build_response(AgentInfraAction, raw, evidence)}
        end

      "banking_risk_action" ->
        with {:ok, action} <- decode_banking_action(Map.get(decoded, "action", %{})),
             {:ok, gov} <- decode_banking_governance(get_governance(decoded)) do
          raw = BankingRiskAction.evaluate(action, gov)
          evidence = BankingRiskAction.export_evidence(raw)
          {:ok, build_response(BankingRiskAction, raw, evidence)}
        end

      "web3_treasury_action" ->
        with {:ok, action} <- decode_web3_action(Map.get(decoded, "action", %{})),
             {:ok, gov} <- decode_web3_governance(get_governance(decoded)) do
          raw = Web3TreasuryAction.evaluate(action, gov)
          evidence = Web3TreasuryAction.export_evidence(raw)
          {:ok, build_response(Web3TreasuryAction, raw, evidence)}
        end

      nil ->
        {:error,
         %{
           error: "missing_gate",
           message: "required field \"gate\" (one of: #{Enum.join(@supported_gates, ", ")})"
         }}

      other ->
        {:error,
         %{
           error: "unknown_gate",
           gate: other,
           message: "supported: #{inspect(@supported_gates)}"
         }}
    end
  end

  defp evaluate_decoded(_),
    do: {:error, %{error: "invalid_body", message: "JSON root must be an object"}}

  defp get_governance(decoded) do
    cond do
      Map.has_key?(decoded, "governance") -> Map.get(decoded, "governance") || %{}
      Map.has_key?(decoded, "governance_record") -> Map.get(decoded, "governance_record") || %{}
      true -> %{}
    end
  end

  defp build_response(mod, {:ok, payload}, evidence) do
    %{
      ok: true,
      outcome: "ALLOW",
      status: "accepted",
      stop_reason: format_stop_reason(payload[:stop_reason]),
      export: mod.export_result({:ok, payload}),
      evidence: evidence
    }
  end

  defp build_response(mod, {:error, payload}, evidence) do
    %{
      ok: true,
      outcome: "BLOCK",
      status: "rejected",
      stop_reason: format_stop_reason(payload[:stop_reason]),
      export: mod.export_result({:error, payload}),
      evidence: evidence
    }
  end

  defp format_stop_reason(nil), do: nil
  defp format_stop_reason(atom) when is_atom(atom), do: Atom.to_string(atom)
  defp format_stop_reason(other), do: to_string(other)

  defp decode_infra_action(raw) when is_map(raw) do
    required = [
      :action_id,
      :action_type,
      :actor_id,
      :resource_id,
      :resource_type,
      :target_environment,
      :action_time,
      :decision_time
    ]

    with {:ok, fields} <- fetch_required_string(raw, required -- [:action_time, :decision_time]),
         {:ok, action_time} <- fetch_iso_datetime(raw, "action_time", :action_time),
         {:ok, decision_time} <- fetch_iso_datetime(raw, "decision_time", :decision_time) do
      {:ok,
       Map.merge(fields, %{
         action_time: action_time,
         decision_time: decision_time
       })}
    end
  end

  defp decode_banking_action(raw) when is_map(raw) do
    strings = [:action_id, :action_type, :operator_id, :account_id]

    with {:ok, fields} <- fetch_required_string(raw, strings),
         {:ok, action_time} <- fetch_iso_datetime(raw, "action_time", :action_time),
         {:ok, decision_time} <- fetch_iso_datetime(raw, "decision_time", :decision_time) do
      {:ok,
       Map.merge(fields, %{
         action_time: action_time,
         decision_time: decision_time
       })}
    end
  end

  defp decode_banking_governance(raw) when is_map(raw) do
    datetimes = [
      :authorization_valid_from,
      :authorization_valid_to,
      :authorization_recorded_at,
      :evidence_observed_at,
      :evidence_valid_until
    ]

    bools = [:decision_time_knowledge_present, :operator_approval_present]

    with {:ok, dt} <- fetch_iso_datetimes(raw, datetimes),
         {:ok, bo} <- fetch_required_bool(raw, bools) do
      {:ok, Map.merge(dt, bo)}
    end
  end

  defp decode_web3_action(raw) when is_map(raw) do
    strings = [
      :action_id,
      :action_type,
      :actor,
      :dao_id,
      :proposal_id,
      :asset,
      :recipient,
      :required_permission
    ]

    with {:ok, fields} <- fetch_required_string(raw, strings),
         {:ok, amount} <- get_int(raw, "amount", :amount),
         {:ok, action_time} <- fetch_iso_datetime(raw, "action_time", :action_time),
         {:ok, decision_time} <- fetch_iso_datetime(raw, "decision_time", :decision_time) do
      {:ok,
       Map.merge(fields, %{
         amount: amount,
         action_time: action_time,
         decision_time: decision_time
       })}
    end
  end

  defp decode_web3_governance(raw) when is_map(raw) do
    strings = [:proposal_id, :permission]

    datetimes = [
      :voting_closed_at,
      :timelock_until,
      :authorization_valid_from,
      :authorization_valid_to,
      :authorization_recorded_at,
      :transfer_expires_at
    ]

    with {:ok, str} <- fetch_required_string(raw, strings),
         {:ok, quorum_met} <- get_bool(raw, "quorum_met", :quorum_met),
         {:ok, dt} <- fetch_iso_datetimes(raw, datetimes) do
      {:ok, Map.merge(str, Map.put(dt, :quorum_met, quorum_met))}
    end
  end

  defp decode_safety_context(raw) when is_map(raw) do
    strings = [:credential_scope, :backup_isolation]

    bools = [
      :explicit_user_approval_present,
      :environment_scope_verified,
      :documentation_verified,
      :dry_run_completed,
      :decision_time_knowledge_present
    ]

    with {:ok, str} <- fetch_required_string(raw, strings),
         {:ok, bo} <- fetch_required_bool(raw, bools) do
      {:ok, Map.merge(str, bo)}
    end
  end

  defp fetch_required_string(raw, fields) do
    Enum.reduce_while(fields, {:ok, %{}}, fn field, {:ok, acc} ->
      key = Atom.to_string(field)

      case get_str(raw, key, field) do
        {:ok, value} -> {:cont, {:ok, Map.put(acc, field, value)}}
        {:error, e} -> {:halt, {:error, e}}
      end
    end)
  end

  defp fetch_required_bool(raw, fields) do
    Enum.reduce_while(fields, {:ok, %{}}, fn field, {:ok, acc} ->
      key = Atom.to_string(field)

      case get_bool(raw, key, field) do
        {:ok, value} -> {:cont, {:ok, Map.put(acc, field, value)}}
        {:error, e} -> {:halt, {:error, e}}
      end
    end)
  end

  defp get_str(raw, key, field) do
    val =
      cond do
        Map.has_key?(raw, key) -> Map.fetch!(raw, key)
        Map.has_key?(raw, field) -> Map.fetch!(raw, field)
        true -> nil
      end

    case val do
      nil ->
        {:error, %{error: "missing_field", field: key}}

      v when is_binary(v) ->
        if String.trim(v) != "" do
          {:ok, v}
        else
          {:error, %{error: "invalid_field", field: key, expected: "non-empty string"}}
        end

      _ ->
        {:error, %{error: "invalid_field", field: key, expected: "non-empty string"}}
    end
  end

  defp get_bool(raw, key, field) do
    val =
      cond do
        Map.has_key?(raw, key) -> Map.fetch!(raw, key)
        Map.has_key?(raw, field) -> Map.fetch!(raw, field)
        true -> nil
      end

    case val do
      true -> {:ok, true}
      false -> {:ok, false}
      nil -> {:error, %{error: "missing_field", field: key}}
      _ -> {:error, %{error: "invalid_field", field: key, expected: "boolean"}}
    end
  end

  defp fetch_iso_datetimes(raw, fields) do
    Enum.reduce_while(fields, {:ok, %{}}, fn field, {:ok, acc} ->
      key = Atom.to_string(field)

      case fetch_iso_datetime(raw, key, field) do
        {:ok, dt} -> {:cont, {:ok, Map.put(acc, field, dt)}}
        {:error, e} -> {:halt, {:error, e}}
      end
    end)
  end

  defp get_int(raw, key, field) do
    val =
      cond do
        Map.has_key?(raw, key) -> Map.fetch!(raw, key)
        Map.has_key?(raw, field) -> Map.fetch!(raw, field)
        true -> nil
      end

    case val do
      nil -> {:error, %{error: "missing_field", field: key}}
      v when is_integer(v) -> {:ok, v}
      v when is_float(v) and trunc(v) == v -> {:ok, trunc(v)}
      _ -> {:error, %{error: "invalid_field", field: key, expected: "integer"}}
    end
  end

  defp fetch_iso_datetime(raw, key, field) do
    val =
      cond do
        Map.has_key?(raw, key) -> Map.fetch!(raw, key)
        Map.has_key?(raw, field) -> Map.fetch!(raw, field)
        true -> nil
      end

    cond do
      is_binary(val) ->
        case DateTime.from_iso8601(val) do
          {:ok, dt, _} -> {:ok, dt}
          {:error, _} -> {:error, %{error: "invalid_datetime", field: key, value: val}}
        end

      true ->
        {:error, %{error: "missing_or_invalid_field", field: key, expected: "ISO-8601 string"}}
    end
  end
end
