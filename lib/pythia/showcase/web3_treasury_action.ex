defmodule Pythia.Showcase.Web3TreasuryAction do
  @moduledoc """
  Deterministic in-memory showcase for Web3 DAO treasury action reasoning.
  """

  @required_governance_fields [
    :proposal_id,
    :permission,
    :quorum_met,
    :voting_closed_at,
    :timelock_until,
    :authorization_valid_from,
    :authorization_valid_to,
    :authorization_recorded_at,
    :transfer_expires_at
  ]

  @check_order [
    :proposal_match_check,
    :permission_check,
    :quorum_check,
    :voting_window_check,
    :timelock_check,
    :authorization_valid_time_check,
    :authorization_transaction_time_check,
    :transfer_expiration_check
  ]
  @envelope_schema "pythia.evidence.envelope.v1"
  @artifact_type "pythia.web3_treasury_action.decision_trace.v1"
  @canonicalization "pythia.canonical_export.v1"
  @integrity_algorithm "sha256"

  @spec evaluate(map(), map()) :: {:ok, map()} | {:error, map()}
  def evaluate(action, governance_record) when is_map(action) and is_map(governance_record) do
    proposed_trace = [proposed_action_trace(action)]

    with :ok <- validate_governance_record(governance_record),
         :ok <- validate_action_timestamps(action),
         {:ok, trace} <- run_checks(action, governance_record, proposed_trace) do
      {:ok,
       %{
         status: :accepted,
         stop_reason: :treasury_transfer_accepted,
         trace: trace ++ [decision_trace(:accept, :treasury_transfer_accepted)]
       }}
    else
      {:error, stop_reason, trace} when is_list(trace) ->
        reject(stop_reason, trace ++ [decision_trace(:reject, stop_reason)])

      {:error, stop_reason, failed_check} when is_atom(failed_check) ->
        trace =
          proposed_trace ++
            [
              check_trace(failed_check, :fail, %{
                reason: failure_reason(stop_reason)
              }),
              decision_trace(:reject, stop_reason)
            ]

        reject(stop_reason, trace)
    end
  end

  def evaluate(_action, _governance_record) do
    trace = [proposed_action_trace(%{}), decision_trace(:reject, :invalid_governance_record)]
    reject(:invalid_governance_record, trace)
  end

  @spec trace_events([map()]) :: [atom()]
  def trace_events(trace), do: Enum.map(trace, & &1.event)

  @spec export_result({:ok, map()} | {:error, map()}) :: map()
  def export_result({status, payload}) when status in [:ok, :error] and is_map(payload) do
    payload
    |> normalize_value()
    |> ensure_export_status()
  end

  @spec export_result_json({:ok, map()} | {:error, map()}) ::
          {:ok, String.t()} | {:error, :json_encoder_unavailable}
  def export_result_json(result) do
    export = export_result(result)

    if Code.ensure_loaded?(Jason) and function_exported?(Jason, :encode!, 2) do
      {:ok, apply(Jason, :encode!, [export, [pretty: true]])}
    else
      {:error, :json_encoder_unavailable}
    end
  end

  @spec canonical_export_string({:ok, map()} | {:error, map()}) :: String.t()
  def canonical_export_string(result) do
    result
    |> export_result()
    |> canonical_encode()
  end

  @spec export_digest({:ok, map()} | {:error, map()}) :: map()
  def export_digest(result) do
    digest =
      result
      |> canonical_export_string()
      |> then(&:crypto.hash(:sha256, &1))
      |> Base.encode16(case: :lower)

    %{
      "algorithm" => @integrity_algorithm,
      "digest" => digest
    }
  end

  @spec export_evidence({:ok, map()} | {:error, map()}) :: map()
  def export_evidence(result) do
    payload = export_result(result)
    digest = digest_export_payload(payload)

    %{
      "artifact_type" => @artifact_type,
      "algorithm" => digest["algorithm"],
      "digest" => digest["digest"],
      "payload" => payload
    }
  end

  @spec digest_export_payload(map()) :: map()
  def digest_export_payload(payload) when is_map(payload) do
    digest =
      payload
      |> canonical_encode()
      |> then(&:crypto.hash(:sha256, &1))
      |> Base.encode16(case: :lower)

    %{
      "algorithm" => @integrity_algorithm,
      "digest" => digest
    }
  end

  @spec verify_evidence(map()) :: {:ok, map()} | {:error, map()}
  def verify_evidence(evidence) when is_map(evidence) do
    artifact_type = Map.get(evidence, "artifact_type")
    algorithm = Map.get(evidence, "algorithm")
    digest = Map.get(evidence, "digest")
    payload = Map.get(evidence, "payload")

    cond do
      not valid_evidence_shape?(artifact_type, algorithm, digest, payload) ->
        invalid_evidence_shape()

      artifact_type != @artifact_type ->
        rejected(:unsupported_artifact_type)

      algorithm != @integrity_algorithm ->
        rejected(:unsupported_algorithm)

      true ->
        actual_digest = digest_export_payload(payload)["digest"]

        if digest == actual_digest do
          {:ok,
           %{
             status: :verified,
             artifact_type: artifact_type,
             algorithm: algorithm,
             digest: digest
           }}
        else
          {:error,
           %{
             status: :rejected,
             reason: :digest_mismatch,
             expected_digest: digest,
             actual_digest: actual_digest
           }}
        end
    end
  end

  def verify_evidence(_evidence), do: invalid_evidence_shape()

  @spec export_evidence_envelope({:ok, map()} | {:error, map()}) :: map()
  def export_evidence_envelope(result) do
    artifact = export_evidence(result)

    %{
      "schema" => @envelope_schema,
      "artifact" => artifact,
      "canonicalization" => @canonicalization,
      "integrity" => %{
        "algorithm" => @integrity_algorithm,
        "digest" => artifact["digest"]
      },
      "signature" => %{
        "status" => "unsigned",
        "algorithm" => nil,
        "public_key" => nil,
        "signature" => nil
      }
    }
  end

  @spec verify_evidence_envelope(map()) :: {:ok, map()} | {:error, map()}
  def verify_evidence_envelope(envelope) when is_map(envelope) do
    schema = Map.get(envelope, "schema")
    artifact = Map.get(envelope, "artifact")
    canonicalization = Map.get(envelope, "canonicalization")
    integrity = Map.get(envelope, "integrity")
    signature = Map.get(envelope, "signature")

    cond do
      not valid_evidence_envelope_shape?(schema, artifact, canonicalization, integrity, signature) ->
        rejected(:invalid_envelope_shape)

      schema != @envelope_schema ->
        rejected(:unsupported_envelope_schema)

      canonicalization != @canonicalization ->
        rejected(:unsupported_canonicalization)

      integrity["algorithm"] != @integrity_algorithm ->
        rejected(:unsupported_algorithm)

      integrity["digest"] != artifact["digest"] ->
        rejected(:integrity_mismatch)

      not unsigned_signature_placeholder?(signature) ->
        rejected(:unsupported_signature_status)

      true ->
        with {:ok, verified_evidence} <- verify_evidence(artifact) do
          {:ok,
           %{
             status: :verified,
             schema: schema,
             canonicalization: canonicalization,
             digest: integrity["digest"],
             evidence: verified_evidence
           }}
        end
    end
  end

  def verify_evidence_envelope(_envelope), do: rejected(:invalid_envelope_shape)

  defp ensure_export_status(export) do
    status =
      case Map.get(export, "status") do
        "accepted" -> "accepted"
        _ -> "rejected"
      end

    stop_reason = Map.get(export, "stop_reason")
    trace = Map.get(export, "trace", [])

    %{
      "status" => status,
      "stop_reason" => stop_reason,
      "trace" => trace
    }
  end

  defp valid_evidence_shape?(artifact_type, algorithm, digest, payload) do
    is_binary(artifact_type) and is_binary(algorithm) and is_map(payload) and
      valid_digest?(digest)
  end

  defp valid_evidence_envelope_shape?(schema, artifact, canonicalization, integrity, signature) do
    is_binary(schema) and is_map(artifact) and is_binary(canonicalization) and is_map(integrity) and
      valid_integrity_shape?(integrity) and is_map(signature)
  end

  defp valid_integrity_shape?(integrity) do
    is_binary(integrity["algorithm"]) and valid_digest?(integrity["digest"])
  end

  defp unsigned_signature_placeholder?(signature) do
    is_map(signature) and
      signature["status"] == "unsigned" and
      is_nil(signature["algorithm"]) and
      is_nil(signature["public_key"]) and
      is_nil(signature["signature"])
  end

  defp valid_digest?(digest),
    do: is_binary(digest) and String.match?(digest, ~r/\A[0-9a-f]{64}\z/)

  defp invalid_evidence_shape(), do: rejected(:invalid_evidence_shape)

  defp rejected(reason), do: {:error, %{status: :rejected, reason: reason}}

  defp normalize_value(value) when is_boolean(value) or is_nil(value), do: value
  defp normalize_value(value) when is_atom(value), do: Atom.to_string(value)
  defp normalize_value(%DateTime{} = value), do: DateTime.to_iso8601(value)

  defp normalize_value(%_{} = struct) do
    struct
    |> Map.from_struct()
    |> normalize_value()
  end

  defp normalize_value(value) when is_map(value) do
    value
    |> Enum.map(fn {key, item} -> {normalize_key(key), normalize_value(item)} end)
    |> Enum.sort_by(fn {key, _item} -> key end)
    |> Map.new()
  end

  defp normalize_value(value) when is_list(value), do: Enum.map(value, &normalize_value/1)

  defp normalize_value(value) when is_binary(value) or is_number(value), do: value

  defp normalize_key(key) when is_atom(key), do: Atom.to_string(key)
  defp normalize_key(key) when is_binary(key), do: key
  defp normalize_key(key), do: to_string(key)

  defp canonical_encode(value) when is_map(value) do
    body =
      value
      |> Enum.sort_by(fn {key, _value} -> key end)
      |> Enum.map_join(",", fn {key, item} ->
        canonical_encode(to_string(key)) <> ":" <> canonical_encode(item)
      end)

    "{" <> body <> "}"
  end

  defp canonical_encode(value) when is_list(value) do
    "[" <> Enum.map_join(value, ",", &canonical_encode/1) <> "]"
  end

  defp canonical_encode(value) when is_binary(value) do
    "\"" <> escape_string(value) <> "\""
  end

  defp canonical_encode(value) when is_number(value), do: to_string(value)
  defp canonical_encode(true), do: "true"
  defp canonical_encode(false), do: "false"
  defp canonical_encode(nil), do: "null"

  defp escape_string(value) do
    value
    |> String.replace("\\", "\\\\")
    |> String.replace("\"", "\\\"")
    |> String.replace("\n", "\\n")
    |> String.replace("\r", "\\r")
    |> String.replace("\t", "\\t")
  end

  defp run_checks(action, governance_record, trace) do
    Enum.reduce_while(@check_order, {:ok, trace}, fn check, {:ok, acc_trace} ->
      case run_check(check, action, governance_record) do
        {:ok, details} ->
          {:cont, {:ok, acc_trace ++ [check_trace(check, :pass, details)]}}

        {:error, stop_reason, details} ->
          fail_trace = acc_trace ++ [check_trace(check, :fail, details)]
          {:halt, {:error, stop_reason, fail_trace}}
      end
    end)
  end

  defp run_check(:proposal_match_check, action, governance_record) do
    expected = fetch(governance_record, :proposal_id)
    actual = fetch(action, :proposal_id)

    if actual == expected do
      {:ok, %{expected: expected, actual: actual}}
    else
      {:error, :missing_proposal_record,
       %{expected: expected, actual: actual, reason: :missing_proposal_record}}
    end
  end

  defp run_check(:permission_check, action, governance_record) do
    expected = fetch(governance_record, :permission)
    actual = fetch(action, :required_permission)

    if actual == expected do
      {:ok, %{expected: expected, actual: actual}}
    else
      {:error, :permission_mismatch,
       %{expected: expected, actual: actual, reason: :permission_mismatch}}
    end
  end

  defp run_check(:quorum_check, _action, governance_record) do
    quorum_met = fetch(governance_record, :quorum_met)

    if quorum_met do
      {:ok, %{actual: quorum_met}}
    else
      {:error, :quorum_not_met, %{actual: quorum_met, reason: :quorum_not_met}}
    end
  end

  defp run_check(:voting_window_check, action, governance_record) do
    action_time = fetch(action, :action_time)
    voting_closed_at = fetch(governance_record, :voting_closed_at)

    if DateTime.compare(action_time, voting_closed_at) == :lt do
      {:error, :voting_window_still_open,
       %{
         reason: :voting_window_still_open,
         action_time: action_time,
         voting_closed_at: voting_closed_at
       }}
    else
      {:ok, %{action_time: action_time, voting_closed_at: voting_closed_at}}
    end
  end

  defp run_check(:timelock_check, action, governance_record) do
    action_time = fetch(action, :action_time)
    timelock_until = fetch(governance_record, :timelock_until)

    if DateTime.compare(action_time, timelock_until) == :lt do
      {:error, :timelock_not_satisfied,
       %{
         reason: :timelock_not_satisfied,
         action_time: action_time,
         timelock_until: timelock_until
       }}
    else
      {:ok, %{action_time: action_time, timelock_until: timelock_until}}
    end
  end

  defp run_check(:authorization_valid_time_check, action, governance_record) do
    action_time = fetch(action, :action_time)
    authorization_valid_from = fetch(governance_record, :authorization_valid_from)
    authorization_valid_to = fetch(governance_record, :authorization_valid_to)

    cond do
      DateTime.compare(action_time, authorization_valid_from) == :lt ->
        {:error, :authorization_not_yet_valid,
         %{
           reason: :authorization_not_yet_valid,
           action_time: action_time,
           authorization_valid_from: authorization_valid_from,
           authorization_valid_to: authorization_valid_to
         }}

      DateTime.compare(action_time, authorization_valid_to) == :gt ->
        {:error, :authorization_expired,
         %{
           reason: :authorization_expired,
           action_time: action_time,
           authorization_valid_from: authorization_valid_from,
           authorization_valid_to: authorization_valid_to
         }}

      true ->
        {:ok,
         %{
           action_time: action_time,
           authorization_valid_from: authorization_valid_from,
           authorization_valid_to: authorization_valid_to
         }}
    end
  end

  defp run_check(:authorization_transaction_time_check, action, governance_record) do
    decision_time = fetch(action, :decision_time)
    authorization_recorded_at = fetch(governance_record, :authorization_recorded_at)

    if DateTime.compare(authorization_recorded_at, decision_time) == :gt do
      {:error, :authorization_valid_but_unknown_at_decision_time,
       %{
         reason: :recorded_after_decision,
         decision_time: decision_time,
         authorization_recorded_at: authorization_recorded_at
       }}
    else
      {:ok, %{decision_time: decision_time, authorization_recorded_at: authorization_recorded_at}}
    end
  end

  defp run_check(:transfer_expiration_check, action, governance_record) do
    action_time = fetch(action, :action_time)
    transfer_expires_at = fetch(governance_record, :transfer_expires_at)

    if DateTime.compare(action_time, transfer_expires_at) == :gt do
      {:error, :transfer_expired,
       %{
         reason: :transfer_expired,
         action_time: action_time,
         transfer_expires_at: transfer_expires_at
       }}
    else
      {:ok, %{action_time: action_time, transfer_expires_at: transfer_expires_at}}
    end
  end

  defp validate_governance_record(governance_record) do
    with true <- Enum.all?(@required_governance_fields, &has_field?(governance_record, &1)),
         true <- is_binary(fetch(governance_record, :proposal_id)),
         true <- is_binary(fetch(governance_record, :permission)),
         true <- is_boolean(fetch(governance_record, :quorum_met)),
         voting_closed_at when is_struct(voting_closed_at, DateTime) <-
           fetch(governance_record, :voting_closed_at),
         timelock_until when is_struct(timelock_until, DateTime) <-
           fetch(governance_record, :timelock_until),
         authorization_valid_from when is_struct(authorization_valid_from, DateTime) <-
           fetch(governance_record, :authorization_valid_from),
         authorization_valid_to when is_struct(authorization_valid_to, DateTime) <-
           fetch(governance_record, :authorization_valid_to),
         authorization_recorded_at when is_struct(authorization_recorded_at, DateTime) <-
           fetch(governance_record, :authorization_recorded_at),
         transfer_expires_at when is_struct(transfer_expires_at, DateTime) <-
           fetch(governance_record, :transfer_expires_at),
         true <- DateTime.compare(authorization_valid_from, authorization_valid_to) != :gt,
         true <- DateTime.compare(voting_closed_at, transfer_expires_at) != :gt,
         true <- DateTime.compare(timelock_until, transfer_expires_at) != :gt do
      :ok
    else
      _ -> {:error, :invalid_governance_record, :proposal_match_check}
    end
  end

  defp validate_action_timestamps(action) do
    action_time = fetch(action, :action_time)
    decision_time = fetch(action, :decision_time)

    if is_struct(action_time, DateTime) and is_struct(decision_time, DateTime) do
      :ok
    else
      {:error, :invalid_governance_record, :voting_window_check}
    end
  end

  defp proposed_action_trace(action) do
    %{
      event: :proposed_action,
      result: :observed,
      action_id: fetch(action, :action_id),
      action_type: fetch(action, :action_type),
      proposal_id: fetch(action, :proposal_id),
      actor: fetch(action, :actor)
    }
  end

  defp check_trace(event, result, details) do
    Map.merge(%{event: event, result: result}, details)
  end

  defp decision_trace(result, stop_reason) do
    %{event: :decision, result: result, stop_reason: stop_reason}
  end

  defp failure_reason(:authorization_valid_but_unknown_at_decision_time),
    do: :recorded_after_decision

  defp failure_reason(other), do: other

  defp reject(stop_reason, trace) do
    {:error,
     %{
       status: :rejected,
       stop_reason: stop_reason,
       trace: trace
     }}
  end

  defp has_field?(map, key) do
    Map.has_key?(map, key) or Map.has_key?(map, Atom.to_string(key))
  end

  defp fetch(map, key) do
    string_key = Atom.to_string(key)

    cond do
      Map.has_key?(map, key) -> Map.get(map, key)
      Map.has_key?(map, string_key) -> Map.get(map, string_key)
      true -> nil
    end
  end
end
