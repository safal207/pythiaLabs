# NLnet Commons Fund reviewer path — Liminal Stack 2026-06-087

Status: umbrella reviewer map for the acknowledged NLnet Commons Fund proposal.

Project: **Liminal Stack: Adaptive Routing, Reactive Storage and Secure Containers for Trustworthy AI Infrastructure**  
Application code: **2026-06-087**  
Call: **Commons Fund**  
Requested amount: **EUR 50,000**  
Submitted duration: **12 months**

This is not a new repository or a fourth product. The proposal is an integration/hardening programme across three existing open-source components:

1. **DAO_lim** — adaptive / intent-aware routing;
2. **LiminalDB** — reactive, replayable storage and audit memory;
3. **GardenLiminal** — Linux process/runtime isolation with structured lifecycle evidence.

The current repositories are the source of truth. This map separates **implemented baseline**, **validation gaps**, and **grant-funded delta**.

## Canonical repositories

| Component | Repository | Role | Evidence snapshot used by this map |
| --- | --- | --- | --- |
| DAO_lim | https://github.com/safal207/DAO_lim | Adaptive AI traffic routing | `e3f9df40bc52d392ed5539b8be6a65f4909e6835` |
| LiminalDB | https://github.com/safal207/LiminalDB | Durable/reactive evidence memory | `0cd6e77d52787bb36a97b75ba1a37cb027268eb3` |
| GardenLiminal | https://github.com/safal207/GardenLiminal | Isolated execution and lifecycle evidence | `d2203fb7ee9a1724702a543f73a1623cd08f7a58` |

The April 2026 application linked LiminalDB using the historical repository name `LiminalBD`. The canonical repository is now `safal207/LiminalDB`.

## Submitted stack thesis

```text
AI / backend request
        ↓
DAO_lim
adaptive routing and backend selection
        ↓
GardenLiminal
bounded execution / isolation controls
        ↓
LiminalDB
replayable state, events and audit history
```

The component evidence is currently stronger than the **full-stack evidence**. A single deterministic DAO → GardenLiminal → LiminalDB demonstration remains a grant-funded integration deliverable.

## Five-minute reviewer path

### DAO_lim

Repository: https://github.com/safal207/DAO_lim

Review:

- `README.md`
- `docs/START_HERE.md`
- `docs/demo/FIVE_MINUTE_ROUTING_DEMO.md`
- `docs/GRANT_EVIDENCE.md`
- `docs/BENCHMARKS.md`

Validation:

```bash
cargo test
cargo build --release
./target/release/daoctl explain --host llm.myapp.com --path /v1/chat/completions --intent realtime
```

Current baseline includes intent-aware/resonant upstream selection, p95/error-rate inputs, hot reload, Prometheus metrics and route-choice explainability.

### LiminalDB

Repository: https://github.com/safal207/LiminalDB

Review:

- `README.md`
- `READY_FOR_REVIEW.md`
- `docs/GRANT_EVIDENCE.md`
- `docs/BENCHMARKS.md`
- `docs/START_HERE.md`

Validation:

```bash
cargo build --release -p liminal-cli
cargo test --workspace --locked
./target/release/liminal-cli --store ./data --ws-port 8787
```

Current baseline includes adaptive runtime primitives, WAL/snapshots/replay, trustworthy-transition records, signed checkpoints, anti-rollback boundaries, CLI/WebSocket surfaces and Rust/TypeScript interfaces.

### GardenLiminal

Repository: https://github.com/safal207/GardenLiminal

Review:

- `README.md`
- `docs/ISOLATION_HARDENING_AUDIT_2026-08-09.md`
- `docs/BENCHMARKS.md`
- `examples/demo-liminaldb.sh`
- Issue `#6` — host-supervisor / workload namespace lifecycle
- Issue `#9` — kernel-enforced capability dropping

Validation available in normal CI:

```bash
cargo check
cargo test
cargo build --release
```

Rootful isolation post-conditions require a supported Linux environment and must not be inferred from ordinary build/test CI or WSL control-plane benchmarks.

