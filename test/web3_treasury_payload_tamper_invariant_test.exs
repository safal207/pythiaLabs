defmodule Pythia.Web3TreasuryPayloadTamperInvariantTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.Web3TreasuryAction

  test "evidence payload field tampering is rejected with digest_mismatch" do
    fields = [
      ["payload", "status"],
      ["payload", "stop_reason"],
      ["payload", "trace"],
      ["payload", "trace", Access.at(0), "event"],
      ["payload", "trace", Access.at(-1), "stop_reason"]
    ]

    Enum.each(fields, fn field_path ->
      tampered = put_in(valid_evidence(), field_path, "tampered_value")

      assert {:error, %{reason: :digest_mismatch}} =
               Web3TreasuryAction.verify_evidence(tampered)
    end)
  end

  test "envelope artifact payload field tampering is rejected with digest_mismatch" do
    fields = [
      ["artifact", "payload", "status"],
      ["artifact", "payload", "stop_reason"],
      ["artifact", "payload", "trace"],
      ["artifact", "payload", "trace", Access.at(0), "event"],
      ["artifact", "payload", "trace", Access.at(-1), "stop_reason"]
    ]

    Enum.each(fields, fn field_path ->
      tampered = put_in(valid_envelope(), field_path, "tampered_value")

      assert {:error, %{reason: :digest_mismatch}} =
               Web3TreasuryAction.verify_evidence_envelope(tampered)
    end)
  end

  test "direct digest tampering is rejected for evidence and envelope" do
    tampered_evidence = Map.put(valid_evidence(), "digest", String.duplicate("0", 64))

    assert {:error, %{reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_evidence(tampered_evidence)

    tampered_integrity =
      put_in(valid_envelope(), ["integrity", "digest"], String.duplicate("0", 64))

    assert {:error, %{reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered_integrity)

    tampered_artifact =
      put_in(valid_envelope(), ["artifact", "digest"], String.duplicate("0", 64))

    assert {:error, %{reason: reason}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered_artifact)

    assert reason in [:integrity_mismatch, :digest_mismatch]
  end

  defp base_action do
    %{
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
  end

  defp base_governance_record do
    %{
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
  end

  defp valid_result do
    Web3TreasuryAction.evaluate(base_action(), base_governance_record())
  end

  defp valid_evidence do
    valid_result()
    |> Web3TreasuryAction.export_evidence()
  end

  defp valid_envelope do
    valid_result()
    |> Web3TreasuryAction.export_evidence_envelope()
  end
end
