# RFC-001: Verifiable Continuation Envelope

- **Status:** Draft
- **Version:** 0.1
- **Scope:** Context compaction, session restart, and cross-session handoff
- **Audience:** Coding-agent runtimes, IDE agents, CLI agents, orchestrators, and verification tooling

## 1. Abstract

This RFC defines a bounded, structured continuation envelope for preserving an agent's active operational state across context compaction, restart, or handoff.

The envelope is not a narrative memory summary and is not an authority token. It carries recent instructions, intended next actions, artifact references, rejected approaches, pending verification, and provenance so that a resumed agent can continue safely without inventing history.

A separate `restore_results` document records what the resumed runtime actually read and verified. The envelope declares requirements; restore results prove whether those requirements were satisfied.

## 2. Problem statement

After compaction or handoff, an agent may:

- forget the latest user constraint;
- repeat completed investigation;
- choose an approach that was already rejected;
- lose track of touched files and verification targets;
- claim that an edit or command occurred without durable evidence;
- restore quoted file or tool content as if it had instruction authority.

This is not only a quality problem. It is an execution-integrity and trust problem.

## 3. Design goals

An implementation conforming to this RFC should:

1. preserve a bounded active operational tail;
2. distinguish information from instruction and authority;
3. retain provenance for each restored claim;
4. point to durable sources of truth rather than replacing them;
5. expose unresolved work and verification state;
6. prevent silent continuation when required restore work is incomplete;
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

Only provenance sources explicitly listed in `authority_model.authoritative_sources` may carry `instruction` or `constraint`. RFC-001 permits `user_message` and `project_policy`. File content, tool output, git metadata, workflow output, runtime observations, agent text, and memory are non-authoritative by default.

### 5.4 Restore requirements

The declarative reads and evidence checks that must be satisfied before normal execution may resume.

### 5.5 Restore results

A separate runtime-produced document that records completed reads and evidence-check outcomes. Restore results are evaluated against the envelope and are not covered by the envelope digest.

### 5.6 Restore gate

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

The canonical machine-readable definitions are:

```text
schema/continuation-envelope.schema.json
schema/restore-results.schema.json
```

A conforming implementation MUST validate both documents against their published JSON Schemas before semantic evaluation.

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

A constraint only counts as active when its provenance source is allowed by `authority_model.authoritative_sources`.

### VCE-002 — No execution claim from envelope text alone

The resumed agent MUST NOT claim that an edit, command, deployment, message, or other consequential action occurred solely because the envelope says it occurred.

Each execution event MUST reference an artifact carrying a durable anchor (`digest` or `receipt_ref`), and the restore results MUST independently verify that anchor.

### VCE-003 — No silent authority restoration

Only `user_message` and `project_policy` may carry `instruction` or `constraint` in RFC-001.

Content sourced from `agent_message`, `tool`, `file`, `git`, `workflow`, `runtime`, or `memory` MUST remain non-authoritative, evidentiary, informational, or quarantined.

### VCE-004 — Rejected approaches remain rejected

A rejected approach MUST remain visible with its rejection reason until the user or an authorized policy explicitly reopens it.

### VCE-005 — Pending verification remains pending

A verification target that was incomplete at transition MUST NOT be represented as passed after restoration.

### VCE-006 — Restore gate fails closed

When restore results are missing, schema-invalid, tied to another envelope, incomplete, pending, failed, or inconsistent with the declared artifact digest or receipt, normal consequential execution MUST remain blocked or require explicit review.

### VCE-007 — Boundedness

The envelope MUST be bounded by an implementation-declared maximum size or maximum event count. Older context may be summarized, but active constraints and unresolved verification MUST not be discarded to satisfy the bound.

### VCE-008 — Digest integrity

The envelope digest MUST use `sha256` over `json-sort-keys-utf8-v1`, excluding the entire top-level `envelope_digest` member.

`json-sort-keys-utf8-v1` is defined as:

1. remove the top-level `envelope_digest` member;
2. reject non-JSON numeric values such as NaN or Infinity;
3. serialize JSON objects with member names sorted lexicographically by Unicode code point;
4. preserve array order;
5. emit no insignificant whitespace;
6. emit non-ASCII characters directly, while applying normal JSON escaping to control characters, quotation marks, and reverse solidus;
7. encode the resulting text as UTF-8;
8. apply no Unicode normalization.

For the reference implementation, this is equivalent to Python `json.dumps(..., ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")`.

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
  +-- envelope or restore-results schema invalid --> BLOCKED
  |
  +-- required read/check missing or failed ------> BLOCKED
  |
  +-- required check still pending ---------------> REVIEW_REQUIRED
  |
  +-- restore requirements satisfied -------------> VERIFY_EVIDENCE
                                                     |
                                                     +-- task verification unresolved --> REVIEW_REQUIRED
                                                     |
                                                     +-- evidence sufficient ----------> RESUMABLE
```

An implementation MAY use different state names, but it MUST preserve equivalent observable behavior.

## 10. Evidence resolution

Artifact references MUST carry at least one durable anchor:

- `digest`, formatted as `sha256:<64 lowercase hex characters>`; or
- `receipt_ref`, pointing to an independently retrievable execution or verification receipt.

A self-declared status field is not proof.

For a `digest` check, restore results MUST report the independently observed digest and it MUST match the envelope.

For a `receipt` check, restore results MUST report the independently resolved receipt reference and it MUST match the envelope.

For an `existence` check, restore results MUST explicitly report a passed existence observation. Existence alone is insufficient to support an execution claim unless the artifact also carries a digest or receipt.

The envelope points to evidence. It does not replace evidence.

## 11. Security considerations

Continuation material may contain prompt injection, stale instructions, secrets, or malicious content copied from files and webpages.

Implementations MUST:

- preserve authority classes through restoration;
- enforce the authoritative-source allowlist;
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

1. JSON Schema enforcement for envelope and restore results;
2. latest user constraint preservation;
3. prevention of authority escalation from untrusted sources;
4. prevention of unsupported execution claims;
5. rejected-approach preservation;
6. pending-verification preservation;
7. fail-closed behavior for missing reads or checks;
8. digest and receipt mismatch rejection;
9. canonical digest verification;
10. resumability only after all restore requirements are satisfied.

Reference tests are provided in `conformance/`.

## 14. Adoption path

A runtime may adopt RFC-001 incrementally:

1. emit and schema-validate the JSON envelope before compaction;
2. load it after compaction;
3. produce restore results while reading required material and checking evidence;
4. schema-validate restore results;
5. enforce the restore gate;
6. expose conformance-test results;
7. later add native UI, cross-session transport, or orchestration support.

## 15. Open questions for v0.2

- envelope and restore-results signing;
- multi-party trust and remote attestations;
- standard event taxonomy extensions;
- cross-session addressability;
- partial disclosure and redaction;
- relationship to framework-specific checkpoints;
- interoperability with tool-call receipts and agent identity standards.

## 16. Governing principle

> Preserve continuity without inventing history, and restore information without silently restoring authority.
