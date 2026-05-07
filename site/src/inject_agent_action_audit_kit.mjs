import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const email = "safal0645@gmail.com";
const docsUrl = "https://github.com/safal207/pythiaLabs/blob/main/docs/AGENT_ACTION_AUDIT_KIT.md";

const css = `
.agent-audit-kit-section {
  background:
    radial-gradient(circle at top left, rgba(124, 196, 255, 0.12), transparent 34rem),
    linear-gradient(180deg, rgba(124, 196, 255, 0.06) 0%, transparent 100%);
}

.agent-audit-kit-intro {
  max-width: 820px;
  color: var(--text-muted);
  font-size: 1.04rem;
}

.agent-audit-kit-punchline {
  max-width: 820px;
  margin: 1rem 0 0;
  padding: 0.95rem 1.05rem;
  border-left: 3px solid var(--accent-strong);
  border-radius: 0 var(--radius) var(--radius) 0;
  background: rgba(124, 196, 255, 0.08);
  color: var(--text);
  font-size: 1rem;
}

.agent-audit-kit-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
  gap: 1.25rem;
  align-items: stretch;
  margin-top: 1.5rem;
}

.agent-audit-kit-card,
.agent-audit-kit-chain {
  border: 1px solid rgba(124, 196, 255, 0.22);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 1.25rem 1.35rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.16);
}

.agent-audit-kit-card h3,
.agent-audit-kit-chain h3 {
  margin: 0 0 0.65rem;
  color: var(--text);
  font-size: 1.08rem;
  line-height: 1.35;
}

.agent-audit-kit-card p,
.agent-audit-kit-chain p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.agent-audit-kit-list {
  display: grid;
  gap: 0.65rem;
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
}

.agent-audit-kit-list li {
  position: relative;
  padding-left: 1.35rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.agent-audit-kit-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--allow);
  font-weight: 800;
}

.agent-audit-kit-chain-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 1rem;
}

.agent-audit-kit-step {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.58rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(22, 27, 34, 0.62);
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 0.76rem;
  line-height: 1.3;
}

.agent-audit-kit-step strong {
  color: var(--text);
  font-weight: 700;
}

.agent-audit-kit-cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.35rem;
}

.agent-audit-kit-note {
  max-width: 820px;
  margin-top: 0.85rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

@media (max-width: 860px) {
  .agent-audit-kit-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .agent-audit-kit-card,
  .agent-audit-kit-chain {
    padding: 1rem;
  }

  .agent-audit-kit-cta .btn {
    width: 100%;
    justify-content: center;
  }
}
`;

