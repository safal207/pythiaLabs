# PythiaLabs MCP (Cursor & compatible hosts)

stdio MCP server that exposes **`pythia_evaluate_agent_infra`** — it shells to `mix pythia.eval_json` in this repository so the deterministic infrastructure gate runs locally (no hosted service).

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

3. Restart Cursor (or reload MCP). You should see tools **`pythia_evaluate_agent_infra`** and **`pythia_mcp_info`**.

## Tool: `pythia_evaluate_agent_infra`

Pass **`input_json`** — a single JSON string matching the schema consumed by `mix pythia.eval_json`:

- **`gate`**: `"agent_infra_action"`
- **`action`**: infrastructure action map (string keys), including ISO-8601 `action_time` and `decision_time`
- **`safety_context`**: safety context map (booleans + string fields as in `examples/agent_infra_action_showcase.exs`)

### Example `input_json` (accept path from showcase)

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

Response maps **`outcome`** to **`ALLOW`** when the gate accepts, **`BLOCK`** when it rejects (deterministic showcase semantics). See stdout JSON for `export`, `evidence`, and `stop_reason`.

## CLI without MCP

```bash
echo '{"gate":"agent_infra_action", ... }' | mix pythia.eval_json
# or
mix pythia.eval_json --file proposal.json
```

## Limitations (MVP)

- One gate id: **`agent_infra_action`**. Banking / Web3 showcases can be wired the same way later.
- Requires local Mix + compiled project; MCP is a bridge, not a remote API.
