defmodule Pythia.Mcp.JsonEvaluator do
  @moduledoc """
  JSON bridge for IDE / MCP clients: decodes a proposal + safety context,
  runs `Pythia.Showcase.AgentInfraAction.evaluate/2`, returns JSON-friendly maps.

  Input is a JSON object with string keys. Required top-level key `"gate"`.
  Currently supported: `"agent_infra_action"` (matches the infrastructure showcase gate).
  """

  alias Pythia.Showcase.AgentInfraAction

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
        with {:ok, action} <- decode_action(Map.get(decoded, "action", %{})),
             {:ok, ctx} <- decode_safety_context(Map.get(decoded, "safety_context", %{})) do
          raw = AgentInfraAction.evaluate(action, ctx)
          evidence = AgentInfraAction.export_evidence(raw)
          {:ok, build_response(raw, evidence)}
        end

      nil ->
        {:error, %{error: "missing_gate", message: "required field \"gate\" (e.g. \"agent_infra_action\")"}}

      other ->
        {:error, %{error: "unknown_gate", gate: other, message: "supported: [\"agent_infra_action\"]"}}
    end
  end

  defp evaluate_decoded(_), do: {:error, %{error: "invalid_body", message: "JSON root must be an object"}}

  defp build_response({:ok, payload}, evidence) do
    %{
      ok: true,
      outcome: "ALLOW",
      status: "accepted",
      stop_reason: format_stop_reason(payload[:stop_reason]),
      export: AgentInfraAction.export_result({:ok, payload}),
      evidence: evidence
    }
  end

  defp build_response({:error, payload}, evidence) do
    %{
      ok: true,
      outcome: "BLOCK",
      status: "rejected",
      stop_reason: format_stop_reason(payload[:stop_reason]),
      export: AgentInfraAction.export_result({:error, payload}),
      evidence: evidence
    }
  end

  defp format_stop_reason(nil), do: nil
  defp format_stop_reason(atom) when is_atom(atom), do: Atom.to_string(atom)
  defp format_stop_reason(other), do: to_string(other)

  defp decode_action(raw) when is_map(raw) do
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
    case Map.get(raw, key) || Map.get(raw, field) do
      v when is_binary(v) ->
        if String.trim(v) != "" do
          {:ok, v}
        else
          {:error, %{error: "invalid_field", field: key, expected: "non-empty string"}}
        end

      nil ->
        {:error, %{error: "missing_field", field: key}}

      _ ->
        {:error, %{error: "invalid_field", field: key, expected: "non-empty string"}}
    end
  end

  defp get_bool(raw, key, field) do
    case Map.get(raw, key) || Map.get(raw, field) do
      true -> {:ok, true}
      false -> {:ok, false}
      nil -> {:error, %{error: "missing_field", field: key}}
      _ -> {:error, %{error: "invalid_field", field: key, expected: "boolean"}}
    end
  end

  defp fetch_iso_datetime(raw, key, field) do
    v = Map.get(raw, key) || Map.get(raw, field)

    cond do
      is_binary(v) ->
        case DateTime.from_iso8601(v) do
          {:ok, dt, _} -> {:ok, dt}
          {:error, _} -> {:error, %{error: "invalid_datetime", field: key, value: v}}
        end

      true ->
        {:error, %{error: "missing_or_invalid_field", field: key, expected: "ISO-8601 string"}}
    end
  end
end
