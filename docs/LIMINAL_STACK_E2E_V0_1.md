# Liminal Stack E2E v0.1

Status: pinned, local, reproducible three-component integration evidence.

## Purpose

The original NLnet Liminal Stack proposal spans three existing repositories. Component-level tests are not enough to claim that the submitted stack has an integration path, so this evidence run exercises one explicit handoff across all three components.

```text
DAO_lim
real explainable routing decision
        ↓ explicit orchestration handoff
GardenLiminal
real isolated workload + host-side lifecycle Store
        ↓ application-valid write impulses
LiminalDB
real WebSocket server + application impulse parser
```

## Pinned component revisions

The workflow intentionally checks out exact revisions rather than floating `main`:

- DAO_lim: `336d538fe203510a345445472d6ce90911b52e54`
- GardenLiminal: `9d5f9c25f3a4d9635c583c9920de6084950a21d9`
- LiminalDB: `0cd6e77d52787bb36a97b75ba1a37cb027268eb3`

All three Rust application workspaces used by the E2E have committed lockfiles at the pinned revisions. DAO_lim and GardenLiminal were explicitly hardened to track `Cargo.lock` and require `--locked` in CI before these final revisions were selected.

The evidence artifact also records the revisions observed with `git rev-parse HEAD` so checkout drift is visible.

## Step 1 — DAO routing evidence

The workflow starts the real DAO gateway with `configs/dao.toml` and calls the real `daoctl explain --json` surface for:

```text
host   = api.example.com
path   = /v1/chat/completions
intent = realtime
```

The harness requires:

- a non-empty `selected` upstream;
- `no_route == false`;
- exactly one candidate marked `winner=true`;
- the winner name equals `selected`.

The complete JSON explanation is preserved as `dao-decision.json`.

## Step 2 — explicit handoff

The current repositories do not claim that DAO natively launches Garden workloads. v0.1 therefore uses an explicit orchestration handoff instead of inventing that coupling.

The selected upstream name is embedded both in the generated Garden Seed environment and in the command executed by the isolated workload. The artifact preserves the selected value.

This proves an inspectable integration boundary while keeping the claim honest: DAO made the decision; the orchestration harness consumed that decision.

## Step 3 — Garden isolation + host-side Store

The harness creates a minimal static-BusyBox rootfs and runs GardenLiminal with:

- a real Seed;
- `net.enable=true`;
- `--store liminal`;
- `LIMINAL_URL=ws://127.0.0.1:8787`;
- a workload that exits successfully after rendering the selected DAO upstream.

GardenLiminal's separately validated namespace boundary keeps the persistent Store connection on the host-supervisor side, so a fresh workload network namespace does not own or sever the LiminalDB connection.

## Step 4 — real LiminalDB application acceptance

The workflow runs a real pinned `liminal-cli` process with its WebSocket server on port 8787 and local persistent store directory.

Garden lifecycle records use the `garden.lifecycle.v1:` application adapter. The E2E requires:

- no `impulse requires pattern` error;
- no `ws command failed` error;
- at least three lifecycle patterns observed by the real LiminalDB process.

This is deliberately stronger than merely proving a WebSocket frame was written: LiminalDB must pass its application-level `Impulse` parser and route multiple Garden lifecycle records.

## Evidence artifact

`liminal-stack-e2e-<run_id>` contains at least:

- `environment.txt`
- `components.json`
- `dao.log`
- `dao-health.txt`
- `dao-decision.json`
- `dao-selected-upstream.txt`
- generated Garden Seed
- `garden.log`
- `liminaldb.log`
- local LiminalDB store files
- `summary.json`

`summary.json` reports PASS only after all three component boundaries have succeeded.

## Post-merge evidence

The workflow also runs on `main` pushes that change the E2E harness or reviewer evidence. A PR run is therefore not the final proof by itself; after the umbrella PR is merged, the corresponding `main` run must also pass on the merged umbrella SHA.

## Claim boundary

A passing v0.1 demonstrates a real, pinned local integration path across DAO routing, Garden isolated execution, and LiminalDB application-level impulse acceptance.

It does **not** establish:

- production readiness of the three-component stack;
- native DAO process-launch coupling to GardenLiminal;
- a per-impulse durable LiminalDB commit acknowledgement;
- distributed consensus / production Raft;
- an independent security audit;
- absence of sandbox escapes.

Those remain separate claims and, where relevant, grant-funded work.
