#!/usr/bin/env node
/**
 * Minimal MCP server (stdio) — forwards tool calls to `mix pythia.eval_json`.
 *
 * Env:
 *   PYTHIA_REPO_ROOT — absolute path to PythiaLabs clone (default: parent of integrations/mcp)
 */

import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";
import * as readline from "node:readline";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaultRoot = path.resolve(__dirname, "..", "..");
const repoRoot = process.env.PYTHIA_REPO_ROOT
  ? path.resolve(process.env.PYTHIA_REPO_ROOT)
  : defaultRoot;

const SUPPORTED_GATES = [
  "agent_infra_action",
  "banking_risk_action",
  "web3_treasury_action",
];

const SERVER_INFO = {
  name: "pythialabs",
  version: "0.3.0",
};

const TOOLS = [
  {
    name: "pythia_evaluate",
    description:
      "Run a deterministic PythiaLabs gate (ALLOW/BLOCK). input_json: {\"gate\":\"agent_infra_action\"|\"banking_risk_action\"|\"web3_treasury_action\", \"action\":{...}, plus safety_context or governance}. See integrations/mcp/README.md.",
    inputSchema: {
      type: "object",
      properties: {
        input_json: {
          type: "string",
          description:
            'JSON string for mix pythia.eval_json (gate + action + safety_context or governance)',
        },
      },
      required: ["input_json"],
    },
  },
  {
    name: "pythia_evaluate_agent_infra",
    description:
      "Alias: same as pythia_evaluate — supports all gates via input_json; name kept for backward compatibility.",
    inputSchema: {
      type: "object",
      properties: {
        input_json: {
          type: "string",
          description:
            'Full JSON body for mix pythia.eval_json, e.g. {"gate":"agent_infra_action","action":{...},"safety_context":{...}}',
        },
      },
      required: ["input_json"],
    },
  },
  {
    name: "pythia_describe_gate",
    description:
      "Return the JSON Schema (draft-07) for one PythiaLabs gate so the agent can compose a valid input_json before calling pythia_evaluate. Schema files live in schemas/mcp/.",
    inputSchema: {
      type: "object",
      properties: {
        gate: {
          type: "string",
          enum: SUPPORTED_GATES,
          description: "Gate id to describe.",
        },
      },
      required: ["gate"],
    },
  },
  {
    name: "pythia_list_gates",
    description: "List supported gate ids served by this MCP server.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "pythia_mcp_info",
    description: "Return PythiaLabs repo root used by this MCP server and supported tools.",
    inputSchema: { type: "object", properties: {} },
  },
];

async function loadGateSchema(gate) {
  const file = path.join(repoRoot, "schemas", "mcp", `${gate}.schema.json`);
  const raw = await readFile(file, "utf8");
  return { file, schema: JSON.parse(raw) };
}

let messageId = 0;
function nextId() {
  messageId += 1;
  return messageId;
}

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + "\n");
}

function runMixEvalJson(jsonBody) {
  return new Promise((resolve, reject) => {
    const child = spawn("mix", ["pythia.eval_json"], {
      cwd: repoRoot,
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env },
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (c) => (out += c));
    child.stderr.on("data", (c) => (err += c));
    child.on("error", reject);
    child.stdin.write(jsonBody);
    child.stdin.end();
    child.on("close", (code) => {
      resolve({ code, out: out.trim(), err: err.trim() });
    });
  });
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

for await (const line of rl) {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    continue;
  }

  const { method, params, id } = msg;

  if (method === "initialize") {
    send({
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: SERVER_INFO,
      },
    });
    continue;
  }

  if (method === "notifications/initialized" || method === "initialized") {
    continue;
  }

  if (method === "tools/list") {
    send({ jsonrpc: "2.0", id, result: { tools: TOOLS } });
    continue;
  }

  if (method === "tools/call") {
    const name = params?.name;
    const args = params?.arguments ?? {};

    if (name === "pythia_list_gates") {
      send({
        jsonrpc: "2.0",
        id,
        result: {
          content: [{ type: "text", text: JSON.stringify(SUPPORTED_GATES, null, 2) }],
          structuredContent: { gates: SUPPORTED_GATES },
        },
      });
      continue;
    }

    if (name === "pythia_describe_gate") {
      const gate = args.gate;
      if (!SUPPORTED_GATES.includes(gate)) {
        send({
          jsonrpc: "2.0",
          id,
          error: {
            code: -32602,
            message: `unknown gate: ${gate} (supported: ${SUPPORTED_GATES.join(", ")})`,
          },
        });
        continue;
      }

      try {
        const { file, schema } = await loadGateSchema(gate);
        send({
          jsonrpc: "2.0",
          id,
          result: {
            content: [{ type: "text", text: JSON.stringify(schema, null, 2) }],
            structuredContent: { gate, file: path.relative(repoRoot, file), schema },
          },
        });
      } catch (e) {
        send({
          jsonrpc: "2.0",
          id,
          error: { code: -32603, message: `failed to load schema for ${gate}: ${e?.message ?? e}` },
        });
      }
      continue;
    }

    if (name === "pythia_mcp_info") {
      send({
        jsonrpc: "2.0",
        id,
        result: {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  server: SERVER_INFO.name,
                  version: SERVER_INFO.version,
                  repoRoot,
                  mixTask: "mix pythia.eval_json",
                  supportedGates: SUPPORTED_GATES,
                  schemasDir: "schemas/mcp",
                  docs: "integrations/mcp/README.md",
                },
                null,
                2,
              ),
            },
          ],
        },
      });
      continue;
    }

    if (name === "pythia_evaluate" || name === "pythia_evaluate_agent_infra") {
      const input = args.input_json;
      if (typeof input !== "string" || !input.trim()) {
        send({
          jsonrpc: "2.0",
          id,
          error: { code: -32602, message: "input_json must be a non-empty string" },
        });
        continue;
      }

      try {
        const { code, out, err } = await runMixEvalJson(input);
        const payload = {
          exitCode: code,
          stdout: out,
          stderr: err || undefined,
        };
        let pretty = out;
        try {
          pretty = JSON.stringify(JSON.parse(out), null, 2);
        } catch {
          /* keep raw */
        }
        send({
          jsonrpc: "2.0",
          id,
          result: {
            content: [{ type: "text", text: pretty }],
            structuredContent: payload,
            isError: code !== 0,
          },
        });
      } catch (e) {
        send({
          jsonrpc: "2.0",
          id,
          error: {
            code: -32603,
            message: e?.message ?? String(e),
          },
        });
      }
      continue;
    }

    send({
      jsonrpc: "2.0",
      id,
      error: { code: -32601, message: `Unknown tool: ${name}` },
    });
    continue;
  }

  if (method === "ping") {
    send({ jsonrpc: "2.0", id, result: {} });
    continue;
  }

  if (id !== undefined && id !== null) {
    send({
      jsonrpc: "2.0",
      id,
      error: { code: -32601, message: `Method not found: ${method}` },
    });
  }
}
