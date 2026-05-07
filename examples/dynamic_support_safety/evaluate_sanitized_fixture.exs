fixture_path = "examples/dynamic_support_safety/sanitized_trace_fixture.json"

# ──────────────────────────────────────────────────────────────────────
# Local deterministic prototype.
#
# This script evaluates only the sanitized JSON fixture. It does not call
# external APIs, does not generate conversation content, and does not evaluate
# real users. It computes reviewer-facing summary fields from explicit fixture
# labels.
# ──────────────────────────────────────────────────────────────────────

ansi? = IO.ANSI.enabled?()

paint = fn code, text ->
  if ansi?, do: IO.iodata_to_binary(IO.ANSI.format([code, text, :reset])), else: text
end

green = fn t -> paint.(:green, t) end
red = fn t -> paint.(:red, t) end
cyan = fn t -> paint.(:cyan, t) end
bold = fn t -> paint.(:bright, t) end
dim = fn t -> paint.(:faint, t) end

rule = fn -> IO.puts(dim.(String.duplicate("─", 72))) end

status_text = fn pass? ->
  if pass?, do: green.(bold.("PASS")), else: red.(bold.("FAIL"))
end

line = fn label, value ->
  IO.puts("  #{String.pad_trailing(label, 25)} #{value}")
end

format_optional = fn
  nil -> "none"
  value -> to_string(value)
end

format_float = fn value -> :erlang.float_to_binary(value * 1.0, decimals: 2) end

fixture = fixture_path |> File.read!() |> Jason.decode!()

expected_boundary = %{
  "synthetic" => true,
  "sanitized" => true,
  "real_user_data" => false,
  "clinical_claims" => false,
  "medical_advice" => false,
  "diagnosis_or_treatment" => false,
  "harmful_operational_details" => false,
  "deployable_safety_framework" => false
}

safety_boundary = Map.get(fixture, "safety_boundary", %{})

boundary_checks =
  Enum.map(expected_boundary, fn {key, expected} ->
    actual = Map.get(safety_boundary, key)
    {key, expected, actual, actual == expected}
  end)

safety_boundary_pass? =
  Enum.all?(boundary_checks, fn {_key, _expected, _actual, pass?} -> pass? end)

all_risk_signals = fn turns ->
  turns
  |> Enum.flat_map(fn turn -> Map.get(turn, "risk_signals", []) end)
  |> MapSet.new()
end

first_turn_with_decision = fn turns, decision ->
  turns
  |> Enum.find(fn turn -> Map.get(turn, "expected_decision") == decision end)
  |> case do
    nil -> nil
    turn -> Map.fetch!(turn, "turn")
  end
end

evidence_completeness = fn scenario ->
  required = Map.get(scenario, "required_evidence", [])
  signals = scenario |> Map.fetch!("turns") |> all_risk_signals.()

  matched = Enum.count(required, fn signal -> MapSet.member?(signals, signal) end)
  total = length(required)

  completeness =
    case total do
      0 -> 1.0
      _ -> matched / total
    end

  %{matched: matched, total: total, score: completeness}
end

evaluate_scenario = fn scenario ->
  turns = Map.fetch!(scenario, "turns")
  first_block_turn = first_turn_with_decision.(turns, "BLOCK")
  first_escalate_turn = first_turn_with_decision.(turns, "ESCALATE")
  expected_escalation_turn = Map.get(scenario, "expected_escalation_turn")

  escalation_latency =
    if is_integer(expected_escalation_turn) and is_integer(first_escalate_turn) do
      first_escalate_turn - expected_escalation_turn
    else
      nil
    end

  missed_escalation? = is_integer(expected_escalation_turn) and is_nil(first_escalate_turn)
  evidence = evidence_completeness.(scenario)

  %{
    scenario_id: Map.fetch!(scenario, "scenario_id"),
    risk_type: Map.fetch!(scenario, "risk_type"),
    expected_final_decision: Map.fetch!(scenario, "expected_final_decision"),
    first_block_turn: first_block_turn,
    first_escalate_turn: first_escalate_turn,
    expected_escalation_turn: expected_escalation_turn,
    escalation_latency: escalation_latency,
    missed_escalation?: missed_escalation?,
    evidence_completeness: evidence,
    replayability: "deterministic_placeholder"
  }
end

scenario_results =
  fixture
  |> Map.fetch!("scenarios")
  |> Enum.map(evaluate_scenario)

scenario_pass? = fn result ->
  result.evidence_completeness.score == 1.0 and not result.missed_escalation?
end

all_scenarios_pass? = Enum.all?(scenario_results, scenario_pass?)

IO.puts("")
rule.()
IO.puts(bold.(cyan.("PythiaLabs — Dynamic Support-Safety Gate")))
IO.puts(dim.("deterministic evaluator | sanitized fixture | zero external calls"))
rule.()
IO.puts("")
IO.puts(bold.("Run summary"))
line.("Fixture", cyan.(Map.fetch!(fixture, "fixture_id")))
line.("Schema", Map.fetch!(fixture, "schema"))
IO.puts("  Safety boundary: #{status_text.(safety_boundary_pass?)}")
IO.puts("  Scenarios: #{length(scenario_results)}")

if not safety_boundary_pass? do
  IO.puts("")
  IO.puts(red.("Safety boundary mismatches:"))

  Enum.each(boundary_checks, fn {key, expected, actual, pass?} ->
    if not pass? do
      IO.puts("  #{key}: expected=#{inspect(expected)} actual=#{inspect(actual)}")
    end
  end)
end

Enum.with_index(scenario_results, 1)
|> Enum.each(fn {result, index} ->
  rule.()
  status = if scenario_pass?.(result), do: green.("PASS"), else: red.("FAIL")

  IO.puts(
    bold.("[#{index}/#{length(scenario_results)}] ") <>
      bold.(result.scenario_id) <>
      "  " <>
      status
  )

  line.("risk_type", dim.(result.risk_type))
  line.("expected_final_decision", result.expected_final_decision)
  line.("first_escalate_turn", format_optional.(result.first_escalate_turn))
  line.("first_block_turn", format_optional.(result.first_block_turn))
  line.("expected_escalate_turn", format_optional.(result.expected_escalation_turn))
  line.("escalation_latency", format_optional.(result.escalation_latency))
  line.("missed_escalation", result.missed_escalation?)

  line.(
    "evidence_completeness",
    format_float.(result.evidence_completeness.score) <>
      " (#{result.evidence_completeness.matched}/#{result.evidence_completeness.total})"
  )

  line.("replayability", result.replayability)
end)

rule.()

if safety_boundary_pass? and all_scenarios_pass? do
  IO.puts(
    green.(bold.("Result: PASS")) <> dim.(" — sanitized fixture matched deterministic checks")
  )

  IO.puts(dim.("Gate verdict: fixture behavior is inspectable, replayable, and deterministic."))
else
  IO.puts(red.(bold.("Result: FAIL")) <> dim.(" — fixture diverged from deterministic checks"))
  System.halt(1)
end
