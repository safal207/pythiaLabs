defmodule Pythia.Mcp.SchemasTest do
  @moduledoc """
  Smoke tests for `schemas/mcp/*.schema.json`: each file is valid JSON Schema
  draft-07, declares the right gate as a const, and lists every top-level
  required key the evaluator actually decodes. Catches schema drift when the
  evaluator gains or loses a field.
  """

  use ExUnit.Case, async: true

  @schema_dir Path.expand("../../schemas/mcp", __DIR__)

  @gate_required %{
    "agent_infra_action" => %{
      "action" => ~w(
        action_id action_type actor_id resource_id resource_type
        target_environment action_time decision_time
      ),
      "safety_context" => ~w(
        credential_scope backup_isolation
        explicit_user_approval_present environment_scope_verified
        documentation_verified dry_run_completed decision_time_knowledge_present
      )
    },
    "banking_risk_action" => %{
      "action" => ~w(
        action_id action_type operator_id account_id action_time decision_time
      ),
      "governance" => ~w(
        authorization_valid_from authorization_valid_to authorization_recorded_at
        evidence_observed_at evidence_valid_until
        decision_time_knowledge_present operator_approval_present
      )
    },
    "web3_treasury_action" => %{
      "action" => ~w(
        action_id action_type actor dao_id proposal_id amount asset recipient
        required_permission action_time decision_time
      ),
      "governance" => ~w(
        proposal_id permission quorum_met
        voting_closed_at timelock_until
        authorization_valid_from authorization_valid_to authorization_recorded_at
        transfer_expires_at
      )
    }
  }

  for {gate, _} <- @gate_required do
    @gate gate
    test "schema for #{gate} parses and pins the gate id" do
      schema = load_schema(@gate)

      assert schema["$schema"] =~ "json-schema.org/draft-07"
      assert schema["type"] == "object"
      assert get_in(schema, ["properties", "gate", "const"]) == @gate
    end

    test "schema for #{gate} lists exactly the evaluator's required fields" do
      schema = load_schema(@gate)
      expected = @gate_required[@gate]

      for {sub_object, fields} <- expected do
        sub_required =
          schema
          |> Map.fetch!("properties")
          |> Map.fetch!(sub_object)
          |> Map.get("required", schema_def_required(schema, sub_object))

        assert Enum.sort(sub_required) == Enum.sort(fields),
               """
               Schema/evaluator drift for #{@gate}.#{sub_object}:
                 schema required:    #{inspect(Enum.sort(sub_required))}
                 evaluator decodes:  #{inspect(Enum.sort(fields))}
               """
      end
    end
  end

  defp load_schema(gate) do
    @schema_dir
    |> Path.join("#{gate}.schema.json")
    |> File.read!()
    |> Jason.decode!()
  end

  defp schema_def_required(schema, sub_object) do
    # Banking and Web3 reuse a $defs/governance block via $ref. Resolve once.
    case get_in(schema, ["properties", sub_object, "$ref"]) do
      "#/$defs/" <> name -> get_in(schema, ["$defs", name, "required"]) || []
      _ -> []
    end
  end
end
