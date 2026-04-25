defmodule Pythia.Web3TreasuryTraceExportTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.Web3TreasuryAction

  setup do
    action = %{
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

    governance_record = %{
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

    %{action: action, governance_record: governance_record}
  end

  test "export_result/1 converts accepted result into string-key map", ctx do
    accepted_result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    exported = Web3TreasuryAction.export_result(accepted_result)

    assert exported["status"] == "accepted"
    assert exported["stop_reason"] == "treasury_transfer_accepted"
    assert is_list(exported["trace"])
    assert hd(exported["trace"])["event"] == "proposed_action"
    assert List.last(exported["trace"])["event"] == "decision"
    assert List.last(exported["trace"])["stop_reason"] == "treasury_transfer_accepted"
  end

  test "export_result/1 converts rejected result into string-key map", ctx do
    rejected_result =
      Web3TreasuryAction.evaluate(ctx.action, %{ctx.governance_record | quorum_met: false})

    exported = Web3TreasuryAction.export_result(rejected_result)

    assert exported["status"] == "rejected"
    assert exported["stop_reason"] == "quorum_not_met"

    quorum_entry = Enum.find(exported["trace"], fn entry -> entry["event"] == "quorum_check" end)

    assert quorum_entry["event"] == "quorum_check"
    assert quorum_entry["result"] == "fail"
    assert quorum_entry["reason"] == "quorum_not_met"
    assert quorum_entry["actual"] == false
  end

  test "DateTime values are converted to ISO8601 strings", ctx do
    accepted_result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    exported = Web3TreasuryAction.export_result(accepted_result)

    voting_entry =
      Enum.find(exported["trace"], fn entry -> entry["event"] == "voting_window_check" end)

    assert is_binary(voting_entry["action_time"])
    assert voting_entry["action_time"] == "2026-04-25T12:00:00Z"
  end

  test "output is deterministic", ctx do
    accepted_result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)

    first = Web3TreasuryAction.export_result(accepted_result)
    second = Web3TreasuryAction.export_result(accepted_result)

    assert first == second
  end

  test "export_result_json/1 handles available and unavailable json encoder", ctx do
    accepted_result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    json_result = Web3TreasuryAction.export_result_json(accepted_result)

    if Code.ensure_loaded?(Jason) and function_exported?(Jason, :encode!, 2) do
      assert {:ok, json} = json_result
      assert is_binary(json)
      assert String.contains?(json, "treasury_transfer_accepted")
      assert String.contains?(json, "proposed_action")
    else
      assert {:error, :json_encoder_unavailable} = json_result
    end
  end
end
