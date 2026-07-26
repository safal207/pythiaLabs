# OWASP AI Incident Response profile examples

Validate the irreversible example with the refined profile:

```bash
python3 protocols/caep/tools/validate_caep_ir.py \
  protocols/caep/examples/irreversible_non_recoverable_episode.json
```

Expected result:

```text
VALID
warning: packet is below F3: not all authorization/dispatch/outcome/recovery records carry independent integrity proofs
```

The example intentionally has no recovery record. Its action is classified as `IRREVERSIBLE`, so the outcome instead provides explicit `NON_RECOVERABLE` incident state, containment status, residual effects, and unresolved dependencies.
