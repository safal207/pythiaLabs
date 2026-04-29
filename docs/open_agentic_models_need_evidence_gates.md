# Open Agentic Models Need Open Evidence Gates

## 1. Why this matters

Recent releases of permissively licensed open agentic models (for example, Xiaomi's MIT-licensed MiMo-V2.5 family) signal a broader shift: strong long-context, tool-using, long-horizon capabilities are increasingly available in open ecosystems.

As model capability becomes more accessible, safety work must also be accessible. Open safety infrastructure needs to keep pace with open execution capability.

## 2. From output review to action review

Traditional LLM evaluation often focuses on output quality: "Is the answer correct, useful, or aligned?" Agentic systems add a second question: "Should this action be allowed to execute under current evidence?"

That changes the control point. In high-risk workflows, pre-execution action review becomes as important as post-hoc output review.

## 3. Where pythiaLabs fits

pythiaLabs focuses on deterministic pre-execution evidence gates for high-risk agentic actions.

In this repository, that layer is represented by:

- deterministic allow/block/escalate gate logic
- stable stop reasons
- replayable decision traces
- tamper-checkable evidence artifacts

The intent is to make action-level decisions inspectable and reproducible, not only model outputs.

## 4. Future evaluation direction

A practical next step for the ecosystem is to evaluate open agentic systems on action-governance properties in addition to task success, such as:

- gate decision consistency under replay
- evidence freshness and authorization checks at decision time
- trace completeness for reviewer audit
- tamper detection on evidence artifacts

This complements model-centric benchmarks by adding execution-risk observability.

## 5. Scope note

This note uses MiMo as one external example of the open-agentic-model trend.

It does **not** claim that pythiaLabs currently integrates with MiMo, has benchmarked MiMo, or has reached production readiness.
