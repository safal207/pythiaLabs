# NLnet Commons Fund reviewer path — Liminal Stack 2026-06-087

Status: umbrella reviewer map for the acknowledged NLnet Commons Fund proposal.

Project: **Liminal Stack: Adaptive Routing, Reactive Storage and Secure Containers for Trustworthy AI Infrastructure**  
Application code: **2026-06-087**  
Call: **Commons Fund**  
Requested amount: **EUR 50,000**  
Submitted duration: **12 months**

This is not a new repository or a new product. The submitted project is an umbrella over three existing open-source components:

1. **DAO_lim** — adaptive / intent-aware routing;
2. **LiminalDB** — reactive, replayable storage and audit memory;
3. **GardenLiminal** — Linux process/container isolation with structured lifecycle evidence.

The purpose of this file is to map the original application to the repositories that exist today and to separate **implemented baseline**, **partially implemented work**, and **grant-funded delta**.

## Canonical repositories

| Component | Current repository | Role in submitted stack | Current main snapshot used for this map |
| --- | --- | --- | --- |
| DAO_lim | https://github.com/safal207/DAO_lim | Adaptive AI traffic routing | `e3f9df40bc52d392ed5539b8be6a65f4909e6835` |
| LiminalDB | https://github.com/safal207/LiminalDB | Reactive / durable evidence storage | `0cd6e77d52787bb36a97b75ba1a37cb027268eb3` |
| GardenLiminal | https://github.com/safal207/GardenLiminal | Isolated execution and lifecycle audit | `6c30422d0492ec312a35624322f90a7761419655` |

The original April 2026 proposal linked LiminalDB using the historical repository name `LiminalBD`. The canonical repository is now `safal207/LiminalDB`.

## Submitted stack thesis

The application described a three-stage infrastructure path:

```text
AI / backend request
        ↓
DAO_lim
adaptive routing and backend selection
        ↓
GardenLiminal
bounded isolated execution
        ↓
LiminalDB
replayable state, events and audit history
```

This remains the useful architectural thesis, but the current evidence is strongest at the **component level**. A single reproducible DAO → GardenLiminal → LiminalDB end-to-end demonstration should be treated as a grant deliverable, not as an already-proven baseline.

## Five-minute reviewer path

### 1. DAO_lim — routing

Repository: https://github.com/safal207/DAO_lim

Start with:

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

Current baseline includes intent-aware/resonant upstream selection, p95/error-rate inputs, hot configuration reload, Prometheus metrics, an admin surface, and `daoctl` explainability.

### 2. LiminalDB — storage / continuity

Repository: https://github.com/safal207/LiminalDB

Start with:

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

Current baseline includes the adaptive runtime, WAL/snapshots/replay, Mirror Timeline concepts, trustworthy-transition records, signed checkpoints, anti-rollback boundaries, CLI/WebSocket surfaces and Rust/TypeScript interfaces.

### 3. GardenLiminal — isolated execution

Repository: https://github.com/safal207/GardenLiminal

Start with:

- `README.md`
- `docs/BENCHMARKS.md`
- `examples/demo-liminaldb.sh`

Validation on a supported Linux host:

```bash
cargo test
cargo build --release
./target/release/gl inspect -f examples/seed-busybox.yaml
```

Runtime paths that create Linux namespaces/cgroups or execute containers require an appropriate Linux environment and privileges/capabilities. A reviewer should not treat WSL/control-plane benchmarks as equivalent to rootful isolation validation.

## Original proposal → current evidence → grant delta

