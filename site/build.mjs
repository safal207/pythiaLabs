import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { transform } from "lightningcss";

import { localeOrder, validateLocales } from "./src/i18n.mjs";
import { renderOgSvg } from "./src/og.mjs";
import { renderPage } from "./src/render.mjs";
import { renderRobots, renderSitemap } from "./src/sitemap.mjs";
import { downloadAssets } from "./src/download_assets.mjs";

// lightningcss browser version encoding: major << 16 | minor << 8 | patch
const browserVersion = (major, minor = 0, patch = 0) => (major << 16) | (minor << 8) | patch;

const buildCssFixes = `
/* Build-time rendering fixes */
.step-list {
  list-style: none;
  padding-left: 0;
}

.downloads-section {
  background: linear-gradient(180deg, rgba(124, 196, 255, 0.06) 0%, transparent 100%);
}

.downloads-section .downloads-intro {
  max-width: 760px;
  color: var(--text-muted);
}

.downloads-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.download-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.4rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.download-card-kicker {
  margin: 0 0 0.55rem;
  color: var(--accent);
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.download-card h3 {
  margin: 0 0 0.65rem;
  font-size: 1.05rem;
  line-height: 1.35;
  color: var(--text);
}

.download-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.download-card .btn {
  align-self: flex-start;
}

.downloads-note {
  margin-top: 1.25rem;
  color: var(--text-muted);
  font-size: 0.92rem;
}
`;

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const downloadCopy = {
  en: {
    eyebrow: "Downloadable assets",
    title: "Give reviewers something concrete to inspect",
    intro:
      "Use these lightweight assets to evaluate whether your agent workflows need a pre-execution gate before code, infrastructure, money, or governance actions run.",
    note: "Markdown files are designed for quick review, copying into internal docs, or conversion to PDF.",
    button: "Download",
    cards: {
      "ai-agent-pre-execution-safety-checklist.md": {
        kicker: "Checklist",
        title: "AI Agent Pre-Execution Safety Checklist",
        desc: "A practical checklist for proposed actions, authorization, evidence freshness, blast radius, decision outcome, and replayability.",
      },
      "pythialabs-one-page-technical-brief.md": {
        kicker: "Brief",
        title: "PythiaLabs One-Page Technical Brief",
        desc: "A compact technical overview for CTOs, security reviewers, grant reviewers, and potential design partners.",
      },
      "pythialabs-pilot-partner-pack.md": {
        kicker: "Pilot",
        title: "Pilot Partner Pack",
        desc: "A focused pilot outline: who it is for, what inputs are needed, and what reviewable outputs a pilot can deliver.",
      },
      "sample-evidence-artifact.json": {
        kicker: "Artifact",
        title: "Sample Evidence Artifact JSON",
        desc: "A concrete ALLOW / BLOCK / ESCALATE-style artifact showing checks, stop reasons, decision-time evidence, and digest metadata.",
      },
    },
  },
  ru: {
    eyebrow: "Материалы для скачивания",
    title: "Дайте ревьюерам конкретный артефакт для проверки",
    intro:
      "Эти материалы помогают оценить, нужен ли вашим AI-agent workflow pre-execution gate до действий с кодом, инфраструктурой, деньгами или governance.",
    note: "Markdown-файлы удобно быстро читать, копировать во внутренние документы или конвертировать в PDF.",
    button: "Скачать",
    cards: {
      "ai-agent-pre-execution-safety-checklist.md": {
        kicker: "Checklist",
        title: "AI Agent Pre-Execution Safety Checklist",
        desc: "Практический чеклист: действие, авторизация, свежесть evidence, blast radius, решение и воспроизводимость.",
      },
      "pythialabs-one-page-technical-brief.md": {
        kicker: "Brief",
        title: "PythiaLabs One-Page Technical Brief",
        desc: "Короткий технический обзор для CTO, security-ревьюеров, грантовых комиссий и design partners.",
      },
      "pythialabs-pilot-partner-pack.md": {
        kicker: "Pilot",
        title: "Pilot Partner Pack",
        desc: "Описание пилота: кому подходит, какие входные данные нужны и какие проверяемые результаты можно получить.",
      },
      "sample-evidence-artifact.json": {
        kicker: "Artifact",
        title: "Sample Evidence Artifact JSON",
        desc: "Пример артефакта ALLOW / BLOCK / ESCALATE с checks, stop reasons, decision-time evidence и digest metadata.",
      },
    },
  },
  zh: {
    eyebrow: "可下载资料",
    title: "Give reviewers concrete artifacts to inspect",
    intro:
      "These lightweight assets help teams evaluate whether agent workflows need a pre-execution gate before code, infrastructure, money, or governance actions run.",
    note: "Markdown files are easy to review, copy into internal docs, or convert to PDF.",
    button: "Download",
    cards: {
      "ai-agent-pre-execution-safety-checklist.md": {
        kicker: "Checklist",
        title: "AI Agent Pre-Execution Safety Checklist",
        desc: "A practical checklist for proposed action, authorization, evidence freshness, blast radius, decision outcome, and replayability.",
      },
      "pythialabs-one-page-technical-brief.md": {
        kicker: "Brief",
        title: "PythiaLabs One-Page Technical Brief",
        desc: "A compact technical overview for CTOs, security reviewers, grant reviewers, and design partners.",
      },
      "pythialabs-pilot-partner-pack.md": {
        kicker: "Pilot",
        title: "Pilot Partner Pack",
        desc: "A focused pilot outline: who it is for, required inputs, and reviewable outputs.",
      },
      "sample-evidence-artifact.json": {
        kicker: "Artifact",
        title: "Sample Evidence Artifact JSON",
        desc: "A concrete ALLOW / BLOCK / ESCALATE-style artifact with checks, stop reasons, evidence, and digest metadata.",
      },
    },
  },
};

