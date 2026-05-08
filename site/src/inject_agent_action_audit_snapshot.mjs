import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const email = "safal0645@gmail.com";
const snapshotDocsUrl = "https://github.com/safal207/pythiaLabs/blob/main/docs/AGENT_ACTION_AUDIT_SNAPSHOT.md";

const css = `
.agent-audit-snapshot-section {
  background:
    radial-gradient(circle at top right, rgba(251, 191, 36, 0.10), transparent 28rem),
    linear-gradient(180deg, rgba(251, 191, 36, 0.055) 0%, transparent 100%);
}

.agent-audit-snapshot-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
  gap: 1.25rem;
  align-items: stretch;
  margin-top: 1.5rem;
}

.agent-audit-snapshot-intro,
.agent-audit-snapshot-note {
  max-width: 820px;
  color: var(--text-muted);
  font-size: 1rem;
}

.agent-audit-snapshot-price {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 1rem 0 0;
  padding: 0.48rem 0.72rem;
  border: 1px solid rgba(251, 191, 36, 0.38);
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.09);
  color: var(--text);
  font-family: var(--mono);
  font-size: 0.86rem;
}

.agent-audit-snapshot-price strong {
  color: var(--escalate);
}

.agent-audit-snapshot-card {
  border: 1px solid rgba(251, 191, 36, 0.26);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 1.25rem 1.35rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.16);
}

.agent-audit-snapshot-card h3 {
  margin: 0 0 0.65rem;
  color: var(--text);
  font-size: 1.08rem;
  line-height: 1.35;
}

.agent-audit-snapshot-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.agent-audit-snapshot-list {
  display: grid;
  gap: 0.62rem;
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
}

.agent-audit-snapshot-list li {
  position: relative;
  padding-left: 1.35rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.agent-audit-snapshot-list li::before {
  content: "→";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--escalate);
  font-weight: 800;
}

.agent-audit-snapshot-cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.35rem;
}

@media (max-width: 860px) {
  .agent-audit-snapshot-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .agent-audit-snapshot-card {
    padding: 1rem;
  }

  .agent-audit-snapshot-cta .btn {
    width: 100%;
    justify-content: center;
  }
}
`;

const copy = {
  en: {
    eyebrow: "OTO · Agent Action Audit Snapshot",
    title: "Not ready for a full pilot? Start with a $197 Snapshot.",
    intro:
      "Send one AI-agent workflow, one action class, and one redacted evidence sample. Get a concise report showing where trust breaks before you scale.",
    price: "Founding Snapshot price",
    priceValue: "$197",
    leftTitle: "What you send",
    leftIntro: "A small first step before the full audit pilot.",
    leftItems: [
      "One bounded AI-agent workflow.",
      "One action class: PR autofix, CI/CD, incident response, tool call, or governance step.",
      "One redacted trace/log/sample description and current approval rule.",
    ],
    rightTitle: "What you get",
    rightIntro: "A 2–3 page evidence-risk snapshot.",
    rightItems: [
      "Action-risk map and first trust break.",
      "ALLOW / BLOCK / ESCALATE recommendation.",
      "Missing evidence, causal-validity gaps, and top 3 controls before scaling.",
    ],
    cta: "Get a $197 Agent Action Audit Snapshot",
    docs: "Read Snapshot details",
    note:
      "This is not legal advice, certification, penetration testing, or production sign-off. It is a focused evidence-risk snapshot for one AI-agent workflow.",
    subject: "Agent Action Audit Snapshot inquiry",
  },
  ru: {
    eyebrow: "OTO · Agent Action Audit Snapshot",
    title: "Не готовы к full pilot? Начните с $197 Snapshot.",
    intro:
      "Пришлите один AI-agent workflow, один action class и один redacted evidence sample. Получите короткий report, где именно ломается trust перед масштабированием.",
    price: "Founding Snapshot price",
    priceValue: "$197",
    leftTitle: "Что вы присылаете",
    leftIntro: "Маленький первый шаг перед full audit pilot.",
    leftItems: [
      "Один ограниченный AI-agent workflow.",
      "Один action class: PR autofix, CI/CD, incident response, tool call или governance step.",
      "Один redacted trace/log/sample description и текущий approval rule.",
    ],
    rightTitle: "Что получаете",
    rightIntro: "2–3 page evidence-risk snapshot.",
    rightItems: [
      "Action-risk map и первое место, где ломается trust.",
      "ALLOW / BLOCK / ESCALATE recommendation.",
      "Missing evidence, causal-validity gaps и top 3 controls before scaling.",
    ],
    cta: "Получить $197 Agent Action Audit Snapshot",
    docs: "Открыть Snapshot details",
    note:
      "Это не legal advice, certification, penetration testing или production sign-off. Это focused evidence-risk snapshot для одного AI-agent workflow.",
    subject: "Agent Action Audit Snapshot inquiry",
  },
  zh: {
    eyebrow: "OTO · Agent Action Audit Snapshot",
    title: "Not ready for a full pilot? Start with a $197 Snapshot.",
    intro:
      "Send one AI-agent workflow, one action class, and one redacted evidence sample. Get a concise report showing where trust breaks before you scale.",
    price: "Founding Snapshot price",
    priceValue: "$197",
    leftTitle: "What you send",
    leftIntro: "A small first step before the full audit pilot.",
    leftItems: [
      "One bounded AI-agent workflow.",
      "One action class: PR autofix, CI/CD, incident response, tool call, or governance step.",
      "One redacted trace/log/sample description and current approval rule.",
    ],
    rightTitle: "What you get",
    rightIntro: "A 2–3 page evidence-risk snapshot.",
    rightItems: [
      "Action-risk map and first trust break.",
      "ALLOW / BLOCK / ESCALATE recommendation.",
      "Missing evidence, causal-validity gaps, and top 3 controls before scaling.",
    ],
    cta: "Get a $197 Agent Action Audit Snapshot",
    docs: "Read Snapshot details",
    note:
      "This is not legal advice, certification, penetration testing, or production sign-off. It is a focused evidence-risk snapshot for one AI-agent workflow.",
    subject: "Agent Action Audit Snapshot inquiry",
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
    "Hi Aleksei,",
    "I am interested in the Agent Action Audit Snapshot.",
    "Workflow / agent system:",
    "Action class:",
    "What can the agent execute today?",
    "What logs/traces can we share safely?",
    "What are we worried could go wrong?",
    "Current stage: prototype / pilot / production / exploring",
    "We will not include secrets, credentials, customer data, or sensitive production details.",
  ].join("\n\n");

  return `mailto:${email}?subject=${encodeURIComponent(t.subject)}&body=${encodeURIComponent(body)}`;
}

