# Glossary

Core decision terms used throughout PythiaLabs.

---

**ALLOW**
The gate has evaluated all available evidence and determined the proposed action is safe to proceed. Execution continues without interruption.

**BLOCK**
The gate has determined the proposed action should not execute. The action is stopped before it touches any real tools or systems, and a stop reason is recorded.

**ESCALATE**
The gate cannot make a confident ALLOW or BLOCK decision on its own. The action is held and surfaced to a human reviewer or an approval workflow before execution can continue.

**pre-execution gate**
A checkpoint that evaluates a proposed action *before* it runs — not after. PythiaLabs sits at this checkpoint, ensuring high-risk actions are reviewed while they can still be stopped.

**proposed action**
An operation an AI agent intends to perform, such as deleting a database, executing a financial transaction, or deploying infrastructure. It has not yet run when the gate evaluates it.

**decision-time evidence**
The structured context collected at the moment a gate evaluation happens — authorization status, environment flags, recovery options, and similar signals. It is what the gate actually reasons over.

**evidence artifact**
A recorded snapshot of the decision-time evidence for a single gate evaluation. Artifacts are stored so human reviewers can later inspect exactly what information the gate used to reach its verdict.

**stop reason**
A stable, machine-readable label explaining why a gate returned BLOCK or ESCALATE. Stop reasons are consistent across runs so they can be queried, compared, and audited without parsing free-form text.

**replayable trace**
A complete, ordered record of a gate evaluation — inputs, evidence, verdict, and stop reason — sufficient to reproduce the decision deterministically. Traces exist so any evaluation can be re-examined or re-run with the same outcome.

**deterministic decision**
A gate verdict that depends only on its inputs and defined rules, not on randomness or opaque model state. Given the same evidence, a deterministic gate always returns the same ALLOW, BLOCK, or ESCALATE result.

**blast radius**
The scope of potential damage if a proposed action executes and goes wrong. A high blast radius (e.g., dropping a production database) makes a proposed action a stronger candidate for BLOCK or ESCALATE.

**authorization context**
The set of permissions, approvals, and credentials that are valid at the moment the gate is evaluated. Missing or expired authorization is a common reason for a BLOCK verdict.

**recovery context**
Information about whether a proposed action can be undone or rolled back if it fails. A low recovery context — meaning the action is difficult or impossible to reverse — increases the gate's scrutiny.

**irreversible action**
A proposed action that cannot be undone once executed, such as sending a financial transfer or permanently deleting data. Irreversible actions receive heightened scrutiny because a wrong ALLOW verdict cannot be corrected after the fact.

**reviewer artifact**
A structured, human-readable output produced by the gate for each ESCALATE verdict. It summarizes the proposed action, the evidence collected, and the reason for escalation so a human reviewer has everything needed to make an approval decision.