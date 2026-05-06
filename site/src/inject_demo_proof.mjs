import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const repoDemoUrl =
  "https://github.com/safal207/pythiaLabs#paid-review-demo-recordable-in-30-seconds";

const css = `
.demo-proof-section {
  background: linear-gradient(180deg, rgba(124, 196, 255, 0.08) 0%, transparent 100%);
}

.demo-proof-section .demo-proof-intro {
  max-width: 820px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.demo-proof-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr);
  gap: 1.25rem;
  align-items: start;
  margin-top: 1.5rem;
}

.demo-terminal {
  overflow-x: auto;
  margin: 0;
  padding: 1.15rem 1.25rem;
  border: 1px solid rgba(124, 196, 255, 0.24);
  border-radius: var(--radius);
  background: rgba(2, 6, 12, 0.86);
  color: var(--text);
  font-family: var(--mono);
  font-size: 0.86rem;
  line-height: 1.55;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22);
}

.demo-terminal code {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.demo-proof-cards {
  display: grid;
  gap: 0.85rem;
}

.demo-proof-card {
  padding: 1rem 1.1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.demo-proof-card h3 {
  margin: 0 0 0.45rem;
  color: var(--text);
  font-size: 1rem;
  line-height: 1.35;
}

.demo-proof-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.93rem;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.demo-proof-cta {
  margin-top: 1.4rem;
}

.demo-proof-note {
  margin-top: 0.75rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

@media (max-width: 860px) {
  .demo-proof-layout {
    grid-template-columns: 1fr;
  }

  .demo-terminal {
    font-size: 0.78rem;
  }
}

@media (max-width: 600px) {
  .demo-terminal {
    padding: 0.9rem;
    font-size: 0.72rem;
    line-height: 1.5;
  }

  .demo-proof-card {
    padding: 0.9rem 1rem;
  }
}
`;

