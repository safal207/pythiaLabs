defmodule Pythia.Web3TreasuryPayloadTamperInvariantTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.Web3TreasuryAction

  @static_payload_field_paths [
    ["status"],
    ["stop_reason"],
    ["trace"]
  ]

  setup do
    result = valid_result()
    evidence = Web3TreasuryAction.export_evidence(result)
    envelope = Web3TreasuryAction.export_evidence_envelope(result)

    evidence_trace = get_in(evidence, ["payload", "trace"])
    envelope_trace = get_in(envelope, ["artifact", "payload", "trace"])

    assert is_list(evidence_trace) and evidence_trace != [],
           "export_evidence produced empty or missing trace — fixture is invalid"

    assert is_list(envelope_trace) and envelope_trace != [],
           "export_evidence_envelope produced empty or missing trace — fixture is invalid"

    first = 0
    last = length(evidence_trace) - 1

    dynamic_payload_paths =
      Enum.uniq([
        ["trace", Access.at(first), "event"],
        ["trace", Access.at(first), "stop_reason"],
        ["trace", Access.at(last), "event"],
        ["trace", Access.at(last), "stop_reason"]
      ])

    all_payload_paths = @static_payload_field_paths ++ dynamic_payload_paths

    evidence_paths = Enum.map(all_payload_paths, &(["payload"] ++ &1))
    envelope_paths = Enum.map(all_payload_paths, &(["artifact", "payload"] ++ &1))

    %{
      evidence: evidence,
      envelope: envelope,
      evidence_paths: evidence_paths,
      envelope_paths: envelope_paths
    }
  end

  test "evidence payload field tampering is rejected with digest_mismatch", ctx do
    for path <- ctx.evidence_paths do
      assert_tamper_rejected(ctx.evidence, path, :digest_mismatch,
        via: &Web3TreasuryAction.verify_evidence/1
      )
    end
  end

  test "evidence direct digest tampering is rejected with digest_mismatch", %{evidence: evidence} do
    tampered = put_in(evidence, ["digest"], zeroed_digest())

    assert {:error, %{reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_evidence(tampered)
  end

  test "envelope artifact payload field tampering is rejected with digest_mismatch", ctx do
    for path <- ctx.envelope_paths do
      assert_tamper_rejected(ctx.envelope, path, :digest_mismatch,
        via: &Web3TreasuryAction.verify_evidence_envelope/1
      )
    end
  end

  test "envelope integrity digest tampering is rejected with integrity_mismatch", %{
    envelope: envelope
  } do
    tampered = put_in(envelope, ["integrity", "digest"], zeroed_digest())

    assert {:error, %{reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "envelope artifact digest tampering is rejected with integrity_mismatch", %{
    envelope: envelope
  } do
    tampered = put_in(envelope, ["artifact", "digest"], zeroed_digest())

    assert {:error, %{reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  defp assert_tamper_rejected(artifact, field_path, expected_reason, via: verify_fun) do
    tampered = put_in(artifact, field_path, "tampered_value")

    assert get_in(tampered, field_path) == "tampered_value",
           "Mutation did not apply — path may be wrong: #{inspect(field_path)}"

    verification = verify_fun.(tampered)

    assert {:error, %{reason: ^expected_reason}} = verification,
           "Expected #{inspect(expected_reason)} after tampering #{inspect(field_path)}, got: #{inspect(verification)}"
  end

  defp zeroed_digest, do: String.duplicate("0", 64)

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
end
