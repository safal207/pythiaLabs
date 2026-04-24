alias Pythia.Showcase.AgentSafetyDemo

safe_action = %{
  action_id: "act_001",
  action_type: "read_public_report",
  actor: "agent_alpha",
  target: "report_q1",
  required_permission: "report.read",
  granted_permissions: ["report.read"],
  metadata: %{source: "showcase"}
}

unsafe_action = %{
  action_id: "act_002",
  action_type: "delete_user_data",
  actor: "agent_alpha",
  target: "user_123",
  required_permission: "user_data.delete",
  granted_permissions: [],
  metadata: %{source: "showcase"}
}

invalid_action = %{
  action_id: "act_003",
  action_type: "",
  actor: "agent_alpha",
  target: "report_q1",
  required_permission: "report.read",
  granted_permissions: ["report.read"],
  metadata: %{source: "showcase"}
}

print_result = fn title, result ->
  IO.puts("\nScenario: #{title}")

  case result do
    {:ok, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Final action: #{payload.action.action_type}")
      IO.puts("Confidence: #{payload.confidence}")
      IO.puts("Stop reason: #{payload.stop_reason}")
      IO.puts("Trace:")
      Enum.each(payload.trace, &IO.puts("- #{inspect(&1)}"))

    {:error, payload} ->
      IO.puts("Status: #{payload.status}")
      IO.puts("Rejected action: #{payload.rejected_action.action_type}")
      IO.puts("Stop reason: #{payload.stop_reason}")
      IO.puts("Trace:")
      Enum.each(payload.trace, &IO.puts("- #{inspect(&1)}"))
  end
end

IO.puts("Agent Safety Showcase")

safe_action
|> AgentSafetyDemo.run()
|> print_result.("safe action")

unsafe_action
|> AgentSafetyDemo.run()
|> print_result.("unsafe action")

invalid_action
|> AgentSafetyDemo.run()
|> print_result.("invalid action")