## Original proposal → current evidence → grant delta

| Submitted area | Current evidence | Current boundary | Grant-funded delta |
| --- | --- | --- | --- |
| Adaptive routing using p95 latency, errors and semantic intent | DAO_lim routing core, `daoctl explain`, benchmark/reviewer docs | Working component baseline | Harden under failure/load; expand reproducible benchmark matrix |
| Hot reload, Prometheus and operator CLI | DAO_lim implementation/docs | Present baseline | Improve exact-revision operator evidence |
| gRPC / circuit-breaker extensions | DAO_lim roadmap/current code direction | Not all proposed extensions are complete | Complete and test a bounded supported subset |
| Safe WASM extension surface | DAO_lim WASM/wasmtime architecture | Broad marketplace/plugin story not complete | Define narrow plugin authority contract + adversarial tests |
| Reactive storage / TRS | LiminalDB adaptive runtime | Implemented single-node/adaptive baseline | Benchmark stability under bounded adversarial load |
| WAL / timeline / auditability | LiminalDB WAL, snapshots, replay, transition ledger, signed checkpoints | Strong current baseline | Expand replay/soak/exact-revision evidence |
| Distributed Raft mode | LiminalDB explicitly does not claim production distributed consensus | Not production baseline | Multi-node work requires safety invariants, election/log-repair and split-brain evidence before production claims |
| GardenLiminal namespace/cgroup/mount isolation | Runtime implementation + hardening audit | Implementation present; rootful evidence incomplete | Kernel-pinned rootful validation pack |
| `pivot_root` isolation | `src/isolate/mount.rs` implements private mounts + bind mount + `pivot_root` + old-root detach | **Implementation exists**; canonical rootful post-condition pack missing | Validate mount propagation, old-root reachability and bootstrap failure behavior |
| Seccomp BPF filtering | `src/isolate/seccomp.rs` builds/applies `strict`, `minimal`, `default` BPF allow-list profiles through `seccompiler` | **Implementation exists**; profile calibration/runtime evidence incomplete | Negative syscall fixtures, architecture/kernel evidence, profile contract documentation |
| Unknown seccomp policy handling | GardenLiminal PR #7 | Unknown names now fail closed | Keep versioned profile semantics explicit |
| Capability / privilege hardening | `no_new_privs` exists; requested `drop_caps` now fails closed rather than pretending success | **Kernel capability dropping not implemented** | Implement effective/permitted/inheritable/bounding/ambient policy + verified post-state; tracked in GardenLiminal Issue #9 |
| Namespace lifecycle | Current supervisor calls namespace transition before fork | Supervisor currently joins non-PID workload namespaces | Redesign bootstrap while preserving PID namespace semantics; tracked in GardenLiminal Issue #6 |
| GardenLiminal → LiminalDB audit path | WebSocket store adapter + demo script | Existing two-component path | Harden backpressure/reconnect/failure evidence |
| DAO → GardenLiminal → LiminalDB | Components exist; Garden→DB path exists | No canonical version-pinned three-component evidence artifact | Publish deterministic end-to-end demo |
| External security audit | Internal hardening/evidence work exists | No completed independent audit claimed | Commission review after supported isolation surface is frozen |
| Stable v1.0 releases | Components have different maturity levels | Not complete | Define release criteria per component rather than forcing simultaneous versions |

## Correction to the April 2026 wording

The proposal captured intended architecture early. Current source state is more precise:

- **GardenLiminal `pivot_root`:** implementation is present; rootful validation is pending.
- **GardenLiminal seccomp:** real BPF profile implementation is present; calibration and negative runtime evidence are pending.
- **GardenLiminal capabilities:** kernel-enforced dropping is **not** present. Non-empty requests now fail closed so they cannot create false `CAPS_DROPPED` evidence.
- **GardenLiminal namespace lifecycle:** supervisor/workload namespace separation still needs redesign and exact evidence.
- **LiminalDB:** do not claim production-grade Raft/distributed consensus.
- **Full stack:** do not claim a proven DAO → GardenLiminal → LiminalDB integration until a version-pinned end-to-end fixture exists.
- **Security:** do not claim an independent external audit until one is completed and verifiably documented.

