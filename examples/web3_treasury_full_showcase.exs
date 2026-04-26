alias Pythia.Showcase.Web3TreasuryAction

base_action = %{
  action_id: "dao_act_001",
  action_type: "treasury_transfer",
  actor: "agent_alpha",
  dao_id: "dao_pythia",
  proposal_id: "prop_001",
  amount: 10_000,
  asset: "USDC",
  recipient: "0xRecipient",
  required_permission: "treasury.transfer",
  action_time: ~U[2026-04-25 12:00:00Z],
  decision_time: ~U[2026-04-25 12:01:00Z]
}

base_governance_record = %{
  proposal_id: "prop_001",
  permission: "treasury.transfer",
  quorum_met: true,
  voting_closed_at: ~U[2026-04-25 11:00:00Z],
  timelock_until: ~U[2026-04-25 11:30:00Z],
  authorization_valid_from: ~U[2026-04-25 11:30:00Z],
  authorization_valid_to: ~U[2026-04-25 13:00:00Z],
  authorization_recorded_at: ~U[2026-04-25 11:45:00Z],
  transfer_expires_at: ~U[2026-04-25 13:00:00Z]
}

extract_payload = fn
  {:ok, payload} -> payload
  {:error, payload} -> payload
end

print_step = fn title ->
  IO.puts("\n=== #{title} ===")
end

find_failed_check = fn trace ->
  trace
  |> Enum.find(fn entry -> entry[:result] == :fail end)
  |> case do
    nil -> "none"
    failed -> to_string(failed[:event] || :unknown)
  end
end

IO.puts("Web3 Treasury Full Showcase")

print_step.("A. Accepted treasury action")
accepted_result = Web3TreasuryAction.evaluate(base_action, base_governance_record)
accepted_payload = extract_payload.(accepted_result)

IO.puts("status: #{accepted_payload.status}")
IO.puts("stop_reason: #{accepted_payload.stop_reason}")
IO.puts("trace_event_count: #{length(accepted_payload.trace)}")
IO.puts("final_decision: #{List.last(accepted_payload.trace).result}")

print_step.("B. Rejected treasury action: quorum_not_met")
rejected_quorum_result =
  Web3TreasuryAction.evaluate(base_action, %{base_governance_record | quorum_met: false})

rejected_quorum_payload = extract_payload.(rejected_quorum_result)

IO.puts("status: #{rejected_quorum_payload.status}")
IO.puts("stop_reason: #{rejected_quorum_payload.stop_reason}")
IO.puts("failed_check: #{find_failed_check.(rejected_quorum_payload.trace)}")

print_step.("C. Rejected treasury action: authorization_valid_but_unknown_at_decision_time")
rejected_unknown_result =
  Web3TreasuryAction.evaluate(base_action, %{
    base_governance_record
    | authorization_recorded_at: ~U[2026-04-25 12:30:00Z]
  })

rejected_unknown_payload = extract_payload.(rejected_unknown_result)

IO.puts("status: #{rejected_unknown_payload.status}")
IO.puts("stop_reason: #{rejected_unknown_payload.stop_reason}")

print_step.("D. Evidence export")
exported_result = Web3TreasuryAction.export_result(accepted_result)
IO.puts("export_status: #{exported_result["status"]}")
IO.puts("export_stop_reason: #{exported_result["stop_reason"]}")
IO.puts("trace_length: #{length(exported_result["trace"])}")

print_step.("E. Evidence digest")
digest = Web3TreasuryAction.export_digest(accepted_result)
IO.puts("algorithm: #{digest["algorithm"]}")
IO.puts("digest: #{digest["digest"]}")

print_step.("F. Evidence verification")
evidence = Web3TreasuryAction.export_evidence(accepted_result)
verified_evidence = Web3TreasuryAction.verify_evidence(evidence)
IO.inspect(verified_evidence, label: "verified_result")

print_step.("G. Tampered evidence rejection")
tampered_evidence = put_in(evidence, ["payload", "stop_reason"], "tampered_stop_reason")
rejected_tampered_evidence = Web3TreasuryAction.verify_evidence(tampered_evidence)
IO.inspect(rejected_tampered_evidence, label: "tamper_rejection")

print_step.("H. Unsigned evidence envelope")
unsigned_envelope = Web3TreasuryAction.export_evidence_envelope(accepted_result)
verified_envelope = Web3TreasuryAction.verify_evidence_envelope(unsigned_envelope)
IO.puts("schema: #{unsigned_envelope["schema"]}")
IO.puts("digest: #{unsigned_envelope["integrity"]["digest"]}")
IO.inspect(verified_envelope, label: "verification_status")

print_step.("I. Signed demo envelope")
{:ok, signed_envelope} =
  Web3TreasuryAction.sign_evidence_envelope_demo(unsigned_envelope, "demo_dao_reviewer")

IO.puts("signature_status: #{signed_envelope["signature"]["status"]}")
IO.puts("algorithm: #{signed_envelope["signature"]["algorithm"]}")
IO.puts("signer_id: #{signed_envelope["signature"]["signer_id"]}")

print_step.("J. Signed demo verification")
verified_signed_envelope = Web3TreasuryAction.verify_signed_evidence_envelope_demo(signed_envelope)
IO.inspect(verified_signed_envelope, label: "signed_verification")

print_step.("K. Tampered signed demo envelope rejection")
tampered_signed_envelope =
  put_in(signed_envelope, ["artifact", "payload", "stop_reason"], "tampered_stop_reason")

rejected_tampered_signed =
  Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered_signed_envelope)

IO.inspect(rejected_tampered_signed, label: "tampered_signed_rejection")
