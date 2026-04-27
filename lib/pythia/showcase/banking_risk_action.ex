defmodule Pythia.Showcase.BankingRiskAction do
  @moduledoc """
  Deterministic local showcase for banking AI-risk pre-execution action control.
  """

  @supported_action_types MapSet.new([
                            "fraud_response",
                            "account_restriction",
                            "vulnerability_escalation",
                            "treasury_hold",
                            "incident_escalation"
                          ])

  @required_action_fields [
    :action_id,
    :action_type,
    :operator_id,
    :action_time,
    :decision_time
  ]

  @required_governance_fields [
    :authorization_valid_from,
    :authorization_valid_to,
    :authorization_recorded_at,
    :evidence_observed_at,
    :evidence_valid_until,
    :decision_time_knowledge_present,
    :operator_approval_present
  ]

  @check_order [
    :action_type_check,
    :authorization_valid_time_check,
    :authorization_decision_time_check,
    :evidence_freshness_check,
    :decision_time_knowledge_check,
    :operator_approval_check
  ]

  @artifact_type "pythia.banking_risk_action.decision_trace.v1"
  @integrity_algorithm "sha256"

  @spec evaluate(map(), map()) :: {:ok, map()} | {:error, map()}
  def evaluate(action, governance_record) when is_map(action) and is_map(governance_record) do
    proposed_trace = [proposed_action_trace(action)]

    with :ok <- validate_action(action),
         :ok <- validate_governance_record(governance_record),
         {:ok, trace} <- run_checks(action, governance_record, proposed_trace) do
      {:ok,
       %{
         status: :accepted,
         stop_reason: :banking_risk_action_accepted,
         trace: trace ++ [decision_trace(:accept, :banking_risk_action_accepted)]
       }}
    else
      {:error, stop_reason, trace} when is_list(trace) ->
        reject(stop_reason, trace ++ [decision_trace(:reject, stop_reason)])

      {:error, stop_reason, failed_check} when is_atom(failed_check) ->
        trace =
          proposed_trace ++
            [
              check_trace(failed_check, :fail, %{reason: stop_reason}),
              decision_trace(:reject, stop_reason)
            ]

        reject(stop_reason, trace)
    end
  end

  def evaluate(_action, _governance_record) do
    reject(:invalid_action_or_governance_record, [
      proposed_action_trace(%{}),
      decision_trace(:reject, :invalid_action_or_governance_record)
    ])
  end

  @spec export_result({:ok, map()} | {:error, map()}) :: map()
  def export_result({status, payload}) when status in [:ok, :error] and is_map(payload) do
    payload
    |> normalize_value()
    |> ensure_export_status()
  end

  @spec export_digest({:ok, map()} | {:error, map()}) :: map()
  def export_digest(result) do
    digest =
      result
      |> export_result()
      |> canonical_encode()
      |> then(&:crypto.hash(:sha256, &1))
      |> Base.encode16(case: :lower)

    %{"algorithm" => @integrity_algorithm, "digest" => digest}
  end

  @spec export_evidence({:ok, map()} | {:error, map()}) :: map()
  def export_evidence(result) do
    payload = export_result(result)
    digest = digest_payload(payload)

    %{
      "artifact_type" => @artifact_type,
      "algorithm" => digest["algorithm"],
      "digest" => digest["digest"],
      "payload" => payload
    }
  end

  @spec verify_evidence(map()) :: {:ok, map()} | {:error, map()}
  def verify_evidence(evidence) when is_map(evidence) do
    artifact_type = evidence["artifact_type"]
    algorithm = evidence["algorithm"]
    digest = evidence["digest"]
    payload = evidence["payload"]

    cond do
      not valid_evidence_shape?(artifact_type, algorithm, digest, payload) ->
        rejected(:invalid_evidence_shape)

      artifact_type != @artifact_type ->
        rejected(:unsupported_artifact_type)

      algorithm != @integrity_algorithm ->
        rejected(:unsupported_algorithm)

      true ->
        actual_digest = digest_payload(payload)["digest"]

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

  def verify_evidence(_evidence), do: rejected(:invalid_evidence_shape)

  defp validate_action(action) do
    with :ok <- validate_required_fields(action, @required_action_fields, :invalid_action_shape),
         :ok <-
           validate_datetime_fields(action, [:action_time, :decision_time], :invalid_action_shape),
         :ok <- validate_decision_time(action) do
      :ok
    end
  end

  defp validate_governance_record(governance_record) do
    datetime_fields = [
      :authorization_valid_from,
      :authorization_valid_to,
      :authorization_recorded_at,
      :evidence_observed_at,
      :evidence_valid_until
    ]

    with :ok <-
           validate_required_fields(
             governance_record,
             @required_governance_fields,
             :invalid_governance_record
           ),
         :ok <-
           validate_datetime_fields(
             governance_record,
             datetime_fields,
             :invalid_governance_record
           ),
         :ok <- validate_boolean_field(governance_record, :decision_time_knowledge_present),
         :ok <- validate_boolean_field(governance_record, :operator_approval_present) do
      :ok
    end
  end

  defp validate_required_fields(record, fields, stop_reason) do
    if Enum.all?(fields, &Map.has_key?(record, &1)) do
      :ok
    else
      {:error, stop_reason, :shape_validation_check}
    end
  end

  defp validate_datetime_fields(record, fields, stop_reason) do
    if Enum.all?(fields, &match?(%DateTime{}, record[&1])) do
      :ok
    else
      {:error, stop_reason, :shape_validation_check}
    end
  end

  defp validate_boolean_field(record, field) do
    if is_boolean(record[field]) do
      :ok
    else
      {:error, :invalid_governance_record, :shape_validation_check}
    end
  end

  defp validate_decision_time(action) do
    case DateTime.compare(action.action_time, action.decision_time) do
      :gt -> {:error, :decision_time_before_action_time, :decision_time_check}
      _ -> :ok
    end
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

  defp run_check(:action_type_check, action, _governance_record) do
    action_type = action.action_type

    if MapSet.member?(@supported_action_types, action_type) do
      {:ok, %{action_type: action_type}}
    else
      {:error, :unsupported_action_type,
       %{action_type: action_type, reason: :unsupported_action_type}}
    end
  end

  defp run_check(:authorization_valid_time_check, action, governance_record) do
    action_time = action.action_time
    valid_from = governance_record.authorization_valid_from
    valid_to = governance_record.authorization_valid_to

    cond do
      DateTime.compare(action_time, valid_from) == :lt ->
        {:error, :authorization_not_yet_valid,
         %{reason: :authorization_not_yet_valid, action_time: action_time, valid_from: valid_from}}

      DateTime.compare(action_time, valid_to) == :gt ->
        {:error, :authorization_expired,
         %{reason: :authorization_expired, action_time: action_time, valid_to: valid_to}}

      true ->
        {:ok, %{action_time: action_time, valid_from: valid_from, valid_to: valid_to}}
    end
  end

  defp run_check(:authorization_decision_time_check, action, governance_record) do
    decision_time = action.decision_time
    authorization_recorded_at = governance_record.authorization_recorded_at

    if DateTime.compare(authorization_recorded_at, decision_time) in [:lt, :eq] do
      {:ok,
       %{
         decision_time: decision_time,
         authorization_recorded_at: authorization_recorded_at
       }}
    else
      {:error, :authorization_unknown_at_decision_time,
       %{
         reason: :authorization_unknown_at_decision_time,
         decision_time: decision_time,
         authorization_recorded_at: authorization_recorded_at
       }}
    end
  end

  defp run_check(:evidence_freshness_check, action, governance_record) do
    decision_time = action.decision_time
    observed_at = governance_record.evidence_observed_at
    valid_until = governance_record.evidence_valid_until

    cond do
      DateTime.compare(valid_until, decision_time) == :lt ->
        {:error, :stale_evidence,
         %{
           reason: :stale_evidence,
           evidence_observed_at: observed_at,
           evidence_valid_until: valid_until,
           decision_time: decision_time
         }}

      DateTime.compare(observed_at, decision_time) == :gt ->
        {:error, :evidence_recorded_after_decision_time,
         %{
           reason: :evidence_recorded_after_decision_time,
           evidence_observed_at: observed_at,
           decision_time: decision_time
         }}

      true ->
        {:ok,
         %{
           evidence_observed_at: observed_at,
           evidence_valid_until: valid_until,
           decision_time: decision_time
         }}
    end
  end

  defp run_check(:decision_time_knowledge_check, _action, governance_record) do
    if governance_record.decision_time_knowledge_present do
      {:ok, %{decision_time_knowledge_present: true}}
    else
      {:error, :missing_decision_time_knowledge,
       %{reason: :missing_decision_time_knowledge, decision_time_knowledge_present: false}}
    end
  end

  defp run_check(:operator_approval_check, _action, governance_record) do
    if governance_record.operator_approval_present do
      {:ok, %{operator_approval_present: true}}
    else
      {:error, :missing_operator_approval,
       %{reason: :missing_operator_approval, operator_approval_present: false}}
    end
  end

  defp ensure_export_status(export) do
    status = if export["status"] == "accepted", do: "accepted", else: "rejected"

    %{
      "status" => status,
      "stop_reason" => export["stop_reason"],
      "trace" => export["trace"] || []
    }
  end

  defp digest_payload(payload) do
    digest =
      payload
      |> canonical_encode()
      |> then(&:crypto.hash(:sha256, &1))
      |> Base.encode16(case: :lower)

    %{"algorithm" => @integrity_algorithm, "digest" => digest}
  end

  defp valid_evidence_shape?(artifact_type, algorithm, digest, payload) do
    is_binary(artifact_type) and is_binary(algorithm) and valid_digest?(digest) and
      is_map(payload)
  end

  defp valid_digest?(digest),
    do: is_binary(digest) and String.match?(digest, ~r/\A[0-9a-f]{64}\z/)

  defp proposed_action_trace(action) do
    %{
      event: :proposed_action,
      result: :observed,
      action_id: action[:action_id],
      action_type: action[:action_type],
      operator_id: action[:operator_id]
    }
  end

  defp check_trace(check, result, details),
    do: Map.merge(%{event: check, result: result}, details)

  defp decision_trace(result, stop_reason),
    do: %{event: :decision, result: result, stop_reason: stop_reason}

  defp reject(stop_reason, trace),
    do: {:error, %{status: :rejected, stop_reason: stop_reason, trace: trace}}

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

  defp canonical_encode(value) when is_binary(value), do: "\"" <> escape_string(value) <> "\""
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
end
