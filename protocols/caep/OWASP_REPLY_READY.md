# Ready-to-post OWASP AISVS follow-up

Implemented in CAEP with schema, validator, examples, and regression tests:

- explicit `gate_path` values for automatic execution, approval gating, blocking, and escalation;
- decision-to-gate-path consistency checks;
- recovery requirements conditioned on `reversibility_class`;
- explicit `NON_RECOVERABLE` incident evidence for irreversible actions;
- failed recovery of a reversible action surfaced as a security finding rather than hidden as an invalid packet.

Implementation PR: https://github.com/safal207/pythiaLabs/pull/250

Suggested reply:

> Implemented in CAEP with schema, validator, examples, and regression tests.
>
> The update adds an explicit gate path and conditions recovery requirements on the action's reversibility class. Irreversible actions now carry explicit `NON_RECOVERABLE` incident evidence, while failed recovery of a reversible action is surfaced as a finding.
>
> Implementation: https://github.com/safal207/pythiaLabs/pull/250
>
> Thank you for turning the open question into a testable distinction.
