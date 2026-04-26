defmodule Pythia.Web3TreasuryPayloadTamperInvariantTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.Web3TreasuryAction

  @replacement_values ["tampered_value", nil, 123, %{"x" => "y"}]

  @static_payload_field_paths [
    ["status"],
    ["stop_reason"],
    ["trace"]
  ]

  setup do
    {:ok, payload} = Web3TreasuryAction.evaluate(base_action(), base_governance_record())
    evidence = Web3TreasuryAction.export_evidence({:ok, payload})
    envelope = Web3TreasuryAction.export_evidence_envelope({:ok, payload})

    evidence_trace = get_in(evidence, ["payload", "trace"])
    envelope_trace = get_in(envelope, ["artifact", "payload", "trace"])

    assert is_list(evidence_trace) and evidence_trace != [],
           "export_evidence produced empty or missing trace — fixture is invalid"

    assert is_list(envelope_trace) and envelope_trace != [],
           "export_evidence_envelope produced empty or missing trace — fixture is invalid"

    trace_fields = extract_trace_fields(evidence_trace)

    first = 0
    last = length(evidence_trace) - 1

    dynamic_payload_paths =
      for pos <- [first, last],
          field <- trace_fields do
        ["trace", Access.at(pos), field]
      end
      |> Enum.uniq()

    all_payload_paths = @static_payload_field_paths ++ dynamic_payload_paths

    evidence_paths = Enum.map(all_payload_paths, &(["payload"] ++ &1))
    envelope_paths = Enum.map(all_payload_paths, &(["artifact", "payload"] ++ &1))

    %{
      evidence: evidence,
      envelope: envelope,
      evidence_paths: evidence_paths,
      envelope_paths: envelope_paths,
      trace_fields: trace_fields,
      trace_len: length(evidence_trace)
    }
  end

  test "evidence payload field tampering is rejected with digest_mismatch", ctx do
    test_tampering(
      ctx.evidence,
      ctx.evidence_paths,
      &Web3TreasuryAction.verify_evidence/1,
      :digest_mismatch
    )
  end

  test "evidence middle trace element tampering is rejected", ctx do
    assert ctx.trace_len >= 3,
           "expected trace length >= 3 for middle-index tamper coverage, got #{ctx.trace_len}"

    middle_paths =
      for i <- 1..(ctx.trace_len - 2),
          field <- ctx.trace_fields do
        ["payload", "trace", Access.at(i), field]
      end

    test_tampering(
      ctx.evidence,
      middle_paths,
      &Web3TreasuryAction.verify_evidence/1,
      :digest_mismatch
    )
  end

  test "evidence direct digest tampering is rejected with digest_mismatch", %{evidence: evidence} do
    tampered = put_in(evidence, ["digest"], tampered_digest())

    assert {:error, %{reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_evidence(tampered)
  end

  test "evidence trace list tampering (append/remove) is rejected", %{evidence: evidence} do
    trace = get_in(evidence, ["payload", "trace"])

    appended = put_in(evidence, ["payload", "trace"], trace ++ [%{"event" => "tampered"}])
    dropped = put_in(evidence, ["payload", "trace"], Enum.drop(trace, -1))

    assert {:error, %{reason: :digest_mismatch}} = Web3TreasuryAction.verify_evidence(appended)
    assert {:error, %{reason: :digest_mismatch}} = Web3TreasuryAction.verify_evidence(dropped)
  end

  test "envelope artifact payload field tampering is rejected with digest_mismatch", ctx do
    test_tampering(
      ctx.envelope,
      ctx.envelope_paths,
      &Web3TreasuryAction.verify_evidence_envelope/1,
      :digest_mismatch
    )
  end

  test "envelope middle trace element tampering is rejected", ctx do
    assert ctx.trace_len >= 3,
           "expected trace length >= 3 for middle-index tamper coverage, got #{ctx.trace_len}"

    middle_paths =
      for i <- 1..(ctx.trace_len - 2),
          field <- ctx.trace_fields do
        ["artifact", "payload", "trace", Access.at(i), field]
      end

    test_tampering(
      ctx.envelope,
      middle_paths,
      &Web3TreasuryAction.verify_evidence_envelope/1,
      :digest_mismatch
    )
  end

  test "envelope trace list tampering (append/remove) is rejected", %{envelope: envelope} do
    trace = get_in(envelope, ["artifact", "payload", "trace"])

    appended =
      put_in(envelope, ["artifact", "payload", "trace"], trace ++ [%{"event" => "tampered"}])

    dropped = put_in(envelope, ["artifact", "payload", "trace"], Enum.drop(trace, -1))

    assert {:error, %{reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(appended)

    assert {:error, %{reason: :digest_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(dropped)
  end

  test "envelope integrity digest tampering is rejected with integrity_mismatch", %{
    envelope: envelope
  } do
    tampered = put_in(envelope, ["integrity", "digest"], tampered_digest())

    assert {:error, %{reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  test "envelope artifact digest tampering is rejected with integrity_mismatch", %{
    envelope: envelope
  } do
    tampered = put_in(envelope, ["artifact", "digest"], tampered_digest())

    assert {:error, %{reason: :integrity_mismatch}} =
             Web3TreasuryAction.verify_evidence_envelope(tampered)
  end

  defp test_tampering(artifact, paths, verify_fun, expected_reason) do
    for path <- paths,
        replacement <- @replacement_values do
      assert_tamper_rejected(artifact, path, expected_reason,
        via: verify_fun,
        replacement: replacement
      )
    end
  end

  defp assert_tamper_rejected(artifact, field_path, expected_reason, opts) do
    verify_fun = Keyword.fetch!(opts, :via)
    replacement = Keyword.get(opts, :replacement, "tampered_value")
    tampered = put_in(artifact, field_path, replacement)

    assert get_in(tampered, field_path) == replacement,
           "Mutation did not apply — path may be wrong: #{inspect(field_path)}"

    verification = verify_fun.(tampered)

    assert {:error, %{reason: ^expected_reason}} = verification,
           "Expected #{inspect(expected_reason)} after tampering #{inspect(field_path)} with #{inspect(replacement)}, got: #{inspect(verification)}"
  end

  defp extract_trace_fields(trace) do
    [List.first(trace), List.last(trace)]
    |> Enum.filter(&is_map/1)
    |> Enum.flat_map(&Map.keys/1)
    |> Enum.filter(&is_binary/1)
    |> Enum.uniq()
  end

  defp tampered_digest, do: String.duplicate("0", 64)

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
end
