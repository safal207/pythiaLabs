defmodule Pythia.AgentSafetyShowcaseTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.AgentSafetyDemo

  test "safe action proceeds" do
    action = %{
      action_id: "act_safe",
      action_type: "read_public_report",
      actor: "agent_alpha",
      target: "report_q1",
      required_permission: "report.read",
      granted_permissions: ["report.read"]
    }

    assert {:ok, %{status: :accepted, stop_reason: :constraints_satisfied, trace: trace}} =
             AgentSafetyDemo.run(action)

    assert Enum.any?(trace, fn entry -> entry.event == :decision and entry.result == :proceed end)
  end

  test "unsafe action is rejected when permission is missing" do
    action = %{
      action_id: "act_unsafe",
      action_type: "delete_user_data",
      actor: "agent_alpha",
      target: "user_123",
      required_permission: "user_data.delete",
      granted_permissions: []
    }

    assert {:error, %{status: :rejected, stop_reason: :missing_authorization, trace: trace}} =
             AgentSafetyDemo.run(action)

    assert Enum.any?(trace, fn entry ->
             entry.event == :constraint_check and entry.constraint == :permission_present and
               entry.result == :fail
           end)
  end

  test "invalid action shape is rejected" do
    invalid_actions = [
      %{
        action_id: "act_invalid_1",
        action_type: "read_public_report",
        actor: "",
        target: "report_q1",
        required_permission: "report.read",
        granted_permissions: ["report.read"]
      },
      %{
        action_id: "act_invalid_2",
        action_type: "",
        actor: "agent_alpha",
        target: "report_q1",
        required_permission: "report.read",
        granted_permissions: ["report.read"]
      },
      %{
        action_id: "act_invalid_3",
        action_type: "read_public_report",
        actor: "agent_alpha",
        target: "",
        required_permission: "report.read",
        granted_permissions: ["report.read"]
      },
      %{
        action_id: "act_invalid_4",
        action_type: "read_public_report",
        actor: "agent_alpha",
        target: "report_q1",
        required_permission: "",
        granted_permissions: ["report.read"]
      }
    ]

    Enum.each(invalid_actions, fn action ->
      assert {:error, %{status: :rejected, stop_reason: :invalid_action}} =
               AgentSafetyDemo.run(action)
    end)
  end

  test "output is deterministic for same input" do
    action = %{
      action_id: "act_deterministic",
      action_type: "transfer_funds",
      actor: "agent_alpha",
      target: "acct_42",
      required_permission: "funds.transfer",
      granted_permissions: []
    }

    first = AgentSafetyDemo.run(action)
    second = AgentSafetyDemo.run(action)

    assert first == second

    assert {:error, %{stop_reason: stop_reason_1}} = first
    assert {:error, %{stop_reason: stop_reason_2}} = second
    assert stop_reason_1 == stop_reason_2
  end
end
