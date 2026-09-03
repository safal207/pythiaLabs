defmodule Pythia.Interop.CgqaConformanceTest do
  use ExUnit.Case, async: true

  alias Pythia.Interop.CgqaConformance

  @suite_path Path.expand("../../../conformance/cgqa-liminalqa-v0.1/suite.json", __DIR__)
  @suite_sha256 "562e2f9ae699f001b9ccf1b2b9f6dd30c435d53d668b5fd9a04ca15ca1e4faac"

  test "embedded canonical suite is exact and all vectors pass" do
    assert {:ok, report} = CgqaConformance.run()
    assert report["suiteSha256"] == @suite_sha256
    assert report["status"] == "PASS"
    assert report["counts"] == %{"total" => 14, "passed" => 14, "failed" => 0}
    assert report["implementation"]["language"] == "elixir"
    assert report["authority"]["mayAuthorizeAction"] == false

    assert Enum.all?(report["results"], fn result ->
             result["status"] == "PASS" and result["sideEffectExecuted"] == false
           end)
  end

  test "explicit vendored suite produces the same deterministic report" do
    assert {:ok, embedded} = CgqaConformance.run()
    assert {:ok, external} = CgqaConformance.run(@suite_path)
    assert external == embedded
  end

  test "suite bytes are pinned before adapter evaluation" do
    raw = File.read!(@suite_path)
    digest = :crypto.hash(:sha256, raw) |> Base.encode16(case: :lower)
    assert digest == @suite_sha256
  end
end