| Submitted area | Current public evidence | Current boundary | Grant-funded delta |
| --- | --- | --- | --- |
| **Adaptive routing using p95 latency, errors and semantic intent** | DAO_lim README, routing core, `daoctl explain`, benchmark/evidence docs | Working component baseline | Harden routing under failure/load; expand reproducible benchmark matrix |
| **Hot reload, Prometheus and operator CLI** | DAO_lim README and review docs | Present baseline | Improve operator validation and exact-revision evidence |
| **gRPC and circuit breaker work** | DAO_lim roadmap / current code direction | Not all originally described routing extensions should be treated as complete | Complete and test the supported production-facing subset |
| **Safe WASM extension surface** | DAO_lim uses WASM/wasmtime in its architecture | Marketplace / broader plugin story is not a completed deliverable | Define a narrow, sandboxed plugin contract and adversarial tests |
| **Reactive / bio-inspired storage with TRS** | LiminalDB adaptive runtime, Cells, Impulses, TRS/Reflexes | Implemented single-node/adaptive baseline | Benchmark TRS stability under adversarial load patterns |
| **Append-only timeline, WAL and auditability** | LiminalDB WAL/snapshots/replay, Mirror Timeline, trustworthy-transition ledger, signed checkpoints | Strong current baseline | Expand exact-revision replay/soak evidence |
| **Distributed Raft mode** | LiminalDB explicitly does not claim production distributed consensus | Not implemented as a production-grade baseline | Treat distributed consensus / multi-node replication as future grant work, with safety invariants and split-brain tests before any production claim |
| **GardenLiminal namespace/cgroup isolation and lifecycle evidence** | GardenLiminal runtime, structured lifecycle events, cgroups/namespaces, LiminalDB WebSocket adapter | Working prototype / platform-dependent | Produce rootful Linux validation pack tied to exact kernel/environment |
| **`pivot_root` isolation** | GardenLiminal roadmap currently says it still uses `chroot` and lists `pivot_root` as pending | The original application description is stronger than current main | Implement and test correct mount/pivot ordering before calling it complete |
| **Full seccomp BPF filtering** | GardenLiminal has security policy/profile structure, but README lists full seccomp implementation as pending | Partial | Complete bounded syscall filtering and negative tests with supported workload profiles |
| **Capability / privilege hardening** | GardenLiminal security model, capability-drop configuration and rootless paths | Requires runtime evidence on supported Linux | Add ordering/invariant tests around `no_new_privs`, capabilities and seccomp |
| **GardenLiminal → LiminalDB audit path** | WebSocket store adapter and `examples/demo-liminaldb.sh` | Existing two-component integration path | Harden protocol failure/backpressure/reconnect evidence |
| **DAO → GardenLiminal → LiminalDB integration** | Components exist independently; Garden→DB path exists | No single canonical full-stack evidence artifact is claimed here | Publish one deterministic end-to-end demo with version-pinned inputs and expected outputs |
| **External security audit** | Internal security work exists across the ecosystem | No completed independent audit is claimed | Commission external review after the supported isolation surface is frozen |
| **Stable v1.0 releases of all three** | Repositories are at different maturity levels; LiminalDB explicitly identifies itself as pre-1.0 | Not complete | Define release criteria per component rather than forcing simultaneous version numbers |

## Important correction to the April 2026 application wording

The application captured the intended architecture at an early stage. Current repository state is the source of truth.

In particular:

- **GardenLiminal:** do not currently claim `pivot_root` or complete seccomp enforcement as finished; its README marks those as pending.
- **LiminalDB:** do not currently claim production-grade Raft/distributed consensus; the project explicitly lists distributed/federated work as incomplete.
- **Full stack:** do not claim a proven DAO → GardenLiminal → LiminalDB integration until a version-pinned end-to-end fixture exists.
- **Security:** do not claim an independent external security audit until one has actually been completed and published or otherwise verifiably documented.

This correction strengthens the proposal because it creates a falsifiable boundary between existing open-source evidence and the work the grant would fund.

## Grant acceptance map

The original proposal did not define formal numbered work packages, so this reviewer map derives acceptance groups from the submitted expected outcomes, challenges and budget. These are **review criteria**, not a rewrite of the submitted application.

### A. Routing hardening — DAO_lim

A reviewer should be able to verify:

- deterministic routing fixtures over p95/error/intent inputs;
- explicit fallback/circuit behavior under backend failure;
- bounded extension/plugin authority;
- reproducible benchmark evidence tied to exact revisions;
- operator-visible explanations for route choice.

### B. Reactive storage hardening — LiminalDB

A reviewer should be able to verify:

