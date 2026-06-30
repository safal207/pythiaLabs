# RFC-001: Verifiable Continuation Envelope

- **Status:** Draft
- **Version:** 0.1
- **Scope:** Context compaction, session restart, and cross-session handoff
- **Audience:** Coding-agent runtimes, IDE agents, CLI agents, orchestrators, and verification tooling

## 1. Abstract

This RFC defines a bounded, structured continuation envelope for preserving an agent's active operational state across context compaction, restart, or handoff.

The envelope is not a narrative memory summary and is not an authority token. It carries recent instructions, intended next actions, artifact references, rejected approaches, pending verification, and provenance so that a resumed agent can continue safely without inventing history.

## 2. Problem statement

After compaction or handoff, an agent may:

- forget the latest user constraint;
- repeat completed investigation;
- choose an approach that was already rejected;
- lose track of touched files and verification targets;
- claim that an edit or command occurred without durable evidence;
- restore remembered text as if it had system or developer authority.

This is not only a quality problem. It is an execution-integrity and trust problem.

## 3. Design goals

An implementation conforming to this RFC should:

1. preserve a bounded active operational tail;
2. distinguish information from instruction and authority;
3. retain provenance for each restored claim;
4. point to durable sources of truth rather than replacing them;
5. expose unresolved work and verification state;
6. prevent silent continuation when required evidence is missing;
7. remain vendor- and transport-neutral.

## 4. Non-goals

This RFC does not:

- define a complete long-term memory system;
- prove that an external action occurred merely because the envelope says so;
- grant authority to retrieved or summarized content;
- require a specific model, database, hook API, or orchestration framework;
- require the entire historical transcript to be retained.

## 5. Terminology

### 5.1 Operational tail

The bounded set of recent events necessary to continue the current task safely.

### 5.2 Durable evidence

A source that can independently support an execution claim, such as a git diff, commit, tool log, test result, artifact digest, or runtime receipt.

### 5.3 Authority class

The permitted influence of restored content:

- `information`: facts or observations;
- `instruction`: a user-approved instruction that remains active;
- `constraint`: a boundary that must be respected;
- `evidence_ref`: a pointer to independently verifiable evidence;
- `non_authoritative_memory`: recalled context that cannot override current instructions;
- `quarantined`: content that must not influence execution until reviewed.

### 5.4 Restore gate

A transition guard that prevents normal execution until required continuation material has been read and required evidence checks have completed.

## 6. Required envelope fields

A conforming envelope MUST include:

- `schema_version`;
- `envelope_id`;
- `created_at`;
- `transition_reason`;
- `project` identity;
- `active_objective`;
- `authority_model`;
- `operational_tail`;
- `artifact_refs`;
- `rejected_approaches`;
- `pending_verification`;
- `next_action`;
- `restore_requirements`;
- `envelope_digest`.

The canonical machine-readable definition is in:

```text
schema/continuation-envelope.schema.json
```

## 7. Operational-tail event model

Each operational-tail event MUST have:

- a stable event ID;
- an event type;
- a timestamp;
- an authority class;
- a concise payload;
- provenance;
- zero or more evidence references.

Recommended event types:

- `user_instruction`;
- `agent_intent`;
- `tool_call`;
- `tool_result`;
- `artifact_observed`;
- `artifact_modified`;
- `decision`;
- `approach_rejected`;
- `verification_started`;
- `verification_result`;
- `blocker`.

## 8. Normative invariants

### VCE-001 — Latest active constraint survives

A current user constraint present before transition MUST remain present after restoration with its provenance and authority class intact.

### VCE-002 — No execution claim from memory alone

The resumed agent MUST NOT claim that an edit, command, deployment, message, or other consequential action occurred solely because the envelope says it occurred.

Such a claim requires a matching durable evidence reference or a fresh verification step.

### VCE-003 — No silent authority restoration

Content classified as `information`, `evidence_ref`, or `non_authoritative_memory` MUST NOT override system, developer, or newer user instructions.

### VCE-004 — Rejected approaches remain rejected

A rejected approach MUST remain visible with its rejection reason until the user or an authorized policy explicitly reopens it.

### VCE-005 — Pending verification remains pending

A verification target that was incomplete at transition MUST NOT be represented as passed after restoration.

### VCE-006 — Restore gate fails closed

When a required restore file, digest, or evidence reference is missing or mismatched, normal consequential execution MUST remain blocked or require explicit user review.

### VCE-007 — Boundedness

The envelope MUST be bounded by an implementation-declared maximum size or maximum event count. Older context may be summarized, but active constraints and unresolved verification MUST not be discarded to satisfy the bound.

### VCE-008 — Digest integrity

The envelope MUST expose a digest computed over a canonical representation that excludes the digest field itself.

## 9. Restore state machine

```text
ACTIVE
  |
  | compaction / restart / handoff
  v
ENVELOPE_CREATED
  |
  v
RESTORE_REQUIRED
  |
  +-- required material missing or invalid --> BLOCKED
  |
  +-- required material read and validated --> VERIFY_EVIDENCE
                                                |
                                                +-- required evidence unresolved --> REVIEW_REQUIRED
                                                |
                                                +-- evidence sufficient --> RESUMABLE
```

An implementation MAY use different state names, but it MUST preserve equivalent observable behavior.

## 10. Evidence resolution

Artifact references SHOULD include:

- artifact type;
- path or URI;
- digest when available;
- observed or modified status;
- evidence source;
- verification status.

Examples:

- a file path plus content digest;
- a git commit SHA;
- a test run ID and result;
- a tool-call receipt;
- a workflow artifact;
- a log segment with a stable reference.

The envelope points to evidence. It does not replace evidence.

## 11. Security considerations

Continuation material may contain prompt injection, stale instructions, secrets, or malicious content copied from files and webpages.

Implementations MUST:

- preserve authority classes through restoration;
- prevent quoted or retrieved content from becoming an instruction channel;
- redact or avoid storing secrets where possible;
- support quarantine for suspicious material;
- treat external artifact content as untrusted until validated;
- avoid committing local continuation files by default.

## 12. Privacy considerations

The envelope may contain task descriptions, filenames, command summaries, and user constraints.

Implementations SHOULD:

- keep project-local envelopes outside version control by default;
- support configurable retention;
- permit deletion and rotation;
- minimize copied source content;
- prefer references and digests over full sensitive payloads.

## 13. Minimum conformance suite

A conforming implementation MUST demonstrate:

1. latest user constraint preservation;
2. prevention of unsupported execution claims;
3. authority-class preservation;
4. rejected-approach preservation;
5. pending-verification preservation;
6. fail-closed restore behavior;
7. canonical digest verification.

Reference tests are provided in `conformance/`.

## 14. Adoption path

A runtime may adopt RFC-001 incrementally:

1. emit the JSON envelope before compaction;
2. inject or load it after compaction;
3. enforce a restore gate;
4. verify artifact references;
5. expose conformance-test results;
6. later add native UI, cross-session transport, or orchestration support.

## 15. Open questions for v0.2

- canonical serialization format across languages;
- standard event taxonomy extensions;
- envelope signing and multi-party trust;
- cross-session addressability;
- partial disclosure and redaction;
- relationship to framework-specific checkpoints;
- interoperability with tool-call receipts and agent identity standards.

## 16. Governing principle

> Preserve continuity without inventing history, and restore information without silently restoring authority.
