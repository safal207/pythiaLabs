defmodule Pythia.Web3TreasuryTraceEvidenceTest do
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

  test "export_digest/1 returns SHA-256 metadata", ctx do
    result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    digest = Web3TreasuryAction.export_digest(result)

    assert digest["algorithm"] == "sha256"
    assert is_binary(digest["digest"])
    assert String.length(digest["digest"]) == 64
    assert digest["digest"] =~ ~r/\A[0-9a-f]{64}\z/
  end

  test "export_evidence/1 returns payload + digest", ctx do
    result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    evidence = Web3TreasuryAction.export_evidence(result)

    assert evidence["artifact_type"] == "pythia.web3_treasury_action.decision_trace.v1"
    assert evidence["algorithm"] == "sha256"
    assert is_binary(evidence["digest"])
    assert evidence["payload"] == Web3TreasuryAction.export_result(result)
  end

  test "digest is deterministic for same accepted result", ctx do
    result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)

    first = Web3TreasuryAction.export_digest(result)
    second = Web3TreasuryAction.export_digest(result)

    assert first == second
  end

  test "digest changes when decision changes", ctx do
    accepted = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)

    rejected =
      Web3TreasuryAction.evaluate(ctx.action, %{ctx.governance_record | quorum_met: false})

    assert Web3TreasuryAction.export_digest(accepted)["digest"] !=
             Web3TreasuryAction.export_digest(rejected)["digest"]
  end

  test "canonical map key order is stable" do
    first =
      {:ok,
       %{
         status: :accepted,
         stop_reason: :treasury_transfer_accepted,
         trace: [
           %{
             event: :decision,
             result: :accept,
             reason: "x",
             context: %{"z" => 3, "a" => 1, "m" => 2}
           }
         ]
       }}

    second =
      {:ok,
       %{
         trace: [
           %{
             result: :accept,
             reason: "x",
             event: :decision,
             context: %{"m" => 2, "a" => 1, "z" => 3}
           }
         ],
         stop_reason: :treasury_transfer_accepted,
         status: :accepted
       }}

    assert Web3TreasuryAction.canonical_export_string(first) ==
             Web3TreasuryAction.canonical_export_string(second)
  end

  test "canonical encoder preserves booleans in rejected payload", ctx do
    rejected =
      Web3TreasuryAction.evaluate(ctx.action, %{ctx.governance_record | quorum_met: false})

    payload = Web3TreasuryAction.export_evidence(rejected)["payload"]

    quorum_entry = Enum.find(payload["trace"], fn entry -> entry["event"] == "quorum_check" end)

    assert quorum_entry["actual"] == false
  end

  test "canonical_export_string/1 returns stable binary fields", ctx do
    result = Web3TreasuryAction.evaluate(ctx.action, ctx.governance_record)
    canonical = Web3TreasuryAction.canonical_export_string(result)

    assert is_binary(canonical)
    assert String.contains?(canonical, "\"status\"")
    assert String.contains?(canonical, "\"trace\"")
    assert String.contains?(canonical, "\"stop_reason\"")
  end
end
