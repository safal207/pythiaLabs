import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const roadmapUrl = "https://github.com/safal207/pythiaLabs/blob/main/docs/research_roadmap.md";
const manifundUrl =
  "https://manifund.org/projects/deterministic-oversight-for-agent-traces--ltp--cml";

const css = `
.research-track-section {
  background: linear-gradient(180deg, rgba(210, 153, 34, 0.055) 0%, transparent 100%);
}

.research-track-section .research-track-intro {
  max-width: 840px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.research-track-panel {
  margin-top: 1.35rem;
  padding: 1.25rem 1.4rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.research-track-formula {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.85rem;
  margin: 1rem 0 0;
}

.research-track-formula-card {
  padding: 0.95rem 1rem;
  border: 1px solid rgba(124, 196, 255, 0.2);
  border-radius: var(--radius);
  background: rgba(124, 196, 255, 0.06);
}

.research-track-formula-card strong {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--text);
}

.research-track-formula-card span {
  color: var(--text-muted);
  font-size: 0.93rem;
  line-height: 1.45;
}

.research-track-question {
  margin: 1rem 0 0;
  padding-left: 1rem;
  border-left: 3px solid var(--escalate);
  color: var(--text);
  font-size: 1rem;
}

.research-track-cta {
  margin-top: 1.25rem;
}

.research-track-note {
  margin-top: 0.7rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
`;

const copy = {
  en: {
    eyebrow: "Related research track",
    title: "PythiaLabs is the gate. LTP + CML are the research foundation.",
    intro:
      "PythiaLabs is the runnable pre-execution gate: it evaluates risky AI-agent actions before tools run. It is connected to a broader research roadmap on deterministic oversight for agent traces: LTP + CML.",
    productLabel: "Product surface",
    productText: "proposed action → evidence → ALLOW / BLOCK / ESCALATE",
    researchLabel: "Research question",
    researchText: "where did the failure enter the agent’s decision trace?",
    question:
      "The landing page stays focused on runnable proof and paid reviews; the research track gives grantmakers and technical reviewers the deeper trace-oversight story.",
    demo: "Run PythiaLabs demo",
    paidReview: "Request paid review",
    roadmap: "Read research roadmap",
    manifund: "View Manifund proposal",
    note: "Manifund is linked as related research funding, not as the primary conversion path.",
  },
  ru: {
    eyebrow: "Связанное research-направление",
    title: "PythiaLabs — это gate. LTP + CML — исследовательский фундамент.",
    intro:
      "PythiaLabs — запускаемый pre-execution gate: он проверяет рискованные действия AI-агента до запуска tools. Он связан с более широкой research roadmap по deterministic oversight для agent traces: LTP + CML.",
    productLabel: "Продуктовая поверхность",
    productText: "proposed action → evidence → ALLOW / BLOCK / ESCALATE",
    researchLabel: "Исследовательский вопрос",
    researchText: "где именно failure вошёл в decision trace агента?",
    question:
      "Лендинг остаётся сфокусированным на runnable proof и paid reviews; research track даёт грантодателям и техническим ревьюерам более глубокую историю trace-oversight.",
    demo: "Запустить демо PythiaLabs",
    paidReview: "Заказать платный разбор",
    roadmap: "Открыть research roadmap",
    manifund: "Посмотреть Manifund proposal",
    note: "Manifund указан как связанное research funding направление, а не как главный CTA лендинга.",
  },
  zh: {
    eyebrow: "Related research track",
    title: "PythiaLabs is the gate. LTP + CML are the research foundation.",
    intro:
      "PythiaLabs is the runnable pre-execution gate: it evaluates risky AI-agent actions before tools run. It is connected to a broader research roadmap on deterministic oversight for agent traces: LTP + CML.",
    productLabel: "Product surface",
    productText: "proposed action → evidence → ALLOW / BLOCK / ESCALATE",
    researchLabel: "Research question",
    researchText: "where did the failure enter the agent’s decision trace?",
    question:
      "The landing page stays focused on runnable proof and paid reviews; the research track gives grantmakers and technical reviewers the deeper trace-oversight story.",
    demo: "Run PythiaLabs demo",
    paidReview: "Request paid review",
    roadmap: "Read research roadmap",
    manifund: "View Manifund proposal",
    note: "Manifund is linked as related research funding, not as the primary conversion path.",
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

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;

  return `
      <section id="research-track" class="section research-track-section" aria-labelledby="research-track-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="research-track-title">${escapeHtml(t.title)}</h2>
          <p class="research-track-intro">${escapeHtml(t.intro)}</p>
          <div class="research-track-panel">
            <div class="research-track-formula">
              <div class="research-track-formula-card">
                <strong>${escapeHtml(t.productLabel)}</strong>
                <span>${escapeHtml(t.productText)}</span>
              </div>
              <div class="research-track-formula-card">
                <strong>${escapeHtml(t.researchLabel)}</strong>
                <span>${escapeHtml(t.researchText)}</span>
              </div>
            </div>
            <p class="research-track-question">${escapeHtml(t.question)}</p>
          </div>
          <p class="research-track-cta">
            <a class="btn btn-primary" href="#demo-proof">${escapeHtml(t.demo)} →</a>
            <a class="btn btn-secondary" href="#paid-review">${escapeHtml(t.paidReview)} →</a>
            <a class="btn btn-ghost" href="${roadmapUrl}" rel="noopener noreferrer">${escapeHtml(t.roadmap)} →</a>
            <a class="btn btn-ghost" href="${manifundUrl}" rel="noopener noreferrer">${escapeHtml(t.manifund)} →</a>
          </p>
          <p class="research-track-note">${escapeHtml(t.note)}</p>
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
  if (html.includes(".research-track-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="research-track"')) return html;

  const section = renderSection(locale);
  const supportMarker = '      <section id="support"';
  if (html.includes(supportMarker)) {
    return html.replace(supportMarker, `${section}\n\n${supportMarker}`);
  }

  const paidReviewMarker = '      <section id="paid-review"';
  if (html.includes(paidReviewMarker)) {
    return html.replace(paidReviewMarker, `${section}\n\n${paidReviewMarker}`);
  }

  return html.replace("\n    </main>", `\n${section}\n    </main>`);
}

const files = await htmlFiles(distDir);

await Promise.all(
  files.map(async (file) => {
    const locale = localeFor(file);
    const original = await readFile(file, "utf8");
    const updated = injectSection(injectCss(original), locale);
    await writeFile(file, updated);
  }),
);

console.log(`Injected research track section into ${files.length} page(s).`);
