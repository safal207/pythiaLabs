#!/usr/bin/env node
/**
 * Smoke test for the PythiaLabs MCP stdio server.
 *
 * Spawns server.mjs once, drives it through JSON-RPC over stdio:
 *  - initialize
 *  - tools/list
 *  - pythia_list_gates
 *  - pythia_describe_gate (valid + invalid)
 *  - pythia_evaluate (against a fake `mix` on $PATH)
 *  - pythia_mcp_info
 *
 * No Elixir runtime needed: a tiny stub `mix` is dropped into a temp dir and
 * prepended to $PATH so the evaluate path can be exercised end-to-end.
 *
 * Exits 0 on success, 1 on any assertion failure.
 */

import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync, chmodSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");

let failures = 0;
function assert(cond, msg) {
  if (cond) {
    process.stdout.write(`  ok    ${msg}\n`);
  } else {
    failures += 1;
    process.stdout.write(`  FAIL  ${msg}\n`);
  }
}

function setupStubMix() {
  const dir = mkdtempSync(path.join(tmpdir(), "pythia-mcp-smoke-"));
  // Stub `mix` that echoes a deterministic JSON line regardless of stdin —
  // good enough for the evaluate-path round-trip.
  const stub = `#!/usr/bin/env bash
cat >/dev/null
echo '{"ok":true,"outcome":"ALLOW","status":"accepted","stop_reason":null}'
`;
  const stubPath = path.join(dir, "mix");
  writeFileSync(stubPath, stub);
  chmodSync(stubPath, 0o755);
  return dir;
}

function spawnServer(envOverrides) {
  const child = spawn(process.execPath, [path.join(__dirname, "server.mjs")], {
    cwd: repoRoot,
    stdio: ["pipe", "pipe", "pipe"],
    env: { ...process.env, ...envOverrides },
  });
  child.stderr.on("data", (c) => process.stderr.write(`[server] ${c}`));
  return child;
}

function rpcDriver(child) {
  // Buffer stdout into newline-delimited JSON messages and resolve pending
  // requests by id. The server emits one JSON object per line.
  const pending = new Map();
  let buf = "";
  child.stdout.on("data", (chunk) => {
    buf += chunk.toString();
    let idx;
    while ((idx = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, idx).trim();
      buf = buf.slice(idx + 1);
      if (!line) continue;
      let msg;
      try {
        msg = JSON.parse(line);
      } catch {
        continue;
      }
      const r = pending.get(msg.id);
      if (r) {
        pending.delete(msg.id);
        r(msg);
      }
    }
  });

  let nextId = 1;
  function call(method, params) {
    const id = nextId++;
    const req = { jsonrpc: "2.0", id, method, params };
    return new Promise((resolve) => {
      pending.set(id, resolve);
      child.stdin.write(JSON.stringify(req) + "\n");
    });
  }
  return { call };
}

async function main() {
  const stubDir = setupStubMix();
  const child = spawnServer({
    PATH: `${stubDir}:${process.env.PATH ?? ""}`,
    PYTHIA_REPO_ROOT: repoRoot,
  });
  const { call } = rpcDriver(child);

  process.stdout.write("MCP smoke test:\n");

  const init = await call("initialize", {});
  assert(init?.result?.serverInfo?.name === "pythialabs", "initialize returns server name");
  assert(typeof init?.result?.serverInfo?.version === "string", "initialize returns version");

  const tools = await call("tools/list", {});
  const names = (tools?.result?.tools ?? []).map((t) => t.name);
  assert(names.includes("pythia_evaluate"), "tools/list contains pythia_evaluate");
  assert(names.includes("pythia_describe_gate"), "tools/list contains pythia_describe_gate");
  assert(names.includes("pythia_list_gates"), "tools/list contains pythia_list_gates");
  assert(names.includes("pythia_mcp_info"), "tools/list contains pythia_mcp_info");

  const list = await call("tools/call", { name: "pythia_list_gates", arguments: {} });
  const listed = list?.result?.structuredContent?.gates ?? [];
  assert(
    listed.length === 3 &&
      listed.includes("agent_infra_action") &&
      listed.includes("banking_risk_action") &&
      listed.includes("web3_treasury_action"),
    "pythia_list_gates returns the three gate ids",
  );

  const describe = await call("tools/call", {
    name: "pythia_describe_gate",
    arguments: { gate: "banking_risk_action" },
  });
  const schema = describe?.result?.structuredContent?.schema;
  assert(schema?.properties?.gate?.const === "banking_risk_action", "describe_gate returns matching schema");
  assert(Array.isArray(schema?.properties?.action?.required), "schema has action.required list");

  const describeBad = await call("tools/call", {
    name: "pythia_describe_gate",
    arguments: { gate: "totally_unknown_gate" },
  });
  assert(describeBad?.error?.code === -32602, "describe_gate rejects unknown gate with -32602");

  const evalCall = await call("tools/call", {
    name: "pythia_evaluate",
    arguments: { input_json: '{"gate":"agent_infra_action"}' },
  });
  const evalStruct = evalCall?.result?.structuredContent;
  assert(evalStruct?.exitCode === 0, "evaluate exits 0 against stub mix");
  assert(typeof evalStruct?.stdout === "string" && evalStruct.stdout.includes("ALLOW"), "evaluate forwards stub stdout");

  const info = await call("tools/call", { name: "pythia_mcp_info", arguments: {} });
  const infoText = info?.result?.content?.[0]?.text ?? "";
  assert(infoText.includes("supportedGates"), "pythia_mcp_info reports supportedGates");
  assert(infoText.includes("schemasDir"), "pythia_mcp_info reports schemasDir");

  child.stdin.end();
  child.kill();

  if (failures > 0) {
    process.stdout.write(`\nFAILED: ${failures} assertion(s) failed.\n`);
    process.exit(1);
  }
  process.stdout.write("\nOK: all assertions passed.\n");
  process.exit(0);
}

main().catch((e) => {
  process.stderr.write(`smoke test crashed: ${e?.stack ?? e}\n`);
  process.exit(1);
});
