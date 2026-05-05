defmodule Pythia.Mcp.JsonEvaluatorTest do
  use ExUnit.Case, async: true

  alias Pythia.Mcp.JsonEvaluator

  @accept_body %{
    "gate" => "agent_infra_action",
    "action" => %{
      "action_id" => "infra_act_001",
      "action_type" => "volume_delete",
      "actor_id" => "agent_ops_7",
      "resource_id" => "db_volume_primary",
      "resource_type" => "database_volume",
      "target_environment" => "production",
      "action_time" => "2026-04-27T12:00:00Z",
      "decision_time" => "2026-04-27T12:00:09Z"
    },
    "safety_context" => %{
      "credential_scope" => "scoped_operator",
      "explicit_user_approval_present" => true,
      "environment_scope_verified" => true,
      "documentation_verified" => true,
      "dry_run_completed" => true,
      "backup_isolation" => "off_target",
      "decision_time_knowledge_present" => true
    }
  }

  @banking_body %{
    "gate" => "banking_risk_action",
    "action" => %{
      "action_id" => "bank_act_001",
      "action_type" => "fraud_response",
      "operator_id" => "risk_operator_7",
      "account_id" => "acct_demo_01",
      "action_time" => "2026-04-26T09:00:00Z",
      "decision_time" => "2026-04-26T09:01:00Z"
    },
    "governance" => %{
      "authorization_valid_from" => "2026-04-26T08:30:00Z",
      "authorization_valid_to" => "2026-04-26T10:30:00Z",
      "authorization_recorded_at" => "2026-04-26T08:45:00Z",
      "evidence_observed_at" => "2026-04-26T08:55:00Z",
      "evidence_valid_until" => "2026-04-26T09:10:00Z",
      "decision_time_knowledge_present" => true,
      "operator_approval_present" => true
    }
  }

  @web3_body %{
    "gate" => "web3_treasury_action",
    "action" => %{
      "action_id" => "dao_act_001",
      "action_type" => "treasury_transfer",
      "actor" => "agent_alpha",
      "dao_id" => "dao_pythia",
      "proposal_id" => "prop_001",
      "amount" => 10_000,
      "asset" => "USDC",
      "recipient" => "0xRecipient",
      "required_permission" => "treasury.transfer",
      "action_time" => "2026-04-25T12:00:00Z",
      "decision_time" => "2026-04-25T12:01:00Z"
    },
    "governance" => %{
      "proposal_id" => "prop_001",
      "permission" => "treasury.transfer",
      "quorum_met" => true,
      "voting_closed_at" => "2026-04-25T11:00:00Z",
      "timelock_until" => "2026-04-25T11:30:00Z",
      "authorization_valid_from" => "2026-04-25T11:30:00Z",
      "authorization_valid_to" => "2026-04-25T13:00:00Z",
      "authorization_recorded_at" => "2026-04-25T11:45:00Z",
      "transfer_expires_at" => "2026-04-25T13:00:00Z"
    }
  }

  test "banking gate ACCEPT and artifact type" do
    json = Jason.encode!(@banking_body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "ALLOW"
    assert resp.evidence["artifact_type"] == "pythia.banking_risk_action.decision_trace.v1"
  end

  test "banking gate BLOCK on missing operator approval" do
    gov = Map.put(@banking_body["governance"], "operator_approval_present", false)
    body = Map.put(@banking_body, "governance", gov)
    json = Jason.encode!(body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "BLOCK"
    assert resp.stop_reason == "missing_operator_approval"
  end

  test "banking accepts governance_record alias key" do
    body =
      @banking_body
      |> Map.delete("governance")
      |> Map.put("governance_record", @banking_body["governance"])

    json = Jason.encode!(body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "ALLOW"
  end

  test "web3 treasury gate ACCEPT and artifact type" do
    json = Jason.encode!(@web3_body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "ALLOW"
    assert resp.stop_reason == "treasury_transfer_accepted"
    assert resp.evidence["artifact_type"] == "pythia.web3_treasury_action.decision_trace.v1"
  end

  test "web3 treasury gate BLOCK on quorum false" do
    gov = Map.put(@web3_body["governance"], "quorum_met", false)
    body = Map.put(@web3_body, "governance", gov)
    json = Jason.encode!(body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "BLOCK"
    assert resp.stop_reason == "quorum_not_met"
  end

  test "accept path maps to ALLOW and includes evidence" do
    json = Jason.encode!(@accept_body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "ALLOW"
    assert resp.status == "accepted"
    assert resp.ok == true
    assert is_map(resp.evidence)
    assert resp.evidence["artifact_type"] == "pythia.agent_infra_action.decision_trace.v1"
  end

  test "reject path maps to BLOCK on missing approval" do
    ctx = Map.put(@accept_body["safety_context"], "explicit_user_approval_present", false)
    body = Map.put(@accept_body, "safety_context", ctx)
    json = Jason.encode!(body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "BLOCK"
    assert resp.status == "rejected"
    assert resp.stop_reason == "destructive_action_requires_explicit_approval"
  end

  test "missing gate returns error" do
    json = Jason.encode!(Map.delete(@accept_body, "gate"))
    assert {:error, err} = JsonEvaluator.run(json)
    assert err.ok == false
    assert err.error == "missing_gate"
  end

  test "explicit false booleans are read correctly (not treated as missing)" do
    ctx =
      @accept_body["safety_context"]
      |> Map.put("explicit_user_approval_present", false)

    body = Map.put(@accept_body, "safety_context", ctx)
    json = Jason.encode!(body)
    assert {:ok, resp} = JsonEvaluator.run(json)
    assert resp.outcome == "BLOCK"
  end
end
