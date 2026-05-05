# PythiaLabs MCP (Cursor & compatible hosts)

stdio MCP server that forwards tool calls to `mix pythia.eval_json` in this repository so deterministic showcase gates run locally (no hosted service).

## Prerequisites

- Elixir / Mix on `PATH` (same as reviewer quickstart: `mix deps.get`, `mix compile`)
- Node.js 18+ (for this thin MCP adapter)

## Install (Cursor)

1. Clone PythiaLabs and run `mix deps.get` once at the repo root.
2. In Cursor: **Settings → MCP → Add server** (or edit `~/.cursor/mcp.json`), e.g.:

```json
{
  "mcpServers": {
    "pythialabs": {
      "command": "node",
      "args": ["/absolute/path/to/pythiaLabs/integrations/mcp/server.mjs"],
      "env": {}
    }
  }
}
```

If the repo is not next to `integrations/mcp` relative to the script, set:

```json
"env": {
  "PYTHIA_REPO_ROOT": "/absolute/path/to/pythiaLabs"
}
```

3. Restart Cursor (or reload MCP). Tools: **`pythia_evaluate`** (main), **`pythia_evaluate_agent_infra`** (alias), **`pythia_mcp_info`**.

## Tool: `pythia_evaluate`

Pass **`input_json`** — one JSON object (string) for `mix pythia.eval_json`.

### `gate` values

| `gate` | Second map | Matches showcase |
|--------|------------|------------------|
| `agent_infra_action` | `safety_context` | `examples/agent_infra_action_showcase.exs` |
| `banking_risk_action` | `governance` (or `governance_record`) | `examples/banking_ai_risk_showcase.exs` |
| `web3_treasury_action` | `governance` (or `governance_record`) | `examples/web3_treasury_action_showcase.exs` |

Use **string keys** and **ISO-8601** datetimes. For Web3, `amount` must be an integer (whole-number floats accepted).

### Example: agent infrastructure (accept path)

```json
{
  "gate": "agent_infra_action",
  "action": {
    "action_id": "infra_act_001",
    "action_type": "volume_delete",
    "actor_id": "agent_ops_7",
    "resource_id": "db_volume_primary",
    "resource_type": "database_volume",
    "target_environment": "production",
    "action_time": "2026-04-27T12:00:00Z",
    "decision_time": "2026-04-27T12:00:09Z"
  },
  "safety_context": {
    "credential_scope": "scoped_operator",
    "explicit_user_approval_present": true,
    "environment_scope_verified": true,
    "documentation_verified": true,
    "dry_run_completed": true,
    "backup_isolation": "off_target",
    "decision_time_knowledge_present": true
  }
}
```

### Example: banking risk

```json
{
  "gate": "banking_risk_action",
  "action": {
    "action_id": "bank_act_001",
    "action_type": "fraud_response",
    "operator_id": "risk_operator_7",
    "account_id": "acct_demo_01",
    "action_time": "2026-04-26T09:00:00Z",
    "decision_time": "2026-04-26T09:01:00Z"
  },
  "governance": {
    "authorization_valid_from": "2026-04-26T08:30:00Z",
    "authorization_valid_to": "2026-04-26T10:30:00Z",
    "authorization_recorded_at": "2026-04-26T08:45:00Z",
    "evidence_observed_at": "2026-04-26T08:55:00Z",
    "evidence_valid_until": "2026-04-26T09:10:00Z",
    "decision_time_knowledge_present": true,
    "operator_approval_present": true
  }
}
```

### Example: Web3 treasury

```json
{
  "gate": "web3_treasury_action",
  "action": {
    "action_id": "dao_act_001",
    "action_type": "treasury_transfer",
    "actor": "agent_alpha",
    "dao_id": "dao_pythia",
    "proposal_id": "prop_001",
    "amount": 10000,
    "asset": "USDC",
    "recipient": "0xRecipient",
    "required_permission": "treasury.transfer",
    "action_time": "2026-04-25T12:00:00Z",
    "decision_time": "2026-04-25T12:01:00Z"
  },
  "governance": {
    "proposal_id": "prop_001",
    "permission": "treasury.transfer",
    "quorum_met": true,
    "voting_closed_at": "2026-04-25T11:00:00Z",
    "timelock_until": "2026-04-25T11:30:00Z",
    "authorization_valid_from": "2026-04-25T11:30:00Z",
    "authorization_valid_to": "2026-04-25T13:00:00Z",
    "authorization_recorded_at": "2026-04-25T11:45:00Z",
    "transfer_expires_at": "2026-04-25T13:00:00Z"
  }
}
```

Response: **`outcome`** **`ALLOW`** or **`BLOCK`**, plus `export`, `evidence`, `stop_reason` (showcase semantics).

## CLI without MCP

```bash
echo '{"gate":"agent_infra_action", ... }' | mix pythia.eval_json
echo '{"gate":"banking_risk_action", ... }' | mix pythia.eval_json
mix pythia.eval_json --file proposal.json
```

## Limitations (MVP)

- Deterministic local showcases only; MCP is a bridge, not a remote API.
- Field decoding is strict JSON (no silent coercion beyond whole-number floats for `amount`).