function downloadHref(currentId, filename) {
  const prefix = currentId === "en" ? "./" : "../";
  return `${prefix}downloads/${filename}`;
}

function renderDownloadsSection(currentId) {
  const copy = downloadCopy[currentId] ?? downloadCopy.en;
  const cards = downloadAssets
    .map((asset) => {
      const card = copy.cards[asset.filename] ?? downloadCopy.en.cards[asset.filename];
      const href = downloadHref(currentId, asset.filename);
      return `
          <article class="download-card">
            <div>
              <p class="download-card-kicker">${escapeHtml(card.kicker)}</p>
              <h3>${escapeHtml(card.title)}</h3>
              <p>${escapeHtml(card.desc)}</p>
            </div>
            <p><a class="btn btn-secondary" href="${escapeHtml(href)}" download>${escapeHtml(copy.button)} →</a></p>
          </article>`;
    })
    .join("");

  return `
      <section id="downloads" class="section section-alt downloads-section" aria-labelledby="downloads-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(copy.eyebrow)}</p>
          <h2 id="downloads-title">${escapeHtml(copy.title)}</h2>
          <p class="downloads-intro">${escapeHtml(copy.intro)}</p>
          <div class="downloads-grid">${cards}
          </div>
          <p class="downloads-note">${escapeHtml(copy.note)}</p>
        </div>
      </section>`;
}

function injectDownloadsSection(html, currentId) {
  const section = renderDownloadsSection(currentId);
  const contactMarker = "      <section id=\"contact\"";
  if (html.includes(contactMarker)) {
    return html.replace(contactMarker, `${section}\n\n${contactMarker}`);
  }
  return html.replace("\n    </main>", `\n${section}\n    </main>`);
}

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
    const html = injectDownloadsSection(
      renderPage(id, year, buildDate).replace("__INLINE_CSS__", minifiedCss),
      id,
    );
    const outDir = id === "en" ? distDir : path.join(distDir, id);
    if (id !== "en") await mkdir(outDir, { recursive: true });
    const outPath = path.join(outDir, "index.html");
    await writeFile(outPath, html, "utf8");
    const size = Buffer.byteLength(html);
    total += size;
    const rel = path.relative(distDir, outPath);
    process.stdout.write(`  ${rel.padEnd(20)} ${(size / 1024).toFixed(2)} KB\n`);
  }

  const downloadsDir = path.join(distDir, "downloads");
  await mkdir(downloadsDir, { recursive: true });
  for (const asset of downloadAssets) {
    await writeFile(path.join(downloadsDir, asset.filename), asset.content, "utf8");
  }

  await writeFile(path.join(distDir, "robots.txt"), renderRobots(), "utf8");
  await writeFile(path.join(distDir, "sitemap.xml"), renderSitemap(), "utf8");
  await writeFile(path.join(distDir, "og.svg"), renderOgSvg(), "utf8");

  process.stdout.write(
    `\nbuilt ${localeOrder.length} pages (${(total / 1024).toFixed(2)} KB total) + ${downloadAssets.length} downloads + robots.txt, sitemap.xml, og.svg\n`,
  );
}

main().catch((err) => {
  process.stderr.write(`build failed: ${err?.stack ?? err}\n`);
  process.exit(1);
});
