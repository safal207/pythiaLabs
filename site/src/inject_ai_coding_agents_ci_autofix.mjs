import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");

const replacements = [
  {
    from: "AI coding agents",
    to: "AI Coding Agents / CI Autofix",
  },
  {
    from:
      "Before merge, patch, or production change, the agent leaves a verifiable trace and passes pre-execution validation.",
    to:
      "Before an autonomous coding agent fixes CI, opens a PR, updates dependencies, or touches deploy-adjacent workflows, PythiaLabs evaluates the proposed action and evidence first.",
  },
  {
    from: "AI coding agents",
    to: "AI Coding Agents / CI Autofix",
  },
  {
    from:
      "Перед merge, patch или production change агент оставляет проверяемый trace и проходит pre-execution validation.",
    to:
      "Перед тем как автономный coding agent чинит CI, открывает PR, обновляет зависимости или трогает deploy-adjacent workflow, PythiaLabs сначала оценивает proposed action и evidence.",
  },
];

async function htmlFiles(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await htmlFiles(full)));
    } else if (entry.isFile() && entry.name === "index.html") {
      files.push(full);
    }
  }
  return files;
}

function inject(html) {
  let updated = html;
  for (const { from, to } of replacements) {
    updated = updated.split(from).join(to);
  }
  return updated;
}

const files = await htmlFiles(distDir);

await Promise.all(
  files.map(async (file) => {
    const original = await readFile(file, "utf8");
    const updated = inject(original);
    await writeFile(file, updated);
  }),
);

console.log(`Injected AI coding agents / CI autofix landing copy into ${files.length} page(s).`);