const copy = {
  en: {
    eyebrow: "Agent Action Audit Kit",
    title: "Audit the actions your AI agents take — not just the answers they give.",
    intro:
      "A bounded pilot wedge for teams building agents that touch code, CI/CD, infrastructure, internal tools, finance, governance, or customer workflows.",
    punchline:
      "Your AI agent may produce the right output. But can you prove it was allowed to do what it did?",
    cardTitle: "What you send",
    cardIntro: "Start small. One concrete workflow is enough.",
    sendItems: [
      "One agent workflow or trace/log sample.",
      "One action class: PR autofix, CI remediation, incident response, tool call, or governance step.",
      "A short description of what the agent is allowed to do today.",
    ],
    chainTitle: "What you get back",
    chainIntro:
      "A reviewer-ready evidence chain showing decision, gate, consequence, execution, replay, and causal-audit findings.",
    steps: [
      ["Signal", "input"],
      ["Care-Case", "policy"],
      ["DRP", "decision"],
      ["DMP", "consequence"],
      ["PythiaLabs", "gate"],
      ["CaPU", "side effect"],
      ["T-Trace / LTP", "replay"],
      ["CML", "causal audit"],
      ["Report", "review"],
    ],
    ctaAudit: "Request an agent action audit",
    ctaDocs: "Read the kit",
    note:
      "First commercial wedge: one workflow, one action class, one trace/log sample, one evidence report. No platform migration required.",
    subject: "Agent Action Audit Kit inquiry",
  },
  ru: {
    eyebrow: "Agent Action Audit Kit",
    title: "Аудитируйте действия AI-агентов — не только их ответы.",
    intro:
      "Узкий pilot wedge для команд, где агенты трогают код, CI/CD, инфраструктуру, internal tools, финансы, governance или customer workflows.",
    punchline:
      "AI-агент может дать правильный результат. Но можете ли вы доказать, что ему было разрешено сделать именно это?",
    cardTitle: "Что вы присылаете",
    cardIntro: "Начинаем узко. Достаточно одного конкретного workflow.",
    sendItems: [
      "Один agent workflow или trace/log sample.",
      "Один action class: PR autofix, CI remediation, incident response, tool call или governance step.",
      "Короткое описание того, что агенту сегодня разрешено делать.",
    ],
    chainTitle: "Что получаете обратно",
    chainIntro:
      "Reviewer-ready evidence chain: decision, gate, consequence, execution, replay и causal-audit findings.",
    steps: [
      ["Signal", "input"],
      ["Care-Case", "policy"],
      ["DRP", "decision"],
      ["DMP", "consequence"],
      ["PythiaLabs", "gate"],
      ["CaPU", "side effect"],
      ["T-Trace / LTP", "replay"],
      ["CML", "causal audit"],
      ["Report", "review"],
    ],
    ctaAudit: "Запросить audit workflow",
    ctaDocs: "Открыть kit",
    note:
      "Первый коммерческий wedge: один workflow, один action class, один trace/log sample, один evidence report. Без миграции платформы.",
    subject: "Agent Action Audit Kit inquiry",
  },
  zh: {
    eyebrow: "Agent Action Audit Kit",
    title: "Audit the actions your AI agents take — not just the answers they give.",
    intro:
      "A bounded pilot wedge for teams building agents that touch code, CI/CD, infrastructure, internal tools, finance, governance, or customer workflows.",
    punchline:
      "Your AI agent may produce the right output. But can you prove it was allowed to do what it did?",
    cardTitle: "What you send",
    cardIntro: "Start small. One concrete workflow is enough.",
    sendItems: [
      "One agent workflow or trace/log sample.",
      "One action class: PR autofix, CI remediation, incident response, tool call, or governance step.",
      "A short description of what the agent is allowed to do today.",
    ],
    chainTitle: "What you get back",
    chainIntro:
      "A reviewer-ready evidence chain showing decision, gate, consequence, execution, replay, and causal-audit findings.",
    steps: [
      ["Signal", "input"],
      ["Care-Case", "policy"],
      ["DRP", "decision"],
      ["DMP", "consequence"],
      ["PythiaLabs", "gate"],
      ["CaPU", "side effect"],
      ["T-Trace / LTP", "replay"],
      ["CML", "causal audit"],
      ["Report", "review"],
    ],
    ctaAudit: "Request an agent action audit",
    ctaDocs: "Read the kit",
    note:
      "First commercial wedge: one workflow, one action class, one trace/log sample, one evidence report. No platform migration required.",
    subject: "Agent Action Audit Kit inquiry",
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

function mailto(locale) {
  const t = copy[locale] ?? copy.en;
  const body = [
    "Workflow / agent system:",
    "Action class:",
    "What can the agent execute today?",
    "What logs/traces can you share safely?",
    "What would you like to prove or audit?",
    "Current stage: prototype / pilot / production / exploring",
    "Please do not include secrets, credentials, customer data, or sensitive production details.",
  ].join("\n\n");

  return `mailto:${email}?subject=${encodeURIComponent(t.subject)}&body=${encodeURIComponent(body)}`;
}

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;
  const items = t.sendItems.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const steps = t.steps
    .map(([name, detail]) => `<span class="agent-audit-kit-step"><strong>${escapeHtml(name)}</strong> ${escapeHtml(detail)}</span>`)
    .join("");

  return `
      <section id="agent-action-audit-kit" class="section section-alt agent-audit-kit-section" aria-labelledby="agent-action-audit-kit-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="agent-action-audit-kit-title">${escapeHtml(t.title)}</h2>
          <p class="agent-audit-kit-intro">${escapeHtml(t.intro)}</p>
          <p class="agent-audit-kit-punchline">${escapeHtml(t.punchline)}</p>
          <div class="agent-audit-kit-layout">
            <article class="agent-audit-kit-card">
              <h3>${escapeHtml(t.cardTitle)}</h3>
              <p>${escapeHtml(t.cardIntro)}</p>
              <ul class="agent-audit-kit-list">${items}</ul>
            </article>
            <article class="agent-audit-kit-chain">
              <h3>${escapeHtml(t.chainTitle)}</h3>
              <p>${escapeHtml(t.chainIntro)}</p>
              <div class="agent-audit-kit-chain-steps" aria-label="Agent audit evidence chain">${steps}</div>
            </article>
          </div>
          <div class="agent-audit-kit-cta">
            <a class="btn btn-primary" href="${mailto(locale)}" rel="noopener noreferrer">${escapeHtml(t.ctaAudit)} →</a>
            <a class="btn btn-secondary" href="${docsUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.ctaDocs)}</a>
          </div>
          <p class="agent-audit-kit-note">${escapeHtml(t.note)}</p>
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
  if (html.includes(".agent-audit-kit-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="agent-action-audit-kit"')) return html;

  const section = renderSection(locale);
  const pilotInterestMarker = '      <section id="pilot-interest"';
  if (html.includes(pilotInterestMarker)) {
    return html.replace(pilotInterestMarker, `${section}\n\n${pilotInterestMarker}`);
  }

  const paidReviewMarker = '      <section id="paid-review"';
  if (html.includes(paidReviewMarker)) {
    return html.replace(paidReviewMarker, `${section}\n\n${paidReviewMarker}`);
  }

  const contactMarker = '      <section id="contact"';
  if (html.includes(contactMarker)) {
    return html.replace(contactMarker, `${section}\n\n${contactMarker}`);
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

console.log(`Injected Agent Action Audit Kit into ${files.length} page(s).`);
