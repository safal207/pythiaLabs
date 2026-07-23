# CAEP — Causal Action Episode Packet

CAEP is a small, vendor-neutral evidence format for consequence-bearing autonomous-agent actions.

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

- JSON Schema 2020-12;
- a standard-library semantic engine;
- a strict causal and time-order enforcement wrapper;
- optional Ed25519 verification for F3+ records;
- a narrow deterministic signed-record canonicalization profile;
- full-record digest-bound JSON Lines transport;
- synthetic, negative, regression, and tamper tests.

It does **not** provide trusted time, remote attestation, protected key storage, revocation distribution, production enforcement, or certified incident-response guarantees.

## Evidence levels and the two-validator rule

- **F0** — unsupported claim.
- **F1** — local runtime log.
- **F2** — structured trace with content hashes.
- **F3** — independently verified integrity proofs on action records.
- **F4** — bounded replay against exact artifacts.
- **F5** — independent reproduction or external verification.

`validate_caep_strict.py` validates structure, exact causal hand-off, decision-time ordering, dispatch binding, outcome semantics, and recovery evidence. It is the recommended path for F0–F2.

For F3–F5, the presence of an `integrity_proof` object is **not verification**. Run `verify_caep_proofs.py` with a separately supplied public keyset. Unknown keys, wrong issuers or roles, unsupported schemes, malformed base64url, invalid signature lengths, modified records, and shared trust roots fail closed.

## Layout

```text
protocols/caep/
├── README.md
├── AISVS_MAPPING.md
├── requirements-crypto.txt
├── schema/caep.schema.json
├── examples/
├── tools/
│   ├── validate_caep.py
│   ├── validate_caep_strict.py
│   ├── caep_canonical.py
│   ├── verify_caep_proofs.py
│   └── export_caep_jsonl.py
└── tests/
```

## Semantic and strict validation

```bash
python3 protocols/caep/tools/validate_caep_strict.py \
  protocols/caep/examples/hypothetical_sandbox_escape_episode.json
```

Machine-readable output:

```bash
python3 protocols/caep/tools/validate_caep_strict.py --json \
  protocols/caep/examples/hypothetical_sandbox_escape_episode.json
```

## F3 cryptographic verification

Install the optional dependency:

```bash
python3 -m pip install -r protocols/caep/requirements-crypto.txt
```

Verify a signed packet:

```bash
python3 protocols/caep/tools/verify_caep_proofs.py \
  signed-episode.json \
  --keyset public-keyset.json
```

Keyset shape:

```json
{
  "caep_keyset_version": "0.1.0",
  "keys": [
    {
      "key_id": "pdp-key-2026-07",
      "scheme": "Ed25519",
      "issuer": "pdp:policy-engine-3",
      "authority_role": "policy_decision_point",
      "public_key": "<base64url raw 32-byte Ed25519 public key>"
    }
  ]
}
```

Proof shape:

```json
{
  "scheme": "Ed25519+caep-jcs-int-v1",
  "key_id": "pdp-key-2026-07",
  "value": "<base64url 64-byte Ed25519 signature>"
}
```

The signature covers the complete record except the `integrity_proof` field itself.

## Authority roles

Each consequence-bearing stage has a distinct verification role:

| Record | Required key role |
|---|---|
| authorization | `policy_decision_point` |
| dispatch | `enforcement_point` |
| outcome | `independent_observer` |
| recovery | `incident_controller` |

One public key cannot represent different issuers or authority roles.

## Canonicalization

Signed records use `caep-jcs-int-v1`, a deliberately narrow interoperable domain:

- UTF-8 JSON values;
- ASCII object member names;
- compact deterministic key ordering;
- strings, booleans, null, arrays, objects, and safe-range integers only;
- floating-point and non-finite numbers rejected;
- duplicate member names rejected;
- invalid Unicode surrogates rejected.

This avoids presenting a language-native serializer as a universal cryptographic contract.

## JSON Lines transport

Export a semantically valid packet:

```bash
python3 protocols/caep/tools/export_caep_jsonl.py export \
  episode.json episode.jsonl
```

Verify record order and digests:

```bash
python3 protocols/caep/tools/export_caep_jsonl.py verify episode.jsonl
```

The first line is a header. Every subsequent line binds one complete record — including its proof envelope — to the episode reference, sequence, and SHA-256 digest. JSONL validation detects payload and signature-envelope mutation but does not replace Ed25519 verification.

## Core invariants

1. **Canonical episode identity** — `episode_ref` derives from the exact intent binding.
2. **Exact dispatch binding** — target, parameters, boundary, credentials, and destination match authorization.
3. **Unknown means stop** — unknown verdicts, conformance states, keys, schemes, or roles fail closed.
4. **No orphan execution** — dispatch requires prior authorization and terminal outcome.
5. **Causal continuity** — each authority stage references its immediate predecessor.
6. **Time continuity** — valid, transaction, authorization, dispatch, outcome, and recovery time cannot move backwards.
7. **Recovery is a result** — status agrees with objective achievement and residual effects.
8. **Append-only correction** — supersession points backward and never rewrites evidence.
9. **Evidence honesty** — semantic validation cannot promote a packet to F3.
10. **Portable verification** — signatures and transport digests can be checked outside the agent runtime.

## Run tests

```bash
python3 -m unittest discover -s protocols/caep/tests -v
```

The cryptographic tests are skipped when `cryptography` is unavailable. The dedicated GitHub Actions workflow installs the dependency and runs the complete suite.

## Integration boundary

A real deployment should keep authorities separate:

```text
agent/orchestrator ≠ policy decision point ≠ enforcement point ≠ observer/incident controller
```

The model must not be able to authorize, execute, and attest to the same action under one trust root.
