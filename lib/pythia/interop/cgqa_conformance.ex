defmodule Pythia.Interop.CgqaConformance do
  @moduledoc """
  Native, offline runner for the pinned ContractGraph-QA/LiminalQA
  interoperability conformance suite.

  The runner verifies exact suite and asset bytes before calling the existing
  external-evidence adapter. It performs no network request, candidate
  execution, database write, or target-system action.
  """

  alias Pythia.Interop.ExternalEvidence

  @suite_schema "org.contractgraph-qa.liminalqa-interop-conformance-suite.v0.1"
  @result_schema "org.contractgraph-qa.liminalqa-interop-conformance-result.v0.1"
  @suite_id "cgqa-liminalqa-v0.1"
  @suite_version "0.1.0"
  @suite_sha256 "562e2f9ae699f001b9ccf1b2b9f6dd30c435d53d668b5fd9a04ca15ca1e4faac"
  @suite_schema_sha256 "34acfc677802683c6c452a728ed533e92803a74d989b397d2d0fe549b1da93f9"
  @result_schema_sha256 "388d0aadbb8d30fb5aee223a89f29884b89a1b3303ac88dae8b21e91ab11b423"
  @valid_non_authorizing "VALID_NON_AUTHORIZING"
  @invalid_blocked "INVALID_BLOCKED"
  @unsafe_accepted "UNSAFE_ACCEPTED"
  @claim_boundary "Synthetic conformance verifies adapter behavior only for these pinned fixtures and mutations. It does not verify a production system, prove security or completeness, authorize an action, or replace independent replay against the exact subject."

  @suite_root Path.expand("../../../conformance/cgqa-liminalqa-v0.1", __DIR__)
  @asset_paths [
    "suite.json",
    "suite.schema.json",
    "result.schema.json",
    "schemas/cgqa-liminalqa-evidence-v0.1.schema.json",
    "schemas/liminalqa-cgqa-candidates-v0.1.schema.json",
    "fixtures/cgqa-liminalqa-evidence-v0.1.json",
    "fixtures/liminalqa-cgqa-candidates-v0.1.json"
  ]

  for path <- @asset_paths do
    @external_resource Path.join(@suite_root, path)
  end

  @embedded_assets Map.new(@asset_paths, fn path ->
                     {path, File.read!(Path.join(@suite_root, path))}
                   end)

  @expected_contracts [
    %{
      "id" => "cgqa-evidence",
      "artifactSchema" => "org.contractgraph-qa.liminalqa-evidence.v0.1",
      "artifactProfile" => "org.contractgraph-qa.bounded-invariant-evidence.v0.1",
      "ownerRepository" => "safal207/ContractGraph-QA",
      "producerCommit" => "bdf7ced074e3a7baf57cf89ac68be9674bd76a02",
      "schemaPath" => "schemas/cgqa-liminalqa-evidence-v0.1.schema.json",
      "schemaSha256" => "53b0b4a0b1f4d77de26b8be9dbb90006ea0bd30c5cd3960a2f3e7d44d9664184",
      "fixturePath" => "fixtures/cgqa-liminalqa-evidence-v0.1.json",
      "fixtureSha256" => "e1d5a14c5c1b75e2cfffaf87bf526fd61e141a0c5b7828de4f275e9792fda3ce"
    },
    %{
      "id" => "liminal-candidates",
      "artifactSchema" => "org.liminalqa.cgqa-candidates.v0.1",
      "artifactProfile" => "org.liminalqa.non-authoritative-candidate-seeds.v0.1",
      "ownerRepository" => "safal207/LiminalQAengineer",
      "producerCommit" => "db9c85f678aafd6e28487e0679a9fb6c3ebfb0c3",
      "schemaPath" => "schemas/liminalqa-cgqa-candidates-v0.1.schema.json",
      "schemaSha256" => "896e32921d41925a976fef5d0ba561a08bd1f2265a08bc9ccf5065a3238a4f60",
      "fixturePath" => "fixtures/liminalqa-cgqa-candidates-v0.1.json",
      "fixtureSha256" => "60b794934959c30f9957d0e54de83d7760ac38b618b0676603d721daa8ef11d3"
    }
  ]

  @suite_keys ~w(schema suiteId version suiteSchema resultSchema contracts cases claimBoundary)
  @categories MapSet.new(
                ~w(golden authority_escalation semantic_mismatch temporal_inversion unknown_field ambiguous_json verification_weakening unsafe_identifier)
              )
  @contract_pin_keys ~w(id artifactSchema artifactProfile ownerRepository producerCommit schemaSha256 fixtureSha256)

  @doc "Run all 14 pinned vectors through Pythia's native Elixir adapter."
  @spec run(nil | binary()) :: {:ok, map()} | {:error, binary()}
  def run(suite_path \\ nil) do
    with {:ok, source, suite_raw} <- load_suite_source(suite_path),
         :ok <-
           ensure(sha256(suite_raw) == @suite_sha256, "suite digest does not match the v0.1 pin"),
         {:ok, suite} <- strict_decode(suite_raw, "suite"),
         :ok <- validate_suite(suite),
         {:ok, assets} <- verify_assets(source, suite),
         {:ok, results} <- run_cases(suite, assets),
         {:ok, report} <- build_report(suite, suite_raw, results) do
      {:ok, report}
    end
  end

  defp load_suite_source(nil), do: {:ok, :embedded, Map.fetch!(@embedded_assets, "suite.json")}

  defp load_suite_source(path) when is_binary(path) do
    with :ok <-
           ensure(
             not Enum.member?(Path.split(path), ".."),
             "suite path must not contain parent traversal"
           ),
         {:ok, %File.Stat{type: :regular}} <- regular_file(path, "suite"),
         resolved = Path.expand(path),
         {:ok, raw} <- read_file(resolved, "suite") do
      {:ok, {:external, Path.dirname(resolved)}, raw}
    end
  end

  defp load_suite_source(_), do: {:error, "suite path must be a string"}

  defp validate_suite(suite) when is_map(suite) do
    cases = suite["cases"]

    with :ok <- exact_keys(suite, @suite_keys, "suite"),
         :ok <- ensure(suite["schema"] == @suite_schema, "suite schema is unsupported"),
         :ok <- ensure(suite["suiteId"] == @suite_id, "suite id is unsupported"),
         :ok <- ensure(suite["version"] == @suite_version, "suite version is unsupported"),
         :ok <-
           ensure(
             suite["claimBoundary"] == @claim_boundary,
             "suite claim boundary is unsupported"
           ),
         :ok <-
           ensure(
             suite["suiteSchema"] == %{
               "path" => "suite.schema.json",
               "sha256" => @suite_schema_sha256
             },
             "suite schema pin is unsupported"
           ),
         :ok <-
           ensure(
             suite["resultSchema"] == %{
               "path" => "result.schema.json",
               "sha256" => @result_schema_sha256
             },
             "result schema pin is unsupported"
           ),
         :ok <-
           ensure(suite["contracts"] == @expected_contracts, "contract pins are unsupported"),
         :ok <- validate_cases(cases) do
      :ok
    end
  end

  defp validate_suite(_), do: {:error, "suite must contain one JSON object"}

  defp validate_cases(cases) when is_list(cases) and length(cases) == 14 do
    if Enum.all?(cases, &valid_case?/1) do
      ids = Enum.map(cases, & &1["id"])
      categories = cases |> Enum.map(& &1["category"]) |> MapSet.new()

      with :ok <- ensure(Enum.uniq(ids) == ids, "suite contains duplicate case ids"),
           :ok <- ensure(categories == @categories, "suite does not cover every control category") do
        :ok
      end
    else
      {:error, "suite contains an invalid case"}
    end
  end

  defp validate_cases(_), do: {:error, "v0.1 suite must contain 14 cases"}

  defp valid_case?(case_data) when is_map(case_data) do
    case_data["contract"] in ["cgqa-evidence", "liminal-candidates"] and
      is_binary(case_data["id"]) and
      is_binary(case_data["description"]) and
      case_data["description"] != "" and
      case_data["expectedSemantics"] in [@valid_non_authorizing, @invalid_blocked] and
      Regex.match?(~r/\A[0-9a-f]{64}\z/, case_data["expectedInputSha256"] || "") and
      valid_operation?(case_data["operation"])
  end

  defp valid_case?(_), do: false

  defp valid_operation?(%{"kind" => "identity"} = operation),
    do: map_size(operation) == 1

  defp valid_operation?(%{"kind" => kind, "pointer" => pointer, "value" => _} = operation)
       when kind in ["add", "replace"],
       do: map_size(operation) == 3 and valid_pointer?(pointer)

  defp valid_operation?(%{"kind" => "remove", "pointer" => pointer} = operation),
    do: map_size(operation) == 2 and valid_pointer?(pointer)

  defp valid_operation?(
         %{"kind" => "duplicate_root_key", "key" => key, "value" => _} = operation
       ),
       do: map_size(operation) == 3 and is_binary(key) and String.trim(key) != ""

  defp valid_operation?(_), do: false

  defp verify_assets(source, suite) do
    with :ok <- verify_json_asset(source, suite["suiteSchema"], "suite schema"),
         :ok <- verify_json_asset(source, suite["resultSchema"], "result schema") do
      Enum.reduce_while(suite["contracts"], {:ok, %{}}, fn contract, {:ok, assets} ->
        with {:ok, schema_raw} <- read_asset(source, contract["schemaPath"]),
             :ok <-
               ensure(
                 sha256(schema_raw) == contract["schemaSha256"],
                 "contract #{contract["id"]} schema digest mismatch"
               ),
             {:ok, _schema} <- strict_decode(schema_raw, "contract #{contract["id"]} schema"),
             {:ok, fixture_raw} <- read_asset(source, contract["fixturePath"]),
             :ok <-
               ensure(
                 sha256(fixture_raw) == contract["fixtureSha256"],
                 "contract #{contract["id"]} fixture digest mismatch"
               ),
             {:ok, fixture} <- strict_decode(fixture_raw, "contract #{contract["id"]} fixture"),
             :ok <-
               ensure(
                 fixture["schema"] == contract["artifactSchema"] and
                   fixture["profile"] == contract["artifactProfile"],
                 "contract #{contract["id"]} fixture identity mismatch"
               ) do
          asset = %{contract: contract, fixture_raw: fixture_raw}
          {:cont, {:ok, Map.put(assets, contract["id"], asset)}}
        else
          {:error, _} = error -> {:halt, error}
        end
      end)
    end
  end

  defp verify_json_asset(source, pin, label) do
    with {:ok, raw} <- read_asset(source, pin["path"]),
         :ok <- ensure(sha256(raw) == pin["sha256"], "#{label} digest mismatch"),
         {:ok, _decoded} <- strict_decode(raw, label) do
      :ok
    end
  end

  defp read_asset(:embedded, relative) do
    with :ok <- safe_relative_json_path(relative),
         {:ok, raw} <- Map.fetch(@embedded_assets, relative) do
      {:ok, raw}
    else
      :error -> {:error, "unsupported embedded suite asset: #{relative}"}
      {:error, _} = error -> error
    end
  end

  defp read_asset({:external, root}, relative) do
    with :ok <- safe_relative_json_path(relative),
         candidate = Path.expand(Path.join(root, relative)),
         :ok <-
           ensure(String.starts_with?(candidate, root <> "/"), "suite asset escapes suite root"),
         {:ok, %File.Stat{type: :regular}} <- regular_file(candidate, "suite asset #{relative}"),
         {:ok, raw} <- read_file(candidate, "suite asset #{relative}") do
      {:ok, raw}
    end
  end

  defp safe_relative_json_path(path) when is_binary(path) do
    parts = Path.split(path)

    ensure(
      Path.type(path) == :relative and Path.extname(path) == ".json" and
        not Enum.any?(parts, &(&1 in [".", ".."])),
      "suite asset path must be a traversal-free relative JSON path"
    )
  end

  defp safe_relative_json_path(_), do: {:error, "suite asset path must be a string"}

  defp regular_file(path, label) do
    case File.lstat(path) do
      {:ok, %File.Stat{type: :regular} = stat} -> {:ok, stat}
      {:ok, _} -> {:error, "#{label} must be a regular non-symlink file"}
      {:error, reason} -> {:error, "#{label} cannot be inspected: #{:file.format_error(reason)}"}
    end
  end

  defp read_file(path, label) do
    case File.read(path) do
      {:ok, raw} -> {:ok, raw}
      {:error, reason} -> {:error, "#{label} cannot be read: #{:file.format_error(reason)}"}
    end
  end

  defp run_cases(suite, assets) do
    Enum.reduce_while(suite["cases"], {:ok, []}, fn case_data, {:ok, results} ->
      asset = Map.fetch!(assets, case_data["contract"])

      with {:ok, input} <- apply_operation(asset.fixture_raw, case_data["operation"]),
           input_sha256 = sha256(input),
           :ok <-
             ensure(
               input_sha256 == case_data["expectedInputSha256"],
               "case #{case_data["id"]} mutation digest does not match the v0.1 pin"
             ) do
        {observed, diagnostic} = observe(asset.contract["artifactSchema"], input)
        status = if observed == case_data["expectedSemantics"], do: "PASS", else: "FAIL"

        result = %{
          "id" => case_data["id"],
          "contract" => case_data["contract"],
          "category" => case_data["category"],
          "status" => status,
          "expectedSemantics" => case_data["expectedSemantics"],
          "observedSemantics" => observed,
          "inputSha256" => input_sha256,
          "diagnostic" => diagnostic,
          "sideEffectExecuted" => false
        }

        {:cont, {:ok, [result | results]}}
      else
        {:error, _} = error -> {:halt, error}
      end
    end)
    |> case do
      {:ok, reversed} -> {:ok, Enum.reverse(reversed)}
      {:error, _} = error -> error
    end
  end

  defp apply_operation(base_raw, %{"kind" => "identity"}), do: {:ok, base_raw}

  defp apply_operation(base_raw, %{
         "kind" => "duplicate_root_key",
         "key" => key,
         "value" => value
       }) do
    with {:ok, base} <- strict_decode(base_raw, "case fixture"),
         :ok <-
           ensure(Map.has_key?(base, key), "duplicate_root_key target does not exist: #{key}"),
         <<"{", rest::binary>> <- String.trim_leading(base_raw) do
      {:ok, "{" <> canonical_json(key) <> ":" <> canonical_json(value) <> "," <> rest}
    else
      :nomatch -> {:error, "duplicate_root_key requires an object fixture"}
      {:error, _} = error -> error
      _ -> {:error, "duplicate_root_key requires an object fixture"}
    end
  end

  defp apply_operation(base_raw, %{"kind" => kind, "pointer" => pointer} = operation)
       when kind in ["add", "replace", "remove"] do
    with {:ok, document} <- strict_decode(base_raw, "case fixture"),
         {:ok, tokens} <- pointer_tokens(pointer),
         {:ok, mutated} <- mutate(document, tokens, kind, operation["value"]) do
      {:ok, canonical_json(mutated) <> "\n"}
    end
  end

  defp apply_operation(_, _), do: {:error, "unsupported conformance operation"}

  defp pointer_tokens(pointer) do
    with :ok <- ensure(valid_pointer?(pointer), "operation pointer must be a valid JSON Pointer") do
      tokens =
        pointer
        |> String.split("/", trim: false)
        |> tl()
        |> Enum.map(fn token ->
          token |> String.replace("~1", "/") |> String.replace("~0", "~")
        end)

      {:ok, tokens}
    end
  end

  defp valid_pointer?(pointer) when is_binary(pointer),
    do: String.starts_with?(pointer, "/") and not Regex.match?(~r/~(?:[^01]|$)/, pointer)

  defp valid_pointer?(_), do: false

  defp mutate(_, [], _, _), do: {:error, "operation pointer must not target the document root"}

  defp mutate(container, [token], kind, value) when is_map(container),
    do: mutate_map(container, token, kind, value)

  defp mutate(container, [token], kind, value) when is_list(container),
    do: mutate_list(container, token, kind, value)

  defp mutate(container, [token | rest], kind, value) when is_map(container) do
    case Map.fetch(container, token) do
      {:ok, child} ->
        with {:ok, mutated} <- mutate(child, rest, kind, value) do
          {:ok, Map.put(container, token, mutated)}
        end

      :error ->
        {:error, "operation pointer component is absent: #{token}"}
    end
  end

  defp mutate(container, [token | rest], kind, value) when is_list(container) do
    with {:ok, index} <- list_index(token),
         :ok <-
           ensure(index < length(container), "operation list index is out of range: #{index}"),
         {:ok, mutated} <- mutate(Enum.at(container, index), rest, kind, value) do
      {:ok, List.replace_at(container, index, mutated)}
    end
  end

  defp mutate(_, _, _, _), do: {:error, "operation pointer traverses a scalar value"}

  defp mutate_map(container, token, "add", value) do
    with :ok <- ensure(not Map.has_key?(container, token), "add target already exists: #{token}") do
      {:ok, Map.put(container, token, value)}
    end
  end

  defp mutate_map(container, token, "replace", value) do
    with :ok <-
           ensure(Map.has_key?(container, token), "operation target does not exist: #{token}") do
      {:ok, Map.put(container, token, value)}
    end
  end

  defp mutate_map(container, token, "remove", _) do
    with :ok <-
           ensure(Map.has_key?(container, token), "operation target does not exist: #{token}") do
      {:ok, Map.delete(container, token)}
    end
  end

  defp mutate_list(container, token, kind, value) do
    with {:ok, index} <- list_index(token) do
      case kind do
        "add" ->
          with :ok <-
                 ensure(
                   index <= length(container),
                   "operation list index is out of range: #{index}"
                 ) do
            {:ok, List.insert_at(container, index, value)}
          end

        "replace" ->
          with :ok <-
                 ensure(
                   index < length(container),
                   "operation list index is out of range: #{index}"
                 ) do
            {:ok, List.replace_at(container, index, value)}
          end

        "remove" ->
          with :ok <-
                 ensure(
                   index < length(container),
                   "operation list index is out of range: #{index}"
                 ) do
            {:ok, List.delete_at(container, index)}
          end
      end
    end
  end

  defp list_index(token) when is_binary(token) do
    if Regex.match?(~r/\A[0-9]+\z/, token) do
      case Integer.parse(token) do
        {index, ""} -> {:ok, index}
        _ -> {:error, "operation list pointer is invalid: #{token}"}
      end
    else
      {:error, "operation list pointer is invalid: #{token}"}
    end
  end

  defp list_index(token), do: {:error, "operation list pointer is invalid: #{inspect(token)}"}

  defp observe(artifact_schema, raw) do
    case ExternalEvidence.evaluate_json(raw) do
      {:ok, assessment} ->
        if safe_assessment?(assessment) and not unsafe_input?(artifact_schema, raw) do
          {@valid_non_authorizing, "profile accepted without action authority"}
        else
          {@unsafe_accepted, "adapter accepted unsafe authority or weakened verification"}
        end

      {:error, rejection} ->
        if safe_rejection?(rejection) do
          {@invalid_blocked, diagnostic(rejection, "profile rejected")}
        else
          {@unsafe_accepted, "adapter returned an unsafe rejection envelope"}
        end

      other ->
        {@unsafe_accepted, "adapter returned an unsupported result: #{inspect(other)}"}
    end
  end

  defp safe_assessment?(assessment) when is_map(assessment) do
    field(assessment, :outcome) == "ESCALATE" and
      field(assessment, :status) == "advisory_only" and
      field(assessment, :stopReason) == "current_authorization_required" and
      field(assessment, :mayAuthorizeAction) == false and
      field(assessment, :sideEffectExecuted) == false
  end

  defp safe_assessment?(_), do: false

  defp safe_rejection?(rejection) when is_map(rejection) do
    field(rejection, :outcome) == "BLOCK" and
      field(rejection, :status) == "rejected" and
      field(rejection, :mayAuthorizeAction) == false and
      field(rejection, :sideEffectExecuted) == false
  end

  defp safe_rejection?(_), do: false

  defp unsafe_input?(artifact_schema, raw) do
    case strict_decode(raw, "accepted case input") do
      {:ok, artifact} -> unsafe_artifact?(artifact_schema, artifact)
      {:error, _} -> true
    end
  end

  defp unsafe_artifact?("org.contractgraph-qa.liminalqa-evidence.v0.1", artifact) do
    get_in(artifact, ["authority", "mayAuthorizeAction"]) != false
  end

  defp unsafe_artifact?("org.liminalqa.cgqa-candidates.v0.1", artifact) do
    authority = artifact["authority"] || %{}

    authority["mayAuthorizeAction"] != false or
      authority["requiresCgqaVerification"] != true or
      missing_fresh_verification?(artifact["candidates"])
  end

  defp unsafe_artifact?(_, _), do: true

  defp missing_fresh_verification?(candidates) when is_list(candidates) do
    Enum.any?(candidates, fn
      %{"requiredChecks" => checks} when is_list(checks) ->
        not ("exact_subject" in checks and "independent_cgqa_replay" in checks)

      _ ->
        true
    end)
  end

  defp missing_fresh_verification?(_), do: true

  defp build_report(suite, suite_raw, results) do
    passed = Enum.count(results, &(&1["status"] == "PASS"))
    total = length(results)

    contract_pins =
      Enum.map(suite["contracts"], fn contract -> Map.take(contract, @contract_pin_keys) end)

    report = %{
      "schema" => @result_schema,
      "suiteId" => suite["suiteId"],
      "suiteVersion" => suite["version"],
      "suiteSha256" => sha256(suite_raw),
      "implementation" => %{
        "name" => "pythialabs",
        "version" => "0.1.0",
        "language" => "elixir"
      },
      "status" => if(passed == total, do: "PASS", else: "FAIL"),
      "counts" => %{"total" => total, "passed" => passed, "failed" => total - passed},
      "contractPins" => contract_pins,
      "results" => results,
      "authority" => %{
        "classification" => "conformance_evidence_only",
        "mayAuthorizeAction" => false
      },
      "claimBoundary" => suite["claimBoundary"]
    }

    report_id =
      "pythialabs-interop-conformance-" <> String.slice(sha256(canonical_json(report)), 0, 24)

    {:ok, Map.put(report, "reportId", report_id)}
  end

  defp strict_decode(raw, field_name) when is_binary(raw) do
    case Jason.decode(raw, objects: :ordered_objects, strings: :copy) do
      {:ok, decoded} -> normalize_ordered(decoded, field_name)
      {:error, error} -> {:error, "#{field_name} is not valid JSON: #{Exception.message(error)}"}
    end
  end

  defp normalize_ordered(%Jason.OrderedObject{values: pairs}, field_name) do
    Enum.reduce_while(pairs, {:ok, %{}}, fn {key, value}, {:ok, normalized} ->
      if Map.has_key?(normalized, key) do
        {:halt, {:error, "#{field_name} contains duplicate JSON key: #{key}"}}
      else
        case normalize_ordered(value, field_name) do
          {:ok, child} -> {:cont, {:ok, Map.put(normalized, key, child)}}
          {:error, _} = error -> {:halt, error}
        end
      end
    end)
  end

  defp normalize_ordered(values, field_name) when is_list(values) do
    Enum.reduce_while(values, {:ok, []}, fn value, {:ok, normalized} ->
      case normalize_ordered(value, field_name) do
        {:ok, child} -> {:cont, {:ok, [child | normalized]}}
        {:error, _} = error -> {:halt, error}
      end
    end)
    |> case do
      {:ok, reversed} -> {:ok, Enum.reverse(reversed)}
      {:error, _} = error -> error
    end
  end

  defp normalize_ordered(value, _field_name), do: {:ok, value}

  defp canonical_json(value) when is_map(value) do
    entries =
      value
      |> Enum.sort_by(fn {key, _value} -> key end)
      |> Enum.map(fn {key, child} -> [Jason.encode!(key), ":", canonical_json(child)] end)
      |> Enum.intersperse(",")

    IO.iodata_to_binary(["{", entries, "}"])
  end

  defp canonical_json(value) when is_list(value) do
    values = value |> Enum.map(&canonical_json/1) |> Enum.intersperse(",")
    IO.iodata_to_binary(["[", values, "]"])
  end

  defp canonical_json(value), do: Jason.encode!(value)

  defp exact_keys(value, expected, label) do
    ensure(
      MapSet.new(Map.keys(value)) == MapSet.new(expected),
      "#{label} has missing or unexpected fields"
    )
  end

  defp field(map, atom_key) do
    if Map.has_key?(map, atom_key),
      do: Map.get(map, atom_key),
      else: Map.get(map, Atom.to_string(atom_key))
  end

  defp diagnostic(value, fallback) do
    case field(value, :message) do
      message when is_binary(message) and message != "" -> message
      _ -> fallback
    end
  end

  defp sha256(raw), do: :crypto.hash(:sha256, raw) |> Base.encode16(case: :lower)
  defp ensure(true, _message), do: :ok
  defp ensure(false, message), do: {:error, message}
end
