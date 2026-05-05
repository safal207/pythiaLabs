alias Pythia.Showcase.Web3TreasuryAction, as: Engine

input_path = "examples/paid_review_demo_input.json"
artifacts_path = "examples/output/paid_review_demo_artifact.json"

# ──────────────────────────────────────────────────────────────────────
# Rendering helpers
# ──────────────────────────────────────────────────────────────────────
ansi? = IO.ANSI.enabled?()

paint = fn code, text ->
  if ansi?, do: IO.iodata_to_binary(IO.ANSI.format([code, text, :reset])), else: text
end

green = fn t -> paint.(:green, t) end
red = fn t -> paint.(:red, t) end
yellow = fn t -> paint.(:yellow, t) end
cyan = fn t -> paint.(:cyan, t) end
bold = fn t -> paint.(:bright, t) end
dim = fn t -> paint.(:faint, t) end

rule = fn -> IO.puts(dim.(String.duplicate("─", 64))) end

status_badge = fn
  s when s in ["accepted", :accepted] -> green.("● ACCEPTED")
  s when s in ["rejected", :rejected] -> red.("● REJECTED")
  other -> yellow.("● #{other}")
end

result_badge = fn
  r when r in [:pass, "pass"] -> green.("PASS")
  r when r in [:fail, "fail"] -> red.("FAIL")
  other -> yellow.(to_string(other))
end

digest_of = fn evidence -> Map.fetch!(evidence, "digest") end

# ──────────────────────────────────────────────────────────────────────
# Input parsing — JSON keys are strings; convert ISO8601 → DateTime so
# the engine's validators accept the record.
# ──────────────────────────────────────────────────────────────────────
parse_dt = fn s ->
  case DateTime.from_iso8601(s) do
    {:ok, dt, _offset} -> dt
    other -> raise "invalid ISO8601 #{inspect(s)}: #{inspect(other)}"
  end
end

datetime_keys = [
  "action_time",
  "decision_time",
  "voting_closed_at",
  "timelock_until",
  "authorization_valid_from",
  "authorization_valid_to",
  "authorization_recorded_at",
  "transfer_expires_at"
]

hydrate = fn map ->
  Enum.reduce(datetime_keys, map, fn k, acc ->
    case Map.get(acc, k) do
      nil -> acc
      iso when is_binary(iso) -> Map.put(acc, k, parse_dt.(iso))
      _ -> acc
    end
  end)
end

deep_merge = fn deep_merge, base, override ->
  Map.merge(base, override, fn _k, l, r ->
    if is_map(l) and is_map(r), do: deep_merge.(deep_merge, l, r), else: r
  end)
end

input = input_path |> File.read!() |> Jason.decode!()
scenarios = Map.fetch!(input, "scenarios")
counterfactual = Map.get(input, "counterfactual")

# ──────────────────────────────────────────────────────────────────────
# Run a single scenario through the real engine; build an evidence
# record with a real sha256 digest and round-trip-verify it via
# Engine.verify_evidence/1 (not the signed-envelope path).
# ──────────────────────────────────────────────────────────────────────
run_scenario = fn scenario ->
  action = hydrate.(scenario["action"])
  governance = hydrate.(scenario["governance_record"])

  {elapsed_us, result} = :timer.tc(fn -> Engine.evaluate(action, governance) end)

  {_tag, payload} = result
  evidence = Engine.export_evidence(result)
  verify = Engine.verify_evidence(evidence)

  # Persisted record omits wall-clock timing so the bundle is byte-stable
  # across runs; latency is reported to the terminal only. Note this is the
  # plain evidence payload + its sha256 digest (Engine.verify_evidence/1),
  # not the signed envelope (Engine.verify_evidence_envelope/1).
  evidence_record = %{
    "scenario" => scenario["name"],
    "headline" => scenario["headline"],
    "expected_status" => scenario["expected_status"],
    "expected_stop_reason" => scenario["expected_stop_reason"],
    "evidence" => evidence,
    "self_verify" =>
      case verify do
        {:ok, %{status: :verified}} -> "verified"
        {:error, %{reason: r}} -> "rejected:#{r}"
      end
  }

  %{
    name: scenario["name"],
    headline: scenario["headline"],
    expected_status: scenario["expected_status"],
    expected_stop_reason: scenario["expected_stop_reason"],
    payload: payload,
    elapsed_us: elapsed_us,
    evidence: evidence,
    record: evidence_record,
    verify: verify
  }
end

