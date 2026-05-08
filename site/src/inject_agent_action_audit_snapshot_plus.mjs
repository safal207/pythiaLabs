import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const email = "safal0645@gmail.com";
const docsUrl = "https://github.com/safal207/pythiaLabs/blob/main/docs/AGENT_ACTION_AUDIT_SNAPSHOT_PLUS.md";

const css = `
.agent-audit-snapshot-plus-section {
  background:
    radial-gradient(circle at top left, rgba(124, 196, 255, 0.10), transparent 30rem),
    linear-gradient(180deg, rgba(124, 196, 255, 0.06) 0%, transparent 100%);
}

.agent-audit-snapshot-plus-layout {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(280px, 1.05fr);
  gap: 1.25rem;
  align-items: stretch;
  margin-top: 1.5rem;
}

.agent-audit-snapshot-plus-intro,
.agent-audit-snapshot-plus-note {
  max-width: 820px;
  color: var(--text-muted);
  font-size: 1rem;
}

.agent-audit-snapshot-plus-price {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 1rem 0 0;
  padding: 0.48rem 0.72rem;
  border: 1px solid rgba(124, 196, 255, 0.42);
  border-radius: 999px;
  background: rgba(124, 196, 255, 0.10);
  color: var(--text);
  font-family: var(--mono);
  font-size: 0.86rem;
}

.agent-audit-snapshot-plus-price strong {
  color: var(--accent);
}

.agent-audit-snapshot-plus-card {
  border: 1px solid rgba(124, 196, 255, 0.28);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 1.25rem 1.35rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.16);
}

.agent-audit-snapshot-plus-card h3 {
  margin: 0 0 0.65rem;
  color: var(--text);
  font-size: 1.08rem;
  line-height: 1.35;
}

.agent-audit-snapshot-plus-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.agent-audit-snapshot-plus-list {
  display: grid;
  gap: 0.62rem;
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
}

.agent-audit-snapshot-plus-list li {
  position: relative;
  padding-left: 1.35rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.agent-audit-snapshot-plus-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--accent);
  font-weight: 800;
}

.agent-audit-snapshot-plus-cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.35rem;
}

@media (max-width: 860px) {
  .agent-audit-snapshot-plus-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .agent-audit-snapshot-plus-card {
    padding: 1rem;
  }

  .agent-audit-snapshot-plus-cta .btn {
    width: 100%;
    justify-content: center;
  }
}
`;

