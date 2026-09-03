defmodule Pythia.Interop.ExternalEvidence do
  @moduledoc """
  Fail-closed intake for ContractGraph-QA bounded evidence and LiminalQA
  candidate seeds.

  A structurally valid external artifact is advisory context only. This
  adapter always returns `ESCALATE` and requires the normal Pythia gate to
  evaluate current authorization, credentials, environment, and recovery
  readiness. Invalid or ambiguous input returns `BLOCK`.
  """

  @assessment_schema "org.pythialabs.external-evidence-assessment.v0.1"
  @cgqa_schema "org.contractgraph-qa.liminalqa-evidence.v0.1"
  @cgqa_profile "org.contractgraph-qa.bounded-invariant-evidence.v0.1"
  @candidate_schema "org.liminalqa.cgqa-candidates.v0.1"
  @candidate_profile "org.liminalqa.non-authoritative-candidate-seeds.v0.1"
  @schema_pins %{
    @cgqa_schema => "53b0b4a0b1f4d77de26b8be9dbb90006ea0bd30c5cd3960a2f3e7d44d9664184",
    @candidate_schema => "896e32921d41925a976fef5d0ba561a08bd1f2265a08bc9ccf5065a3238a4f60"
  }

  @cgqa_keys MapSet.new(~w(
    schema profile exportId producer subject identity times adapter bound assessment checks
    artifacts causalParents verificationDebt limitations authority
  ))
  @candidate_keys MapSet.new(~w(
    schema profile exportId producer sourceEvidence subject identity derivedAt authority
    candidates causalParents limitations verificationDebt
  ))
  @subject_keys MapSet.new(~w(repository commitSha contract network scopeId))
  @identity_keys MapSet.new(~w(traceId operationId attemptId))
  @safe_id ~r/\A[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\z/
  @sha256 ~r/\A[0-9a-f]{64}\z/

  @spec evaluate_json(binary()) :: {:ok, map()} | {:error, map()}
  def evaluate_json(json) when is_binary(json) do
    with {:ok, ordered} <- decode_ordered(json),
         {:ok, decoded} <- normalize_ordered(ordered),
         {:ok, source} <- validate_source(decoded) do
      {:ok, assessment(source, json)}
    else
      {:error, error} when is_map(error) -> {:error, blocked(error)}
    end
  end

  def evaluate_json(_), do: {:error, blocked(error("invalid_input", "input must be JSON bytes"))}

  defp decode_ordered(json) do
    case Jason.decode(json, objects: :ordered_objects, strings: :copy) do
      {:ok, value} -> {:ok, value}
      {:error, exception} -> {:error, error("invalid_json", Exception.message(exception))}
    end
  end

  # Ordered-object decoding preserves duplicate properties long enough for the
  # boundary to reject them instead of accepting a parser-dependent winner.
  defp normalize_ordered(%Jason.OrderedObject{values: pairs}) do
    keys = Enum.map(pairs, &elem(&1, 0))

    if length(keys) != MapSet.size(MapSet.new(keys)) do
      duplicate = keys |> Enum.frequencies() |> Enum.find(fn {_key, count} -> count > 1 end) |> elem(0)
      {:error, error("duplicate_json_key", "duplicate JSON object key: #{duplicate}")}
    else
      Enum.reduce_while(pairs, {:ok, %{}}, fn {key, value}, {:ok, result} ->
        case normalize_ordered(value) do
          {:ok, normalized} -> {:cont, {:ok, Map.put(result, key, normalized)}}
          {:error, _} = failure -> {:halt, failure}
        end
      end)
    end
  end

  defp normalize_ordered(values) when is_list(values) do
    Enum.reduce_while(values, {:ok, []}, fn value, {:ok, result} ->
      case normalize_ordered(value) do
        {:ok, normalized} -> {:cont, {:ok, [normalized | result]}}
        {:error, _} = failure -> {:halt, failure}
      end
    end)
    |> case do
      {:ok, reversed} -> {:ok, Enum.reverse(reversed)}
      failure -> failure
    end
  end

  defp normalize_ordered(value), do: {:ok, value}

  defp validate_source(%{"schema" => @cgqa_schema} = source) do
    with :ok <- exact_keys(source, @cgqa_keys, "evidence"),
         :ok <- equals(source["profile"], @cgqa_profile, "evidence.profile"),
         :ok <- safe_id(source["exportId"], "evidence.exportId"),
         :ok <- producer(source["producer"], "contractgraph-qa", "evidence.producer"),
         :ok <- subject(source["subject"], "evidence.subject"),
         :ok <- identity(source["identity"], "evidence.identity"),
         :ok <- evidence_times(source["times"]),
         :ok <- evidence_adapter(source["adapter"]),
         :ok <- evidence_assessment(source["assessment"], source["checks"], source["bound"]),
         :ok <- evidence_artifacts(source["artifacts"]),
         :ok <- safe_id_list(source["causalParents"], "evidence.causalParents", true),
         :ok <- evidence_debt(source["verificationDebt"], source["checks"]),
         :ok <- non_blank_list(source["limitations"], "evidence.limitations"),
         :ok <- evidence_authority(source["authority"]) do
      {:ok,
       %{
         schema: source["schema"],
         export_id: source["exportId"],
         subject: source["subject"],
         identity: source["identity"],
         semantics: "bounded_evidence"
       }}
    end
  end

  defp validate_source(%{"schema" => @candidate_schema} = source) do
    with :ok <- exact_keys(source, @candidate_keys, "candidateExport"),
         :ok <- equals(source["profile"], @candidate_profile, "candidateExport.profile"),
         :ok <- safe_id(source["exportId"], "candidateExport.exportId"),
         :ok <- producer(source["producer"], "liminalqa", "candidateExport.producer"),
         :ok <- source_evidence(source["sourceEvidence"]),
         :ok <- subject(source["subject"], "candidateExport.subject"),
         :ok <- identity(source["identity"], "candidateExport.identity"),
         {:ok, _} <- timestamp(source["derivedAt"], "candidateExport.derivedAt"),
         :ok <- candidate_authority(source["authority"]),
         :ok <- candidates(source["candidates"]),
         :ok <- candidate_debt(source["verificationDebt"], source["candidates"]),
         :ok <- causal_parent(source["causalParents"], source["sourceEvidence"]["exportId"]),
         :ok <- non_blank_list(source["limitations"], "candidateExport.limitations") do
      {:ok,
       %{
         schema: source["schema"],
         export_id: source["exportId"],
         subject: source["subject"],
         identity: source["identity"],
         semantics: "non_authoritative_seed"
       }}
    end
  end

  defp validate_source(%{"schema" => schema}) when is_binary(schema),
    do: {:error, error("unsupported_schema", "unsupported external evidence schema: #{schema}")}

  defp validate_source(_),
    do: {:error, error("invalid_profile", "JSON root must contain a supported schema")}

  defp producer(value, expected_name, field) when is_map(value) do
    with :ok <- exact_keys(value, MapSet.new(~w(name version)), field),
         :ok <- equals(value["name"], expected_name, "#{field}.name"),
         :ok <- non_blank(value["version"], "#{field}.version") do
      :ok
    end
  end

  defp producer(_, _, field), do: {:error, error("invalid_profile", "#{field} must be an object")}

  defp subject(value, field) when is_map(value) do
    with :ok <- exact_keys(value, @subject_keys, field),
         :ok <- non_blank(value["repository"], "#{field}.repository"),
         :ok <- matches(value["commitSha"], ~r/\A[0-9a-f]{40}\z/, "#{field}.commitSha"),
         :ok <- non_blank(value["contract"], "#{field}.contract"),
         :ok <- non_blank(value["network"], "#{field}.network"),
         :ok <- non_blank(value["scopeId"], "#{field}.scopeId") do
      :ok
    end
  end

  defp subject(_, field), do: {:error, error("invalid_profile", "#{field} must be an object")}

  defp identity(value, field) when is_map(value) do
    with :ok <- exact_keys(value, @identity_keys, field),
         :ok <- safe_id(value["traceId"], "#{field}.traceId"),
         :ok <- safe_id(value["operationId"], "#{field}.operationId"),
         :ok <- safe_id(value["attemptId"], "#{field}.attemptId") do
      :ok
    end
  end

  defp identity(_, field), do: {:error, error("invalid_profile", "#{field} must be an object")}

  defp evidence_times(value) when is_map(value) do
    with :ok <- exact_keys(value, MapSet.new(~w(validAt observedAt recordedAt)), "evidence.times"),
         {:ok, valid_at} <- timestamp(value["validAt"], "evidence.times.validAt"),
         {:ok, observed_at} <- timestamp(value["observedAt"], "evidence.times.observedAt"),
         {:ok, recorded_at} <- timestamp(value["recordedAt"], "evidence.times.recordedAt"),
         :ok <- ordered_times(valid_at, observed_at, recorded_at) do
      :ok
    end
  end

  defp evidence_times(_),
    do: {:error, error("invalid_profile", "evidence.times must be an object")}

  defp ordered_times(valid_at, observed_at, recorded_at) do
    if DateTime.compare(valid_at, observed_at) in [:lt, :eq] and
         DateTime.compare(observed_at, recorded_at) in [:lt, :eq] do
      :ok
    else
      {:error,
       error(
         "temporal_inversion",
         "evidence.times must satisfy validAt <= observedAt <= recordedAt"
       )}
    end
  end

  defp evidence_adapter(value) when is_map(value) do
    with :ok <- exact_keys(value, MapSet.new(~w(id version digest)), "evidence.adapter"),
         :ok <- non_blank(value["id"], "evidence.adapter.id"),
         :ok <- non_blank(value["version"], "evidence.adapter.version"),
         :ok <- digest(value["digest"], "evidence.adapter.digest") do
      :ok
    end
  end

  defp evidence_adapter(_),
    do: {:error, error("invalid_profile", "evidence.adapter must be an object")}

  defp digest(value, field) when is_map(value) do
    with :ok <- exact_keys(value, MapSet.new(~w(algorithm value)), field),
         :ok <- equals(value["algorithm"], "sha256", "#{field}.algorithm"),
         :ok <- matches(value["value"], @sha256, "#{field}.value") do
      :ok
    end
  end

  defp digest(_, field), do: {:error, error("invalid_profile", "#{field} must be an object")}

  defp evidence_assessment(assessment, checks, bound)
       when is_map(assessment) and is_list(checks) and is_map(bound) do
    with :ok <-
           exact_keys(
             assessment,
             MapSet.new(~w(kind statusVocabulary counts continuityVerdict)),
             "evidence.assessment"
           ),
         :ok <- equals(assessment["kind"], "bounded_invariant_search", "evidence.assessment.kind"),
         :ok <-
           equals(
             assessment["statusVocabulary"],
             ["violated", "not_found_within_bound", "inconclusive"],
             "evidence.assessment.statusVocabulary"
           ),
         :ok <-
           equals(
             assessment["continuityVerdict"],
             "not_computed",
             "evidence.assessment.continuityVerdict"
           ),
         {:ok, actual_counts, explored} <- invariant_checks(checks),
         :ok <- count_map(assessment["counts"], actual_counts),
         :ok <- search_bound(bound, explored) do
      :ok
    end
  end

  defp evidence_assessment(_, _, _),
    do: {:error, error("invalid_profile", "evidence assessment/checks/bound shape is invalid")}

  defp invariant_checks([]),
    do: {:error, error("invalid_profile", "evidence.checks must be non-empty")}

  defp invariant_checks(checks) do
    initial = {:ok, %{"violated" => 0, "not_found_within_bound" => 0, "inconclusive" => 0}, 0, MapSet.new()}

    Enum.reduce_while(checks, initial, fn check, {:ok, counts, explored, seen} ->
      case invariant_check(check, seen) do
        {:ok, status, count, next_seen} ->
          {:cont, {:ok, Map.update!(counts, status, &(&1 + 1)), explored + count, next_seen}}

        {:error, _} = failure ->
          {:halt, failure}
      end
    end)
    |> case do
      {:ok, counts, explored, _seen} -> {:ok, counts, explored}
      failure -> failure
    end
  end

  defp invariant_check(check, seen) when is_map(check) do
    status = check["status"]
    common = MapSet.new(~w(invariantId title severity status exploredCandidates notes))
    expected = if status == "violated", do: MapSet.union(common, MapSet.new(~w(findingId pathLength))), else: common

    with :ok <- exact_keys(check, expected, "evidence.checks[]"),
         :ok <- safe_id(check["invariantId"], "evidence.checks[].invariantId"),
         :ok <- unique_id(check["invariantId"], seen, "evidence.checks[].invariantId"),
         :ok <- member(status, ~w(violated not_found_within_bound inconclusive), "evidence.checks[].status"),
         :ok <- non_blank(check["title"], "evidence.checks[].title"),
         :ok <- member(check["severity"], ~w(critical high medium low info), "evidence.checks[].severity"),
         :ok <- non_negative_integer(check["exploredCandidates"], "evidence.checks[].exploredCandidates"),
         :ok <- non_blank(check["notes"], "evidence.checks[].notes"),
         :ok <- violation_fields(check, status) do
      {:ok, status, check["exploredCandidates"], MapSet.put(seen, check["invariantId"])}
    end
  end

  defp invariant_check(_, _),
    do: {:error, error("invalid_profile", "evidence.checks[] must be an object")}

  defp violation_fields(check, "violated") do
    with :ok <- safe_id(check["findingId"], "evidence.checks[].findingId"),
         :ok <- positive_integer(check["pathLength"], "evidence.checks[].pathLength") do
      :ok
    end
  end

  defp violation_fields(_, _), do: :ok

  defp count_map(value, actual) when is_map(value) do
    with :ok <- exact_keys(value, MapSet.new(~w(violated not_found_within_bound inconclusive)), "evidence.assessment.counts"),
         :ok <- equals(value, actual, "evidence.assessment.counts") do
      :ok
    end
  end

  defp count_map(_, _),
    do: {:error, error("invalid_profile", "evidence.assessment.counts must be an object")}

  defp search_bound(value, explored) do
    with :ok <- exact_keys(value, MapSet.new(~w(searchRunId maxDepth exploredCandidates replay)), "evidence.bound"),
         :ok <- safe_id(value["searchRunId"], "evidence.bound.searchRunId"),
         :ok <- positive_integer(value["maxDepth"], "evidence.bound.maxDepth"),
         :ok <- equals(value["exploredCandidates"], explored, "evidence.bound.exploredCandidates"),
         :ok <- non_blank(value["replay"], "evidence.bound.replay") do
      :ok
    end
  end

  defp evidence_artifacts([]),
    do: {:error, error("invalid_profile", "evidence.artifacts must be non-empty")}

  defp evidence_artifacts(artifacts) when is_list(artifacts) do
    Enum.reduce_while(artifacts, {:ok, MapSet.new()}, fn artifact, {:ok, seen} ->
      result =
        with true <- is_map(artifact),
             :ok <- exact_keys(artifact, MapSet.new(~w(artifactId mediaType sha256 bytes)), "evidence.artifacts[]"),
             :ok <- safe_id(artifact["artifactId"], "evidence.artifacts[].artifactId"),
             :ok <- unique_id(artifact["artifactId"], seen, "evidence.artifacts[].artifactId"),
             :ok <- non_blank(artifact["mediaType"], "evidence.artifacts[].mediaType"),
             :ok <- matches(artifact["sha256"], @sha256, "evidence.artifacts[].sha256"),
             :ok <- positive_integer(artifact["bytes"], "evidence.artifacts[].bytes") do
          {:ok, MapSet.put(seen, artifact["artifactId"])}
        else
          false -> {:error, error("invalid_profile", "evidence.artifacts[] must be an object")}
          {:error, _} = failure -> failure
        end

      case result do
        {:ok, next_seen} -> {:cont, {:ok, next_seen}}
        {:error, _} = failure -> {:halt, failure}
      end
    end)
    |> case do
      {:ok, _seen} -> :ok
      failure -> failure
    end
  end

  defp evidence_artifacts(_),
    do: {:error, error("invalid_profile", "evidence.artifacts must be an array")}

  defp evidence_authority(value) when is_map(value) do
    with :ok <-
           exact_keys(
             value,
             MapSet.new(~w(classification mayAuthorizeAction actionAuthorization continuityVerdictOwner)),
             "evidence.authority"
           ),
         :ok <- equals(value["classification"], "evidence_only", "evidence.authority.classification"),
         :ok <- equals(value["mayAuthorizeAction"], false, "evidence.authority.mayAuthorizeAction"),
         :ok <- equals(value["actionAuthorization"], "not_evaluated", "evidence.authority.actionAuthorization"),
         :ok <- equals(value["continuityVerdictOwner"], "ltp", "evidence.authority.continuityVerdictOwner") do
      :ok
    end
  end

  defp evidence_authority(_),
    do: {:error, error("invalid_profile", "evidence.authority must be an object")}

  defp source_evidence(value) when is_map(value) do
    with :ok <- exact_keys(value, MapSet.new(~w(schema exportId sha256)), "candidateExport.sourceEvidence"),
         :ok <- equals(value["schema"], @cgqa_schema, "candidateExport.sourceEvidence.schema"),
         :ok <- safe_id(value["exportId"], "candidateExport.sourceEvidence.exportId"),
         :ok <- matches(value["sha256"], @sha256, "candidateExport.sourceEvidence.sha256") do
      :ok
    end
  end

  defp source_evidence(_),
    do: {:error, error("invalid_profile", "candidateExport.sourceEvidence must be an object")}

  defp candidate_authority(value) when is_map(value) do
    with :ok <-
           exact_keys(
             value,
             MapSet.new(~w(classification mayAuthorizeAction requiresCgqaVerification)),
             "candidateExport.authority"
           ),
         :ok <- equals(value["classification"], "non_authoritative_seed", "candidateExport.authority.classification"),
         :ok <- equals(value["mayAuthorizeAction"], false, "candidateExport.authority.mayAuthorizeAction"),
         :ok <- equals(value["requiresCgqaVerification"], true, "candidateExport.authority.requiresCgqaVerification") do
      :ok
    end
  end

  defp candidate_authority(_),
    do: {:error, error("invalid_profile", "candidateExport.authority must be an object")}

  defp candidates(values) when is_list(values) do
    expected = MapSet.new(~w(candidateId invariantId sourceStatus kind priority reason requiredChecks))

    Enum.reduce_while(values, {:ok, MapSet.new(), MapSet.new()}, fn candidate,
                                                                   {:ok, seen_ids,
                                                                    seen_invariants} ->
      result =
        with true <- is_map(candidate),
             :ok <- exact_keys(candidate, expected, "candidateExport.candidates[]"),
             :ok <- safe_id(candidate["candidateId"], "candidateExport.candidates[].candidateId"),
             :ok <- unique_id(candidate["candidateId"], seen_ids, "candidateExport.candidates[].candidateId"),
             :ok <- safe_id(candidate["invariantId"], "candidateExport.candidates[].invariantId"),
             :ok <-
               unique_id(
                 candidate["invariantId"],
                 seen_invariants,
                 "candidateExport.candidates[].invariantId"
               ),
             :ok <- member(candidate["sourceStatus"], ~w(violated inconclusive), "candidateExport.candidates[].sourceStatus"),
             :ok <- member(candidate["kind"], ~w(replay_regression verification_debt), "candidateExport.candidates[].kind"),
             :ok <- candidate_kind(candidate["sourceStatus"], candidate["kind"]),
             :ok <- member(candidate["priority"], ~w(critical high medium low), "candidateExport.candidates[].priority"),
             :ok <- non_blank(candidate["reason"], "candidateExport.candidates[].reason"),
             :ok <- required_candidate_checks(candidate) do
          {:ok, MapSet.put(seen_ids, candidate["candidateId"]),
           MapSet.put(seen_invariants, candidate["invariantId"])}
        else
          false -> {:error, error("invalid_profile", "candidateExport.candidates[] must be an object")}
          {:error, _} = failure -> failure
        end

      case result do
        {:ok, next_ids, next_invariants} ->
          {:cont, {:ok, next_ids, next_invariants}}

        {:error, _} = failure -> {:halt, failure}
      end
    end)
    |> case do
      {:ok, _seen_ids, _seen_invariants} -> :ok
      failure -> failure
    end
  end

  defp candidates(_),
    do: {:error, error("invalid_profile", "candidateExport.candidates must be an array")}

  defp candidate_kind("violated", "replay_regression"), do: :ok
  defp candidate_kind("inconclusive", "verification_debt"), do: :ok

  defp candidate_kind(_, _),
    do:
      {:error,
       error(
         "invalid_profile",
         "candidateExport.candidates[].kind must match sourceStatus"
       )}

  defp required_candidate_checks(candidate) do
    checks = candidate["requiredChecks"]

    status_specific =
      if candidate["sourceStatus"] == "violated",
        do: "failing_path_integrity",
        else: "reviewed_bound_change"

    required = ["exact_subject", "independent_cgqa_replay", status_specific]

    with :ok <- non_blank_list(checks, "candidateExport.candidates[].requiredChecks"),
         true <- Enum.all?(required, &(&1 in checks)) do
      :ok
    else
      false ->
        {:error,
         error(
           "invalid_profile",
           "candidateExport.candidates[].requiredChecks omits mandatory fresh-verification checks"
         )}

      {:error, _} = failure ->
        failure
    end
  end

  defp evidence_debt(values, checks) when is_list(values) and is_list(checks) do
    expected =
      checks
      |> Enum.filter(&(&1["status"] == "inconclusive"))
      |> Enum.map(& &1["invariantId"])
      |> MapSet.new()

    with {:ok, actual} <- debt_rows(values, true, "evidence.verificationDebt"),
         true <- MapSet.equal?(actual, expected) do
      :ok
    else
      false ->
        {:error,
         error(
           "invalid_profile",
           "evidence.verificationDebt must enumerate every and only inconclusive check"
         )}

      {:error, _} = failure ->
        failure
    end
  end

  defp evidence_debt(_, _),
    do: {:error, error("invalid_profile", "evidence.verificationDebt must be an array")}

  defp candidate_debt(values, candidates) when is_list(values) and is_list(candidates) do
    expected =
      candidates
      |> Enum.filter(&(&1["sourceStatus"] == "inconclusive"))
      |> Enum.map(& &1["invariantId"])
      |> MapSet.new()

    with {:ok, actual} <- debt_rows(values, false, "candidateExport.verificationDebt"),
         true <- MapSet.equal?(actual, expected) do
      :ok
    else
      false ->
        {:error,
         error(
           "invalid_profile",
           "candidateExport.verificationDebt must enumerate every and only inconclusive candidate"
         )}

      {:error, _} = failure ->
        failure
    end
  end

  defp candidate_debt(_, _),
    do:
      {:error,
       error("invalid_profile", "candidateExport.verificationDebt must be an array")}

  defp debt_rows(values, with_status, field) do
    expected =
      if with_status,
        do: MapSet.new(~w(invariantId status reason)),
        else: MapSet.new(~w(invariantId reason))

    Enum.reduce_while(values, {:ok, MapSet.new()}, fn row, {:ok, seen} ->
      result =
        with true <- is_map(row),
             :ok <- exact_keys(row, expected, "#{field}[]"),
             :ok <- safe_id(row["invariantId"], "#{field}[].invariantId"),
             :ok <- unique_id(row["invariantId"], seen, "#{field}[].invariantId"),
             :ok <- debt_status(row, with_status, field),
             :ok <- non_blank(row["reason"], "#{field}[].reason") do
          {:ok, MapSet.put(seen, row["invariantId"])}
        else
          false -> {:error, error("invalid_profile", "#{field}[] must be an object")}
          {:error, _} = failure -> failure
        end

      case result do
        {:ok, next_seen} -> {:cont, {:ok, next_seen}}
        {:error, _} = failure -> {:halt, failure}
      end
    end)
  end

  defp debt_status(row, true, field),
    do: equals(row["status"], "inconclusive", "#{field}[].status")

  defp debt_status(_, false, _), do: :ok

  defp causal_parent(values, expected) when is_list(values) do
    with :ok <- safe_id_list(values, "candidateExport.causalParents", false),
         true <- expected in values do
      :ok
    else
      false -> {:error, error("invalid_profile", "candidateExport.causalParents must include source exportId")}
      {:error, _} = failure -> failure
    end
  end

  defp causal_parent(_, _),
    do: {:error, error("invalid_profile", "candidateExport.causalParents must be an array")}

  defp assessment(source, raw) do
    source_sha = :crypto.hash(:sha256, raw) |> Base.encode16(case: :lower)
    assessment_id =
      :crypto.hash(:sha256, source.schema <> ":" <> source.export_id <> ":" <> source_sha)
      |> Base.encode16(case: :lower)
      |> binary_part(0, 24)

    %{
      schema: @assessment_schema,
      assessmentId: "pythia-external-evidence-#{assessment_id}",
      source: %{
        schema: source.schema,
        schemaSha256: Map.fetch!(@schema_pins, source.schema),
        exportId: source.export_id,
        sha256: source_sha,
        semantics: source.semantics
      },
      subject: source.subject,
      identity: source.identity,
      outcome: "ESCALATE",
      status: "advisory_only",
      stopReason: "current_authorization_required",
      mayAuthorizeAction: false,
      sideEffectExecuted: false,
      requiredNextChecks: [
        "current_authorization",
        "credential_scope",
        "environment_state",
        "recovery_readiness"
      ],
      claimBoundary:
        "External evidence can inform a Pythia decision but cannot independently authorize an action."
    }
  end

  defp blocked(cause) do
    %{
      ok: false,
      outcome: "BLOCK",
      status: "rejected",
      stopReason: cause.code,
      message: cause.message,
      mayAuthorizeAction: false,
      sideEffectExecuted: false
    }
  end

  defp exact_keys(value, expected, field) do
    actual = value |> Map.keys() |> MapSet.new()

    if MapSet.equal?(actual, expected) do
      :ok
    else
      {:error, error("invalid_profile", "#{field} has missing or unexpected fields")}
    end
  end

  defp safe_id(value, field), do: matches(value, @safe_id, field)

  defp matches(value, regex, field) when is_binary(value) do
    if Regex.match?(regex, value),
      do: :ok,
      else: {:error, error("invalid_profile", "#{field} has invalid format")}
  end

  defp matches(_, _, field),
    do: {:error, error("invalid_profile", "#{field} must be a string")}

  defp non_blank(value, field) when is_binary(value) do
    if String.trim(value) == "",
      do: {:error, error("invalid_profile", "#{field} must be non-empty")},
      else: :ok
  end

  defp non_blank(_, field),
    do: {:error, error("invalid_profile", "#{field} must be a string")}

  defp non_blank_list(values, field) when is_list(values) and values != [] do
    if Enum.all?(values, &(is_binary(&1) and String.trim(&1) != "")) and
         MapSet.size(MapSet.new(values)) == length(values) do
      :ok
    else
      {:error, error("invalid_profile", "#{field} must contain unique non-empty strings")}
    end
  end

  defp non_blank_list(_, field),
    do: {:error, error("invalid_profile", "#{field} must be a non-empty array")}

  defp safe_id_list([], _field, true), do: :ok

  defp safe_id_list(values, field, _allow_empty) when is_list(values) and values != [] do
    with true <- Enum.all?(values, &(is_binary(&1) and Regex.match?(@safe_id, &1))),
         true <- MapSet.size(MapSet.new(values)) == length(values) do
      :ok
    else
      false ->
        {:error,
         error("invalid_profile", "#{field} must contain unique safe identifiers")}
    end
  end

  defp safe_id_list(_, field, _),
    do: {:error, error("invalid_profile", "#{field} must be an array of safe identifiers")}

  defp timestamp(value, field) when is_binary(value) do
    case DateTime.from_iso8601(value) do
      {:ok, parsed, _offset} -> {:ok, parsed}
      {:error, _} -> {:error, error("invalid_profile", "#{field} must be an RFC 3339 timestamp")}
    end
  end

  defp timestamp(_, field),
    do: {:error, error("invalid_profile", "#{field} must be a string")}

  defp equals(actual, expected, field) do
    if actual == expected,
      do: :ok,
      else: {:error, error("invalid_profile", "#{field} has an unsupported value")}
  end

  defp member(value, allowed, field) do
    if value in allowed,
      do: :ok,
      else: {:error, error("invalid_profile", "#{field} has an unsupported value")}
  end

  defp non_negative_integer(value, _field) when is_integer(value) and value >= 0, do: :ok

  defp non_negative_integer(_, field),
    do: {:error, error("invalid_profile", "#{field} must be a non-negative integer")}

  defp positive_integer(value, _field) when is_integer(value) and value > 0, do: :ok

  defp positive_integer(_, field),
    do: {:error, error("invalid_profile", "#{field} must be a positive integer")}

  defp unique_id(value, seen, field) do
    if MapSet.member?(seen, value),
      do: {:error, error("invalid_profile", "#{field} must be unique")},
      else: :ok
  end

  defp error(code, message), do: %{code: code, message: message}
end
