import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { transform } from "lightningcss";

import { localeOrder } from "./src/i18n.mjs";
import { renderPage } from "./src/render.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.join(here, "dist");
const cssPath = path.join(here, "src", "styles.css");

const cssSource = await readFile(cssPath);
const { code } = transform({
  filename: "styles.css",
  code: cssSource,
  minify: true,
  sourceMap: false,
  targets: { chrome: 100, firefox: 100, safari: 14 << 16 },
});
const minifiedCss = code.toString();

await rm(distDir, { recursive: true, force: true });
await mkdir(distDir, { recursive: true });

const year = new Date().getFullYear();
let total = 0;

for (const id of localeOrder) {
  const html = renderPage(id, year).replace("__INLINE_CSS__", minifiedCss);
  const outDir = id === "en" ? distDir : path.join(distDir, id);
  if (id !== "en") await mkdir(outDir, { recursive: true });
  const outPath = path.join(outDir, "index.html");
  await writeFile(outPath, html, "utf8");
  total += Buffer.byteLength(html);
  const rel = path.relative(distDir, outPath);
  process.stdout.write(`  ${rel.padEnd(20)} ${(Buffer.byteLength(html) / 1024).toFixed(2)} KB\n`);
}

process.stdout.write(`\nbuilt ${localeOrder.length} pages (${(total / 1024).toFixed(2)} KB total)\n`);
