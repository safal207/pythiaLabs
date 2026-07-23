# Acceptance criteria

- Removing a required English or Russian contract term produces `DRIFT`.
- A regression test that is not discovered by configured CI produces `DRIFT`.
- Missing snapshots, refs, or exact commit identities produce `UNKNOWN`, never `PASS`.
- Evidence records checked file paths and SHA-256 hashes.
- Audit results remain advisory and grant no execution or merge authority.