const copy = {
  en: {
    eyebrow: "Upsell · Snapshot Plus",
    title: "Want deeper review? Upgrade to Snapshot Plus.",
    intro:
      "Get the written Snapshot plus a 45-minute walkthrough and prioritized hardening roadmap for your team.",
    price: "Snapshot Plus",
    priceValue: "$497",
    leftTitle: "Everything in Snapshot",
    leftIntro: "The same focused evidence-risk review for one workflow.",
    leftItems: [
      "2–3 page evidence-risk Snapshot.",
      "Action-risk map and first trust break.",
      "ALLOW / BLOCK / ESCALATE recommendation.",
    ],
    rightTitle: "Plus live interpretation",
    rightIntro: "Built for teams that need to explain the trust break internally.",
    rightItems: [
      "45-minute walkthrough call.",
      "Prioritized hardening roadmap.",
      "Decision: no pilot, internal hardening, or full audit pilot.",
    ],
    cta: "Upgrade to Snapshot Plus — $497",
    docs: "Read Snapshot Plus details",
    note:
      "Best when engineering, security, or leadership needs to understand the evidence gap before committing to a full pilot.",
    subject: "Agent Action Audit Snapshot Plus inquiry",
  },
  ru: {
    eyebrow: "Upsell · Snapshot Plus",
    title: "Нужен deeper review? Upgrade to Snapshot Plus.",
    intro:
      "Получите written Snapshot плюс 45-minute walkthrough и prioritized hardening roadmap для команды.",
    price: "Snapshot Plus",
    priceValue: "$497",
    leftTitle: "Всё из Snapshot",
    leftIntro: "Тот же focused evidence-risk review для одного workflow.",
    leftItems: [
      "2–3 page evidence-risk Snapshot.",
      "Action-risk map и first trust break.",
      "ALLOW / BLOCK / ESCALATE recommendation.",
    ],
    rightTitle: "Плюс live interpretation",
    rightIntro: "Для команд, которым нужно объяснить trust break внутри компании.",
    rightItems: [
      "45-minute walkthrough call.",
      "Prioritized hardening roadmap.",
      "Decision: no pilot, internal hardening или full audit pilot.",
    ],
    cta: "Upgrade to Snapshot Plus — $497",
    docs: "Открыть Snapshot Plus details",
    note:
      "Лучше всего, когда engineering, security или leadership должны понять evidence gap до full pilot.",
    subject: "Agent Action Audit Snapshot Plus inquiry",
  },
  zh: {
    eyebrow: "Upsell · Snapshot Plus",
    title: "Want deeper review? Upgrade to Snapshot Plus.",
    intro:
      "Get the written Snapshot plus a 45-minute walkthrough and prioritized hardening roadmap for your team.",
    price: "Snapshot Plus",
    priceValue: "$497",
    leftTitle: "Everything in Snapshot",
    leftIntro: "The same focused evidence-risk review for one workflow.",
    leftItems: [
      "2–3 page evidence-risk Snapshot.",
      "Action-risk map and first trust break.",
      "ALLOW / BLOCK / ESCALATE recommendation.",
    ],
    rightTitle: "Plus live interpretation",
    rightIntro: "Built for teams that need to explain the trust break internally.",
    rightItems: [
      "45-minute walkthrough call.",
      "Prioritized hardening roadmap.",
      "Decision: no pilot, internal hardening, or full audit pilot.",
    ],
    cta: "Upgrade to Snapshot Plus — $497",
    docs: "Read Snapshot Plus details",
    note:
      "Best when engineering, security, or leadership needs to understand the evidence gap before committing to a full pilot.",
    subject: "Agent Action Audit Snapshot Plus inquiry",
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
    "I am interested in Snapshot Plus.",
    "Workflow / agent system:",
    "Action class:",
    "Current stage: prototype / pilot / production / exploring",
    "What would we like to understand live?",
    "Who should join the walkthrough?",
    "What decision do we need after the review?",
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
      <section id="agent-action-audit-snapshot-plus" class="section section-alt agent-audit-snapshot-plus-section" aria-labelledby="agent-action-audit-snapshot-plus-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="agent-action-audit-snapshot-plus-title">${escapeHtml(t.title)}</h2>
          <p class="agent-audit-snapshot-plus-intro">${escapeHtml(t.intro)}</p>
          <p class="agent-audit-snapshot-plus-price"><span>${escapeHtml(t.price)}</span> <strong>${escapeHtml(t.priceValue)}</strong></p>
          <div class="agent-audit-snapshot-plus-layout">
            <article class="agent-audit-snapshot-plus-card">
              <h3>${escapeHtml(t.leftTitle)}</h3>
              <p>${escapeHtml(t.leftIntro)}</p>
              <ul class="agent-audit-snapshot-plus-list">${renderList(t.leftItems)}</ul>
            </article>
            <article class="agent-audit-snapshot-plus-card">
              <h3>${escapeHtml(t.rightTitle)}</h3>
              <p>${escapeHtml(t.rightIntro)}</p>
              <ul class="agent-audit-snapshot-plus-list">${renderList(t.rightItems)}</ul>
            </article>
          </div>
          <div class="agent-audit-snapshot-plus-cta">
            <a class="btn btn-primary" href="${mailto(locale)}" rel="noopener noreferrer">${escapeHtml(t.cta)} →</a>
            <a class="btn btn-secondary" href="${docsUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.docs)}</a>
          </div>
          <p class="agent-audit-snapshot-plus-note">${escapeHtml(t.note)}</p>
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
  if (html.includes(".agent-audit-snapshot-plus-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="agent-action-audit-snapshot-plus"')) return html;
  const section = renderSection(locale);

  const snapshotMarker = '      <section id="agent-action-audit-snapshot"';
  if (html.includes(snapshotMarker)) {
    const paidReviewMarker = '      <section id="paid-review"';
    if (html.includes(paidReviewMarker)) return html.replace(paidReviewMarker, `${section}\n\n${paidReviewMarker}`);
    const contactMarker = '      <section id="contact"';
    if (html.includes(contactMarker)) return html.replace(contactMarker, `${section}\n\n${contactMarker}`);
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

console.log(`Injected Agent Action Audit Snapshot Plus into ${files.length} page(s).`);
