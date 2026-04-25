defmodule Pythia.Web3TreasuryActionShowcaseTest do
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

  test "accepted transfer returns treasury_transfer_accepted", ctx do
    assert {:ok, %{status: :accepted, stop_reason: :treasury_transfer_accepted}} =
             Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
  end

  test "missing proposal returns missing_proposal_record", ctx do
    action = %{ctx.action | proposal_id: "prop_missing"}

    assert {:error, %{status: :rejected, stop_reason: :missing_proposal_record}} =
             Web3TreasuryAction.evaluate(action, ctx.governance_record)
  end

  test "permission mismatch returns permission_mismatch", ctx do
    action = %{ctx.action | required_permission: "dao.upgrade"}

    assert {:error, %{status: :rejected, stop_reason: :permission_mismatch}} =
             Web3TreasuryAction.evaluate(action, ctx.governance_record)
  end

  test "quorum not met returns quorum_not_met", ctx do
    record = %{ctx.governance_record | quorum_met: false}

    assert {:error, %{status: :rejected, stop_reason: :quorum_not_met}} =
             Web3TreasuryAction.evaluate(ctx.action, record)
  end

  test "voting still open returns voting_window_still_open", ctx do
    record = %{ctx.governance_record | voting_closed_at: ~U[2026-04-25 12:30:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :voting_window_still_open}} =
             Web3TreasuryAction.evaluate(ctx.action, record)
  end

  test "timelock not satisfied returns timelock_not_satisfied", ctx do
    record = %{ctx.governance_record | timelock_until: ~U[2026-04-25 12:30:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :timelock_not_satisfied}} =
             Web3TreasuryAction.evaluate(ctx.action, record)
  end

  test "authorization not yet valid returns authorization_not_yet_valid", ctx do
    record = %{ctx.governance_record | authorization_valid_from: ~U[2026-04-25 12:30:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :authorization_not_yet_valid}} =
             Web3TreasuryAction.evaluate(ctx.action, record)
  end

  test "authorization expired returns authorization_expired", ctx do
    action = %{ctx.action | action_time: ~U[2026-04-25 13:30:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :authorization_expired}} =
             Web3TreasuryAction.evaluate(action, ctx.governance_record)
  end

  test "authorization valid but unknown returns authorization_valid_but_unknown_at_decision_time",
       ctx do
    record = %{ctx.governance_record | authorization_recorded_at: ~U[2026-04-25 12:30:00Z]}

    assert {:error,
            %{status: :rejected, stop_reason: :authorization_valid_but_unknown_at_decision_time}} =
             Web3TreasuryAction.evaluate(ctx.action, record)
  end

  test "transfer expired returns transfer_expired", ctx do
    action = %{ctx.action | action_time: ~U[2026-04-25 12:40:00Z]}

    record = %{
      ctx.governance_record
      | transfer_expires_at: ~U[2026-04-25 12:30:00Z],
        authorization_valid_to: ~U[2026-04-25 13:30:00Z]
    }

    assert {:error, %{status: :rejected, stop_reason: :transfer_expired}} =
             Web3TreasuryAction.evaluate(action, record)
  end

  test "malformed governance record returns invalid_governance_record", ctx do
    malformed = Map.delete(ctx.governance_record, :timelock_until)

    assert {:error, %{status: :rejected, stop_reason: :invalid_governance_record}} =
             Web3TreasuryAction.evaluate(ctx.action, malformed)
  end

  test "repeated input returns deterministic output", ctx do
    first = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    second = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)

    assert first == second
  end

  test "accepted trace has exact chronological event order", ctx do
    assert {:ok, %{trace: trace}} = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)

    assert trace == [
             :proposed_action,
             :proposal_match_check,
             :permission_check,
             :quorum_check,
             :voting_window_check,
             :timelock_check,
             :authorization_valid_time_check,
             :authorization_transaction_time_check,
             :transfer_expiration_check,
             :decision
           ]
  end

  test "rejected trace ends with decision", ctx do
    action = %{ctx.action | proposal_id: "missing"}

    assert {:error, %{trace: trace}} = Web3TreasuryAction.evaluate(action, ctx.governance_record)
    assert List.last(trace) == :decision
  end

  test "action_time == voting_closed_at is accepted for voting window", ctx do
    action = %{ctx.action | action_time: ctx.governance_record.voting_closed_at}
    voting_closed_at = ctx.governance_record.voting_closed_at

    record = %{
      ctx.governance_record
      | timelock_until: voting_closed_at,
        authorization_valid_from: voting_closed_at
    }

    assert {:ok, %{status: :accepted}} =
             Web3TreasuryAction.evaluate(action, record)
  end

  test "action_time == timelock_until is accepted for timelock", ctx do
    action = %{ctx.action | action_time: ctx.governance_record.timelock_until}

    assert {:ok, %{status: :accepted}} =
             Web3TreasuryAction.evaluate(action, ctx.governance_record)
  end

  test "action_time == authorization_valid_from is accepted", ctx do
    action = %{ctx.action | action_time: ctx.governance_record.authorization_valid_from}

    assert {:ok, %{status: :accepted}} =
             Web3TreasuryAction.evaluate(action, ctx.governance_record)
  end

  test "action_time == authorization_valid_to is accepted", ctx do
    action = %{ctx.action | action_time: ctx.governance_record.authorization_valid_to}

    assert {:ok, %{status: :accepted}} =
             Web3TreasuryAction.evaluate(action, ctx.governance_record)
  end

  test "authorization_recorded_at == decision_time is accepted", ctx do
    record = %{ctx.governance_record | authorization_recorded_at: ctx.action.decision_time}

    assert {:ok, %{status: :accepted}} = Web3TreasuryAction.evaluate(ctx.action, record)
  end

  test "action_time == transfer_expires_at is accepted", ctx do
    action = %{ctx.action | action_time: ctx.governance_record.transfer_expires_at}

    record = %{
      ctx.governance_record
      | authorization_valid_to: ctx.governance_record.transfer_expires_at
    }

    assert {:ok, %{status: :accepted}} = Web3TreasuryAction.evaluate(action, record)
  end

  test "string-key action and governance input works" do
    action = %{
      "action_id" => "dao_act_001",
      "action_type" => "treasury_transfer",
      "actor" => "agent_alpha",
      "dao_id" => "dao_pythia",
      "proposal_id" => "prop_001",
      "amount" => 10_000,
      "asset" => "USDC",
      "recipient" => "0xRecipient",
      "required_permission" => "treasury.transfer",
      "action_time" => ~U[2026-04-25 12:00:00Z],
      "decision_time" => ~U[2026-04-25 12:01:00Z]
    }

    governance_record = %{
      "proposal_id" => "prop_001",
      "permission" => "treasury.transfer",
      "quorum_met" => true,
      "voting_closed_at" => ~U[2026-04-25 11:00:00Z],
      "timelock_until" => ~U[2026-04-25 11:30:00Z],
      "authorization_valid_from" => ~U[2026-04-25 11:30:00Z],
      "authorization_valid_to" => ~U[2026-04-25 13:00:00Z],
      "authorization_recorded_at" => ~U[2026-04-25 11:45:00Z],
      "transfer_expires_at" => ~U[2026-04-25 13:00:00Z]
    }

    assert {:ok, %{status: :accepted, stop_reason: :treasury_transfer_accepted}} =
             Web3TreasuryAction.evaluate(action, governance_record)
  end

  test "string-key quorum false preserves false value and rejects with quorum_not_met", ctx do
    action = Map.new(ctx.action, fn {k, v} -> {Atom.to_string(k), v} end)
    governance_record = Map.new(ctx.governance_record, fn {k, v} -> {Atom.to_string(k), v} end)
    governance_record = Map.put(governance_record, "quorum_met", false)

    assert {:error, %{status: :rejected, stop_reason: :quorum_not_met}} =
             Web3TreasuryAction.evaluate(action, governance_record)
  end
end
