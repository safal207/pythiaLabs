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

  test "accepted trace includes account_id in proposed_action", ctx do
    assert {:ok, %{trace: trace}} = BankingRiskAction.evaluate(ctx.action, ctx.governance_record)
    assert hd(trace).account_id == "acct_demo_01"
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

  test "evidence with unexpected top-level key is rejected", ctx do
    result = BankingRiskAction.evaluate(ctx.action, ctx.governance_record)

    tampered =
      result
      |> BankingRiskAction.export_evidence()
      |> Map.put("hidden_policy", "fake")

    assert {:error, %{status: :rejected, reason: :invalid_evidence_shape}} =
             BankingRiskAction.verify_evidence(tampered)
  end

  test "unsupported action_type returns unsupported_action_type", ctx do
    action = %{ctx.action | action_type: "wire_override"}

    assert {:error, %{status: :rejected, stop_reason: :unsupported_action_type}} =
             BankingRiskAction.evaluate(action, ctx.governance_record)
  end

  test "authorization_not_yet_valid is rejected", ctx do
    record = %{ctx.governance_record | authorization_valid_from: ~U[2026-04-26 09:30:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :authorization_not_yet_valid}} =
             BankingRiskAction.evaluate(ctx.action, record)
  end

  test "authorization_expired is rejected", ctx do
    record = %{ctx.governance_record | authorization_valid_to: ~U[2026-04-26 08:50:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :authorization_expired}} =
             BankingRiskAction.evaluate(ctx.action, record)
  end

  test "evidence_recorded_after_decision_time is rejected", ctx do
    record = %{ctx.governance_record | evidence_observed_at: ~U[2026-04-26 09:03:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :evidence_recorded_after_decision_time}} =
             BankingRiskAction.evaluate(ctx.action, record)
  end

  test "missing_decision_time_knowledge is rejected", ctx do
    record = %{ctx.governance_record | decision_time_knowledge_present: false}

    assert {:error, %{status: :rejected, stop_reason: :missing_decision_time_knowledge}} =
             BankingRiskAction.evaluate(ctx.action, record)
  end

  test "decision_time_before_action_time is rejected", ctx do
    action = %{ctx.action | decision_time: ~U[2026-04-26 08:59:00Z]}

    assert {:error, %{status: :rejected, stop_reason: :decision_time_before_action_time}} =
             BankingRiskAction.evaluate(action, ctx.governance_record)
  end

  test "missing required action field reports missing_field details", ctx do
    action = Map.delete(ctx.action, :account_id)

    assert {:error, %{status: :rejected, stop_reason: :invalid_action_shape, trace: trace}} =
             BankingRiskAction.evaluate(action, ctx.governance_record)

    assert Enum.at(trace, 1).missing_field == :account_id
  end

  test "invalid governance record boolean shape reports invalid field", ctx do
    record = %{ctx.governance_record | operator_approval_present: "yes"}

    assert {:error, %{status: :rejected, stop_reason: :invalid_governance_record, trace: trace}} =
             BankingRiskAction.evaluate(ctx.action, record)

    assert Enum.at(trace, 1).invalid_field == :operator_approval_present
    assert Enum.at(trace, 1).expected_type == :boolean
  end

  test "evaluate fallback rejects non-map inputs" do
    assert {:error, %{status: :rejected, stop_reason: :invalid_action_or_governance_record}} =
             BankingRiskAction.evaluate(nil, nil)
  end

  test "verify_evidence rejects non-map input" do
    assert {:error, %{status: :rejected, reason: :invalid_evidence_shape}} =
             BankingRiskAction.verify_evidence("not-a-map")
  end

  test "verify_evidence remains stable when payload keys are reordered", ctx do
    result = BankingRiskAction.evaluate(ctx.action, ctx.governance_record)
    evidence = BankingRiskAction.export_evidence(result)
    shuffled_payload_pairs = evidence["payload"] |> Map.to_list() |> Enum.shuffle()
    reordered_payload = Map.new(shuffled_payload_pairs)
    reordered_evidence = Map.put(evidence, "payload", reordered_payload)

    assert {:ok, %{status: :verified}} = BankingRiskAction.verify_evidence(reordered_evidence)

    assert evidence["digest"] ==
             BankingRiskAction.digest_export_payload(reordered_payload)["digest"]
  end

  test "evidence digest is stable for accepted snapshot", ctx do
    result = BankingRiskAction.evaluate(ctx.action, ctx.governance_record)
    digest = BankingRiskAction.export_digest(result)

    assert digest["algorithm"] == "sha256"
    assert digest["digest"] == "db3eaf5416545ea0d6cd50e61a904dd703b6b3933ec62b599316566f07825865"
  end

  test "canonicalization handles control characters and float values" do
    payload = %{
      status: :accepted,
      stop_reason: :banking_risk_action_accepted,
      trace: [
        %{
          event: :decision,
          result: :accept,
          note: "line1\nline2\ttab\bbackspace\fform" <> <<1>>,
          confidence: 0.85
        }
      ]
    }

    evidence = BankingRiskAction.export_evidence({:ok, payload})
    assert {:ok, %{status: :verified}} = BankingRiskAction.verify_evidence(evidence)
  end
end
