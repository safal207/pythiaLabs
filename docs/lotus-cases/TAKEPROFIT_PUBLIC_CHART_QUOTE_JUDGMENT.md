# TakeProfit public chart and quote Lotus judgment

**Verdict:** `ESCALATE`  
**Case:** `takeprofit-public-chart-quote-2026-07-19`  
**Packet SHA-256:** `1de70835dcc22aec035beeca0c090447bbf7c6e3cda4f131f1bf029e33cf2f10`

This case applies the Pythia Lotus judgment boundary to the passive, unauthenticated TakeProfit chart and quote evidence in LiminalQA PR #56 and the cross-domain Lotus adapter in PR #61.

## Judgment

One finding is sufficiently supported for human reporting:

1. `P2` — the published BTC/USDT indicator chart initializes with missing required ChartStore fields and repeats the same validation failure after reload. The historical defect family remains `STILL_PRESENT_IN_CHANGED_FORM`.

The evidence also shows that the public card loaded historical bars, received changing quote payloads, resumed market-data activity after a short interruption, and reconstructed after reload.

## Preserved uncertainty

The five-second interruption was shorter than the observed approximately 42–60 second quote cadence. Therefore the absence of an `offline`, `stale`, `delayed`, or `reconnecting` marker is **not yet publishable as a confirmed stale-price defect**.

Authenticated-workspace transport, history backfill, candle/indicator layer integrity, symbol/timeframe atomicity, and trading-decision impact remain unknown.

## Next falsifying experiment

Run three controlled 90–120 second interruptions and record:

- last successful quote timestamp and quote age;
- expected polling or heartbeat cadence;
- the first visible freshness warning;
- whether old and new symbol responses can cross;
- recovery time and duplicate request/subscription counts.

The stale-price hypothesis may leave `ESCALATE` only after the interruption exceeds the product freshness threshold and the UI still presents the last value as current.

## Pythia boundary

`ESCALATE` means: present the confirmed regression and bounded hypotheses to an authorized human owner. It does not mean approve, contact TakeProfit, publish externally, execute, deliver, or merge.

The machine-readable packet is `examples/lotus-cases/takeprofit-public-chart-quote-judgment-v1.json`.
