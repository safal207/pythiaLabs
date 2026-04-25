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

    result = Web3TreasuryAction.evaluate(action, governance_record)
    envelope = Web3TreasuryAction.export_evidence_envelope(result)

    %{action: action, governance_record: governance_record, result: result, envelope: envelope}
  end

  test "valid unsigned signature placeholder verifies successfully", %{envelope: envelope} do
    assert {:ok, %{status: :verified}} = Web3TreasuryAction.verify_evidence_envelope(envelope)
  end

  test "envelope contains expected artifact and integrity shape", %{envelope: envelope} do
    assert envelope["schema"] == "pythia.evidence.envelope.v1"

    assert envelope["artifact"]["artifact_type"] ==
             "pythia.web3_treasury_action.decision_trace.v1"

    assert envelope["artifact"]["algorithm"] == "sha256"
    assert envelope["artifact"]["digest"] =~ ~r/\A[0-9a-f]{64}\z/
    assert is_map(envelope["artifact"]["payload"])
    assert envelope["integrity"]["algorithm"] == "sha256"
    assert envelope["integrity"]["digest"] == envelope["artifact"]["digest"]
    assert envelope["canonicalization"] == "pythia.canonical_export.v1"
    assert envelope["signature"]["status"] == "unsigned"
  end

  test "envelope export is deterministic", %{result: result} do
    first = Web3TreasuryAction.export_evidence_envelope(result)
    second = Web3TreasuryAction.export_evidence_envelope(result)

    assert first == second
  end

  test "verification result exposes schema, canonicalization and digest", %{envelope: envelope} do
    assert {:ok, verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)
    assert verification.status == :verified
    assert verification.schema == "pythia.evidence.envelope.v1"
    assert verification.canonicalization == "pythia.canonical_export.v1"
    assert verification.digest == envelope["integrity"]["digest"]
    assert verification.evidence.status == :verified
  end

  test "top-level integrity mismatch is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["integrity", "digest"], String.duplicate("0", 64))

    assert {:error, %{status: :rejected, reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "tampered artifact payload is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["artifact", "payload", "stop_reason"], "tampered_stop_reason")

    assert {:error, %{status: :rejected, reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "unsupported envelope schema is rejected", %{envelope: envelope} do
    tampered = Map.put(envelope, "schema", "pythia.evidence.envelope.v2")

    assert {:error, %{status: :rejected, reason: :unsupported_envelope_schema}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "unsupported canonicalization is rejected", %{envelope: envelope} do
    tampered = Map.put(envelope, "canonicalization", "pythia.canonical_export.v2")

    assert {:error, %{status: :rejected, reason: :unsupported_canonicalization}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "unsupported integrity algorithm is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["integrity", "algorithm"], "sha512")

    assert {:error, %{status: :rejected, reason: :unsupported_algorithm}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "unsigned envelope with non-nil signature algorithm is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["signature", "algorithm"], "ed25519")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "unsigned envelope with non-nil public_key is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["signature", "public_key"], "fake-public-key")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "unsigned envelope with non-nil signature is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["signature", "signature"], "fake-signature")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "non-unsigned signature status is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["signature", "status"], "signed")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "unsigned signature map with unexpected key is rejected", %{envelope: envelope} do
    tampered = put_in(envelope, ["signature", "sig_v2"], "fake")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "missing signature map returns invalid_envelope_shape", %{envelope: envelope} do
    malformed = Map.delete(envelope, "signature")

    assert {:error, %{status: :rejected, reason: :invalid_envelope_shape}} =
             Web3TreasuryAction.verify_evidence_envelope(malformed)
  end

  test "missing integrity map returns invalid_envelope_shape", %{envelope: envelope} do
    malformed = Map.delete(envelope, "integrity")

    assert {:error, %{status: :rejected, reason: :invalid_envelope_shape}} =
             Web3TreasuryAction.verify_evidence_envelope(malformed)
  end

  test "boolean false is preserved inside rejected quorum envelope payload", ctx do
    envelope =
      ctx.action
      |> Web3TreasuryAction.evaluate(%{ctx.governance_record | quorum_met: false})
      |> Web3TreasuryAction.export_evidence_envelope()

    assert {:ok, _verification} = Web3TreasuryAction.verify_evidence_envelope(envelope)

    quorum_entry =
      envelope["artifact"]["payload"]["trace"]
      |> Enum.find(fn entry -> entry["event"] == "quorum_check" end)

    assert quorum_entry["actual"] == false
  end
end
