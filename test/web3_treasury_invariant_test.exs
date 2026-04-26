defmodule Pythia.Web3TreasuryInvariantTest do
  use ExUnit.Case, async: true
  use ExUnitProperties

  alias Pythia.Showcase.Web3TreasuryAction

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

  defp unsigned_envelope do
    base_action()
    |> Web3TreasuryAction.evaluate(base_governance_record())
    |> Web3TreasuryAction.export_evidence_envelope()
  end

  @tag :property
  property "accepted valid input preserves accepted decision invariants" do
    check all(max_runs: 50) do
      assert {:ok, payload} = Web3TreasuryAction.evaluate(base_action(), base_governance_record())
      assert payload.status == :accepted
      assert List.last(payload.trace).event == :decision
      assert List.last(payload.trace).result == :accept
      assert payload.stop_reason == :treasury_transfer_accepted
    end
  end

  @tag :property
  property "quorum false always rejects with quorum invariant" do
    check all(quorum_met <- boolean(), max_runs: 50) do
      record = %{base_governance_record() | quorum_met: quorum_met}
      result = Web3TreasuryAction.evaluate(base_action(), record)

      if quorum_met do
        assert {:ok, %{status: :accepted}} = result
      else
        assert {:error, %{status: :rejected, stop_reason: :quorum_not_met, trace: trace}} = result

        assert Enum.any?(trace, fn entry ->
                 entry == %{
                   event: :quorum_check,
                   result: :fail,
                   actual: false,
                   reason: :quorum_not_met
                 }
               end)
      end
    end
  end

  @tag :property
  property "tampered evidence payload always triggers digest mismatch" do
    check all(
            tampered_reason <- string(:alphanumeric, min_length: 1, max_length: 30),
            max_runs: 50
          ) do
      result = Web3TreasuryAction.evaluate(base_action(), base_governance_record())
      evidence = Web3TreasuryAction.export_evidence(result)
      original_reason = get_in(evidence, ["payload", "stop_reason"])

      if tampered_reason != original_reason do
        tampered = put_in(evidence, ["payload", "stop_reason"], tampered_reason)

        assert {:error, %{reason: :digest_mismatch}} =
                 Web3TreasuryAction.verify_evidence(tampered)
      end
    end
  end

  @tag :property
  property "tampered envelope artifact payload always triggers digest mismatch" do
    check all(
            tampered_reason <- string(:alphanumeric, min_length: 1, max_length: 30),
            max_runs: 50
          ) do
      envelope = unsigned_envelope()
      original_reason = get_in(envelope, ["artifact", "payload", "stop_reason"])

      if tampered_reason != original_reason do
        tampered = put_in(envelope, ["artifact", "payload", "stop_reason"], tampered_reason)

        assert {:error, %{reason: :digest_mismatch}} =
                 Web3TreasuryAction.verify_evidence_envelope(tampered)
      end
    end
  end

  @reserved_top_level_keys ~w(schema artifact canonicalization integrity signature)

  @tag :property
  property "unknown top-level envelope fields are rejected" do
    key_gen =
      string(:alphanumeric, min_length: 1, max_length: 20)
      |> filter(fn key -> key not in @reserved_top_level_keys end)

    check all(
            key <- key_gen,
            value <- one_of([string(:printable, min_length: 0, max_length: 20), integer()]),
            max_runs: 50
          ) do
      envelope = unsigned_envelope()
      tampered = Map.put(envelope, key, value)

      assert {:error, %{reason: :invalid_envelope_shape}} =
               Web3TreasuryAction.verify_evidence_envelope(tampered)
    end
  end

  @tag :property
  property "signed demo verification succeeds and signer_id changes signature" do
    check all(
            signer_id <- string(:alphanumeric, min_length: 1, max_length: 24),
            alt_signer_id <- string(:alphanumeric, min_length: 1, max_length: 24),
            signer_id != alt_signer_id,
            max_runs: 50
          ) do
      envelope = unsigned_envelope()

      assert {:ok, signed_envelope} =
               Web3TreasuryAction.sign_evidence_envelope_demo(envelope, signer_id)

      assert {:ok, %{status: :verified}} =
               Web3TreasuryAction.verify_signed_evidence_envelope_demo(signed_envelope)

      assert {:ok, alt_signed_envelope} =
               Web3TreasuryAction.sign_evidence_envelope_demo(envelope, alt_signer_id)

      refute get_in(signed_envelope, ["signature", "signature"]) ==
               get_in(alt_signed_envelope, ["signature", "signature"])
    end
  end

  @tag :property
  property "blank signer_id values are rejected" do
    blank_gen =
      one_of([
        constant(""),
        string([?	, ?\s], min_length: 1, max_length: 8)
      ])

    check all(
            blank_signer_id <- blank_gen,
            max_runs: 50
          ) do
      envelope = unsigned_envelope()

      assert {:error, %{reason: :invalid_signer_id}} =
               Web3TreasuryAction.sign_evidence_envelope_demo(envelope, blank_signer_id)
    end
  end
end
