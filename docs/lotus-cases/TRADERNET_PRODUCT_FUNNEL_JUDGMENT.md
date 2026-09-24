# Tradernet product-funnel Lotus judgment

**Verdict:** `ESCALATE`  
**Case:** `tradernet-product-funnel-2026-07-21`  
**Source:** `safal207/LiminalQAengineer` PR `#102`  
**Exact source head:** `d14d0e0cf434000c10609dc8627c288df5306df6`

## Decision

The source audit is suitable for human product review because it cleanly separates:

- four confirmed public findings;
- bounded product hypotheses;
- authenticated journeys that still require evidence;
- ethical funnel patterns that are recommendations rather than subject evidence;
- explicit guardrails and authority limits.

`ESCALATE` means present the packet to an authorised human product, design or QA owner. It does not mean approve, publish, contact Tradernet, run an experiment, access an account, place an order, deploy or merge.

## Confirmed for human reporting

1. `P1` — mobile public chart user-agents receive a generic 404 experience.
2. `P1-performance` — late mobile hero discovery materially delays meaningful content.
3. `P2` — mobile terminal entry downloads a hidden `346,800` byte image.
4. `P3` — terminal entry requests a missing first-party onboarding asset.

These conclusions inherit the existing exact-run evidence chain from LiminalQA PRs `#54`, `#58` and `#60`.

## Product conclusions allowed as recommendations

The packet may recommend that Tradernet validate:

- intent-segmented public entry;
- demo-first activation;
- persistent real/demo, session and data state;
- complete order consequences preview;
- marketable-limit explanation;
- explicit cancellation state;
- in-context Stop Loss and Take Profit;
- mobile task cards;
- safe mobile draft recovery.

These are not confirmed defects unless the source status is `CONFIRMED`.

## Claims that remain blocked

The evidence does not support claims that:

- the authenticated order form currently hides fees or consequences;
- Stop Loss or Take Profit is currently unusable;
- mobile web necessarily uses compressed desktop tables;
- users currently confuse real and demo accounts;
- a specific funnel variant will increase conversion;
- one shared mobile root cause explains every public defect;
- any security vulnerability exists.

The correct labels are `HYPOTHESIS`, `NEEDS_AUTHENTICATED_EVIDENCE` or `UNKNOWN`.

## Product-lens judgment

| Lotus petal | Source observation | Judgment |
|---|---|---|
| Intent before conversion | Entry segmentation proposed | `TESTABLE_RECOMMENDATION` |
| Continuity before friction | Mobile and onboarding recovery gaps proposed | `NEEDS_EVIDENCE` |
| Complementary value before upsell | No paid or risk-increasing choice should be preselected | `GUARDRAIL` |
| One click without hidden commitment | Full financial consequence preview proposed | `NEEDS_AUTHENTICATED_EVIDENCE` |
| Recovery before pressure | Restore intention without pressure to trade | `GUARDRAIL` |
| Evidence before growth claims | Qualified activation and harm signals defined | `MEASUREMENT_READY` |
| Human freedom at every stage | Decline, correction and state challenge required | `GUARDRAIL` |

## Why this packet is stronger than a conventional UX review

The source does not collapse screenshots, opinions, product ideas and defects into one list. Each recommendation has:

- an evidence label;
- a priority;
- a bounded next test;
- acceptance criteria or measurement plan;
- guardrails;
- a human authority boundary.

## Recommended human action

1. Review the confirmed public findings as separate repair items.
2. Use the P0 authenticated validation matrix before filing order, cancellation or protection defects.
3. Run only bounded experiments with qualified activation and harm guardrails.
4. Keep ClickFunnels and SamCart as pattern references, never as evidence that Tradernet will achieve a stated result.
5. Preserve exact-build evidence and invalidate stale conclusions when the tested head or environment changes.

Machine-readable judgment: `examples/lotus-cases/tradernet-product-funnel-judgment-v1.json`.
