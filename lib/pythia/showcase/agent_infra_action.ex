defmodule Pythia.Showcase.AgentInfraAction do
  @moduledoc """
  Deterministic local showcase for agent infrastructure action safety reasoning.
  This module models decision-time replay / pre-execution reasoning and does not implement
  production infrastructure controls.
  """

  @supported_action_types MapSet.new([
                            "volume_delete",
                            "database_drop",
                            "secret_rotate",
                            "production_config_change",
                            "deployment_rollback"
                          ])

  @destructive_action_types MapSet.new(["volume_delete", "database_drop"])
  @broad_credential_scopes MapSet.new(["admin", "global_admin", "full_api"])
  @unsafe_backup_isolation MapSet.new(["same_resource", "same_volume"])

  @required_action_fields [
    :action_id,
    :action_type,
    :actor_id,
    :resource_id,
    :resource_type,
    :target_environment,
    :action_time,
    :decision_time
  ]

  @required_safety_context_fields [
    :credential_scope,
    :explicit_user_approval_present,
    :environment_scope_verified,
    :documentation_verified,
    :dry_run_completed,
    :backup_isolation,
    :decision_time_knowledge_present
  ]

  @check_order [
    :action_type_check,
    :destructive_action_check,
    :target_environment_check,
    :credential_scope_check,
    :approval_check,
    :environment_scope_check,
    :documentation_check,
    :dry_run_check,
    :backup_isolation_check,
    :decision_time_knowledge_check
  ]

  @artifact_type "pythia.agent_infra_action.decision_trace.v1"
  @integrity_algorithm "sha256"
  @evidence_keys MapSet.new(["artifact_type", "algorithm", "digest", "payload"])
  @export_payload_keys MapSet.new(["status", "stop_reason", "trace"])

  @spec evaluate(map(), map()) :: {:ok, map()} | {:error, map()}
  def evaluate(action, safety_context)
      when is_map(action) and not is_struct(action) and is_map(safety_context) and
             not is_struct(safety_context) do
    proposed_trace = [proposed_action_trace(action)]

    with :ok <- validate_action(action),
         :ok <- validate_safety_context(safety_context),
         {:ok, trace} <- run_checks(action, safety_context, proposed_trace) do
      {:ok,
       %{
         status: :accepted,
         stop_reason: :agent_infra_action_accepted,
         trace: trace ++ [decision_trace(:accept, :agent_infra_action_accepted)]
       }}
    else
      {:error, stop_reason, trace} when is_list(trace) ->
        reject(stop_reason, trace ++ [decision_trace(:reject, stop_reason)])

      {:error, stop_reason, failed_check, details}
      when is_atom(failed_check) and is_map(details) ->
        trace =
          proposed_trace ++
            [
              check_trace(failed_check, :fail, Map.put(details, :reason, stop_reason)),
              decision_trace(:reject, stop_reason)
            ]

        reject(stop_reason, trace)
    end
  end

  def evaluate(_action, _safety_context) do
    reject(:invalid_action_or_safety_context, [
      proposed_action_trace(%{}),
      decision_trace(:reject, :invalid_action_or_safety_context)
    ])
  end

  @spec export_result({:ok, map()} | {:error, map()}) :: map()
  def export_result({status, payload}) when status in [:ok, :error] and is_map(payload) do
    payload
    |> normalize_value()
    |> whitelist_payload_fields()
  end

  @spec export_digest({:ok, map()} | {:error, map()}) :: map()
  def export_digest(result) do
    result
    |> export_result()
    |> digest_export_payload()
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

  @spec verify_evidence(map()) :: {:ok, map()} | {:error, map()}
  def verify_evidence(evidence) when is_map(evidence) do
    artifact_type = evidence["artifact_type"]
    algorithm = evidence["algorithm"]
    digest = evidence["digest"]
    payload = evidence["payload"]

    cond do
      not valid_evidence_key_set?(evidence) ->
        rejected(:invalid_evidence_shape)

      not valid_evidence_shape?(artifact_type, algorithm, digest, payload) ->
        rejected(:invalid_evidence_shape)

      not valid_export_payload_shape?(payload) ->
        rejected(:invalid_evidence_shape)

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

  def verify_evidence(_evidence), do: rejected(:invalid_evidence_shape)

  @spec digest_export_payload(map()) :: map()
  def digest_export_payload(payload) when is_map(payload) do
    normalized_payload =
      payload
      |> normalize_value()
      |> whitelist_payload_fields()

    digest =
      normalized_payload
      |> canonical_encode()
      |> then(&:crypto.hash(:sha256, &1))
      |> Base.encode16(case: :lower)

    %{"algorithm" => @integrity_algorithm, "digest" => digest}
  end

  defp validate_action(action) do
    with :ok <- validate_required_fields(action, @required_action_fields, :invalid_action_shape),
         :ok <-
           validate_datetime_fields(action, [:action_time, :decision_time], :invalid_action_shape),
         :ok <-
           validate_string_fields(
             action,
             @required_action_fields -- [:action_time, :decision_time],
             :invalid_action_shape
           ),
         :ok <- validate_decision_time(action) do
      :ok
    end
  end

  defp validate_safety_context(safety_context) do
    with :ok <-
           validate_required_fields(
             safety_context,
             @required_safety_context_fields,
             :invalid_safety_context
           ),
         :ok <-
           validate_boolean_fields(safety_context, [
             :explicit_user_approval_present,
             :environment_scope_verified,
             :documentation_verified,
             :dry_run_completed,
             :decision_time_knowledge_present
           ]),
         :ok <-
           validate_string_fields(
             safety_context,
             [:credential_scope, :backup_isolation],
             :invalid_safety_context
           ) do
      :ok
    end
  end

  defp validate_required_fields(record, fields, stop_reason) do
    case Enum.find(fields, &(not Map.has_key?(record, &1))) do
      nil ->
        :ok

      missing_field ->
        {:error, stop_reason, :shape_validation_check, %{missing_field: missing_field}}
    end
  end

  defp validate_datetime_fields(record, fields, stop_reason) do
    case Enum.find(fields, &(not match?(%DateTime{}, record[&1]))) do
      nil ->
        :ok

      invalid_field ->
        {:error, stop_reason, :shape_validation_check,
         %{invalid_field: invalid_field, expected_type: :datetime}}
    end
  end

  defp validate_boolean_fields(record, fields) do
    case Enum.find(fields, &(not is_boolean(record[&1]))) do
      nil ->
        :ok

      invalid_field ->
        {:error, :invalid_safety_context, :shape_validation_check,
         %{invalid_field: invalid_field, expected_type: :boolean}}
    end
  end

  defp validate_string_fields(record, fields, stop_reason) do
    case Enum.find(fields, &(not valid_string?(record[&1]))) do
      nil ->
        :ok

      invalid_field ->
        {:error, stop_reason, :shape_validation_check,
         %{invalid_field: invalid_field, expected_type: :non_empty_string}}
    end
  end

  defp validate_decision_time(action) do
    case DateTime.compare(action.action_time, action.decision_time) do
      :gt ->
        {:error, :invalid_action_shape, :shape_validation_check,
         %{invalid_field: :decision_time, reason: :decision_time_before_action_time}}

      _ ->
        :ok
    end
  end

  defp run_checks(action, safety_context, trace) do
    Enum.reduce_while(@check_order, {:ok, trace}, fn check, {:ok, acc_trace} ->
      case run_check(check, action, safety_context) do
        {:ok, details} ->
          {:cont, {:ok, acc_trace ++ [check_trace(check, :pass, details)]}}

        {:error, stop_reason, details} ->
          fail_trace = acc_trace ++ [check_trace(check, :fail, details)]
          {:halt, {:error, stop_reason, fail_trace}}
      end
    end)
  end

  defp run_check(:action_type_check, action, _safety_context) do
    if MapSet.member?(@supported_action_types, action.action_type) do
      {:ok, %{action_type: action.action_type, action_id: action.action_id}}
    else
      {:error, :unsupported_action_type,
       %{
         action_type: action.action_type,
         action_id: action.action_id,
         reason: :unsupported_action_type
       }}
    end
  end

  defp run_check(:destructive_action_check, action, safety_context) do
    destructive = MapSet.member?(@destructive_action_types, action.action_type)

    cond do
      destructive and not safety_context.explicit_user_approval_present ->
        {:error, :destructive_action_requires_explicit_approval,
         %{
           action_type: action.action_type,
           action_id: action.action_id,
           target_environment: action.target_environment,
           reason: :destructive_action_requires_explicit_approval
         }}

      true ->
        {:ok,
         %{
           action_type: action.action_type,
           action_id: action.action_id,
           destructive_action: destructive
         }}
    end
  end

  defp run_check(:target_environment_check, action, safety_context) do
    if action.target_environment == "production" and not safety_context.environment_scope_verified do
      {:error, :production_target_requires_verified_scope,
       %{
         target_environment: action.target_environment,
         action_id: action.action_id,
         environment_scope_verified: safety_context.environment_scope_verified,
         reason: :production_target_requires_verified_scope
       }}
    else
      {:ok,
       %{
         action_id: action.action_id,
         target_environment: action.target_environment,
         environment_scope_verified: safety_context.environment_scope_verified
       }}
    end
  end

  defp run_check(:credential_scope_check, action, safety_context) do
    if MapSet.member?(@broad_credential_scopes, safety_context.credential_scope) do
      {:error, :credential_scope_too_broad,
       %{
         action_id: action.action_id,
         credential_scope: safety_context.credential_scope,
         reason: :credential_scope_too_broad
       }}
    else
      {:ok, %{action_id: action.action_id, credential_scope: safety_context.credential_scope}}
    end
  end

  defp run_check(:approval_check, action, safety_context) do
    if action.target_environment == "production" and
         not safety_context.explicit_user_approval_present do
      {:error, :missing_explicit_user_approval,
       %{
         action_id: action.action_id,
         target_environment: action.target_environment,
         explicit_user_approval_present: safety_context.explicit_user_approval_present,
         reason: :missing_explicit_user_approval
       }}
    else
      {:ok,
       %{
         action_id: action.action_id,
         explicit_user_approval_present: safety_context.explicit_user_approval_present
       }}
    end
  end

  defp run_check(:environment_scope_check, action, safety_context) do
    if not safety_context.environment_scope_verified do
      {:error, :environment_scope_not_verified,
       %{
         action_id: action.action_id,
         target_environment: action.target_environment,
         environment_scope_verified: false,
         reason: :environment_scope_not_verified
       }}
    else
      {:ok, %{action_id: action.action_id, environment_scope_verified: true}}
    end
  end

  defp run_check(:documentation_check, action, safety_context) do
    if not safety_context.documentation_verified do
      {:error, :documentation_not_verified,
       %{
         action_id: action.action_id,
         resource_id: action.resource_id,
         documentation_verified: false,
         reason: :documentation_not_verified
       }}
    else
      {:ok, %{action_id: action.action_id, documentation_verified: true}}
    end
  end

  defp run_check(:dry_run_check, action, safety_context) do
    if not safety_context.dry_run_completed do
      {:error, :dry_run_not_completed,
       %{
         action_id: action.action_id,
         resource_id: action.resource_id,
         dry_run_completed: false,
         reason: :dry_run_not_completed
       }}
    else
      {:ok, %{action_id: action.action_id, dry_run_completed: true}}
    end
  end

  defp run_check(:backup_isolation_check, action, safety_context) do
    if MapSet.member?(@unsafe_backup_isolation, safety_context.backup_isolation) do
      {:error, :backup_not_isolated_from_target,
       %{
         action_id: action.action_id,
         resource_id: action.resource_id,
         backup_isolation: safety_context.backup_isolation,
         reason: :backup_not_isolated_from_target
       }}
    else
      {:ok, %{action_id: action.action_id, backup_isolation: safety_context.backup_isolation}}
    end
  end

  defp run_check(:decision_time_knowledge_check, action, safety_context) do
    if safety_context.decision_time_knowledge_present do
      {:ok,
       %{
         action_id: action.action_id,
         decision_time: action.decision_time,
         decision_time_knowledge_present: true
       }}
    else
      {:error, :missing_decision_time_knowledge,
       %{
         action_id: action.action_id,
         decision_time: action.decision_time,
         decision_time_knowledge_present: false,
         reason: :missing_decision_time_knowledge
       }}
    end
  end

  defp whitelist_payload_fields(export) do
    keys = export |> Map.keys() |> MapSet.new()

    unless MapSet.equal?(keys, @export_payload_keys) do
      raise ArgumentError, "export payload must contain only status, stop_reason, trace"
    end

    status = Map.fetch!(export, "status")
    stop_reason = Map.fetch!(export, "stop_reason")
    trace = Map.fetch!(export, "trace")

    unless status in ["accepted", "rejected"] do
      raise ArgumentError, "unsupported export status: #{inspect(status)}"
    end

    unless is_list(trace) do
      raise ArgumentError, "trace must be a list, got: #{inspect(trace)}"
    end

    %{"status" => status, "stop_reason" => stop_reason, "trace" => trace}
  end

  defp valid_evidence_shape?(artifact_type, algorithm, digest, payload) do
    is_binary(artifact_type) and is_binary(algorithm) and valid_digest?(digest) and
      is_map(payload)
  end

  defp valid_export_payload_shape?(payload) when is_map(payload) do
    payload_keys = payload |> Map.keys() |> MapSet.new()

    payload_keys == @export_payload_keys and
      payload["status"] in ["accepted", "rejected"] and
      is_list(payload["trace"])
  end

  defp valid_export_payload_shape?(_payload), do: false

  defp valid_evidence_key_set?(evidence) when is_map(evidence) do
    evidence
    |> Map.keys()
    |> MapSet.new()
    |> MapSet.equal?(@evidence_keys)
  end

  defp valid_evidence_key_set?(_evidence), do: false

  defp valid_digest?(digest),
    do: is_binary(digest) and String.match?(digest, ~r/\A[0-9a-f]{64}\z/)

  defp proposed_action_trace(action) do
    %{
      event: :proposed_action,
      result: :observed,
      action_id: action[:action_id],
      action_type: action[:action_type],
      actor_id: action[:actor_id],
      resource_id: action[:resource_id],
      resource_type: action[:resource_type],
      target_environment: action[:target_environment]
    }
  end

  defp check_trace(check, result, details),
    do: Map.merge(%{event: check, result: result}, details)

  defp decision_trace(result, stop_reason),
    do: %{event: :decision, result: result, stop_reason: stop_reason}

  defp reject(stop_reason, trace),
    do: {:error, %{status: :rejected, stop_reason: stop_reason, trace: trace}}

  defp rejected(reason), do: {:error, %{status: :rejected, reason: reason}}

  defp valid_string?(value), do: is_binary(value) and String.trim(value) != ""

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
  defp canonical_encode(value) when is_integer(value), do: Integer.to_string(value)
  defp canonical_encode(value) when is_float(value), do: :erlang.float_to_binary(value, [:short])
  defp canonical_encode(true), do: "true"
  defp canonical_encode(false), do: "false"
  defp canonical_encode(nil), do: "null"

  defp escape_string(value) do
    value
    |> String.to_charlist()
    |> Enum.map_join(&escape_codepoint/1)
  end

  defp escape_codepoint(?\\), do: "\\\\"
  defp escape_codepoint(?"), do: "\\\""
  defp escape_codepoint(?\n), do: "\\n"
  defp escape_codepoint(?\r), do: "\\r"
  defp escape_codepoint(?\t), do: "\\t"
  defp escape_codepoint(?\b), do: "\\b"
  defp escape_codepoint(?\f), do: "\\f"

  defp escape_codepoint(codepoint) when codepoint in 0..31 do
    "\\u" <> (codepoint |> Integer.to_string(16) |> String.pad_leading(4, "0"))
  end

  defp escape_codepoint(codepoint), do: <<codepoint::utf8>>
end
