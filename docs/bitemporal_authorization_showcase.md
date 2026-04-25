# Bitemporal Authorization Showcase

## Problem

In agentic systems, a permission can be valid in the domain at one time, but the system may learn about it later.

This creates an important safety question:

Was the action authorized at the action time, and did the system know that authorization at the decision time?

## Time axes

- action_time: when the agent action was proposed or attempted
- decision_time: when the system allowed or rejected the action
- valid_time: when the permission is true in the domain
- transaction_time / recorded_at: when the system learned or recorded the permission

## What the showcase demonstrates

- authorization valid and known
- authorization valid but unknown at decision time
- expired authorization
- future authorization
- deterministic stop_reason
- trace explaining the temporal decision boundary

## How to run

mix run examples/bitemporal_authorization_showcase.exs

## Relation to Temporal-Causal Memory Stack

This showcase demonstrates the XTDB-style temporal memory layer without adding XTDB or any database dependency.

It is an in-memory deterministic demo of valid_time and transaction_time reasoning.