const copy = {
  en: {
    eyebrow: "Runnable proof",
    title: "See PythiaLabs evaluate risky AI-agent actions before execution",
    intro:
      "Run one command. Watch the real Web3 treasury engine evaluate four scenarios, verify SHA-256 evidence, and show a counterfactual decision flip.",
    terminal: `$ make demo\n# Windows: mix run examples/paid_review_demo.exs\n\nPythiaLabs — Paid Review Demo\n\n[1/4] Clean 25,000 USDC treasury transfer\n  decision    : ● ACCEPTED\n  evidence    : verified\n\n[2/4] Quorum threshold not reached\n  decision    : ● REJECTED\n  stop_reason : quorum_not_met\n  evidence    : verified\n\nCounterfactual\n  rejected → accepted\n\nResult: PASS`,
    cards: [
      {
        title: "Real engine",
        desc: "Uses Pythia.Showcase.Web3TreasuryAction.evaluate/2 — not a mock.",
      },
      {
        title: "Evidence verification",
        desc: "Each scenario produces SHA-256 evidence and verifies it with verify_evidence/1.",
      },
      {
        title: "Counterfactual control",
        desc: "Changing one evidence field flips the decision from rejected to accepted.",
      },
    ],
    runDemo: "Run the demo",
    paidReview: "Request paid review",
    note: "The demo is local, deterministic, and does not require external APIs. On Windows, run the Mix command directly if make is not installed.",
  },
  ru: {
    eyebrow: "Запускаемое доказательство",
    title: "Посмотрите, как PythiaLabs проверяет рискованные действия AI-агента до выполнения",
    intro:
      "Одна команда запускает реальный Web3 treasury engine: четыре сценария, SHA-256 evidence verification и counterfactual, где изменение одного evidence-поля меняет решение.",
    terminal: `$ make demo\n# Windows: mix run examples/paid_review_demo.exs\n\nPythiaLabs — Paid Review Demo\n\n[1/4] Clean 25,000 USDC treasury transfer\n  decision    : ● ACCEPTED\n  evidence    : verified\n\n[2/4] Quorum threshold not reached\n  decision    : ● REJECTED\n  stop_reason : quorum_not_met\n  evidence    : verified\n\nCounterfactual\n  rejected → accepted\n\nResult: PASS`,
    cards: [
      {
        title: "Реальный engine",
        desc: "Демо использует настоящий Web3 treasury evaluator — не mock.",
      },
      {
        title: "Evidence verification",
        desc: "Каждый сценарий создаёт SHA-256 evidence и проверяет его через verify_evidence/1.",
      },
      {
        title: "Counterfactual control",
        desc: "Изменение одного поля evidence переводит решение из rejected в accepted.",
      },
    ],
    runDemo: "Запустить демо",
    paidReview: "Заказать платный разбор",
    note: "Демо локальное, детерминированное и не требует внешних API. На Windows запускайте Mix-команду напрямую, если make не установлен.",
  },
  zh: {
    eyebrow: "Runnable proof",
    title: "See PythiaLabs evaluate risky AI-agent actions before execution",
    intro:
      "Run one command. Watch the real Web3 treasury engine evaluate four scenarios, verify SHA-256 evidence, and show a counterfactual decision flip.",
    terminal: `$ make demo\n# Windows: mix run examples/paid_review_demo.exs\n\nPythiaLabs — Paid Review Demo\n\n[1/4] Clean 25,000 USDC treasury transfer\n  decision    : ● ACCEPTED\n  evidence    : verified\n\n[2/4] Quorum threshold not reached\n  decision    : ● REJECTED\n  stop_reason : quorum_not_met\n  evidence    : verified\n\nCounterfactual\n  rejected → accepted\n\nResult: PASS`,
    cards: [
      {
        title: "Real engine",
        desc: "Uses Pythia.Showcase.Web3TreasuryAction.evaluate/2 — not a mock.",
      },
      {
        title: "Evidence verification",
        desc: "Each scenario produces SHA-256 evidence and verifies it with verify_evidence/1.",
      },
      {
        title: "Counterfactual control",
        desc: "Changing one evidence field flips the decision from rejected to accepted.",
      },
    ],
    runDemo: "Run the demo",
    paidReview: "Request paid review",
    note: "The demo is local, deterministic, and does not require external APIs. On Windows, run the Mix command directly if make is not installed.",
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
  const cards = t.cards
    .map(
      (card) => `
            <article class="demo-proof-card">
              <h3>${escapeHtml(card.title)}</h3>
              <p>${escapeHtml(card.desc)}</p>
            </article>`,
    )
    .join("");

  return `
      <section id="demo-proof" class="section section-alt demo-proof-section" aria-labelledby="demo-proof-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="demo-proof-title">${escapeHtml(t.title)}</h2>
          <p class="demo-proof-intro">${escapeHtml(t.intro)}</p>
          <div class="demo-proof-layout">
            <pre class="demo-terminal" aria-label="PythiaLabs demo terminal output"><code>${escapeHtml(t.terminal)}</code></pre>
            <div class="demo-proof-cards">${cards}
            </div>
          </div>
          <p class="demo-proof-cta">
            <a class="btn btn-primary" href="${repoDemoUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.runDemo)} →</a>
            <a class="btn btn-secondary" href="#paid-review">${escapeHtml(t.paidReview)} →</a>
          </p>
          <p class="demo-proof-note">${escapeHtml(t.note)}</p>
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
  if (html.includes(".demo-proof-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="demo-proof"')) return html;

  const section = renderSection(locale);
  const heroMatch = html.match(/<section class="hero">[\s\S]*?<\/section>/);
  if (heroMatch) {
    return html.replace(heroMatch[0], `${heroMatch[0]}\n${section}`);
  }

  const downloadsMarker = '      <section id="downloads"';
  if (html.includes(downloadsMarker)) {
    return html.replace(downloadsMarker, `${section}\n\n${downloadsMarker}`);
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

console.log(`Injected demo proof section into ${files.length} page(s).`);
