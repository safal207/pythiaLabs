# Grant Portfolio Status

Last updated: 2026-08-09

## Purpose

Mission-control view for the current NLnet portfolio: application code, reviewer readiness, exact evidence entrypoint, and next action.

## Current portfolio

| Priority | Code | Fund | Project | Status |
|---:|---|---|---|---|
| 1 | 2026-08-00b | NGI TALER | ProofPath Agent Payment Guard | Submitted; reviewer-ready |
| 2 | 2026-08-00c | NGI Fediversity | LiminalDB | Submitted; budget corrected; reviewer-ready |
| 3 | 2026-06-133 | NGI Commons | PythiaLabs | Acknowledged; primary version; reviewer-ready |
| 4 | 2026-06-087 | NGI Commons | Liminal Stack | Acknowledged; **reviewer-ready + pinned 3-component E2E PASS** |
| 5 | 2026-06-0c5 | NGI Commons | LiminalQAengineer | Acknowledged; grant-specific reviewer path prepared |
| 6 | 2026-06-0fe | NGI Commons | PythiaLabs | Acknowledged; duplicate/older variant |

## Primary reviewer-ready paths

### ProofPath — 2026-08-00b

Repository: `safal207/ProofPath`  
Requested amount: EUR 50,000

Reviewer entrypoints:

- `docs/NGI_TALER_REVIEWER_PATH.md`
- `docs/TALER_ALIGNMENT.md`
- `docs/AGENT_PAYMENT_GUARD_DEMO.md`
- `docs/BUDGET_AND_MILESTONES.md`
- `docs/GRANT_MILESTONE_TRACKER.md`

Next action: wait for NLnet review; answer clarification from the existing evidence/milestone map rather than expanding scope.

### LiminalDB — 2026-08-00c

Repository: `safal207/LiminalDB`  
Requested amount: EUR 50,000

Reviewer entrypoints:

- `docs/FEDIVERSITY_REVIEWER_PATH.md`
- `docs/FEDERATED_EVENT_SOURCING_ALIGNMENT.md`
- `docs/ACTIVITYPUB_MATRIX_INTEGRATION_PLAN.md`
- `docs/BUDGET_AND_MILESTONES_FEDIVERSITY.md`
- `docs/GRANT_MILESTONE_TRACKER_FEDIVERSITY.md`

Next action: wait for NLnet review; keep the reviewer path clean and avoid unrelated scope growth.

### PythiaLabs — 2026-06-133

Repository: `safal207/pythiaLabs`  
Requested amount: EUR 30,000

Reviewer entrypoints:

- `docs/NGI_COMMONS_REVIEWER_PATH.md`
- `docs/REVIEWER_PATH.md`
- `docs/PYTHIALABS_ONE_PAGE_SUMMARY.md`
- `docs/BUDGET_AND_MILESTONES_COMMONS.md`
- `docs/GRANT_MILESTONE_TRACKER_COMMONS.md`

Next action: wait for NLnet review; use `2026-06-133` as the intended current PythiaLabs application.

## Liminal Stack — 2026-06-087

Project: **Liminal Stack: Adaptive Routing, Reactive Storage and Secure Containers for Trustworthy AI Infrastructure**  
Requested amount: EUR 50,000  
Submitted duration: 12 months  
Status: **reviewer-ready component baseline + pinned three-component E2E evidence**

Reviewer entrypoints:

- [`NLNET_LIMINAL_STACK_REVIEWER_PATH_2026-06-087.md`](NLNET_LIMINAL_STACK_REVIEWER_PATH_2026-06-087.md)
- [`LIMINAL_STACK_E2E_V0_1.md`](LIMINAL_STACK_E2E_V0_1.md)
- `.github/workflows/liminal-stack-e2e.yml`
- `scripts/liminal-stack-e2e-v0.1.sh`

Canonical pinned components:

```text
DAO_lim       336d538fe203510a345445472d6ce90911b52e54
GardenLiminal 9d5f9c25f3a4d9635c583c9920de6084950a21d9
LiminalDB     0cd6e77d52787bb36a97b75ba1a37cb027268eb3
```

First successful pinned E2E evidence:

```text
run       31316410242
artifact  9038912459
sha256    24770a809dd634e51bd4465881be92f497be33f7148e616f60977c5600ecffc2
result    PASS
```

Artifact-verified path:

```text
DAO explain
  route=api-v1
  policy=resonant
  intent=realtime
  selected=api-backend-1
        ↓ explicit orchestration handoff
GardenLiminal workload
  selected upstream embedded in workload
  net namespace requested
  store=liminal
  exit=0
        ↓
real LiminalDB process
  application-valid garden.lifecycle.v1 records = 10
  impulse schema errors = 0
```

Completed since the earlier umbrella map:

- Garden kernel capability enforcement + post-state evidence;
- privileged `pivot_root` and seccomp postconditions;
- host supervisor / workload namespace separation with Store outside the workload boundary;
- bounded LiminalDB reconnect/replay outbox;
- Garden lifecycle → real LiminalDB `Impulse` application adapter;
- committed `Cargo.lock` + locked CI in DAO_lim and GardenLiminal;
- canonical version-pinned DAO → Garden → LiminalDB E2E.

Remaining honest grant/hardening delta:

- broader routing failure/load/adversarial matrices;
- optional bounded plugin/extension authority work;
- LiminalDB adversarial soak and any future multi-node safety work;
- **no production Raft/distributed-consensus claim yet**;
- broader kernel/architecture/workload validation;
- durable per-impulse acknowledgement would require a shared protocol extension;
- **independent external security audit remains pending**.

Next action:

```text
Do not create a new Liminal Stack repository.
Do not add more architecture merely for appearance.
Wait for NLnet review and answer from the pinned reviewer path + E2E artifact.
```

## LiminalQAengineer — 2026-06-0c5

Repository: `safal207/LiminalQAengineer`  
Status: acknowledged; grant-specific reviewer path prepared and merged.

Reviewer entrypoint:

- `docs/NLNET_COMMONS_REVIEWER_PATH_2026-06-0c5.md`

Next action: wait for NLnet review; keep implementation-vs-grant-delta traceability explicit.

## PythiaLabs older variant — 2026-06-0fe

Status: acknowledged older/duplicate variant.

Next action: do not use as the primary PythiaLabs application; use `2026-06-133`.

## NLnet communication boundary

- LiminalDB budget correction to EUR 50,000 was acknowledged.
- The latest PythiaLabs proposal is the intended current version by default.
- Liminal Stack `2026-06-087` was acknowledged; absence of a later email is not interpreted as selection or rejection.

## Response playbook

If NLnet asks:

1. confirm application code;
2. link the exact reviewer path;
3. state what is already implemented;
4. point to exact revisions and runnable evidence;
5. state what grant work remains;
6. keep non-claims explicit;
7. avoid creating extra repositories or widening scope unless the reviewer asks.

## Strategic focus

```text
Reviewer confidence > number of new projects.

Keep clean:
1. ProofPath
2. LiminalDB
3. PythiaLabs
4. Liminal Stack
5. LiminalQAengineer

Do not submit or invent additional work merely to increase activity.
```
