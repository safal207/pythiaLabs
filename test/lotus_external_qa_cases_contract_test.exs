defmodule Pythia.LotusExternalQACasesContractTest do
  use ExUnit.Case, async: true

  @root Path.expand("..", __DIR__)
  @tradernet Path.join(@root, "examples/lotus-cases/tradernet-public-web-judgment-v1.json")
  @takeprofit Path.join(@root, "examples/lotus-cases/takeprofit-public-chart-quote-judgment-v1.json")

  defp load!(path), do: path |> File.read!() |> Jason.decode!()

  test "external QA cases remain audit-only and non-executing" do
    for packet <- [load!(@tradernet), load!(@takeprofit)] do
      assert packet["verdict"] == "ESCALATE"
      assert packet["authority"]["mode"] == "audit_only"

      for grant <- [
            "ownership",
            "approval",
            "execution",
            "delivery",
            "external_submission",
            "merge"
          ] do
        assert packet["authority"][grant] == false
      end
    end
  end

  test "TakeProfit publishes only the bounded ChartStore regression" do
    packet = load!(@takeprofit)
    findings = packet["confirmed_findings"]

    assert length(findings) == 1
    assert hd(findings)["id"] == "chartstore-required-fields-changed-form"
    assert hd(findings)["severity"] == "P2"
    assert hd(findings)["status"] == "STILL_PRESENT_IN_CHANGED_FORM"
    assert hd(findings)["evidence"]["exact_head_sha"] ==
             "27bf4fe23d8c63dcf6691ae7cf3b5f34b672e89c"

    assert hd(findings)["evidence"]["run_id"] == 29_662_910_618
  end

  test "stale-price harm remains a bounded hypothesis until cadence-aware evidence exists" do
    packet = load!(@takeprofit)

    hypothesis =
      Enum.find(packet["bounded_hypotheses"], fn item ->
        item["id"] == "stale-quote-without-freshness-boundary"
      end)

    assert hypothesis["status"] == "NEEDS_LONGER_OUTAGE_EVIDENCE"
    assert hypothesis["confidence"] == 65
    assert hypothesis["falsifier"] =~ "42–60 second quote cadence"

    refute Enum.any?(packet["confirmed_findings"], fn item ->
             item["id"] == "stale-quote-without-freshness-boundary"
           end)
  end

  test "unknown authenticated and trading impact stays explicit" do
    packet = load!(@takeprofit)
    unknowns = Enum.join(packet["unknowns"], " ")

    assert unknowns =~ "authenticated workspace"
    assert unknowns =~ "trading-decision impact"
    assert packet["verdict_meaning"] =~ "do not claim stale-price harm"
  end
end
