# Security Policy

## Current security posture

PythiaLabs is an early-stage MVP and deterministic local demo stack.

The project currently demonstrates:

- deterministic action checks
- temporal authorization reasoning
- evidence artifact export
- SHA-256 digest verification
- tamper detection
- unsigned evidence envelopes
- local `signed_demo` envelope flow

## Important limitations

PythiaLabs currently does not claim:

- production cryptography
- wallet integration
- smart contract execution
- RPC/indexer integration
- on-chain enforcement
- production identity verification
- production key management
- persistent external storage

The `signed_demo` flow is deterministic local demo logic only and is not production cryptography.

## Reporting security issues

Please do not open public issues for sensitive security reports.

Instead, contact the maintainer privately through GitHub with:

- summary of the issue
- affected file or flow
- reproduction steps
- expected impact
- suggested fix if available

## What is in scope

Security reports may include:

- incorrect accept/reject behavior in safety gates
- evidence verification bypass
- digest mismatch not detected
- malformed envelope accepted incorrectly
- hidden fields influencing verification
- unsafe production claims in documentation
- accidental secret exposure

## What is out of scope

Currently out of scope:

- production wallet security
- smart contract vulnerabilities
- chain RPC attacks
- key compromise
- production cryptographic signature failures

These are out of scope because the current MVP does not implement those systems.

## Recommended local checks

Before merging changes, run:

```bash
mix format
mix test
```


## CI security automation

PythiaLabs includes a GitHub Actions security workflow for secret scanning.

See:

- `.github/workflows/security.yml`
- `docs/security_automation.md`

This is an initial security hygiene layer.

It does not replace production security review, cryptographic review, smart contract auditing, wallet security, or key management.

For future security hardening, the project may add:

- secret scanning
- dependency vulnerability scanning
- static analysis
- property-based testing
- external verifier test vectors
