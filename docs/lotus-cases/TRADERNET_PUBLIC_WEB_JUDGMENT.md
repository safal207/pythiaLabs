# Tradernet public-web Lotus judgment

**Verdict:** `ESCALATE`  
**Case:** `tradernet-public-web-2026-07-18`  
**Packet SHA-256:** `8aa933cd153a4805a1e2d930b8a7afe2ebb40aa68f52ecd76032a0af64372651`

This case applies the Pythia Lotus judgment boundary to the passive, unauthenticated Tradernet evidence in LiminalQA PRs #54, #58, and #60.

## Judgment

Four findings are sufficiently supported for human reporting:

1. `P1` — mobile user-agents receive the 404 route for a public chart.
2. `P1-performance` — late mobile hero discovery materially increases LCP.
3. `P2` — the mobile terminal login downloads a hidden 346,800-byte 2x image.
4. `P3` — terminal entry requests a missing first-party onboarding asset.

The evidence does **not** support a security-vulnerability claim, autonomous external submission, or a claim that every mobile finding has one root cause.

## Preserved uncertainty

The repeated mobile-only pattern supports a 75% hypothesis of a shared device-routing or responsive-resource branch, but the causal identity of that shared branch is not proven. Live quote freshness, reconnect behavior, the single 7.48-second chart-visibility signal, the render-context console error, and minute-label anomalies remain unresolved.

## Pythia boundary

`ESCALATE` means: present the evidence to an authorized human owner for review. It does not mean approve, publish, contact Tradernet, deploy, merge, or execute any external action.

The machine-readable packet is `examples/lotus-cases/tradernet-public-web-judgment-v1.json`.
