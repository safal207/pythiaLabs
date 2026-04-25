# Design Principles

This document defines the core design doctrine behind PythiaLabs.

## Principle 1: Timely and Mature Action

An action is not safe merely because it is executable.

A safe agent action must be:

- structurally valid
- causally permitted
- temporally valid
- known to the system at decision time
- traceable after execution or rejection

PythiaLabs treats action maturity as a decision boundary:
an action should proceed only when the system can explain why it is allowed now.

## Application direction: consensus reason layers

In consensus-driven systems, it is not enough to prove that a transaction happened.
High-stakes agentic systems also need to explain why an action was allowed, rejected, delayed, or blocked.

This is a future application direction, not part of the current MVP.

## Why this matters

For high-stakes domains (finance, public sector, regulated operations, critical infrastructure),
a decision error is not only a technical bug. It can become:

- financial loss
- unauthorized access
- sanctions exposure
- regulatory non-compliance
- failed auditability
- irreproducible accountability

PythiaLabs is designed to make actions not only executable, but provable in context.

## Working formulation

**PythiaLabs is a temporal-causal reasoning layer for agent actions.**

It helps systems decide not only whether an action is allowed,
but whether it is allowed at the right time,
for the right reason,
with a trace that can be replayed and audited.