function renderList(items) {
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;
  return `
      <section id="agent-action-audit-snapshot" class="section agent-audit-snapshot-section" aria-labelledby="agent-action-audit-snapshot-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="agent-action-audit-snapshot-title">${escapeHtml(t.title)}</h2>
          <p class="agent-audit-snapshot-intro">${escapeHtml(t.intro)}</p>
          <p class="agent-audit-snapshot-price"><span>${escapeHtml(t.price)}</span> <strong>${escapeHtml(t.priceValue)}</strong></p>
          <div class="agent-audit-snapshot-layout">
            <article class="agent-audit-snapshot-card">
              <h3>${escapeHtml(t.leftTitle)}</h3>
              <p>${escapeHtml(t.leftIntro)}</p>
              <ul class="agent-audit-snapshot-list">${renderList(t.leftItems)}</ul>
            </article>
            <article class="agent-audit-snapshot-card">
              <h3>${escapeHtml(t.rightTitle)}</h3>
              <p>${escapeHtml(t.rightIntro)}</p>
              <ul class="agent-audit-snapshot-list">${renderList(t.rightItems)}</ul>
            </article>
          </div>
          <div class="agent-audit-snapshot-cta">
            <a class="btn btn-primary" href="${mailto(locale)}" rel="noopener noreferrer">${escapeHtml(t.cta)} →</a>
            <a class="btn btn-secondary" href="${snapshotDocsUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.docs)}</a>
          </div>
          <p class="agent-audit-snapshot-note">${escapeHtml(t.note)}</p>
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
  if (html.includes(".agent-audit-snapshot-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="agent-action-audit-snapshot"')) return html;
  const section = renderSection(locale);

  const onePagerMarker = '      <section id="agent-action-audit-kit"';
  if (html.includes(onePagerMarker)) {
    const nextMarker = '      <section id="pilot-interest"';
    if (html.includes(nextMarker)) return html.replace(nextMarker, `${section}\n\n${nextMarker}`);
  }

  const paidReviewMarker = '      <section id="paid-review"';
  if (html.includes(paidReviewMarker)) return html.replace(paidReviewMarker, `${section}\n\n${paidReviewMarker}`);

  const contactMarker = '      <section id="contact"';
  if (html.includes(contactMarker)) return html.replace(contactMarker, `${section}\n\n${contactMarker}`);

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

console.log(`Injected Agent Action Audit Snapshot into ${files.length} page(s).`);
