# Agent Safety Showcase

## Problem

AI agents can produce actions that look valid at the surface level but are unsafe because the causal/authorization boundary is missing.

Example:
An agent proposes `delete_user_data`.
The JSON shape may be valid.
The action may be executable.
But the required authorization is missing.

Ordinary logs may show that an action happened.
Pythia should show why the action was allowed, stopped, or rejected.

## What the showcase demonstrates

- deterministic action evaluation
- explicit constraints
- observable trace
- stable stop_reason
- safe action proceeds
- unsafe action is rejected

## How to run

```bash
mix run examples/agent_safety_showcase.exs
```

## Expected result

Safe action:
- accepted
- constraints_satisfied

Unsafe action:
- rejected
- missing_authorization

Invalid action:
- rejected
- invalid_action

## Relation to Liminal Stack

PythiaLabs:
- controlled reasoning/refinement loop

CML:
- causal validity / why a transition is allowed

LTP:
- trace transport / replayable transition history

This showcase is not a full CML/LTP integration yet.
It is the first deterministic bridge toward that architecture.
