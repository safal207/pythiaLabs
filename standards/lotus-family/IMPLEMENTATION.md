# Implementation slice v0.1

This first slice turns the Lotus Family strength map into executable checks.
It intentionally audits materialized exact snapshots and does not perform remote
repository access or consequential actions.

The runtime binds every configured executable test source to its manifest
digest and rejects local interpreter/import shadows that can terminate pytest
without collecting that source.
