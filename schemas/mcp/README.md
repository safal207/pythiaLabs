# PythiaLabs MCP gate input schemas

Machine-readable contract for the JSON payload accepted by `mix pythia.eval_json`,
`bin/pythia eval`, and the MCP tool `pythia_evaluate`. One file per gate.

| Gate                    | Schema                                                                |
| ----------------------- | --------------------------------------------------------------------- |
| `agent_infra_action`    | [`agent_infra_action.schema.json`](agent_infra_action.schema.json)    |
| `banking_risk_action`   | [`banking_risk_action.schema.json`](banking_risk_action.schema.json)  |
| `web3_treasury_action`  | [`web3_treasury_action.schema.json`](web3_treasury_action.schema.json)|

Each schema is JSON Schema draft-07 with `additionalProperties: false`, so
unknown keys fail validation locally before they ever reach the gate.

## Using the schemas

These files describe the input shape only. The Elixir evaluator
(`Pythia.Mcp.JsonEvaluator`) is the source of truth for behaviour and still
produces structured per-field errors at runtime; the schemas are an editor /
client-side convenience so you can:

- get autocomplete and inline errors in editors that pick up JSON Schema (VS
  Code, IntelliJ, Neovim with `coc-json`, etc.) — point your editor settings at
  the relevant `$id` URL or local path;
- validate a payload before invoking the gate, with any draft-07 validator
  (`ajv`, `jsonschema`, `python-jsonschema`, …);
- generate skeleton requests in your own tooling.

## Quick CLI access

```bash
# List supported gates
./bin/pythia gates

# Print a schema for one gate (raw JSON)
./bin/pythia describe banking_risk_action
```

## Notes

- Both `governance` and `governance_record` are accepted as the second object
  for the banking and web3 gates; the schemas express this with `oneOf`.
- `amount` in `web3_treasury_action.action` is declared as an integer, but the
  Elixir evaluator also accepts a JSON number whose fractional part is zero
  (e.g. `10000.0`). Validators that strictly require `"type": "integer"` will
  reject the float form — keep payloads as integers if you want both layers
  to agree.
