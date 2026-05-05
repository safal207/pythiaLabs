# Expected output — Paid Review Demo

Run:

```bash
make demo
```

The demo loads `examples/paid_review_demo_input.json`, evaluates each scenario
through the real `Pythia.Showcase.Web3TreasuryAction` engine (no mocks), prints
the per-scenario evidence trace, and writes a deterministic artifact bundle to
`examples/output/paid_review_demo_artifact.json`.

Reviewer-facing terminal output (timing values and digest hex are runtime/data
dependent and are shown here as `<...>` placeholders):

```text
PythiaLabs — Paid Review Demo
deterministic evidence layer for agentic oversight
scenario_set=paid_review_demo_2026_05  schema=pythia.demo.input.v2
────────────────────────────────────────────────────────────────
[1/4] Clean 25,000 USDC treasury transfer
scenario=accepted_transfer
  decision    : ● ACCEPTED  (<x.xx ms>)
  stop_reason : treasury_transfer_accepted
  expected    : accepted / treasury_transfer_accepted → MATCH
  evidence trace:
    PASS  proposal_match_check
    PASS  permission_check
    PASS  quorum_check
    PASS  voting_window_check
    PASS  timelock_check
    PASS  authorization_valid_time_check
    PASS  authorization_transaction_time_check
    PASS  transfer_expiration_check
  sha256[:16] : <16-hex-prefix>
  evidence    : verified
────────────────────────────────────────────────────────────────
[2/4] Quorum threshold not reached
scenario=quorum_not_met
  decision    : ● REJECTED  (<x.xx ms>)
  stop_reason : quorum_not_met
  expected    : rejected / quorum_not_met → MATCH
  evidence trace:
    PASS  proposal_match_check
    PASS  permission_check
    FAIL  quorum_check
  sha256[:16] : <16-hex-prefix>
  evidence    : verified
────────────────────────────────────────────────────────────────
[3/4] Timelock has not yet expired
scenario=timelock_not_satisfied
  decision    : ● REJECTED  (<x.xx ms>)
  stop_reason : timelock_not_satisfied
  expected    : rejected / timelock_not_satisfied → MATCH
  evidence trace:
    PASS  proposal_match_check
    PASS  permission_check
    PASS  quorum_check
    PASS  voting_window_check
    FAIL  timelock_check
  sha256[:16] : <16-hex-prefix>
  evidence    : verified
────────────────────────────────────────────────────────────────
[4/4] Authorization window has expired
scenario=transfer_window_expired
  decision    : ● REJECTED  (<x.xx ms>)
  stop_reason : transfer_expired
  expected    : rejected / transfer_expired → MATCH
  evidence trace:
    PASS  proposal_match_check
    PASS  permission_check
    PASS  quorum_check
    PASS  voting_window_check
    PASS  timelock_check
    PASS  authorization_valid_time_check
    PASS  authorization_transaction_time_check
    FAIL  transfer_expiration_check
  sha256[:16] : <16-hex-prefix>
  evidence    : verified
────────────────────────────────────────────────────────────────
Counterfactual
from=quorum_not_met  patch={"governance_record":{"quorum_met":true}}
  rejected → accepted  (decision flipped as expected)
────────────────────────────────────────────────────────────────
Summary
  scenario                 status      stop_reason                          ms      sha256[:8]
  accepted_transfer        accepted    treasury_transfer_accepted           <x.xx>  <8hex>
  quorum_not_met           rejected    quorum_not_met                       <x.xx>  <8hex>
  timelock_not_satisfied   rejected    timelock_not_satisfied               <x.xx>  <8hex>
  transfer_window_expired  rejected    transfer_expired                     <x.xx>  <8hex>
────────────────────────────────────────────────────────────────
Artifact bundle written to examples/output/paid_review_demo_artifact.json
  4 evidence record(s); each digest re-verified via Engine.verify_evidence/1
────────────────────────────────────────────────────────────────
Result: PASS — all scenarios matched expectations
```

## What this demo proves

1. **Real engine, not mocks** — every decision comes from
   `Pythia.Showcase.Web3TreasuryAction.evaluate/2`; the demo only formats the
   input and output.
2. **Deterministic evidence verification** — each evidence record is
   canonically encoded and digested with SHA-256; the demo immediately calls
   `Pythia.Showcase.Web3TreasuryAction.verify_evidence/1` on every artifact and
   reports `verified` only when the digest round-trips. (This is plain
   evidence verification, not the signed-envelope path —
   `verify_evidence_envelope/1` is a separate, stricter mode.)
3. **Multiple failure modes** — the four scenarios cover an accepted transfer
   plus three orthogonal rejection reasons (quorum, timelock, expiration), so a
   reviewer sees both `accept` and `reject` paths exercised.
4. **Counterfactual** — flipping a single evidence field (`quorum_met: false →
   true`) is shown to flip the decision, demonstrating that the gate is driven
   by evidence rather than action shape.
5. **Audit trail on disk** — `examples/output/paid_review_demo_artifact.json`
   is a bundle of evidence records that an external auditor can re-verify
   independently.

The artifact bundle is gitignored — running `make demo` regenerates it. To
re-verify a previously written bundle without re-running the engine, use any
SHA-256 implementation against each `payload` (canonicalized) and compare to
the recorded `digest`.
