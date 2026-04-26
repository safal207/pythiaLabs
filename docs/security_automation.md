# Security Automation

## Current status

PythiaLabs includes a minimal CI security workflow for repository secret scanning.

The workflow runs on:

- pull requests
- pushes to `main`
- manual dispatch

## Implemented checks

### Secret scanning

The repository uses Gitleaks through GitHub Actions to detect accidentally committed secrets.

Workflow:

```bash
.github/workflows/security.yml
```

This helps detect:

- API keys
- tokens
- private keys
- credentials
- accidental secret-like strings

## Why this matters

PythiaLabs works with evidence artifacts, governance traces, and future authorization flows.

Even though the current MVP does not include production keys, wallets, or live credentials, early secret scanning reduces the chance of unsafe project hygiene as the repository grows.

## Current limitations

This workflow does not yet provide:

- dependency vulnerability scanning
- static security analysis
- container image scanning
- production cryptographic review
- smart contract security checks
- wallet or RPC security checks

These are future hardening areas.

## Recommended local checks

Before opening or merging a PR:

```bash
mix format
mix test
```

## Future hardening ideas

Potential future additions:

- dependency vulnerability scanning
- static analysis for Elixir code
- Rust dependency audit
- signed release artifacts
- external verifier test vectors
- CI checks for documentation claims
