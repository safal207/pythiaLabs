# Change note — OWASP AISVS AI Incident Response feedback

This change implements the first external design feedback received on the CAEP proposal in OWASP/AISVS #1083.

The implementation keeps the existing v0.1 evidence model compatible while adding a stricter incident-response profile for:

- explicit gate-path evidence;
- reversibility-conditioned recovery;
- honest representation of irreversible consequences;
- explicit findings for failed reversible recovery.

The distinction is deliberate:

```text
valid evidence packet ≠ safe system outcome
```

A packet can be valid because it truthfully proves that recovery failed.
