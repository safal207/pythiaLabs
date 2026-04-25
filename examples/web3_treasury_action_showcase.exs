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

scenario_inputs = [
  {"accepted transfer", base_action, base_governance_record},
  {"quorum not met", base_action, %{base_governance_record | quorum_met: false}},
  {"voting still open", base_action,
   %{base_governance_record | voting_closed_at: ~U[2026-04-25 12:30:00Z]}},
  {"timelock not satisfied", base_action,
   %{base_governance_record | timelock_until: ~U[2026-04-25 12:30:00Z]}},
  {
    "valid authorization but unknown",
    base_action,
    %{base_governance_record | authorization_recorded_at: ~U[2026-04-25 12:30:00Z]}
  },
  {
    "transfer expired",
    %{base_action | action_time: ~U[2026-04-25 12:40:00Z]},
    %{
      base_governance_record
      | transfer_expires_at: ~U[2026-04-25 12:30:00Z],
        authorization_valid_to: ~U[2026-04-25 13:30:00Z]
    }
  }
]

print_result = fn scenario_name, result ->
  IO.puts("\nScenario: #{scenario_name}")

  case result do
    {:ok, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Stop reason: #{payload.stop_reason}")

    {:error, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Stop reason: #{payload.stop_reason}")
  end
end

IO.puts("Web3 Treasury Action Showcase")

Enum.each(scenario_inputs, fn {name, action, governance_record} ->
  action
  |> Web3TreasuryAction.evaluate(governance_record)
  |> print_result.(name)
end)
