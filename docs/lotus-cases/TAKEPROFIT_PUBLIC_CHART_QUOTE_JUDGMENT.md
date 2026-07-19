# TakeProfit public chart and quote Lotus judgment

**Verdict:** `ESCALATE`  
**Case:** `takeprofit-public-chart-quote-2026-07-19`  
**Packet SHA-256:** `7443ffd0ad618a59656a4257d978af8e5a947532e3056e724e0ff0d86591b7a5`

This case applies the Pythia Lotus judgment boundary to passive, unauthenticated TakeProfit evidence in LiminalQA PRs #56, #61, #63, and #69.

## Judgment

Two findings are sufficiently supported for human reporting:

1. `P2` — the published BTC/USDT indicator chart initializes with missing required ChartStore fields and repeats the same validation failure after reload. The historical defect family remains `STILL_PRESENT_IN_CHANGED_FORM`.
2. `P2` — when current quote requests are unavailable, the public chart remains fully visible and plausible while the only visible connection-state change is disappearance of a small green icon next to `BYBIT`. No textual `offline`, `stale`, `delayed`, `disconnected`, `reconnecting`, `snapshot`, or last-updated state appears.

The second finding is `CONFIRMED_ICON_ONLY_STATE_LOSS`, supported by both cadence-aware outages and three paired baseline-versus-quote-block counterfactuals.

## Causal correction

The new evidence narrows several earlier claims:

```text
first-load request family
→ overlapping quote responses can occur
→ older-after-newer transport delivery can be created

steady-state quote request pending
→ next non-empty poll is not initiated
→ no steady-state overlap reproduced in 3/3 rounds

ListQuotes blocked
→ small green status icon disappears
→ chart, candles, axes, labels, and body text remain unchanged
→ no explicit textual connection or freshness state appears
```

Therefore:

- visible quote rollback is not confirmed;
- the displayed `61516.2` value is not classified as a stale current BTC price;
- the public chart is not proven to consume current quote payloads;
- the broad “unused quote polling” hypothesis is rejected because the status icon visibly depends on quote transport.

## User-control impact

A user can continue reading a credible-looking financial chart after current quote connectivity is unavailable. The state change is communicated through the **absence of a small icon**, rather than a visible and accessible explanation.

A clearer contract would show one of:

```text
Live · updated 2s ago
Delayed · last update 14:32:05
Offline · showing snapshot from 14:31:00
```

## Preserved uncertainty

The evidence does not establish whether the public chart is live, delayed, or an intentionally fixed published snapshot. It also does not establish numerical price inaccuracy, authenticated-workspace behavior, visible rollback, historical backfill integrity, symbol/timeframe atomicity, or trading-decision impact.

## Pythia boundary

`ESCALATE` means: present the two bounded P2 findings and their limitations to an authorized human owner. It does not mean approve, contact TakeProfit, publish externally, execute, deliver, or merge.

The machine-readable packet is `examples/lotus-cases/takeprofit-public-chart-quote-judgment-v1.json`.
