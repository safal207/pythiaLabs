alias Jason

input_path = "examples/paid_review_demo_input.json"
artifact_path = "examples/output/paid_review_demo_artifact.json"

input =
  input_path
  |> File.read!()
  |> Jason.decode!()

proposed_action = input["proposed_action"]
evidence_context = input["evidence_context"]
expected_decision = input["expected_decision"]
trace_id = input["trace_id"]

authorization_ok? = evidence_context["authorization"] == true
wallet_allowlist_ok? = evidence_context["wallet_allowlist"] == true
quorum_approval_ok? = evidence_context["quorum_approval"] == true

policy_freshness_ok? =
  evidence_context["policy_freshness_seconds"] <= evidence_context["policy_freshness_ttl_seconds"]

action_risk = evidence_context["action_risk"]

decision =
  cond do
    not authorization_ok? or not wallet_allowlist_ok? -> "BLOCK"
    not quorum_approval_ok? or not policy_freshness_ok? -> "ESCALATE"
    action_risk == "high_value_low_reversibility" -> "ESCALATE"
    true -> "ALLOW"
  end

stop_reason =
  cond do
    decision == "BLOCK" ->
      "authorization_or_wallet_allowlist_failed"

    not quorum_approval_ok? and not policy_freshness_ok? ->
      "missing_quorum_approval_and_stale_policy_state"

    not quorum_approval_ok? ->
      "missing_quorum_approval"

    not policy_freshness_ok? ->
      "stale_policy_state"

    decision == "ESCALATE" ->
      "high_value_low_reversibility_action"

    true ->
      "approved_under_current_evidence"
  end

execution_allowed = decision == "ALLOW"

checks = [
  %{name: "authorization", status: if(authorization_ok?, do: "PASS", else: "FAIL")},
  %{name: "wallet_allowlist", status: if(wallet_allowlist_ok?, do: "PASS", else: "FAIL")},
  %{name: "quorum_approval", status: if(quorum_approval_ok?, do: "PASS", else: "FAIL")},
  %{name: "policy_freshness", status: if(policy_freshness_ok?, do: "PASS", else: "FAIL")},
  %{
    name: "action_risk",
    status: if(action_risk == "high_value_low_reversibility", do: "REVIEW", else: "PASS")
  }
]

artifact = %{
  schema: "pythia.demo.artifact.v1",
  artifact_id: "artifact_paid_review_demo_001",
  trace_id: trace_id,
  proposed_action: proposed_action,
  decision_time_evidence: evidence_context,
  checks: checks,
  outcome: decision,
  execution_allowed: execution_allowed,
  stop_reason: stop_reason,
  digest: %{
    algorithm: "sha256",
    value: "deterministic_demo_digest_placeholder"
  }
}

File.mkdir_p!(Path.dirname(artifact_path))
File.write!(artifact_path, Jason.encode!(artifact, pretty: true) <> "\n")

check_line = fn name, status ->
  dots = String.duplicate(".", max(1, 20 - String.length(name)))
  "  #{name} #{dots} #{status}"
end

IO.puts("PythiaLabs Demo: Web3 treasury action\n")
IO.puts("Proposed action:")
IO.puts("  #{proposed_action["action_id"]}\n")
IO.puts("Checks:")
Enum.each(checks, fn c -> IO.puts(check_line.(c.name, c.status)) end)
IO.puts("\nDecision:")
IO.puts("  #{decision}\n")
IO.puts("Execution allowed:")
IO.puts("  #{execution_allowed}\n")
IO.puts("Stop reason:")
IO.puts("  #{stop_reason}\n")
IO.puts("Artifact:")
IO.puts("  #{artifact_path}\n")
IO.puts("Result:")

result_label = if decision == expected_decision, do: "PASS", else: "FAIL"
IO.puts("  #{result_label} — expected #{expected_decision}, got #{decision}")
