defmodule Pythia.Web3TreasuryTraceVerificationTest do
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

  test "valid evidence verifies successfully", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()

    assert {:ok, verification} = Web3TreasuryAction.verify_evidence(evidence)
    assert verification.status == :verified
    assert verification.artifact_type == "pythia.web3_treasury_action.decision_trace.v1"
    assert verification.algorithm == "sha256"
    assert verification.digest == evidence["digest"]
  end

  test "tampered payload returns digest_mismatch", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()

    tampered = put_in(evidence, ["payload", "stop_reason"], "tampered_stop_reason")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence(tampered)
    assert verification.status == :rejected
    assert verification.reason == :digest_mismatch
    assert verification.expected_digest == tampered["digest"]
    assert verification.actual_digest != tampered["digest"]
  end

  test "unsupported artifact type returns unsupported_artifact_type", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()
      |> Map.put("artifact_type", "pythia.other_artifact.v1")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence(evidence)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_artifact_type
  end

  test "unsupported algorithm returns unsupported_algorithm", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()
      |> Map.put("algorithm", "sha512")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence(evidence)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_algorithm
  end

  test "missing digest returns invalid_evidence_shape", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()
      |> Map.delete("digest")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence(evidence)
    assert verification.status == :rejected
    assert verification.reason == :invalid_evidence_shape
  end

  test "missing payload returns invalid_evidence_shape", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()
      |> Map.delete("payload")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence(evidence)
    assert verification.status == :rejected
    assert verification.reason == :invalid_evidence_shape
  end

  test "invalid digest format returns invalid_evidence_shape", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()
      |> Map.put("digest", "INVALID_DIGEST")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence(evidence)
    assert verification.status == :rejected
    assert verification.reason == :invalid_evidence_shape
  end

  test "verification is deterministic", ctx do
    evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence()

    first = Web3TreasuryAction.verify_evidence(evidence)
    second = Web3TreasuryAction.verify_evidence(evidence)

    assert first == second
  end

  test "digest verification preserves booleans", ctx do
    rejected_evidence =
      ctx.action
      |> Web3TreasuryAction.evaluate(%{ctx.governance_record | quorum_met: false})
      |> Web3TreasuryAction.export_evidence()

    assert {:ok, _verification} = Web3TreasuryAction.verify_evidence(rejected_evidence)

    quorum_entry =
      rejected_evidence["payload"]["trace"]
      |> Enum.find(fn entry -> entry["event"] == "quorum_check" end)

    assert quorum_entry["actual"] == false
  end
end
