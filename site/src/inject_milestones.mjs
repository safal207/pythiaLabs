import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");

const css = `
.milestones-section {
  background: linear-gradient(180deg, rgba(124, 196, 255, 0.04) 0%, transparent 100%);
}

.milestones-section .milestones-intro {
  max-width: 840px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.milestones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.milestone-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.2rem 1.35rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.milestone-quarter {
  margin: 0;
  color: var(--accent);
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.milestone-card h3 {
  margin: 0;
  font-size: 1.02rem;
  line-height: 1.35;
  color: var(--text);
}

.milestone-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.94rem;
  line-height: 1.5;
}

.milestone-status {
  margin: 0;
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.milestone-status.done {
  color: var(--accept, #6fcf7f);
}

.milestones-note {
  margin-top: 1.25rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
`;

const milestones = [
  {
    quarter: "Q1 2026",
    statusKey: "shipped",
    title: {
      en: "Pre-execution gate v1 + paid review tier",
      ru: "Pre-execution gate v1 + платный review-тариф",
      zh: "Pre-execution gate v1 + paid review tier",
    },
    desc: {
      en: "ALLOW / BLOCK / ESCALATE decisions, sample evidence artifact, runnable demo, paid review intake.",
      ru: "Решения ALLOW / BLOCK / ESCALATE, sample evidence artifact, runnable demo, приём платных review.",
      zh: "ALLOW / BLOCK / ESCALATE decisions, sample evidence artifact, runnable demo, paid review intake.",
    },
  },
  {
    quarter: "Q2 2026",
    statusKey: "inProgress",
    title: {
      en: "Threat model + reproducibility hardening",
      ru: "Threat model + усиление reproducibility",
      zh: "Threat model + reproducibility hardening",
    },
    desc: {
      en: "Public threat model, reproducible evidence-gate runs, expanded evaluator coverage, first design partners.",
      ru: "Публичный threat model, воспроизводимые запуски evidence-gate, расширенное покрытие evaluator, первые design partners.",
      zh: "Public threat model, reproducible evidence-gate runs, expanded evaluator coverage, first design partners.",
    },
  },
  {
    quarter: "Q3 2026",
    statusKey: "planned",
    title: {
      en: "Trace-oversight research preview (LTP + CML)",
      ru: "Превью research по trace-oversight (LTP + CML)",
      zh: "Trace-oversight research preview (LTP + CML)",
    },
    desc: {
      en: "First public LTP + CML research artifacts, integration with one external agent framework, replayable traces.",
      ru: "Первые публичные артефакты LTP + CML, интеграция с одним внешним agent framework, replayable traces.",
      zh: "First public LTP + CML research artifacts, integration with one external agent framework, replayable traces.",
    },
  },
  {
    quarter: "Q4 2026",
    statusKey: "planned",
    title: {
      en: "Pilot deployments + grant deliverables",
      ru: "Пилотные внедрения + grant deliverables",
      zh: "Pilot deployments + grant deliverables",
    },
    desc: {
      en: "2–3 pilot deployments in high-risk agent workflows, grant milestone reports, public case studies.",
      ru: "2–3 пилотных внедрения в high-risk agent workflows, отчёты по grant milestones, публичные case studies.",
      zh: "2–3 pilot deployments in high-risk agent workflows, grant milestone reports, public case studies.",
    },
  },
];

const copy = {
  en: {
    eyebrow: "Roadmap",
    title: "Quarterly milestones",
    intro:
      "Public milestones for grant reviewers and design partners. Updated as work ships.",
    note: "Roadmap reflects current scope; specifics may shift based on pilot feedback and grant timelines.",
    statuses: { shipped: "Shipped", inProgress: "In progress", planned: "Planned" },
  },
  ru: {
    eyebrow: "Roadmap",
    title: "Квартальные milestones",
    intro:
      "Публичные milestones для grant-ревьюеров и design partners. Обновляются по мере выпуска.",
    note: "Roadmap отражает текущий scope; детали могут меняться по обратной связи пилотов и срокам грантов.",
    statuses: { shipped: "Готово", inProgress: "В работе", planned: "Планируется" },
  },
  zh: {
    eyebrow: "Roadmap",
    title: "Quarterly milestones",
    intro:
      "Public milestones for grant reviewers and design partners. Updated as work ships.",
    note: "Roadmap reflects current scope; specifics may shift based on pilot feedback and grant timelines.",
    statuses: { shipped: "Shipped", inProgress: "In progress", planned: "Planned" },
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

function renderCard(milestone, locale, statuses) {
  const title = milestone.title[locale] ?? milestone.title.en;
  const desc = milestone.desc[locale] ?? milestone.desc.en;
  const statusLabel = statuses[milestone.statusKey] ?? statuses.planned;
  const statusClass = milestone.statusKey === "shipped" ? " done" : "";
  return `
          <article class="milestone-card">
            <p class="milestone-quarter">${escapeHtml(milestone.quarter)}</p>
            <h3>${escapeHtml(title)}</h3>
            <p>${escapeHtml(desc)}</p>
            <p class="milestone-status${statusClass}">${escapeHtml(statusLabel)}</p>
          </article>`;
}

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;
  const cards = milestones
    .map((m) => renderCard(m, locale, t.statuses))
    .join("");

  return `
      <section id="milestones" class="section milestones-section" aria-labelledby="milestones-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="milestones-title">${escapeHtml(t.title)}</h2>
          <p class="milestones-intro">${escapeHtml(t.intro)}</p>
          <div class="milestones-grid">${cards}
          </div>
          <p class="milestones-note">${escapeHtml(t.note)}</p>
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
  if (html.includes(".milestones-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="milestones"')) return html;

  const section = renderSection(locale);
  const validationMarker = '      <section id="validation-tracks"';
  if (html.includes(validationMarker)) {
    return html.replace(validationMarker, `${section}\n\n${validationMarker}`);
  }
  const supportMarker = '      <section id="support"';
  if (html.includes(supportMarker)) {
    return html.replace(supportMarker, `${section}\n\n${supportMarker}`);
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

console.log(`Injected milestones section into ${files.length} page(s).`);