- replay correctness from durable events/WAL;
- deterministic snapshot/checkpoint validation;
- TRS/adaptive-control behavior under bounded adversarial load fixtures;
- explicit safety invariants for any multi-node work;
- no production distributed-consensus claim without split-brain/election/log-repair evidence.

### C. Runtime isolation hardening — GardenLiminal

A reviewer should be able to verify on a supported Linux environment:

- namespace/mount/cgroup setup fails closed;
- `pivot_root` replaces the current weaker rootfs boundary before the claim is made;
- seccomp and capability ordering is explicit and tested;
- supported security profiles have positive and negative workload fixtures;
- lifecycle/audit events remain complete across failure paths.

### D. Cross-component integration

One canonical demo should prove:

```text
request
→ DAO routing decision
→ bounded GardenLiminal execution
→ structured lifecycle/result events
→ durable LiminalDB replay
```

The demo should record:

- exact commit SHAs of all three repositories;
- configuration and fixture inputs;
- environment/kernel information where isolation behavior matters;
- expected decision/event sequence;
- hashes or immutable references for output artifacts;
- failure behavior when one component is unavailable.

### E. External security review

The external review should focus on the frozen supported surface rather than the entire roadmap. Highest-value boundaries are:

- routing/plugin authority in DAO_lim;
- WAL/checkpoint/replay integrity in LiminalDB;
- mount/namespace/seccomp/capability ordering in GardenLiminal;
- trust assumptions at the WebSocket/integration boundary.

## Budget traceability

The submitted EUR 50,000 budget was:

| Submitted budget item | Amount | Reviewer interpretation |
| --- | ---: | --- |
| Developer/researcher salary, 12 months | EUR 36,000 | Core implementation, tests, integration and documentation across the three components |
| Compute/cloud infrastructure | EUR 6,000 | CI, benchmarks and reproducible demo infrastructure |
| External security audit | EUR 5,000 | Independent review after the supported surface is frozen |
| Conference/community | EUR 2,000 | Open-source dissemination/community feedback |
| Documentation tooling/subscriptions | EUR 1,000 | Reviewer/operator documentation and supporting tooling |

No line in this map should be read as evidence that an expense has already occurred.

## Evidence maturity snapshot

At creation of this reviewer map:

- **LiminalDB** is the most actively hardened component and has the strongest current evidence/reviewer packaging.
- **DAO_lim** has a concrete routing implementation, explainability and benchmark/reviewer material, but its current main revision predates the recent LiminalDB hardening work.
- **GardenLiminal** has a substantial prototype and a published control-plane benchmark, but the most security-sensitive original claims (`pivot_root`, full seccomp, external audit) remain unfinished and should be treated as priority grant work.

That maturity difference is expected in an umbrella proposal and is preferable to presenting all three repositories as equally complete.

## Explicit non-claims

This umbrella proposal should not currently be represented as proving:

- production-grade container isolation;
- production-grade distributed consensus;
- universal routing optimality;
- a completed independent security audit;
- full-stack production readiness;
- stable v1.0 releases of all three components;
- compatibility with every AI backend, Linux distribution or workload;
- that bio-inspired terminology itself provides a security or correctness guarantee.

## Reviewer response playbook

If NLnet asks about application `2026-06-087`:

1. Confirm the application code and EUR 50,000 / 12-month scope.
2. Link this umbrella reviewer map.
3. Link the three canonical repositories.
4. Explain that `LiminalBD` was the historical LiminalDB repository name/link.
5. State which submitted capabilities are already implemented.
6. State clearly that distributed consensus, `pivot_root`, full seccomp, a canonical three-component integration demo, and external audit remain grant-funded work.
7. Offer exact revision evidence rather than broad architecture claims.

## Bottom line

The strongest present-day framing is:

```text
Liminal Stack is not a fourth product.
It is an integration and hardening programme across three existing Rust projects:

DAO_lim        — choose where work should go
GardenLiminal  — bound how work executes
LiminalDB      — preserve what happened and replay it
```

NLnet funding would be most defensible when used to turn those independently working components into a **version-pinned, security-reviewed, end-to-end reproducible stack**, while keeping every unfinished security or distributed-systems claim explicit.