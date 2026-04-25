defmodule Pythia.Web3TreasuryEvidenceEnvelopeTest do
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

  test "export_evidence_envelope/1 returns expected envelope shape", ctx do
    result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    envelope = Web3TreasuryAction.export_evidence_envelope(result)

    assert envelope["schema"] == "pythia.evidence.envelope.v1"
    assert envelope["artifact_type"] == "pythia.web3_treasury_action.decision_trace.v1"
    assert envelope["canonicalization"] == "pythia.canonical_export.v1"
    assert envelope["integrity"]["algorithm"] == "sha256"
    assert envelope["integrity"]["digest"] =~ ~r/\A[0-9a-f]{64}\z/
    assert envelope["payload"] == Web3TreasuryAction.export_result(result)
    assert envelope["signature"]["status"] == "unsigned"
  end

  test "envelope export is deterministic", ctx do
    result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)

    first = Web3TreasuryAction.export_evidence_envelope(result)
    second = Web3TreasuryAction.export_evidence_envelope(result)

    assert first == second
  end

  test "valid envelope verifies successfully", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()

    assert {:ok, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :verified
    assert verification.schema == "pythia.evidence.envelope.v1"
    assert verification.artifact_type == "pythia.web3_treasury_action.decision_trace.v1"
    assert verification.integrity == :verified
    assert verification.signature == :unsigned
    assert verification.digest == envelope["integrity"]["digest"]
  end

  test "tampered payload returns digest_mismatch", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()

    tampered = put_in(envelope, ["payload", "stop_reason"], "tampered_stop_reason")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(tampered)
    assert verification.status == :rejected
    assert verification.reason == :digest_mismatch
    assert verification.expected_digest == tampered["integrity"]["digest"]
    assert verification.actual_digest != tampered["integrity"]["digest"]
  end

  test "unsupported schema returns unsupported_schema", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> Map.put("schema", "pythia.evidence.envelope.v2")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_schema
  end

  test "unsupported artifact type returns unsupported_artifact_type", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> Map.put("artifact_type", "pythia.other_artifact.v1")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_artifact_type
  end

  test "unsupported canonicalization returns unsupported_canonicalization", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> Map.put("canonicalization", "pythia.canonical_export.v2")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_canonicalization
  end

  test "unsupported algorithm returns unsupported_algorithm", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> put_in(["integrity", "algorithm"], "sha512")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_algorithm
  end

  test "missing integrity returns invalid_envelope_shape", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> Map.delete("integrity")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :invalid_envelope_shape
  end

  test "missing payload returns invalid_envelope_shape", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> Map.delete("payload")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :invalid_envelope_shape
  end

  test "unsupported signature status returns unsupported_signature_status", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> put_in(["signature", "status"], "signed")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_signature_status
  end

  test "unsigned signature placeholder requires nil signature fields", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(ctx.governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()
      |> put_in(["signature", "algorithm"], "ed25519")
      |> put_in(["signature", "public_key"], "fake_public_key")
      |> put_in(["signature", "signature"], "fake_signature")

    assert {:error, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :rejected
    assert verification.reason == :unsupported_signature_status
  end

  test "boolean false is preserved inside rejected quorum envelope payload", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(%{ctx.governance_record | quorum_met: false})
      |> Web3TreasuryAction.export_evidence_envelope()

    assert {:ok, _verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)

    quorum_entry =
      envelope["payload"]["trace"]
      |> Enum.find(fn entry -> entry["event"] == "quorum_check" end)

    assert quorum_entry["actual"] == false
  end
end
