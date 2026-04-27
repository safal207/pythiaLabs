alias Pythia.Showcase.BankingRiskAction

base_action = %{
  action_id: "bank_act_001",
  action_type: "fraud_response",
  operator_id: "risk_operator_7",
  account_id: "acct_demo_01",
  action_time: ~U[2026-04-26 09:00:00Z],
  decision_time: ~U[2026-04-26 09:01:00Z]
}

base_governance_record = %{
  authorization_valid_from: ~U[2026-04-26 08:30:00Z],
  authorization_valid_to: ~U[2026-04-26 10:30:00Z],
  authorization_recorded_at: ~U[2026-04-26 08:45:00Z],
  evidence_observed_at: ~U[2026-04-26 08:55:00Z],
  evidence_valid_until: ~U[2026-04-26 09:10:00Z],
  decision_time_knowledge_present: true,
  operator_approval_present: true
}

extract_payload = fn
  {:ok, payload} -> payload
  {:error, payload} -> payload
end

print_step = fn title ->
  IO.puts("\n=== #{title} ===")
end

print_verification = fn result ->
  case result do
    {:ok, payload} ->
      IO.puts("verification_status: #{payload.status}")
      IO.puts("algorithm: #{payload.algorithm}")
      IO.puts("digest: #{payload.digest}")

    {:error, payload} ->
      IO.puts("verification_status: #{payload.status}")
      IO.puts("reason: #{payload.reason}")
  end
end

IO.puts("Banking AI Risk Showcase")

IO.puts(
  "Deterministic local showcase only; not production banking integration, regulatory compliance, or cybersecurity protection."
)

print_step.("A. Accepted banking risk action")
accepted_result = BankingRiskAction.evaluate(base_action, base_governance_record)
accepted_payload = extract_payload.(accepted_result)

IO.puts("status: #{accepted_payload.status}")
IO.puts("stop_reason: #{accepted_payload.stop_reason}")
IO.puts("trace_event_count: #{length(accepted_payload.trace)}")

print_step.("B. Rejected action: missing operator approval")

missing_approval_result =
  BankingRiskAction.evaluate(base_action, %{
    base_governance_record
    | operator_approval_present: false
  })

missing_approval_payload = extract_payload.(missing_approval_result)
IO.puts("status: #{missing_approval_payload.status}")
IO.puts("stop_reason: #{missing_approval_payload.stop_reason}")

print_step.("C. Rejected action: stale evidence")

stale_evidence_result =
  BankingRiskAction.evaluate(base_action, %{
    base_governance_record
    | evidence_valid_until: ~U[2026-04-26 08:59:00Z]
  })

stale_evidence_payload = extract_payload.(stale_evidence_result)
IO.puts("status: #{stale_evidence_payload.status}")
IO.puts("stop_reason: #{stale_evidence_payload.stop_reason}")

print_step.("D. Rejected action: valid authorization but unknown at decision time")

unknown_auth_result =
  BankingRiskAction.evaluate(base_action, %{
    base_governance_record
    | authorization_recorded_at: ~U[2026-04-26 09:03:00Z]
  })

unknown_auth_payload = extract_payload.(unknown_auth_result)
IO.puts("status: #{unknown_auth_payload.status}")
IO.puts("stop_reason: #{unknown_auth_payload.stop_reason}")

print_step.("E. Evidence export")
exported = BankingRiskAction.export_result(accepted_result)
IO.puts("export_status: #{exported["status"]}")
IO.puts("export_stop_reason: #{exported["stop_reason"]}")

print_step.("F. Evidence digest")
digest = BankingRiskAction.export_digest(accepted_result)
IO.puts("algorithm: #{digest["algorithm"]}")
IO.puts("digest: #{digest["digest"]}")

print_step.("G. Evidence verification")
evidence = BankingRiskAction.export_evidence(accepted_result)
verification = BankingRiskAction.verify_evidence(evidence)
print_verification.(verification)

print_step.("H. Tampered evidence rejection")
tampered = put_in(evidence, ["payload", "stop_reason"], "tampered_stop_reason")
tampered_verification = BankingRiskAction.verify_evidence(tampered)
print_verification.(tampered_verification)

IO.puts("\nShowcase completed.")
