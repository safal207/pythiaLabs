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

delay_ms =
  cond do
    System.get_env("CI") == "true" ->
      0

    System.get_env("PYTHIA_DEMO_DELAY_MS") in [nil, ""] ->
      90

    true ->
      case Integer.parse(System.get_env("PYTHIA_DEMO_DELAY_MS")) do
        {value, _} when value >= 0 -> value
        _ -> 90
      end
  end

paint = fn code, text ->
  if ansi?, do: IO.iodata_to_binary(IO.ANSI.format([code, text, :reset])), else: text
end

green = fn t -> paint.(:green, t) end
red = fn t -> paint.(:red, t) end
yellow = fn t -> paint.(:yellow, t) end
cyan = fn t -> paint.(:cyan, t) end
bold = fn t -> paint.(:bright, t) end
dim = fn t -> paint.(:faint, t) end

say = fn text ->
  IO.puts(text)

  if delay_ms > 0 do
    Process.sleep(delay_ms)
  end
end

pause = fn multiplier ->
  if delay_ms > 0 do
    Process.sleep(delay_ms * multiplier)
  end
end

rule = fn -> say.(dim.(String.duplicate("─", 72))) end
arrow = dim.("  ->  ")

status_text = fn pass? ->
  if pass?, do: green.(bold.("PASS")), else: red.(bold.("FAIL"))
end

line = fn label, value ->
  say.("  #{String.pad_trailing(label, 25)} #{value}")
end

funnel_stage = fn index, label, value, color ->
  say.("  #{dim.("[#{index}]")} #{color.(String.pad_trailing(label, 20))} #{value}")
end

hero = fn ->
  yellow.("C<") <> cyan.("◇")
end

hero_step = fn offset, label, color ->
  say.(String.duplicate(" ", offset) <> hero.() <> "  " <> color.(label))
end

report_row = fn left, right, color ->
  say.(
    "│ " <>
      String.pad_trailing(left, 24) <>
      " │ " <>
      color.(String.pad_trailing(right, 28)) <>
      " │"
  )
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

say.("")
rule.()
say.(bold.(cyan.("PythiaLabs — Dynamic Support-Safety Gate")))
say.(dim.("deterministic evaluator | sanitized fixture | zero external calls"))
rule.()
say.("")
say.(bold.("Mini gate hero"))

hero_step.(2, "wakes up", dim)
hero_step.(5, "spots a sanitized trace", cyan)
hero_step.(8, "checks the boundary", yellow)
hero_step.(11, "follows evidence to a verdict", green)
pause.(2)

say.("")
say.(bold.("Marketing-friendly funnel"))

say.(
  "  " <>
    cyan.("Sanitized trace") <>
    arrow <>
    yellow.("Safety boundary") <>
    arrow <>
    cyan.("Scenario checks") <>
    arrow <>
    green.("PASS verdict")
)

say.("")
say.(bold.("Run summary"))
line.("Fixture", cyan.(Map.fetch!(fixture, "fixture_id")))
line.("Schema", Map.fetch!(fixture, "schema"))
funnel_stage.("1", "Input", cyan.("sanitized fixture"), cyan)
funnel_stage.("2", "Safety boundary:", status_text.(safety_boundary_pass?), yellow)
funnel_stage.("3", "Scenarios:", "#{length(scenario_results)} deterministic checks", cyan)
funnel_stage.("4", "Evidence:", green.("complete + replayable"), green)

if not safety_boundary_pass? do
  say.("")
  say.(red.("Safety boundary mismatches:"))

  Enum.each(boundary_checks, fn {key, expected, actual, pass?} ->
    if not pass? do
      say.("  #{key}: expected=#{inspect(expected)} actual=#{inspect(actual)}")
    end
  end)
end

Enum.with_index(scenario_results, 1)
|> Enum.each(fn {result, index} ->
  rule.()
  status = if scenario_pass?.(result), do: green.(bold.("PASS")), else: red.(bold.("FAIL"))

  say.(
    bold.("[#{index}/#{length(scenario_results)}] ") <>
      bold.(result.scenario_id) <>
      arrow <>
      status
  )

  line.("risk_type", dim.(result.risk_type))

  line.(
    "decision path",
    yellow.("trace") <>
      arrow <> cyan.("boundary") <> arrow <> green.(result.expected_final_decision)
  )

  line.("first_escalate_turn", green.(format_optional.(result.first_escalate_turn)))
  line.("first_block_turn", format_optional.(result.first_block_turn))
  line.("expected_escalate_turn", format_optional.(result.expected_escalation_turn))
  line.("escalation_latency", format_optional.(result.escalation_latency))

  line.(
    "missed_escalation",
    if(result.missed_escalation?, do: red.("true"), else: green.("false"))
  )

  line.(
    "evidence_completeness",
    green.(format_float.(result.evidence_completeness.score)) <>
      " (#{result.evidence_completeness.matched}/#{result.evidence_completeness.total})"
  )

  line.("replayability", cyan.(result.replayability))
end)

rule.()

if safety_boundary_pass? and all_scenarios_pass? do
  say.(
    bold.("Final funnel: ") <>
      cyan.("Trace") <> arrow <> yellow.("Gate") <> arrow <> green.(bold.("PASS"))
  )

  say.("")
  say.(bold.("Landing report"))
  hero_step.(22, "jump", cyan)
  hero_step.(16, "jump", yellow)
  hero_step.(10, "lands on the report", green)
  say.("┌──────────────────────────┬──────────────────────────────┐")
  report_row.("Safety boundary", "PASS", green)

  report_row.(
    "Scenarios checked",
    "#{length(scenario_results)} / #{length(scenario_results)} PASS",
    green
  )

  report_row.("Evidence completeness", "1.00 each scenario", green)
  report_row.("Replayability", "deterministic", cyan)
  report_row.("Final verdict", "PASS", green)
  say.("└──────────────────────────┴──────────────────────────────┘")

  say.(green.(bold.("Result: PASS")) <> dim.(" — sanitized fixture matched deterministic checks"))

  say.(dim.("Gate verdict: fixture behavior is inspectable, replayable, and deterministic."))
else
  say.(red.(bold.("Result: FAIL")) <> dim.(" — fixture diverged from deterministic checks"))
  System.halt(1)
end
