# TakeProfit public chart and quote Lotus judgment

**Verdict:** `ESCALATE`  
**Case:** `takeprofit-public-chart-quote-2026-07-19`  
**Packet SHA-256:** `a5d09cb2e29330be742fab3ee447a559f748239983b7080803613bbe2cce13cc`

This case applies the Pythia Lotus judgment boundary to the passive, unauthenticated TakeProfit evidence in LiminalQA PRs #56, #61, and #63.

## Judgment

Two findings are sufficiently supported for human reporting:

1. `P2` — the published BTC/USDT indicator chart initializes with missing required ChartStore fields and repeats the same validation failure after reload. The historical defect family remains `STILL_PRESENT_IN_CHANGED_FORM`.
2. `P2` — during three independent browser-level outages of 90, 105, and 120 seconds, zero quote responses arrived, yet the public BTC/USDT chart and price remained visibly plausible without an `offline`, `stale`, `delayed`, `disconnected`, or `reconnecting` state. A new non-empty quote response arrived after every restore.

The cadence-aware outage evidence upgrades the earlier freshness hypothesis to `CONFIRMED_REPEATED_OUTAGE`.

## Methodological correction

An earlier delayed-response experiment allowed newer responses to continue while one older response was held. That run is valid transport-order evidence, but it is **not** freshness-outage evidence because the application may have remained current through the newer responses.

The confirmed freshness finding is based only on the corrected browser-offline experiment where all quote delivery stopped during each outage.

## Preserved uncertainty

The evidence does not show that `61616.2` was numerically wrong relative to an external market source. It also does not establish authenticated-workspace behavior, visible rollback after an older response, historical backfill integrity, symbol/timeframe atomicity, or trading-decision impact.

## Pythia boundary

`ESCALATE` means: present the two bounded P2 findings and their limitations to an authorized human owner. It does not mean approve, contact TakeProfit, publish externally, execute, deliver, or merge.

The machine-readable packet is `examples/lotus-cases/takeprofit-public-chart-quote-judgment-v1.json`.
