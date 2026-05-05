import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { transform } from "lightningcss";

import { localeOrder, validateLocales } from "./src/i18n.mjs";
import { renderOgSvg } from "./src/og.mjs";
import { renderPage } from "./src/render.mjs";
import { renderRobots, renderSitemap } from "./src/sitemap.mjs";

// lightningcss browser version encoding: major << 16 | minor << 8 | patch
const browserVersion = (major, minor = 0, patch = 0) => (major << 16) | (minor << 8) | patch;

const buildCssFixes = `
/* Build-time rendering fixes */
.step-list {
  list-style: none;
  padding-left: 0;
}
`;

async function main() {
  validateLocales();

  const here = path.dirname(fileURLToPath(import.meta.url));
  const distDir = path.join(here, "dist");
  const cssPath = path.join(here, "src", "styles.css");

  const cssSource = Buffer.concat([await readFile(cssPath), Buffer.from(buildCssFixes)]);
  const { code } = transform({
    filename: "styles.css",
    code: cssSource,
    minify: true,
    sourceMap: false,
    targets: {
      chrome: browserVersion(100),
      firefox: browserVersion(100),
      safari: browserVersion(14),
    },
  });
  const minifiedCss = code.toString();

  await rm(distDir, { recursive: true, force: true });
  await mkdir(distDir, { recursive: true });

  const year = new Date().getFullYear();
  const buildDate = new Date().toISOString();
  let total = 0;

  for (const id of localeOrder) {
    const html = renderPage(id, year, buildDate).replace("__INLINE_CSS__", minifiedCss);
    const outDir = id === "en" ? distDir : path.join(distDir, id);
    if (id !== "en") await mkdir(outDir, { recursive: true });
    const outPath = path.join(outDir, "index.html");
    await writeFile(outPath, html, "utf8");
    const size = Buffer.byteLength(html);
    total += size;
    const rel = path.relative(distDir, outPath);
    process.stdout.write(`  ${rel.padEnd(20)} ${(size / 1024).toFixed(2)} KB\n`);
  }

  await writeFile(path.join(distDir, "robots.txt"), renderRobots(), "utf8");
  await writeFile(path.join(distDir, "sitemap.xml"), renderSitemap(), "utf8");
  await writeFile(path.join(distDir, "og.svg"), renderOgSvg(), "utf8");

  process.stdout.write(
    `\nbuilt ${localeOrder.length} pages (${(total / 1024).toFixed(2)} KB total) + robots.txt, sitemap.xml, og.svg\n`,
  );
}

main().catch((err) => {
  process.stderr.write(`build failed: ${err?.stack ?? err}\n`);
  process.exit(1);
});
