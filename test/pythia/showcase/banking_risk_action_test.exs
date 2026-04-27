defmodule Pythia.Showcase.BankingRiskActionTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.BankingRiskAction

  setup do
    action = %{
      action_id: "bank_act_001",
      action_type: "fraud_response",
      operator_id: "risk_operator_7",
      account_id: "acct_demo_01",
      action_time: ~U[2026-04-26 09:00:00Z],
      decision_time: ~U[2026-04-26 09:01:00Z]
    }

    governance_record = %{
      authorization_valid_from: ~U[2026-04-26 08:30:00Z],
      authorization_valid_to: ~U[2026-04-26 10:30:00Z],
      authorization_recorded_at: ~U[2026-04-26 08:45:00Z],
      evidence_observed_at: ~U[2026-04-26 08:55:00Z],
      evidence_valid_until: ~U[2026-04-26 09:10:00Z],
      decision_time_knowledge_present: true,
      operator_approval_present: true
    }

    %{action: action, governance_record: governance_record}
  end

  test "accepted action returns banking_risk_action_accepted", ctx do
    assert {:ok, %{status: :accepted, stop_reason: :banking_risk_action_accepted}} =
             BankingRiskAction.evaluate(ctx.action, ctx.governance_record)
  end

  test "missing operator approval returns missing_operator_approval", ctx do
    record = %{ctx.governance_record | operator_approval_present: false}

    assert {:error, %{status: :rejected, stop_reason: :missing_operator_approval}} =
             BankingRiskAction.evaluate(ctx.action, record)
  end

  test "stale evidence returns stale_evidence", ctx do
    record = %{ctx.governance_record | evidence_valid_until: ~U[2026-04-26 08:59:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :stale_evidence}} =
             BankingRiskAction.evaluate(ctx.action, record)
  end

  test "authorization known after decision_time returns authorization_unknown_at_decision_time",
       ctx do
    record = %{ctx.governance_record | authorization_recorded_at: ~U[2026-04-26 09:03:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :authorization_unknown_at_decision_time}} =
             BankingRiskAction.evaluate(ctx.action, record)
  end

  test "evidence verification succeeds for clean evidence", ctx do
    result = BankingRiskAction.evaluate(ctx.action, ctx.governance_record)
    evidence = BankingRiskAction.export_evidence(result)

    assert {:ok, %{status: :verified, algorithm: "sha256"}} =
             BankingRiskAction.verify_evidence(evidence)
  end

  test "evidence verification fails for tampered evidence", ctx do
    result = BankingRiskAction.evaluate(ctx.action, ctx.governance_record)

    tampered =
      result
      |> BankingRiskAction.export_evidence()
      |> put_in(["payload", "stop_reason"], "tampered_stop_reason")

    assert {:error, %{status: :rejected, reason: :digest_mismatch}} =
             BankingRiskAction.verify_evidence(tampered)
  end
end
