defmodule Pythia.Showcase.AgentInfraActionTest do
  use ExUnit.Case, async: true

  alias Pythia.Showcase.AgentInfraAction

  setup do
    action = %{
      action_id: "infra_act_001",
      action_type: "volume_delete",
      actor_id: "agent_ops_7",
      resource_id: "db_volume_primary",
      resource_type: "database_volume",
      target_environment: "production",
      action_time: ~U[2026-04-27 12:00:00Z],
      decision_time: ~U[2026-04-27 12:00:09Z]
    }

    safety_context = %{
      credential_scope: "scoped_operator",
      explicit_user_approval_present: true,
      environment_scope_verified: true,
      documentation_verified: true,
      dry_run_completed: true,
      backup_isolation: "off_target",
      decision_time_knowledge_present: true
    }

    %{action: action, safety_context: safety_context}
  end

  test "accepted safe action", ctx do
    safe_action = %{
      ctx.action
      | action_type: "deployment_rollback",
        target_environment: "staging"
    }

    assert {:ok, %{status: :accepted, stop_reason: :agent_infra_action_accepted}} =
             AgentInfraAction.evaluate(safe_action, ctx.safety_context)
  end

  test "missing explicit approval rejects", ctx do
    context = %{ctx.safety_context | explicit_user_approval_present: false}

    assert {:error,
            %{status: :rejected, stop_reason: :destructive_action_requires_explicit_approval}} =
             AgentInfraAction.evaluate(ctx.action, context)
  end

  test "production target with unverified scope rejects", ctx do
    context = %{ctx.safety_context | environment_scope_verified: false}

    assert {:error, %{status: :rejected, stop_reason: :production_target_requires_verified_scope}} =
             AgentInfraAction.evaluate(ctx.action, context)
  end

  test "admin/global credential scope rejects", ctx do
    assert {:error, %{status: :rejected, stop_reason: :credential_scope_too_broad}} =
             AgentInfraAction.evaluate(ctx.action, %{
               ctx.safety_context
               | credential_scope: "admin"
             })

    assert {:error, %{status: :rejected, stop_reason: :credential_scope_too_broad}} =
             AgentInfraAction.evaluate(ctx.action, %{
               ctx.safety_context
               | credential_scope: "global_admin"
             })
  end

  test "same-volume/same-resource backup isolation rejects", ctx do
    assert {:error, %{status: :rejected, stop_reason: :backup_not_isolated_from_target}} =
             AgentInfraAction.evaluate(ctx.action, %{
               ctx.safety_context
               | backup_isolation: "same_volume"
             })

    assert {:error, %{status: :rejected, stop_reason: :backup_not_isolated_from_target}} =
             AgentInfraAction.evaluate(ctx.action, %{
               ctx.safety_context
               | backup_isolation: "same_resource"
             })
  end

  test "documentation_not_verified rejects", ctx do
    context = %{ctx.safety_context | documentation_verified: false}

    assert {:error, %{status: :rejected, stop_reason: :documentation_not_verified}} =
             AgentInfraAction.evaluate(ctx.action, context)
  end

  test "dry_run_not_completed rejects", ctx do
    context = %{ctx.safety_context | dry_run_completed: false}

    assert {:error, %{status: :rejected, stop_reason: :dry_run_not_completed}} =
             AgentInfraAction.evaluate(ctx.action, context)
  end

  test "missing_decision_time_knowledge rejects", ctx do
    context = %{ctx.safety_context | decision_time_knowledge_present: false}

    assert {:error, %{status: :rejected, stop_reason: :missing_decision_time_knowledge}} =
             AgentInfraAction.evaluate(ctx.action, context)
  end

  test "unsupported action type rejects", ctx do
    action = %{ctx.action | action_type: "schema_migrate"}

    assert {:error, %{status: :rejected, stop_reason: :unsupported_action_type}} =
             AgentInfraAction.evaluate(action, ctx.safety_context)
  end

  test "evidence verification succeeds for clean evidence", ctx do
    result = AgentInfraAction.evaluate(ctx.action, ctx.safety_context)
    evidence = AgentInfraAction.export_evidence(result)

    assert {:ok, %{status: :verified, algorithm: "sha256"}} =
             AgentInfraAction.verify_evidence(evidence)
  end

  test "tampered payload returns :digest_mismatch", ctx do
    result = AgentInfraAction.evaluate(ctx.action, ctx.safety_context)

    tampered =
      result
      |> AgentInfraAction.export_evidence()
      |> put_in(["payload", "stop_reason"], "tampered_stop_reason")

    assert {:error, %{status: :rejected, reason: :digest_mismatch}} =
             AgentInfraAction.verify_evidence(tampered)
  end

  test "unexpected evidence top-level key returns :invalid_evidence_shape", ctx do
    result = AgentInfraAction.evaluate(ctx.action, ctx.safety_context)

    malformed =
      result
      |> AgentInfraAction.export_evidence()
      |> Map.put("extra", "not_allowed")

    assert {:error, %{status: :rejected, reason: :invalid_evidence_shape}} =
             AgentInfraAction.verify_evidence(malformed)
  end

  test "malformed payload missing trace returns :invalid_evidence_shape", ctx do
    result = AgentInfraAction.evaluate(ctx.action, ctx.safety_context)

    malformed =
      result
      |> AgentInfraAction.export_evidence()
      |> put_in(["payload"], %{
        "status" => "rejected",
        "stop_reason" => "missing_explicit_user_approval"
      })

    assert {:error, %{status: :rejected, reason: :invalid_evidence_shape}} =
             AgentInfraAction.verify_evidence(malformed)
  end

  test "non-map evidence returns :invalid_evidence_shape" do
    assert {:error, %{status: :rejected, reason: :invalid_evidence_shape}} =
             AgentInfraAction.verify_evidence("invalid")
  end

  test "canonical payload key reorder still verifies", ctx do
    result = AgentInfraAction.evaluate(ctx.action, ctx.safety_context)
    evidence = AgentInfraAction.export_evidence(result)

    Enum.each(1..20, fn _ ->
      reordered_payload = evidence["payload"] |> Map.to_list() |> Enum.shuffle() |> Map.new()
      reordered_evidence = Map.put(evidence, "payload", reordered_payload)

      assert {:ok, %{status: :verified}} = AgentInfraAction.verify_evidence(reordered_evidence)

      assert evidence["digest"] ==
               AgentInfraAction.digest_export_payload(reordered_payload)["digest"]
    end)
  end

  test "trace includes resource_id, target_environment, and actor_id", ctx do
    assert {:ok, %{trace: trace}} = AgentInfraAction.evaluate(ctx.action, ctx.safety_context)

    proposed = hd(trace)
    assert proposed.resource_id == "db_volume_primary"
    assert proposed.target_environment == "production"
    assert proposed.actor_id == "agent_ops_7"
  end
end
