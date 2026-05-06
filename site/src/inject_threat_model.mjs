import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");

const threatModelUrl =
  "https://github.com/safal207/pythiaLabs/blob/main/docs/THREAT_MODEL.md";

const css = `
.threat-model-section {
  background: linear-gradient(180deg, rgba(248, 81, 73, 0.04) 0%, transparent 100%);
}

.threat-model-section .threat-model-intro {
  max-width: 840px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.threat-model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.threat-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.2rem 1.35rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.threat-id {
  margin: 0;
  color: var(--block);
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.threat-card h3 {
  margin: 0;
  font-size: 1.02rem;
  line-height: 1.35;
  color: var(--text);
}

.threat-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.94rem;
  line-height: 1.5;
}

.threat-card .threat-mitigation {
  border-top: 1px solid var(--border);
  padding-top: 0.55rem;
  font-size: 0.9rem;
}

.threat-card .threat-mitigation strong {
  color: var(--allow, #6fcf7f);
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.threat-model-cta {
  margin-top: 1.5rem;
}
`;

const threats = [
  {
    id: "T1",
    title: {
      en: "Prompt-injected tool call",
      ru: "Tool call через prompt-injection",
      zh: "Prompt-injected tool call",
    },
    risk: {
      en: "Injected content coerces the agent into a high-impact tool call.",
      ru: "Внешний контент склоняет агента к опасному tool call.",
      zh: "Injected content coerces the agent into a high-impact tool call.",
    },
    mitigation: {
      en: "Decisions are deterministic over evidence, not over agent rationale; ESCALATE on insufficient corroboration.",
      ru: "Решения детерминированы по evidence, а не по rationale агента; ESCALATE при недостаточной corroboration.",
      zh: "Decisions are deterministic over evidence, not over agent rationale; ESCALATE on insufficient corroboration.",
    },
  },
  {
    id: "T2",
    title: {
      en: "Stale evidence",
      ru: "Устаревшее evidence",
      zh: "Stale evidence",
    },
    risk: {
      en: "Authorization, balances, or policy state changed since evidence was fetched.",
      ru: "Authorization, баланс или policy изменились после сбора evidence.",
      zh: "Authorization, balances, or policy state changed since evidence was fetched.",
    },
    mitigation: {
      en: "Evidence has freshness windows; stale data triggers ESCALATE or BLOCK with a stop_reason.",
      ru: "У evidence есть окна свежести; устаревшие данные дают ESCALATE/BLOCK со stop_reason.",
      zh: "Evidence has freshness windows; stale data triggers ESCALATE or BLOCK with a stop_reason.",
    },
  },
  {
    id: "T3",
    title: {
      en: "Blast-radius underestimation",
      ru: "Недооценка blast radius",
      zh: "Blast-radius underestimation",
    },
    risk: {
      en: "Action looks bounded but downstream impact is much larger.",
      ru: "Действие выглядит локальным, но downstream-эффект значительно шире.",
      zh: "Action looks bounded but downstream impact is much larger.",
    },
    mitigation: {
      en: "Action schema classifies blast radius; ESCALATE is the default for unclassified high-impact verbs.",
      ru: "Action schema классифицирует blast radius; ESCALATE по умолчанию для неклассифицированных high-impact verbs.",
      zh: "Action schema classifies blast radius; ESCALATE is the default for unclassified high-impact verbs.",
    },
  },
];

const copy = {
  en: {
    eyebrow: "Threat model",
    title: "What the gate is built to stop",
    intro:
      "Three of the top threats PythiaLabs is designed to address. Full threat model documents trust boundaries, six tracked threats, residual risks, and the reproducibility commitment.",
    cta: "Read full threat model",
    risk: "Risk",
    mitigation: "Mitigation",
  },
  ru: {
    eyebrow: "Threat model",
    title: "Против чего работает gate",
    intro:
      "Три ключевые угрозы, которые PythiaLabs закрывает. Полный threat model описывает trust boundaries, шесть отслеживаемых угроз, residual risks и reproducibility commitment.",
    cta: "Открыть полный threat model",
    risk: "Риск",
    mitigation: "Mitigation",
  },
  zh: {
    eyebrow: "Threat model",
    title: "What the gate is built to stop",
    intro:
      "Three of the top threats PythiaLabs is designed to address. Full threat model documents trust boundaries, six tracked threats, residual risks, and the reproducibility commitment.",
    cta: "Read full threat model",
    risk: "Risk",
    mitigation: "Mitigation",
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

function renderCard(threat, locale, t) {
  const title = threat.title[locale] ?? threat.title.en;
  const risk = threat.risk[locale] ?? threat.risk.en;
  const mitigation = threat.mitigation[locale] ?? threat.mitigation.en;
  return `
          <article class="threat-card">
            <p class="threat-id">${escapeHtml(threat.id)}</p>
            <h3>${escapeHtml(title)}</h3>
            <p><strong>${escapeHtml(t.risk)}.</strong> ${escapeHtml(risk)}</p>
            <p class="threat-mitigation"><strong>${escapeHtml(t.mitigation)}</strong><br>${escapeHtml(mitigation)}</p>
          </article>`;
}

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;
  const cards = threats.map((th) => renderCard(th, locale, t)).join("");

  return `
      <section id="threat-model" class="section threat-model-section" aria-labelledby="threat-model-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="threat-model-title">${escapeHtml(t.title)}</h2>
          <p class="threat-model-intro">${escapeHtml(t.intro)}</p>
          <div class="threat-model-grid">${cards}
          </div>
          <p class="threat-model-cta">
            <a class="btn btn-secondary" href="${threatModelUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.cta)} →</a>
          </p>
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
  if (html.includes(".threat-model-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="threat-model"')) return html;
  const section = renderSection(locale);
  const milestonesMarker = '      <section id="milestones"';
  if (html.includes(milestonesMarker)) {
    return html.replace(milestonesMarker, `${section}\n\n${milestonesMarker}`);
  }
  const validationMarker = '      <section id="validation-tracks"';
  if (html.includes(validationMarker)) {
    return html.replace(validationMarker, `${section}\n\n${validationMarker}`);
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

console.log(`Injected threat model section into ${files.length} page(s).`);
