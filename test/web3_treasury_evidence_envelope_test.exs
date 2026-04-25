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

    %{envelope: envelope}
  end

  test "valid unsigned signature placeholder verifies successfully", %{envelope: envelope} do
    assert {:ok, %{status: :verified}} = Web3TreasuryAction.verify_evidence_envelope(envelope)
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

  test "missing signature map returns invalid_envelope_shape", %{envelope: envelope} do
    malformed = Map.delete(envelope, "signature")

    assert {:error, %{status: :rejected, reason: :invalid_envelope_shape}} =
             Web3TreasuryAction.verify_evidence_envelope(malformed)
  end
end
