defmodule Pythia.BitemporalAuthorizationShowcaseTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.BitemporalAuthorization

  setup do
    action = %{
      action_id: "act_001",
      action_type: "delete_user_data",
      actor: "agent_alpha",
      target: "user_123",
      required_permission: "user_data.delete",
      action_time: ~U[2026-04-25 10:15:00Z],
      decision_time: ~U[2026-04-25 10:16:00Z]
    }

    permission_record = %{
      permission: "user_data.delete",
      valid_from: ~U[2026-04-25 10:00:00Z],
      valid_to: ~U[2026-04-25 10:30:00Z],
      recorded_at: ~U[2026-04-25 10:10:00Z]
    }

    %{action: action, permission_record: permission_record}
  end

  test "valid and known authorization is accepted", ctx do
    assert {:ok, %{status: :accepted, stop_reason: :authorization_valid_and_known, trace: trace}} =
             BitemporalAuthorization.evaluate(ctx.action, ctx.permission_record)

    assert Enum.map(trace, & &1.event) == [
             :proposed_action,
             :required_permission,
             :permission_match_check,
             :valid_time_check,
             :transaction_time_check,
             :decision
           ]
  end

  test "valid but unknown authorization is rejected", ctx do
    unknown_permission_record = %{ctx.permission_record | recorded_at: ~U[2026-04-25 10:20:00Z]}

    assert {:error,
            %{
              status: :rejected,
              stop_reason: :authorization_valid_but_unknown_at_decision_time,
              trace: trace
            }} =
             BitemporalAuthorization.evaluate(ctx.action, unknown_permission_record)

    assert Enum.map(trace, & &1.event) == [
             :proposed_action,
             :required_permission,
             :permission_match_check,
             :valid_time_check,
             :transaction_time_check,
             :decision
           ]
  end

  test "expired authorization is rejected", ctx do
    expired_action = %{ctx.action | action_time: ~U[2026-04-25 10:35:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :authorization_expired, trace: trace}} =
             BitemporalAuthorization.evaluate(expired_action, ctx.permission_record)

    assert Enum.map(trace, & &1.event) == [
             :proposed_action,
             :required_permission,
             :permission_match_check,
             :valid_time_check,
             :transaction_time_check,
             :decision
           ]
  end

  test "future authorization is rejected", ctx do
    future_action = %{ctx.action | action_time: ~U[2026-04-25 09:55:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :authorization_not_yet_valid}} =
             BitemporalAuthorization.evaluate(future_action, ctx.permission_record)
  end

  test "missing permission record is rejected", ctx do
    missing_permission_record = %{ctx.permission_record | permission: "billing.read"}

    assert {:error, %{status: :rejected, stop_reason: :missing_permission_record}} =
             BitemporalAuthorization.evaluate(ctx.action, missing_permission_record)
  end

  test "malformed temporal data is rejected", ctx do
    malformed_permission_record = %{ctx.permission_record | valid_to: nil}

    assert {:error, %{status: :rejected, stop_reason: :invalid_temporal_record}} =
             BitemporalAuthorization.evaluate(ctx.action, malformed_permission_record)
  end

  test "repeated input returns deterministic output", ctx do
    first = BitemporalAuthorization.evaluate(ctx.action, ctx.permission_record)
    second = BitemporalAuthorization.evaluate(ctx.action, ctx.permission_record)

    assert first == second
  end

  test "trace contains valid_time and transaction_time checks", ctx do
    assert {:error,
            %{
              stop_reason: :authorization_valid_but_unknown_at_decision_time,
              trace: trace
            }} =
             BitemporalAuthorization.evaluate(ctx.action, %{
               ctx.permission_record
               | recorded_at: ~U[2026-04-25 10:20:00Z]
             })

    assert Enum.any?(trace, fn entry ->
             entry.event == :valid_time_check and entry.result == :pass
           end)

    assert Enum.any?(trace, fn entry ->
             entry.event == :transaction_time_check and entry.result == :fail
           end)
  end

  test "action_time == valid_from is accepted", ctx do
    action_at_valid_from = %{ctx.action | action_time: ctx.permission_record.valid_from}

    assert {:ok, %{status: :accepted, stop_reason: :authorization_valid_and_known}} =
             BitemporalAuthorization.evaluate(action_at_valid_from, ctx.permission_record)
  end

  test "action_time == valid_to is accepted", ctx do
    action_at_valid_to = %{ctx.action | action_time: ctx.permission_record.valid_to}

    assert {:ok, %{status: :accepted, stop_reason: :authorization_valid_and_known}} =
             BitemporalAuthorization.evaluate(action_at_valid_to, ctx.permission_record)
  end

  test "recorded_at == decision_time is accepted", ctx do
    permission_known_at_decision = %{
      ctx.permission_record
      | recorded_at: ctx.action.decision_time
    }

    assert {:ok, %{status: :accepted, stop_reason: :authorization_valid_and_known}} =
             BitemporalAuthorization.evaluate(ctx.action, permission_known_at_decision)
  end
end
