# Acceptance criteria

- Removing a required English or Russian contract term produces `DRIFT`.
- A regression test that is not discovered by configured CI produces `DRIFT`.
- Explicit discovery commands target their checked `test_path`; every executed
  Python or Elixir test source must match its manifest-pinned SHA-256.
- Repository-local pytest modules, packages, sourceless bytecode, native
  extensions, and Python startup hooks that can preempt collection produce
  `DRIFT`.
- Missing snapshots, refs, or exact commit identities produce `UNKNOWN`, never `PASS`.
- Evidence records checked file paths and SHA-256 hashes.
- Audit results remain advisory and grant no execution or merge authority.
