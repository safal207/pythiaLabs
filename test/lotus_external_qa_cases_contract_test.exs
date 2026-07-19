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

    quote_status = by_id["quote-connectivity-status-icon-only"]
    assert quote_status["severity"] == "P2"
    assert quote_status["status"] == "CONFIRMED_ICON_ONLY_STATE_LOSS"

    paired = quote_status["evidence"]["paired_quote_block"]
    assert paired["run_id"] == 29_666_238_811
    assert paired["exact_head_sha"] == "18d703929c31d53789814890a3565550283d5120"
    assert length(paired["pairs"]) == 3
    assert Enum.all?(paired["pairs"], &(&1["chart_visible"] && &1["body_text_same"]))
  end

  test "quote-status evidence blocks stale-live and rollback overclaims" do
    packet = load!(@takeprofit)
    confirmed_text = packet["confirmed_findings"] |> Jason.encode!()
    unknowns = Enum.join(packet["unknowns"], " ")

    refute confirmed_text =~ "SUPPORTED_STALE_STATE_GAP"
    refute confirmed_text =~ "stale current BTC price"
    assert unknowns =~ "not proven to consume current quote payloads"
    assert unknowns =~ "Visible application rollback"
    assert packet["verdict_meaning"] =~ "do not claim numerical price inaccuracy"
  end

  test "paired quote block preserves state-visibility boundaries" do
    packet = load!(@takeprofit)

    quote_status =
      Enum.find(packet["confirmed_findings"], &(&1["id"] == "quote-connectivity-status-icon-only"))

    evidence = quote_status["evidence"]["paired_quote_block"]

    assert evidence["visual_difference"] =~ "small green status icon disappears"
    assert evidence["visual_difference"] =~ "body text remain unchanged"
    assert quote_status["claim"] =~ "no textual offline"
  end

  test "unknown authenticated and trading impact stays explicit" do
    packet = load!(@takeprofit)
    unknowns = Enum.join(packet["unknowns"], " ")

    assert unknowns =~ "authenticated workspace"
    assert unknowns =~ "trading-decision impact"
    assert unknowns =~ "external market source"
    assert unknowns =~ "live, delayed, or snapshot"
  end
end
