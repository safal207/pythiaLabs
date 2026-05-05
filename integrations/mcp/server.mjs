#!/usr/bin/env node
/**
 * Minimal MCP server (stdio) — forwards tool calls to `mix pythia.eval_json`.
 *
 * Env:
 *   PYTHIA_REPO_ROOT — absolute path to PythiaLabs clone (default: parent of integrations/mcp)
 */

import { spawn } from "node:child_process";
import * as readline from "node:readline";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const defaultRoot = path.resolve(__dirname, "..", "..");
const repoRoot = process.env.PYTHIA_REPO_ROOT
  ? path.resolve(process.env.PYTHIA_REPO_ROOT)
  : defaultRoot;

const SERVER_INFO = {
  name: "pythialabs",
  version: "0.1.0",
};

const TOOLS = [
  {
    name: "pythia_evaluate_agent_infra",
    description:
      "Run the deterministic PythiaLabs agent infrastructure gate (ALLOW/BLOCK style outcome). Input: JSON with gate, action, safety_context per repo docs.",
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
    name: "pythia_mcp_info",
    description: "Return PythiaLabs repo root used by this MCP server and supported tools.",
    inputSchema: { type: "object", properties: {} },
  },
];

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

    if (name === "pythia_evaluate_agent_infra") {
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
