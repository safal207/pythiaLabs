import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { siteConfig } from "./config.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");

const css = `
.hero-icp-line {
  max-width: 760px;
  margin: 0 0 0.85rem;
  color: var(--accent);
  font-size: 1.03rem;
  font-weight: 650;
  line-height: 1.45;
}

.hero-proof-section {
  padding: 2.35rem 0;
  border-bottom: 1px solid var(--border);
  background: var(--bg-alt);
}

.hero-proof-header {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 1.15rem;
}

.hero-proof-header h2 {
  margin: 0;
  font-size: clamp(1.35rem, 2.5vw, 1.75rem);
}

.hero-proof-header p {
  margin: 0;
  max-width: 760px;
  color: var(--text-muted);
}

.hero-proof-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.hero-proof-card {
  padding: 0.9rem 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.hero-proof-card strong {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--text);
  font-size: 0.95rem;
  line-height: 1.35;
}

.hero-proof-card span {
  display: block;
  color: var(--text-muted);
  font-size: 0.86rem;
  line-height: 1.4;
}

.hero-proof-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem 1rem;
  align-items: center;
  margin: 1.15rem 0 0;
}

.hero-proof-metric {
  display: inline-flex;
  gap: 0.35rem;
  align-items: baseline;
  color: var(--text-muted);
  font-size: 0.86rem;
}

.hero-proof-metric strong {
  color: var(--accent-strong);
  font-family: var(--mono);
  font-size: 1rem;
}

.hero-proof-badges {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  margin: 1rem 0 0;
  align-items: center;
}

@media (max-width: 600px) {
  .hero-icp-line {
    font-size: 0.98rem;
  }

  .hero-proof-section {
    padding: 2rem 0;
  }
}
`;

const copy = {
  en: {
    eyebrow: "Pre-execution safety gate · Open-source · Apache-2.0",
    headline: "Stop risky AI-agent actions before they execute.",
    icp: "For teams deploying AI agents that can change code, infrastructure, money, or governance workflows.",
    subtitle:
      "PythiaLabs evaluates proposed agent actions and returns ALLOW / BLOCK / ESCALATE with reviewer-facing evidence.",
    runDemo: "Run demo",
    paidReview: "Request paid review",
    github: "View GitHub",
    proofTitle: "Current proof",
    proofIntro:
      "The first screen stays focused on the user and the action. The proof signals are still here — just below the fold where reviewers can inspect them.",
    cards: [
      ["Open-source MVP", "Apache-2.0 and self-hostable."],
      ["Real-engine demo", "Web3 treasury action gate, not a mock."],
      ["SHA-256 evidence", "Evidence records verified via digest."],
      ["Deterministic decisions", "ALLOW / BLOCK / ESCALATE before tools run."],
      ["Research roadmap", "LTP + CML for trace oversight depth."],
    ],
    metrics: {
      showcases: "deterministic local showcases",
      tests: "Elixir test files",
      llm: "LLM calls in the gate",
    },
  },
  ru: {
    eyebrow: "Pre-execution safety gate · Open-source · Apache-2.0",
    headline: "Останавливайте рискованные действия AI-агентов до выполнения.",
    icp: "Для команд, чьи AI-агенты могут менять код, инфраструктуру, деньги или governance workflows.",
    subtitle:
      "PythiaLabs оценивает proposed agent actions и возвращает ALLOW / BLOCK / ESCALATE с evidence для ревьюеров.",
    runDemo: "Запустить демо",
    paidReview: "Заказать paid review",
    github: "Открыть GitHub",
    proofTitle: "Текущие proof-сигналы",
    proofIntro:
      "Первый экран теперь фокусируется на пользователе и действии. Доказательные сигналы остаются рядом — ниже первого экрана, где их удобно проверить.",
    cards: [
      ["Open-source MVP", "Apache-2.0 и self-hostable."],
      ["Real-engine demo", "Web3 treasury action gate, не mock."],
      ["SHA-256 evidence", "Evidence records проверяются через digest."],
      ["Deterministic decisions", "ALLOW / BLOCK / ESCALATE до запуска tools."],
      ["Research roadmap", "LTP + CML для trace oversight depth."],
    ],
    metrics: {
      showcases: "детерминированных local showcases",
      tests: "файлов Elixir tests",
      llm: "LLM calls in the gate",
    },
  },
  zh: {
    eyebrow: "Pre-execution safety gate · Open-source · Apache-2.0",
    headline: "Stop risky AI-agent actions before they execute.",
    icp: "For teams deploying AI agents that can change code, infrastructure, money, or governance workflows.",
    subtitle:
      "PythiaLabs evaluates proposed agent actions and returns ALLOW / BLOCK / ESCALATE with reviewer-facing evidence.",
    runDemo: "Run demo",
    paidReview: "Request paid review",
    github: "View GitHub",
    proofTitle: "Current proof",
    proofIntro:
      "The first screen stays focused on the user and the action. The proof signals are still here — just below the fold where reviewers can inspect them.",
    cards: [
      ["Open-source MVP", "Apache-2.0 and self-hostable."],
      ["Real-engine demo", "Web3 treasury action gate, not a mock."],
      ["SHA-256 evidence", "Evidence records verified via digest."],
      ["Deterministic decisions", "ALLOW / BLOCK / ESCALATE before tools run."],
      ["Research roadmap", "LTP + CML for trace oversight depth."],
    ],
    metrics: {
      showcases: "deterministic local showcases",
      tests: "Elixir test files",
      llm: "LLM calls in the gate",
    },
  },
};

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