This is not a weakening of the grant case. It creates a falsifiable boundary between existing open-source evidence and work the grant would fund.

## Grant acceptance map

### A. DAO routing hardening

A reviewer should be able to verify:

- deterministic routing fixtures over p95/error/intent inputs;
- explicit fallback/circuit behavior under backend failure;
- bounded extension/plugin authority;
- reproducible benchmark evidence tied to exact revisions;
- operator-visible route explanations.

### B. LiminalDB storage hardening

A reviewer should be able to verify:

- replay correctness from durable events/WAL;
- deterministic snapshot/checkpoint validation;
- adaptive-control behavior under bounded adversarial fixtures;
- explicit safety invariants for any multi-node work;
- no production distributed-consensus claim without election/split-brain/log-repair evidence.

### C. GardenLiminal isolation hardening

A reviewer should be able to verify on supported Linux:

- bootstrap failures stop workload execution;
- `pivot_root` post-conditions are demonstrated, not merely compiled;
- `no_new_privs` is proven before seccomp installation;
- supported seccomp profiles have positive and negative fixtures;
- non-empty capability policies are either actually enforced + verified or fail closed;
- host supervisor remains outside workload namespaces after Issue #6 is completed;
- lifecycle evidence never claims a control that was not actually enforced.

### D. Cross-component integration

One canonical demo should prove:

```text
request
→ DAO routing decision
→ bounded GardenLiminal execution
→ structured lifecycle/result events
→ durable LiminalDB replay
```

The evidence should include exact component SHAs, configuration/fixtures, environment/kernel metadata where relevant, expected event sequence, immutable output references and failure behavior when a component is unavailable.

### E. External review

Highest-value boundaries:

- routing/plugin authority in DAO_lim;
- WAL/checkpoint/replay integrity in LiminalDB;
- namespace/mount/capability/seccomp ordering and post-conditions in GardenLiminal;
- trust assumptions at component integration boundaries.

## Budget traceability

Submitted EUR 50,000 budget:

| Item | Amount | Reviewer interpretation |
| --- | ---: | --- |
| Developer/researcher salary, 12 months | EUR 36,000 | Implementation, tests, integration and documentation |
| Compute/cloud infrastructure | EUR 6,000 | CI, benchmarks and reproducible demo infrastructure |
| External security audit | EUR 5,000 | Independent review after supported surface is frozen |
| Conference/community | EUR 2,000 | Open-source dissemination/community feedback |
| Documentation tooling/subscriptions | EUR 1,000 | Reviewer/operator documentation and tooling |

No budget line is evidence that an expense has already occurred.

## Explicit non-claims

Do not currently represent the umbrella proposal as proving:

- production-grade container isolation;
- production-grade distributed consensus;
- universal routing optimality;
- completed independent security audit;
- full-stack production readiness;
- stable v1.0 releases of all three components;
- compatibility with every backend, Linux distribution or workload;
- absence of sandbox escapes.

## Reviewer response playbook

If NLnet asks about `2026-06-087`:

1. Confirm application code and EUR 50,000 / 12-month scope.
2. Link this umbrella map.
3. Link the three canonical repositories.
4. Explain `LiminalBD` as the historical LiminalDB link/name.
5. State what is already implemented.
6. Separate implementation from validation evidence.
7. Name the concrete remaining work: capability enforcement, namespace lifecycle, rootful isolation evidence, multi-node storage work, canonical three-component demo, external audit.
8. Offer exact revision evidence rather than broad architecture claims.

## Bottom line

```text
Liminal Stack is an integration and hardening programme across three existing Rust projects:

DAO_lim        — choose where work should go
GardenLiminal  — bound how work executes
LiminalDB      — preserve what happened and replay it
```

The strongest funding case is to turn these independently useful components into a **version-pinned, independently reviewed, end-to-end reproducible stack**, while keeping unfinished controls and validation gaps explicit.
