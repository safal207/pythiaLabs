# CAEP — Causal Action Episode Packet

CAEP is a small, vendor-neutral evidence format for consequence-bearing autonomous-agent actions.

It treats one action as a single auditable episode:

```text
intent → authorization → exact dispatch → observable outcome → containment/recovery
```

Corrections are appended as supersession records rather than rewriting prior evidence.

## Why this exists

Pre-execution authorization is necessary but incomplete. An incident responder must also be able to answer:

- Did the dispatched target, parameters, network destination, credentials, and execution boundary still match the authorization?
- Which permitted step causally enabled a later step?
- What external effects actually occurred?
- Did containment merely run, or did the system recover to an acceptable state?
- Was historical evidence corrected transparently or silently rewritten?

CAEP makes those questions machine-checkable without trusting the agent's narrative of success.

## Status and scope

Version `0.1.0` is an executable protocol sketch associated with [RFC #242](https://github.com/safal207/pythiaLabs/issues/242).

It provides:

- a JSON Schema;
- a low-level standard-library semantic validator;
- a strict enforcement wrapper for causal hand-off, time ordering, and evidence honesty;
- a synthetic incident packet showing `t− → t0 → t+ → recovery`;
- negative fixtures for parameter drift, missing outcomes, and false recovery claims;
- unit tests for fail-closed invariants.

It does **not** provide production cryptography, trusted time, remote attestation, or a production enforcement point.

## Validator boundary

`validate_caep.py` is the low-level semantic engine used by the tests and extension modules.

External callers should use `validate_caep_strict.py`. The strict profile additionally requires:

- authorization to reference the exact intent record;
- dispatch to reference the authorization record;
- outcome to reference dispatch;
- recovery to reference outcome;
- event and decision timestamps to remain causally ordered;
- F3–F5 claims to fail unless a separate verifier has actually checked the proofs.

An `integrity_proof` object is not evidence merely because it exists.

## Layout

```text
protocols/caep/
├── README.md
├── AISVS_MAPPING.md
├── schema/caep.schema.json
├── examples/
│   ├── hypothetical_sandbox_escape_episode.json
│   ├── invalid_parameter_drift.json
│   ├── invalid_missing_outcome.json
│   └── invalid_false_recovery.json
├── tools/
│   ├── validate_caep.py
│   └── validate_caep_strict.py
└── tests/
    ├── test_validate_caep.py
    └── test_strict_validation.py
```

## Run

From the repository root:

```bash
python3 protocols/caep/tools/validate_caep_strict.py \
  protocols/caep/examples/hypothetical_sandbox_escape_episode.json
```

Machine-readable output:

```bash
python3 protocols/caep/tools/validate_caep_strict.py --json \
  protocols/caep/examples/hypothetical_sandbox_escape_episode.json
```

Run the test suite:

```bash
python3 -m unittest discover -s protocols/caep/tests -v
```

## Core invariants

1. **Canonical episode identity** — `episode_ref` is derived from the exact intent binding.
2. **Exact binding** — authorization and dispatch preserve target, parameter hash, boundary, credential class, and permitted network destination.
3. **Unknown means stop** — only `ALLOW`, `DENY`, `REQUIRE_APPROVAL`, and `REVISE` are accepted.
4. **No orphan execution** — a dispatch requires one prior authorization and one terminal outcome.
5. **Exact causal hand-off** — authorization, dispatch, outcome, and recovery each reference the immediately preceding authority record.
6. **Time continuity** — event, valid, transaction, authorization, dispatch, outcome, and recovery time cannot move backwards.
7. **Recovery is a result** — recovery status agrees with `objective_met`, residual effects, and unresolved dependencies.
8. **Append-only correction** — a supersession record points backward; it cannot erase or mutate the prior record.
9. **Evidence honesty** — semantic validation alone cannot establish F3, F4, or F5.

## Canonical episode reference

The validator derives `episode_ref` as:

```text
sha256(JCS-like canonical JSON({
  actor_id,
  agent_runtime_id,
  action_type,
  target_resource,
  params_hash,
  boundary_id,
  requested_capabilities,
  valid_time,
  transaction_time
}))
```

The prototype uses sorted compact UTF-8 JSON. The verified-evidence extension in stacked PR #244 introduces a strict signed-record canonicalization profile.

## Evidence levels

- **F0** — unsupported claim.
- **F1** — local runtime log.
- **F2** — structured trace with content hashes.
- **F3** — independently verified integrity proofs on action records.
- **F4** — bounded replay against exact artifacts.
- **F5** — independent reproduction or external verification.

The included example is deliberately marked **F2**. It is a synthetic protocol demonstration, not a forensic reconstruction of any real incident.

## Integration boundary

A real deployment should keep four authorities separate where practical:

```text
agent/orchestrator ≠ policy decision point ≠ dispatcher/enforcement point ≠ observer/receipt issuer
```

The model must not be able to authorize, execute, and attest to the same action under one trust root.
