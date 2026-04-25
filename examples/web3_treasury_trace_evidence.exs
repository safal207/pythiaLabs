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

rejected_result =
  Web3TreasuryAction.evaluate(base_action, %{base_governance_record | quorum_met: false})

accepted_evidence = Web3TreasuryAction.export_evidence(accepted_result)
rejected_evidence = Web3TreasuryAction.export_evidence(rejected_result)

print_evidence = fn label, evidence ->
  payload = evidence["payload"]

  IO.puts("\n#{label}:")
  IO.puts("Artifact type: #{evidence["artifact_type"]}")
  IO.puts("Algorithm: #{evidence["algorithm"]}")
  IO.puts("Digest: #{evidence["digest"]}")
  IO.puts("Status: #{payload["status"]}")
  IO.puts("Stop reason: #{payload["stop_reason"]}")
end

IO.puts("Web3 Treasury Trace Evidence")
print_evidence.("Accepted evidence", accepted_evidence)
print_evidence.("Rejected evidence", rejected_evidence)
