# NLnet Commons Fund reviewer path — Liminal Stack 2026-06-087

Status: **reviewer-ready component baseline + pinned three-component E2E evidence**.

Project: **Liminal Stack: Adaptive Routing, Reactive Storage and Secure Containers for Trustworthy AI Infrastructure**  
Application code: **2026-06-087**  
Call: **Commons Fund**  
Requested amount: **EUR 50,000**  
Submitted duration: **12 months**

This application is an integration/hardening programme across three existing open-source components, not a fourth product:

1. **DAO_lim** — adaptive / intent-aware routing;
2. **GardenLiminal** — bounded Linux execution and lifecycle evidence;
3. **LiminalDB** — reactive, replayable evidence memory.

## Final pinned reviewer revisions

| Component | Role | Pinned revision |
| --- | --- | --- |
| `safal207/DAO_lim` | routing decision + explainability | `336d538fe203510a345445472d6ce90911b52e54` |
| `safal207/GardenLiminal` | isolated execution + lifecycle evidence | `9d5f9c25f3a4d9635c583c9920de6084950a21d9` |
| `safal207/LiminalDB` | application-level lifecycle memory | `0cd6e77d52787bb36a97b75ba1a37cb027268eb3` |

DAO_lim and GardenLiminal now track `Cargo.lock` and require `--locked` in CI. LiminalDB already tracks its workspace lockfile.

The April 2026 application used the historical repository name `LiminalBD`; the canonical project is `safal207/LiminalDB`.

## Five-minute reviewer path

### 1. DAO_lim

Review:

- `README.md`
- `docs/START_HERE.md`
- `docs/demo/FIVE_MINUTE_ROUTING_DEMO.md`
- `docs/GRANT_EVIDENCE.md`

Reproduce:

```bash
cargo check --locked --workspace
cargo test --locked --workspace --no-fail-fast
cargo build --locked -p dao -p daoctl
```

Current evidence includes intent-aware/resonant routing, route explanations, circuit state, Prometheus/operator surfaces, and reproducible locked builds.

### 2. GardenLiminal

Review:

- `README.md`
- `docs/ISOLATION_HARDENING_AUDIT_2026-08-09.md`
- `docs/CAPABILITY_ENFORCEMENT.md`
- `docs/ROOTFUL_ISOLATION_POSTCONDITIONS.md`
- `docs/LIMINALDB_RECONNECT_EVIDENCE.md`
- `docs/LIMINALDB_IMPULSE_ADAPTER.md`
- merged PRs `#10`, `#11`, `#12`, `#14`, `#15`, `#16`

Current verified boundaries:

- kernel capability enforcement covers Effective / Permitted / Inheritable / Bounding / Ambient sets;
- `CAPS_DROPPED` is emitted only after verified kernel post-state;
- privileged CI proves a tested drop survives child `execve` with `NoNewPrivs=1`;
- `pivot_root` has privileged post-condition evidence: new root visible, old root detached, host-only sentinel unreachable;
- seccomp has privileged kernel evidence: filter mode active and a denied `socket(2)` receives `EPERM`;
- host supervisor remains outside workload namespaces and owns the Store/LiminalDB connection;
- workload namespace boundary includes PID 1 and a separate network namespace;
- LiminalDB transport uses a bounded FIFO and ordered reconnect/replay rather than silent event loss;
- Garden lifecycle records are encoded into the application-level LiminalDB `Impulse` schema with a required versioned `pattern`.

### 3. LiminalDB

Review:

- `README.md`
- `READY_FOR_REVIEW.md`
- `docs/GRANT_EVIDENCE.md`
- `docs/BENCHMARKS.md`
- `docs/START_HERE.md`

Reproduce:

```bash
cd liminal-db
cargo build --locked -p liminal-cli
cargo test --workspace --locked
```

Current baseline includes WAL/snapshot/replay primitives, trustworthy-transition records, signed checkpoints, anti-rollback boundaries, CLI/WebSocket surfaces, and the application-level `Impulse` parser used by the stack E2E.

## Canonical full-stack evidence

Umbrella workflow:

```text
.github/workflows/liminal-stack-e2e.yml
scripts/liminal-stack-e2e-v0.1.sh
```

Evidence model:

