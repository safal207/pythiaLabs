alias Pythia.Showcase.BitemporalAuthorization

base_action = %{
  action_id: "act_001",
  action_type: "delete_user_data",
  actor: "agent_alpha",
  target: "user_123",
  required_permission: "user_data.delete"
}

scenario_inputs = [
  {
    "valid and known",
    Map.merge(base_action, %{
      action_time: ~U[2026-04-25 10:15:00Z],
      decision_time: ~U[2026-04-25 10:16:00Z]
    }),
    %{
      permission: "user_data.delete",
      valid_from: ~U[2026-04-25 10:00:00Z],
      valid_to: ~U[2026-04-25 10:30:00Z],
      recorded_at: ~U[2026-04-25 10:10:00Z]
    }
  },
  {
    "valid but unknown",
    Map.merge(base_action, %{
      action_time: ~U[2026-04-25 10:15:00Z],
      decision_time: ~U[2026-04-25 10:16:00Z]
    }),
    %{
      permission: "user_data.delete",
      valid_from: ~U[2026-04-25 10:00:00Z],
      valid_to: ~U[2026-04-25 10:30:00Z],
      recorded_at: ~U[2026-04-25 10:20:00Z]
    }
  },
  {
    "expired",
    Map.merge(base_action, %{
      action_time: ~U[2026-04-25 10:35:00Z],
      decision_time: ~U[2026-04-25 10:36:00Z]
    }),
    %{
      permission: "user_data.delete",
      valid_from: ~U[2026-04-25 10:00:00Z],
      valid_to: ~U[2026-04-25 10:30:00Z],
      recorded_at: ~U[2026-04-25 10:10:00Z]
    }
  },
  {
    "future permission",
    Map.merge(base_action, %{
      action_time: ~U[2026-04-25 09:55:00Z],
      decision_time: ~U[2026-04-25 09:56:00Z]
    }),
    %{
      permission: "user_data.delete",
      valid_from: ~U[2026-04-25 10:00:00Z],
      valid_to: ~U[2026-04-25 10:30:00Z],
      recorded_at: ~U[2026-04-25 09:45:00Z]
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

IO.puts("Bitemporal Authorization Showcase")

Enum.each(scenario_inputs, fn {name, action, permission_record} ->
  action
  |> BitemporalAuthorization.evaluate(permission_record)
  |> print_result.(name)
end)
