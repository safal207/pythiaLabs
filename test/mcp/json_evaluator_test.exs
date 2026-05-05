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
end