function localeFor(filePath) {
  const normalized = filePath.split(path.sep).join("/");
  if (normalized.endsWith("/ru/index.html")) return "ru";
  if (normalized.endsWith("/zh/index.html")) return "zh";
  return "en";
}

function badge(src, alt, href, width) {
  return `<a href="${href}" class="badge-link" target="_blank" rel="noopener noreferrer"><img src="${src}" alt="${escapeHtml(alt)}" loading="lazy" decoding="async" width="${width}" height="20" /></a>`;
}

function renderHero(locale) {
  const t = copy[locale] ?? copy.en;

  return `      <section class="hero">
        <div class="container">
          <p class="eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h1 class="hero-headline">${escapeHtml(t.headline)}</h1>
          <p class="hero-icp-line">${escapeHtml(t.icp)}</p>
          <p class="hero-subtitle">${escapeHtml(t.subtitle)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="#demo-proof">${escapeHtml(t.runDemo)}</a>
            <a class="btn btn-secondary" href="#paid-review">${escapeHtml(t.paidReview)}</a>
            <a class="btn btn-ghost" href="${siteConfig.repoUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.github)}</a>
          </div>
        </div>
      </section>`;
}

function renderProof(locale) {
  const t = copy[locale] ?? copy.en;
  const cards = t.cards
    .map(
      ([title, desc]) => `
            <article class="hero-proof-card"><strong>${escapeHtml(title)}</strong><span>${escapeHtml(desc)}</span></article>`,
    )
    .join("");

  const badges = [
    badge(
      `https://img.shields.io/github/stars/${siteConfig.repoSlug}?style=flat-square&label=stars&color=0b0d10`,
      "GitHub stars",
      `${siteConfig.repoUrl}/stargazers`,
      90,
    ),
    badge(
      `https://img.shields.io/github/license/${siteConfig.repoSlug}?style=flat-square&color=0b0d10`,
      "License",
      `${siteConfig.repoUrl}/blob/main/LICENSE`,
      100,
    ),
    badge(
      "https://img.shields.io/badge/MCP-ready-7cc4ff?style=flat-square&color=0b0d10",
      "MCP-ready",
      `${siteConfig.repoUrl}/blob/main/integrations/mcp/README.md`,
      92,
    ),
  ].join("");

  return `
      <section id="current-proof" class="hero-proof-section" aria-labelledby="current-proof-title">
        <div class="container">
          <div class="hero-proof-header">
            <h2 id="current-proof-title">${escapeHtml(t.proofTitle)}</h2>
            <p>${escapeHtml(t.proofIntro)}</p>
          </div>
          <div class="hero-proof-grid">${cards}
          </div>
          <div class="hero-proof-metrics" aria-label="Repository proof signals">
            <span class="hero-proof-metric"><strong>${escapeHtml(siteConfig.showcaseScriptCount)}</strong>${escapeHtml(t.metrics.showcases)}</span>
            <span class="hero-proof-metric"><strong>${escapeHtml(siteConfig.testFileCount)}</strong>${escapeHtml(t.metrics.tests)}</span>
            <span class="hero-proof-metric"><strong>0</strong>${escapeHtml(t.metrics.llm)}</span>
          </div>
          <p class="hero-proof-badges">${badges}</p>
        </div>
      </section>`;
}

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

function injectCss(html) {
  if (html.includes(".hero-icp-line")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectHero(html, locale) {
  const heroMatch = html.match(/      <section class="hero">[\s\S]*?\n      <\/section>/);
  if (!heroMatch) return html;
  return html.replace(heroMatch[0], renderHero(locale));
}

function injectProof(html, locale) {
  if (html.includes('id="current-proof"')) return html;
  const proof = renderProof(locale);
  const demoMarker = '      <section id="demo-proof"';
  if (html.includes(demoMarker)) {
    return html.replace(demoMarker, `${proof}\n\n${demoMarker}`);
  }

  const heroMatch = html.match(/      <section class="hero">[\s\S]*?\n      <\/section>/);
  if (heroMatch) {
    return html.replace(heroMatch[0], `${heroMatch[0]}\n${proof}`);
  }

  return html.replace("\n    </main>", `\n${proof}\n    </main>`);
}

const files = await htmlFiles(distDir);

await Promise.all(
  files.map(async (file) => {
    const locale = localeFor(file);
    const original = await readFile(file, "utf8");
    const updated = injectProof(injectHero(injectCss(original), locale), locale);
    await writeFile(file, updated);
  }),
);

console.log(`Injected clarified hero into ${files.length} page(s).`);