print_scenario = fn idx, total, r ->
  rule.()
  IO.puts(bold.("[#{idx}/#{total}] ") <> bold.(r.headline))
  IO.puts(dim.("scenario=#{r.name}"))

  status = to_string(r.payload[:status] || "rejected")
  stop_reason = to_string(r.payload[:stop_reason] || r.payload[:reason] || "—")
  expected_match? = status == r.expected_status and stop_reason == r.expected_stop_reason
  ms = :erlang.float_to_binary(r.elapsed_us / 1000, decimals: 2)

  IO.puts("  decision    : #{status_badge.(status)}  #{dim.("(#{ms} ms)")}")
  IO.puts("  stop_reason : #{stop_reason}")

  IO.puts(
    "  expected    : #{r.expected_status} / #{r.expected_stop_reason} → " <>
      if(expected_match?, do: green.("MATCH"), else: red.("MISMATCH"))
  )

  trace = r.payload[:trace] || []
  check_events = Enum.filter(trace, fn e -> e.event not in [:proposed_action, :decision] end)

  if check_events != [] do
    IO.puts(dim.("  evidence trace:"))

    Enum.each(check_events, fn e ->
      IO.puts("    " <> result_badge.(e.result) <> "  " <> Atom.to_string(e.event))
    end)
  end

  IO.puts("  sha256[:16] : #{cyan.(String.slice(digest_of.(r.evidence), 0, 16))}")

  verify_label =
    case r.verify do
      {:ok, %{status: :verified}} -> green.("verified")
      {:error, %{reason: reason}} -> red.("rejected:#{reason}")
    end

  IO.puts("  evidence    : #{verify_label}")

  expected_match?
end

# ──────────────────────────────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────────────────────────────
IO.puts("")
IO.puts(bold.("PythiaLabs — Paid Review Demo"))
IO.puts(dim.("deterministic evidence layer for agentic oversight"))
IO.puts(dim.("scenario_set=#{input["scenario_set_id"]}  schema=#{input["schema"]}"))

# ──────────────────────────────────────────────────────────────────────
# Run all scenarios
# ──────────────────────────────────────────────────────────────────────
total = length(scenarios)

results =
  scenarios
  |> Enum.with_index(1)
  |> Enum.map(fn {scenario, idx} ->
    r = run_scenario.(scenario)
    matched? = print_scenario.(idx, total, r)
    Map.put(r, :matched?, matched?)
  end)

# ──────────────────────────────────────────────────────────────────────
# Counterfactual: flip one input field and show the decision flips too.
# This is the headline claim of an evidence-driven gate.
# ──────────────────────────────────────────────────────────────────────
{cf_record, cf_status_str} =
  case counterfactual do
    nil ->
      {nil, nil}

    %{"from_scenario" => from_name, "patch" => patch, "expected_status" => expected_cf} ->
      base = Enum.find(scenarios, &(&1["name"] == from_name))
      patched = deep_merge.(deep_merge, base, patch)
      cf = run_scenario.(patched)

      base_result = Enum.find(results, &(&1.name == from_name))
      base_status = to_string(base_result.payload[:status])
      cf_status = to_string(cf.payload[:status])

      rule.()
      IO.puts(bold.("Counterfactual"))
      IO.puts(dim.("from=#{from_name}  patch=#{Jason.encode!(patch)}"))

      flipped_label =
        if cf_status == expected_cf,
          do: green.("(decision flipped as expected)"),
          else: red.("(unexpected: wanted #{expected_cf})")

      IO.puts("  #{base_status} → #{cf_status}  #{flipped_label}")

      env = %{
        "from_scenario" => from_name,
        "patch" => patch,
        "expected_status" => expected_cf,
        "actual_status" => cf_status,
        "evidence" => cf.evidence
      }

      {env, cf_status}
  end

# ──────────────────────────────────────────────────────────────────────
# Summary table
# ──────────────────────────────────────────────────────────────────────
rule.()
IO.puts(bold.("Summary"))

name_width = results |> Enum.map(&String.length(&1.name)) |> Enum.max() |> max(8)

reason_width =
  results
  |> Enum.map(fn r ->
    String.length(to_string(r.payload[:stop_reason] || r.payload[:reason] || ""))
  end)
  |> Enum.max()
  |> max(12)

header =
  "  " <>
    String.pad_trailing("scenario", name_width + 2) <>
    String.pad_trailing("status", 12) <>
    String.pad_trailing("stop_reason", reason_width + 2) <>
    String.pad_trailing("ms", 8) <> "sha256[:8]"

IO.puts(dim.(header))

Enum.each(results, fn r ->
  status = to_string(r.payload[:status] || "rejected")
  reason = to_string(r.payload[:stop_reason] || r.payload[:reason] || "—")
  ms = :erlang.float_to_binary(r.elapsed_us / 1000, decimals: 2)
  digest8 = String.slice(digest_of.(r.evidence), 0, 8)

  status_cell =
    case status do
      "accepted" -> green.(String.pad_trailing(status, 10))
      "rejected" -> red.(String.pad_trailing(status, 10))
      other -> yellow.(String.pad_trailing(other, 10))
    end

  IO.puts(
    "  " <>
      String.pad_trailing(r.name, name_width + 2) <>
      status_cell <>
      "  " <>
      String.pad_trailing(reason, reason_width + 2) <>
      String.pad_trailing(ms, 8) <>
      cyan.(digest8)
  )
end)

# ──────────────────────────────────────────────────────────────────────
# Persist evidence bundle for auditors
# ──────────────────────────────────────────────────────────────────────
File.mkdir_p!(Path.dirname(artifacts_path))

bundle = %{
  "schema" => "pythia.demo.artifact_bundle.v1",
  "scenario_set_id" => input["scenario_set_id"],
  "scenarios" => Enum.map(results, & &1.record),
  "counterfactual" => cf_record
}

File.write!(artifacts_path, Jason.encode!(bundle, pretty: true) <> "\n")

rule.()
IO.puts("Artifact bundle written to #{cyan.(artifacts_path)}")
IO.puts(dim.("  #{length(results)} evidence record(s); each digest re-verified via Engine.verify_evidence/1"))

# ──────────────────────────────────────────────────────────────────────
# Final pass/fail
# ──────────────────────────────────────────────────────────────────────
all_matched = Enum.all?(results, & &1.matched?)
cf_ok = is_nil(counterfactual) or cf_status_str == counterfactual["expected_status"]

rule.()

if all_matched and cf_ok do
  IO.puts(green.(bold.("Result: PASS")) <> dim.(" — all scenarios matched expectations"))
else
  IO.puts(red.(bold.("Result: FAIL")) <> dim.(" — one or more scenarios diverged from expected"))
  System.halt(1)
end
