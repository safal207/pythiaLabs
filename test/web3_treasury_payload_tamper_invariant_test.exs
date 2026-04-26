defmodule Pythia.Web3TreasuryPayloadTamperInvariantTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.Web3TreasuryAction

  @payload_field_paths [
    ["status"],
    ["stop_reason"],
    ["trace"],
    ["trace", Access.at(0), "event"],
    ["trace", Access.at(-1), "stop_reason"]
    # Requires non-empty trace; guarded by "valid fixtures include non-empty trace"
  ]

  @evidence_field_paths Enum.map(@payload_field_paths, &["payload" | &1])
  @envelope_field_paths Enum.map(@payload_field_paths, &["artifact", "payload" | &1])

  test "valid fixtures include non-empty trace" do
    evidence_trace = get_in(valid_evidence(), ["payload", "trace"])
    envelope_trace = get_in(valid_envelope(), ["artifact", "payload", "trace"])

    assert is_list(evidence_trace)
    assert evidence_trace != []
    assert is_list(envelope_trace)
    assert envelope_trace != []
  end

  test "evidence payload field tampering is rejected with digest_mismatch" do
    evidence = valid_evidence()

    for field_path <- @evidence_field_paths do
      tampered = put_in(evidence, field_path, "tampered_value")

      assert {:error, %{reason: :digest_mismatch}} =
               Web3TreasuryAction.verify_evidence(tampered),
             "Failed for path: #{inspect(field_path)}"
    end
  end

  test "envelope artifact payload field tampering is rejected with digest_mismatch" do
    envelope = valid_envelope()

    for field_path <- @envelope_field_paths do
      tampered = put_in(envelope, field_path, "tampered_value")

      assert {:error, %{reason: :digest_mismatch}} =
               Web3TreasuryAction.verify_evidence_envelope(tampered),
             "Failed for path: #{inspect(field_path)}"
    end
  end

  test "direct digest tampering is rejected for evidence and envelope" do
    tampered_evidence =
      put_in(valid_evidence(), ["digest"], String.duplicate("0", 64))

    assert {:error, %{reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_evidence(tampered_evidence)

    tampered_integrity =
      put_in(valid_envelope(), ["integrity", "digest"], String.duplicate("0", 64))

    assert {:error, %{reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered_integrity)

    tampered_artifact =
      put_in(valid_envelope(), ["artifact", "digest"], String.duplicate("0", 64))

    assert {:error, %{reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered_artifact)
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
    {:ok, payload} = Web3TreasuryAction.evaluate(base_action(), base_governance_record())
    {:ok, payload}
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
