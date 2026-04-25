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

accepted_result = Web3TreasuryAction.evaluate(base_action, base_governance_record)
unsigned_envelope = Web3TreasuryAction.export_evidence_envelope(accepted_result)

signed_envelope =
  Web3TreasuryAction.sign_evidence_envelope_demo(unsigned_envelope, "demo_dao_reviewer")

tampered_signed_envelope =
  put_in(signed_envelope, ["artifact", "payload", "stop_reason"], "tampered_stop_reason")

print_verification = fn label, verification_result ->
  IO.puts("\n#{label}:")

  case verification_result do
    {:ok, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Signature: #{payload.signature}")
      IO.puts("Signer: #{payload.signer_id}")

    {:error, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Reason: #{payload.reason}")
  end
end

IO.puts("Web3 Treasury Signed Envelope Demo")

IO.puts("\nSigned envelope:")
IO.puts("Status: #{signed_envelope["signature"]["status"]}")
IO.puts("Algorithm: #{signed_envelope["signature"]["algorithm"]}")
IO.puts("Signer: #{signed_envelope["signature"]["signer_id"]}")
IO.puts("Signature: #{signed_envelope["signature"]["signature"]}")

print_verification.(
  "Verification",
  Web3TreasuryAction.verify_signed_evidence_envelope_demo(signed_envelope)
)

print_verification.(
  "Tampered verification",
  Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered_signed_envelope)
)
