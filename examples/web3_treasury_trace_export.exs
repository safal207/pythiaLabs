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

accepted_export = Web3TreasuryAction.export_result(accepted_result)
rejected_export = Web3TreasuryAction.export_result(rejected_result)

IO.puts("Web3 Treasury Trace Export\n")

IO.puts("Accepted export:")
IO.inspect(accepted_export, pretty: true)

IO.puts("\nRejected export:")
IO.inspect(rejected_export, pretty: true)

if function_exported?(Web3TreasuryAction, :export_result_json, 1) do
  {:ok, accepted_json} = Web3TreasuryAction.export_result_json(accepted_result)
  {:ok, rejected_json} = Web3TreasuryAction.export_result_json(rejected_result)

  IO.puts("\nAccepted JSON export:")
  IO.puts(accepted_json)

  IO.puts("\nRejected JSON export:")
  IO.puts(rejected_json)
end
