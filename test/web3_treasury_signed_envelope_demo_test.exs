defmodule Pythia.Web3TreasurySignedEnvelopeDemoTest do
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

    unsigned_envelope =
      action
      |> Web3TreasuryAction.evaluate(governance_record)
      |> Web3TreasuryAction.export_evidence_envelope()

    %{unsigned_envelope: unsigned_envelope}
  end

  test "sign_evidence_envelope_demo/2 returns signed_demo envelope", %{
    unsigned_envelope: envelope
  } do
    assert {:ok, signed} =
             Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "demo_dao_reviewer")

    assert signed["signature"]["status"] == "signed_demo"
    assert signed["signature"]["algorithm"] == "sha256-demo"
    assert signed["signature"]["signer_id"] == "demo_dao_reviewer"
    assert signed["signature"]["signature"] =~ ~r/\A[0-9a-f]{64}\z/
  end

  test "signing is deterministic", %{unsigned_envelope: envelope} do
    {:ok, first} = Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "demo_dao_reviewer")
    {:ok, second} = Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "demo_dao_reviewer")

    assert first["signature"]["signature"] == second["signature"]["signature"]
  end

  test "different signer_id changes signature", %{unsigned_envelope: envelope} do
    {:ok, first} = Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "demo_dao_reviewer")

    {:ok, second} =
      Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "demo_security_reviewer")

    refute first["signature"]["signature"] == second["signature"]["signature"]
  end

  test "valid signed envelope verifies", %{unsigned_envelope: envelope} do
    {:ok, signed} = Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "demo_dao_reviewer")

    assert {:ok, verification} = Web3TreasuryAction.verify_signed_evidence_envelope_demo(signed)
    assert verification.status == :verified
    assert verification.signature == :verified_demo
    assert verification.signer_id == "demo_dao_reviewer"
    assert verification.digest == envelope["integrity"]["digest"]
  end

  test "tampered artifact payload is rejected", %{unsigned_envelope: envelope} do
    tampered =
      envelope
      |> Web3TreasuryAction.sign_evidence_envelope_demo("demo_dao_reviewer")
      |> then(fn {:ok, signed} -> signed end)
      |> put_in(["artifact", "payload", "stop_reason"], "tampered_stop_reason")

    assert {:error, %{status: :rejected, reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered)
  end

  test "tampered signature is rejected with :signature_mismatch", %{unsigned_envelope: envelope} do
    tampered =
      envelope
      |> Web3TreasuryAction.sign_evidence_envelope_demo("demo_dao_reviewer")
      |> then(fn {:ok, signed} -> signed end)
      |> put_in(["signature", "signature"], String.duplicate("f", 64))

    assert {:error, %{status: :rejected, reason: :signature_mismatch}} =
             Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered)
  end

  test "unsupported signature algorithm is rejected", %{unsigned_envelope: envelope} do
    tampered =
      envelope
      |> Web3TreasuryAction.sign_evidence_envelope_demo("demo_dao_reviewer")
      |> then(fn {:ok, signed} -> signed end)
      |> put_in(["signature", "algorithm"], "sha512-demo")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_algorithm}} =
             Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered)
  end

  test "unsupported signature status is rejected", %{unsigned_envelope: envelope} do
    tampered =
      envelope
      |> Web3TreasuryAction.sign_evidence_envelope_demo("demo_dao_reviewer")
      |> then(fn {:ok, signed} -> signed end)
      |> put_in(["signature", "status"], "signed")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered)
  end

  test "signed demo signature map with unexpected key is rejected", %{unsigned_envelope: envelope} do
    tampered =
      envelope
      |> Web3TreasuryAction.sign_evidence_envelope_demo("demo_dao_reviewer")
      |> then(fn {:ok, signed} -> signed end)
      |> put_in(["signature", "sig_v2"], "fake")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered)
  end

  test "blank signer_id is rejected", %{unsigned_envelope: envelope} do
    tampered =
      envelope
      |> Web3TreasuryAction.sign_evidence_envelope_demo("demo_dao_reviewer")
      |> then(fn {:ok, signed} -> signed end)
      |> put_in(["signature", "signer_id"], "")

    assert {:error, %{status: :rejected, reason: :invalid_signer_id}} =
             Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered)
  end

  test "unsigned envelope is still verified by verify_evidence_envelope/1", %{
    unsigned_envelope: envelope
  } do
    assert {:ok, %{status: :verified}} = Web3TreasuryAction.verify_evidence_envelope(envelope)
  end

  test "signed_demo envelope is rejected by unsigned verifier", %{unsigned_envelope: envelope} do
    {:ok, signed} = Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "demo_dao_reviewer")

    assert {:error, %{status: :rejected, reason: :unsupported_signature_status}} =
             Web3TreasuryAction.verify_evidence_envelope(signed)
  end

  test "signed envelope with unexpected top-level key is rejected", %{unsigned_envelope: envelope} do
    tampered =
      envelope
      |> Web3TreasuryAction.sign_evidence_envelope_demo("demo_dao_reviewer")
      |> then(fn {:ok, signed} -> signed end)
      |> Map.put("hidden_policy", "fake")

    assert {:error, %{status: :rejected, reason: :invalid_signed_envelope_shape}} =
             Web3TreasuryAction.verify_signed_evidence_envelope_demo(tampered)
  end

  test "signing invalid unsigned envelope returns invalid_envelope_shape", %{
    unsigned_envelope: envelope
  } do
    malformed = Map.put(envelope, "hidden_policy", "fake")

    assert {:error, %{status: :rejected, reason: :invalid_envelope_shape}} =
             Web3TreasuryAction.sign_evidence_envelope_demo(malformed, "demo_dao_reviewer")
  end

  test "signing with blank signer_id is rejected", %{unsigned_envelope: envelope} do
    assert {:error, %{status: :rejected, reason: :invalid_signer_id}} =
             Web3TreasuryAction.sign_evidence_envelope_demo(envelope, "")
  end

  test "signing non-map envelope is rejected" do
    assert {:error, %{status: :rejected, reason: :invalid_envelope_shape}} =
             Web3TreasuryAction.sign_evidence_envelope_demo("bad-envelope", "demo_dao_reviewer")
  end

  test "signing with non-binary signer_id is rejected", %{unsigned_envelope: envelope} do
    assert {:error, %{status: :rejected, reason: :invalid_signer_id}} =
             Web3TreasuryAction.sign_evidence_envelope_demo(envelope, :demo_dao_reviewer)
  end
end
