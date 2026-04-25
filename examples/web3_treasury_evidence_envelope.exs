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
envelope = Web3TreasuryAction.export_evidence_envelope(accepted_result)
tampered_envelope = put_in(envelope, ["payload", "stop_reason"], "tampered_stop_reason")

print_verification = fn label, verification_result ->
  IO.puts("\n#{label}:")

  case verification_result do
    {:ok, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Integrity: #{payload.integrity}")
      IO.puts("Signature: #{payload.signature}")

    {:error, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Reason: #{payload.reason}")
  end
end

IO.puts("Web3 Treasury Evidence Envelope")
IO.puts("\nEnvelope:")
IO.puts("Schema: #{envelope["schema"]}")
IO.puts("Artifact type: #{envelope["artifact_type"]}")
IO.puts("Canonicalization: #{envelope["canonicalization"]}")
IO.puts("Integrity algorithm: #{envelope["integrity"]["algorithm"]}")
IO.puts("Digest: #{envelope["integrity"]["digest"]}")
IO.puts("Signature status: #{envelope["signature"]["status"]}")

print_verification.(
  "Valid envelope verification",
  Web3TreasuryAction.verify_evidence_envelope(envelope)
)

print_verification.(
  "Tampered envelope verification",
  Web3TreasuryAction.verify_evidence_envelope(tampered_envelope)
)
