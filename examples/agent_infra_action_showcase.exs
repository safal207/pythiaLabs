alias Pythia.Showcase.AgentInfraAction

base_action = %{
  action_id: "infra_act_001",
  action_type: "volume_delete",
  actor_id: "agent_ops_7",
  resource_id: "db_volume_primary",
  resource_type: "database_volume",
  target_environment: "production",
  action_time: ~U[2026-04-27 12:00:00Z],
  decision_time: ~U[2026-04-27 12:00:09Z]
}

base_safety_context = %{
  credential_scope: "scoped_operator",
  explicit_user_approval_present: true,
  environment_scope_verified: true,
  documentation_verified: true,
  dry_run_completed: true,
  backup_isolation: "off_target",
  decision_time_knowledge_present: true
}

extract_payload = fn
  {:ok, payload} -> payload
  {:error, payload} -> payload
end

print_step = fn title ->
  IO.puts("\n=== #{title} ===")
end

print_verification = fn result ->
  case result do
    {:ok, payload} ->
      IO.puts("verification_status: #{payload.status}")
      IO.puts("algorithm: #{payload.algorithm}")
      IO.puts("digest: #{payload.digest}")

    {:error, payload} ->
      IO.puts("verification_status: #{payload.status}")
      IO.puts("reason: #{payload.reason}")
  end
end

IO.puts("Production Volume Deletion Safety Showcase")

IO.puts(
  "Deterministic local showcase only; decision-time replay reasoning. It does not implement production infrastructure controls, cloud-provider integration, IAM enforcement, backup management, or cybersecurity protection."
)

print_step.("A. Rejected destructive production volume delete: missing explicit approval")

missing_approval_result =
  AgentInfraAction.evaluate(base_action, %{
    base_safety_context
    | explicit_user_approval_present: false
  })

missing_approval_payload = extract_payload.(missing_approval_result)
IO.puts("status: #{missing_approval_payload.status}")
IO.puts("stop_reason: #{missing_approval_payload.stop_reason}")

print_step.("B. Rejected destructive production volume delete: credential scope too broad")

broad_scope_result =
  AgentInfraAction.evaluate(base_action, %{base_safety_context | credential_scope: "admin"})

broad_scope_payload = extract_payload.(broad_scope_result)
IO.puts("status: #{broad_scope_payload.status}")
IO.puts("stop_reason: #{broad_scope_payload.stop_reason}")

print_step.("C. Rejected destructive production volume delete: backup not isolated from target")

backup_result =
  AgentInfraAction.evaluate(base_action, %{base_safety_context | backup_isolation: "same_volume"})

backup_payload = extract_payload.(backup_result)
IO.puts("status: #{backup_payload.status}")
IO.puts("stop_reason: #{backup_payload.stop_reason}")

print_step.("D. Rejected destructive production volume delete: documentation not verified")

doc_result =
  AgentInfraAction.evaluate(base_action, %{base_safety_context | documentation_verified: false})

doc_payload = extract_payload.(doc_result)
IO.puts("status: #{doc_payload.status}")
IO.puts("stop_reason: #{doc_payload.stop_reason}")

print_step.("E. Accepted non-production action with safe scoped credentials and approval")

safe_non_prod_action = %{
  base_action
  | action_type: "deployment_rollback",
    target_environment: "staging"
}

accepted_result = AgentInfraAction.evaluate(safe_non_prod_action, base_safety_context)
accepted_payload = extract_payload.(accepted_result)
IO.puts("status: #{accepted_payload.status}")
IO.puts("stop_reason: #{accepted_payload.stop_reason}")
IO.puts("trace_event_count: #{length(accepted_payload.trace)}")

print_step.("F. Evidence export")
exported = AgentInfraAction.export_result(accepted_result)
IO.puts("export_status: #{exported["status"]}")
IO.puts("export_stop_reason: #{exported["stop_reason"]}")

print_step.("G. Evidence digest")
digest = AgentInfraAction.export_digest(accepted_result)
IO.puts("algorithm: #{digest["algorithm"]}")
IO.puts("digest: #{digest["digest"]}")

print_step.("H. Evidence verification")
evidence = AgentInfraAction.export_evidence(accepted_result)
verification = AgentInfraAction.verify_evidence(evidence)
print_verification.(verification)

print_step.("I. Tampered evidence rejection")
tampered = put_in(evidence, ["payload", "stop_reason"], "tampered_stop_reason")
tampered_verification = AgentInfraAction.verify_evidence(tampered)
print_verification.(tampered_verification)

IO.puts("\nShowcase completed.")
