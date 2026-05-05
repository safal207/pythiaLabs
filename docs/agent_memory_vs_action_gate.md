# Agent Memory vs. Pre-Execution Action Gates

PythiaLabs is not an organizational memory product.

It is a pre-execution safety gate for AI-agent actions.

This document clarifies the difference between memory systems that preserve what a team knows and action-gating systems that decide whether an agent should execute a risky action.

## The category distinction

Many agent-memory systems focus on persistent knowledge:

- chats,
- decisions,
- documents,
- entities,
- semantic search,
- knowledge graphs,
- Q&A with citations,
- MCP access to organizational context.

That category answers questions like:

- What does the organization know?
- Who decided this?
- Why was this choice made?
- Which entities are connected?
- What changed over time?

PythiaLabs focuses on a different control point:

> Should this AI-agent action execute before it touches real tools?

It answers questions like:

- What exact action is proposed?
- What evidence exists at decision time?
- Is the evidence fresh?
- Is the action authorized?
- What is the blast radius?
- Should the action be ALLOW, BLOCK, or ESCALATE?
- Can the decision be replayed later?

## Short positioning

> Agent-memory systems remember what the team knows.
>
> PythiaLabs decides what the agent is allowed to do.

## Architecture comparison

| Layer | Agent-memory systems | PythiaLabs |
|---|---|---|
| Primary object | Knowledge | Proposed action |
| Main question | What do we know? | Should this execute? |
| Output | Answer, wiki, citation, graph | ALLOW / BLOCK / ESCALATE |
| Risk boundary | Retrieval quality | Execution permission |
| Reviewer artifact | Source citation | Decision-time evidence artifact |
| Failure mode | Wrong or stale memory | Unsafe action execution |

## What PythiaLabs can learn from agent-memory systems

### 1. MCP-first access

Modern AI-agent tools increasingly expect a Model Context Protocol surface.

For PythiaLabs, MCP should not only retrieve knowledge. It should expose gates:

- describe available gates,
- list gate requirements,
- evaluate a proposed action,
- return evidence requirements,
- produce ALLOW / BLOCK / ESCALATE outcomes,
- return replayable artifacts.

Positioning:

> Cursor, Claude, Codex, or another agent should be able to ask PythiaLabs whether a risky action should proceed before execution.

### 2. Fast mock mode

A strong safety project needs a five-minute local demo.

Target developer experience:

```bash
make demo
# or
npm run demo
# or
docker compose up
```

Expected demo flow:

1. Load a sample risky action.
2. Run it through a PythiaLabs gate.
3. Return ALLOW / BLOCK / ESCALATE.
4. Print a stable stop reason.
5. Emit a sample evidence artifact.

This is important for grant reviewers, CTOs, security reviewers, and design partners.

### 3. Evidence quality gates

Agent-memory systems often filter low-quality or low-confidence knowledge before storing it.

PythiaLabs should apply the same discipline before execution:

- stale evidence should not silently pass,
- missing authorization should block or escalate,
- incomplete quorum should escalate,
- high blast radius should require stronger evidence,
- irreversible actions should require stricter review.

Positioning:

> Memory systems filter low-quality knowledge before it enters memory.
>
> PythiaLabs filters high-risk actions before they enter execution.

## Relationship to the storage roadmap

PythiaLabs separates three kinds of truth:

- **Postgres** — product truth: teams, paid reviews, pilots, workflow submissions.
- **TimescaleDB** — temporal measurement truth: decision events, latency, outcome trends, failure classes.
- **LiminalDB** — adaptive causal-memory truth: agentic state, causal transitions, evidence evolution, and replayable decision context.

This keeps the project focused:

- PythiaLabs is the gate.
- Storage preserves why the gate decision was valid, measurable, and auditable.
- LiminalDB is the native causal-memory substrate, not a generic vector or chat memory store.

## Roadmap implications

Near-term priorities:

1. Keep the public category narrow: pre-execution safety gate for AI agents.
2. Improve the MCP surface around action evaluation.
3. Add a five-minute local mock/demo path.
4. Keep producing reviewer-facing evidence artifacts.
5. Use paid reviews to collect real risky workflows.

Out of scope for now:

- broad organizational wiki,
- general-purpose chat memory,
- generic semantic search product,
- full knowledge-management platform,
- multi-database production stack before real workflows require it.

## Final framing

The market is moving toward persistent agent memory.

PythiaLabs takes the adjacent safety-critical position:

> Persistent memory tells agents what the world knows.
>
> PythiaLabs decides whether an agent is allowed to act on that knowledge.
