defmodule Pythia.Interop.ExternalEvidenceTest do
  use ExUnit.Case, async: true

  alias Pythia.Interop.ExternalEvidence

  @fixture Path.expand("../../fixtures/cgqa-liminalqa-evidence-v0.1.json", __DIR__)
  @candidate_fixture Path.expand(
                       "../../fixtures/liminalqa-cgqa-candidates-v0.1.json",
                       __DIR__
                     )

  test "valid CGQA evidence is advisory and never authorizes an action" do
    raw = File.read!(@fixture)

    assert {:ok, assessment} = ExternalEvidence.evaluate_json(raw)
    assert assessment.outcome == "ESCALATE"
    assert assessment.status == "advisory_only"
    assert assessment.stopReason == "current_authorization_required"
    assert assessment.mayAuthorizeAction == false
    assert assessment.sideEffectExecuted == false
    assert assessment.source.semantics == "bounded_evidence"
    assert assessment.source.schemaSha256 ==
             "53b0b4a0b1f4d77de26b8be9dbb90006ea0bd30c5cd3960a2f3e7d44d9664184"
    assert assessment.source.sha256 == (:crypto.hash(:sha256, raw) |> Base.encode16(case: :lower))
  end

  test "attempt to turn external evidence into authorization is blocked" do
    body =
      @fixture
      |> File.read!()
      |> Jason.decode!()
      |> put_in(["authority", "mayAuthorizeAction"], true)
      |> Jason.encode!()

    assert {:error, rejection} = ExternalEvidence.evaluate_json(body)
    assert rejection.outcome == "BLOCK"
    assert rejection.mayAuthorizeAction == false
    assert rejection.sideEffectExecuted == false
  end

  test "duplicate JSON keys are rejected before map normalization" do
    body =
      File.read!(@fixture)
      |> String.replace(
        ~s("schema": "org.contractgraph-qa.liminalqa-evidence.v0.1"),
        ~s("schema": "ambiguous", "schema": "org.contractgraph-qa.liminalqa-evidence.v0.1"),
        global: false
      )

    assert {:error, rejection} = ExternalEvidence.evaluate_json(body)
    assert rejection.stopReason == "duplicate_json_key"
    assert rejection.outcome == "BLOCK"
  end

  test "status-count tampering is blocked" do
    body =
      @fixture
      |> File.read!()
      |> Jason.decode!()
      |> put_in(["assessment", "counts", "violated"], 0)
      |> Jason.encode!()

    assert {:error, rejection} = ExternalEvidence.evaluate_json(body)
    assert rejection.outcome == "BLOCK"
    assert rejection.stopReason == "invalid_profile"
  end

  test "valid LiminalQA candidate export remains a non-authoritative seed" do
    assert {:ok, assessment} =
             @candidate_fixture |> File.read!() |> ExternalEvidence.evaluate_json()

    assert assessment.outcome == "ESCALATE"
    assert assessment.source.semantics == "non_authoritative_seed"
    assert assessment.source.schemaSha256 ==
             "896e32921d41925a976fef5d0ba561a08bd1f2265a08bc9ccf5065a3238a4f60"
    assert assessment.mayAuthorizeAction == false
  end

  test "weak or duplicated candidate seeds are blocked" do
    candidate = @candidate_fixture |> File.read!() |> Jason.decode!()

    weak =
      update_in(
        candidate,
        ["candidates", Access.at(0), "requiredChecks"],
        &List.delete(&1, "independent_cgqa_replay")
      )

    assert {:error, weak_rejection} =
             weak |> Jason.encode!() |> ExternalEvidence.evaluate_json()

    assert weak_rejection.outcome == "BLOCK"

    duplicate_invariant =
      put_in(
        candidate,
        ["candidates", Access.at(1), "invariantId"],
        get_in(candidate, ["candidates", Access.at(0), "invariantId"])
      )

    assert {:error, duplicate_rejection} =
             duplicate_invariant |> Jason.encode!() |> ExternalEvidence.evaluate_json()

    assert duplicate_rejection.outcome == "BLOCK"
  end

  test "unsafe causal identifiers are blocked" do
    body =
      @candidate_fixture
      |> File.read!()
      |> Jason.decode!()
      |> update_in(["causalParents"], &["../unsafe" | &1])
      |> Jason.encode!()

    assert {:error, rejection} = ExternalEvidence.evaluate_json(body)
    assert rejection.outcome == "BLOCK"
  end

  test "consumer contracts pin exact producer commits and schema hashes" do
    root = Path.expand("../../../schemas/interop", __DIR__)

    cgqa =
      root
      |> Path.join("cgqa-liminalqa-evidence-v0.1.external-contract.json")
      |> File.read!()
      |> Jason.decode!()

    liminal =
      root
      |> Path.join("liminalqa-cgqa-candidates-v0.1.external-contract.json")
      |> File.read!()
      |> Jason.decode!()

    assert cgqa["producerCommit"] == "bdf7ced074e3a7baf57cf89ac68be9674bd76a02"
    assert cgqa["schemaSha256"] ==
             "53b0b4a0b1f4d77de26b8be9dbb90006ea0bd30c5cd3960a2f3e7d44d9664184"

    assert liminal["producerCommit"] == "db9c85f678aafd6e28487e0679a9fb6c3ebfb0c3"
    assert liminal["schemaSha256"] ==
             "896e32921d41925a976fef5d0ba561a08bd1f2265a08bc9ccf5065a3238a4f60"
  end
end