```text
real DAO `daoctl explain --json`
        ↓
explicit orchestration handoff of selected upstream
        ↓
real GardenLiminal Seed
  + net.enable=true
  + host-side Liminal Store
        ↓
application-valid `garden.lifecycle.v1:` write impulses
        ↓
real pinned LiminalDB process / application parser
```

Successful PR evidence run:

- workflow run: **`31316410242`** (`Liminal Stack E2E` #4);
- umbrella source SHA: `73e18ac593839738ae0b790cefd131e458acd434`;
- artifact: **`liminal-stack-e2e-31316410242`**;
- artifact ID: **`9038912459`**;
- artifact digest: **`sha256:24770a809dd634e51bd4465881be92f497be33f7148e616f60977c5600ecffc2`**.

Artifact-verified result:

```text
DAO route          = api-v1
DAO policy         = resonant
DAO intent         = realtime
DAO candidates     = 2
selected upstream  = api-backend-1
Garden exit        = 0
Garden net ns      = requested
Garden store       = liminal
LiminalDB process  = real
LiminalDB ws port  = 8787
accepted lifecycle pattern matches = 10
application schema errors           = 0
result                              = PASS
```

The generated Garden workload itself prints `DAO_SELECTED_UPSTREAM=api-backend-1`, proving that the actual DAO decision entered the bounded execution step rather than being replaced with a second hard-coded choice.

## Original proposal → current evidence → remaining grant delta

| Submitted area | Current verified evidence | Remaining honest delta |
| --- | --- | --- |
| Adaptive / intent-aware routing | DAO routing core + explain JSON + locked CI + E2E decision | broader failure/load matrices and bounded extension/plugin authority |
| Hot reload / operator visibility | DAO implementation/docs | production/operator hardening |
| Reactive storage / audit memory | LiminalDB single-node durable/replay baseline | adversarial soak and any future multi-node safety work |
| Distributed Raft mode | **not claimed as production baseline** | election/log-repair/split-brain invariants before any production consensus claim |
| `pivot_root` | implemented + privileged post-condition evidence | broader supported-kernel compatibility matrix |
| Seccomp BPF | implemented + negative privileged syscall evidence | profile calibration/versioning across supported architectures/workloads |
| Capability dropping | implemented + all-five-set verification + execve evidence | broader capability/policy fixtures, external review |
| Host/workload namespace separation | implemented in canonical Seed path + privileged boundary evidence | multi-container/Pod path remains a separate surface |
| Garden → LiminalDB reliability | bounded FIFO + ordered reconnect/replay tests | durable per-impulse acknowledgement would require a shared protocol extension |
| Garden → LiminalDB schema | real `Impulse` application adapter | future typed metadata/lifecycle command if desired |
| DAO → Garden → LiminalDB | **pinned E2E PASS** | native orchestration coupling is optional future product work, not claimed today |
| Independent security audit | internal evidence/review only | **still pending** |

## Claim boundary

The evidence now supports this statement:

> At the pinned revisions above, Liminal Stack has a reproducible local integration path in which DAO_lim produces an explainable routing decision, that selected value is handed explicitly into a GardenLiminal isolated workload, and Garden lifecycle records are accepted by a real LiminalDB application parser.

It does **not** establish:

- production-grade container or distributed-system certification;
- native DAO process-launch coupling to GardenLiminal;
- a per-impulse durable LiminalDB commit acknowledgement;
- production distributed consensus / Raft;
- a completed independent external security audit;
- compatibility with every Linux/kernel/backend/workload;
- absence of sandbox escapes.

## Reviewer response playbook

If NLnet asks about `2026-06-087`:

1. identify the three canonical repos and exact pinned revisions above;
2. link this reviewer path and `docs/LIMINAL_STACK_E2E_V0_1.md`;
3. point to the E2E workflow/run/artifact;
4. state that component builds are lockfile-pinned;
5. distinguish verified current baseline from remaining grant-funded hardening;
6. explicitly keep Raft, durable ACK, native orchestration and external-audit claims out of the current baseline.

## Bottom line

```text
DAO_lim       — choose where work should go
      ↓
GardenLiminal — bound how selected work executes
      ↓
LiminalDB     — accept and preserve lifecycle evidence
```

The earlier integration gap is now closed with version-pinned, reproducible local evidence. The highest-value remaining grant work is **hardening, broader validation, multi-node safety work if pursued, and independent external review** — not inventing a fourth repository or pretending unfinished controls are already certified.
