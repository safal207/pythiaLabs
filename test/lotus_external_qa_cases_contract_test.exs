defmodule Pythia.LotusExternalQACasesContractTest do
  use ExUnit.Case, async: true

  @root Path.expand("..", __DIR__)
  @cases Path.join(@root, "examples/lotus-cases")
  @tradernet Path.join(@cases, "tradernet-public-web-judgment-v1.json")
  @takeprofit Path.join(@cases, "takeprofit-public-chart-quote-judgment-v1.json")

  defp load!(path), do: path |> File.read!() |> Jason.decode!()

  test "external QA cases remain audit-only and non-executing" do
    for packet <- [load!(@tradernet), load!(@takeprofit)] do
      assert packet["verdict"] == "ESCALATE"
      assert packet["authority"]["mode"] == "audit_only"

      for grant <- ~w(ownership approval execution delivery external_submission merge) do
        assert packet["authority"][grant] == false
      end
    end
  end

  test "TakeProfit publishes exactly two bounded P2 findings" do
    packet = load!(@takeprofit)
    findings = packet["confirmed_findings"]
    by_id = Map.new(findings, &{&1["id"], &1})

    assert length(findings) == 2

    chartstore = by_id["chartstore-required-fields-changed-form"]
    assert chartstore["severity"] == "P2"
    assert chartstore["status"] == "STILL_PRESENT_IN_CHANGED_FORM"
    assert chartstore["evidence"]["run_id"] == 29_662_910_618

    freshness = by_id["public-chart-missing-freshness-boundary-during-outage"]
    assert freshness["severity"] == "P2"
    assert freshness["status"] == "CONFIRMED_REPEATED_OUTAGE"
    assert freshness["evidence"]["run_id"] == 29_665_413_400

    assert freshness["evidence"]["exact_head_sha"] ==
             "fe17c3ddad4e4540d91cb30ba40456f2114dc997"

    assert Enum.map(freshness["evidence"]["rounds"], & &1["quote_responses_during_outage"]) ==
             [0, 0, 0]
  end

  test "the superseded overlapping-response method cannot support freshness confirmation" do
    packet = load!(@takeprofit)
    confirmed_text = packet["confirmed_findings"] |> Jason.encode!()
    unknowns = Enum.join(packet["unknowns"], " ")

    refute confirmed_text =~ "SUPPORTED_STALE_STATE_GAP"
    assert unknowns =~ "Visible application rollback"
    assert packet["verdict_meaning"] =~ "do not claim numerical price inaccuracy"
  end

  test "unknown authenticated and trading impact stays explicit" do
    packet = load!(@takeprofit)
    unknowns = Enum.join(packet["unknowns"], " ")

    assert unknowns =~ "authenticated workspace"
    assert unknowns =~ "trading-decision impact"
    assert unknowns =~ "external market source"
  end
end
