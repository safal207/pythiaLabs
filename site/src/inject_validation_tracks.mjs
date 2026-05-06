import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");

const manifundUrl =
  "https://manifund.org/projects/deterministic-oversight-for-agent-traces--ltp--cml";

const css = `
.validation-tracks-section {
  background: linear-gradient(180deg, rgba(124, 196, 255, 0.05) 0%, transparent 100%);
}

.validation-tracks-section .validation-tracks-intro {
  max-width: 840px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.validation-tracks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.validation-track-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.2rem 1.35rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.validation-track-status {
  margin: 0;
  color: var(--accent);
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.validation-track-card h3 {
  margin: 0;
  font-size: 1.02rem;
  line-height: 1.35;
  color: var(--text);
}

.validation-track-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.94rem;
  line-height: 1.5;
}

.validation-track-card .validation-track-link {
  margin-top: 0.35rem;
  font-size: 0.88rem;
}

.validation-tracks-disclaimer {
  margin-top: 1.25rem;
  padding: 0.85rem 1rem;
  border-left: 3px solid var(--border);
  border-radius: 0 var(--radius) var(--radius) 0;
  background: rgba(22, 27, 34, 0.45);
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.5;
}
`;

const tracks = [
  {
    status: "Submitted",
    title: "NLnet NGI Zero Commons Fund",
    desc: {
      en: "Submitted for open-source evidence-gate infrastructure.",
      ru: "Заявка отправлена: open-source evidence-gate инфраструктура.",
      zh: "Submitted for open-source evidence-gate infrastructure.",
    },
  },
  {
    status: "Submitted",
    title: "Open Technology Fund",
    desc: {
      en: "Submitted for reproducible evidence gates for high-risk digital workflows.",
      ru: "Заявка отправлена: воспроизводимые evidence gates для high-risk digital workflows.",
      zh: "Submitted for reproducible evidence gates for high-risk digital workflows.",
    },
  },
  {
    status: "Submitted",
    title: "K-Startup Grand Challenge 2026",
    desc: {
      en: "Submitted as an AI assurance infrastructure project for the Korean market.",
      ru: "Заявка отправлена: AI assurance инфраструктура для корейского рынка.",
      zh: "Submitted as an AI assurance infrastructure project for the Korean market.",
    },
  },
  {
    status: "Submission confirmed",
    title: "OpenAI Cybersecurity Grant Program",
    desc: {
      en: "Application submitted to OpenAI Cybersecurity Grant Program (external review).",
      ru: "Заявка подана в OpenAI Cybersecurity Grant Program (на внешнем review).",
      zh: "Application submitted to OpenAI Cybersecurity Grant Program (external review).",
    },
  },
  {
    status: "Live research funding track",
    title: "Manifund",
    desc: {
      en: "Deterministic oversight for agent traces: LTP + CML.",
      ru: "Deterministic oversight для agent traces: LTP + CML.",
      zh: "Deterministic oversight for agent traces: LTP + CML.",
    },
    href: manifundUrl,
    linkLabel: {
      en: "View Manifund proposal →",
      ru: "Посмотреть Manifund proposal →",
      zh: "View Manifund proposal →",
    },
  },
];

const copy = {
  en: {
    eyebrow: "Project validation tracks",
    title: "PythiaLabs is being tested across multiple funding and review pathways",
    intro:
      "PythiaLabs is being evaluated through startup, open-source, public-interest, AI-security, and research funding tracks. Each entry is a real submission or live proposal — not an endorsement.",
    disclaimer:
      "Program references indicate submitted applications, active proposals, or exploratory pathways. They do not imply acceptance, endorsement, or funding unless explicitly stated.",
  },
  ru: {
    eyebrow: "Контуры проверки проекта",
    title: "PythiaLabs проходит несколько контуров funding и review",
    intro:
      "PythiaLabs проверяется через startup, open-source, public-interest, AI-security и research funding треки. Каждый пункт — реальная заявка или активное предложение, а не endorsement.",
    disclaimer:
      "Упоминания программ означают поданные заявки, активные предложения или exploratory pathways. Это не подразумевает принятие, поддержку или финансирование, если не указано явно.",
  },
  zh: {
    eyebrow: "Project validation tracks",
    title: "PythiaLabs is being tested across multiple funding and review pathways",
    intro:
      "PythiaLabs is being evaluated through startup, open-source, public-interest, AI-security, and research funding tracks. Each entry is a real submission or live proposal — not an endorsement.",
    disclaimer:
      "Program references indicate submitted applications, active proposals, or exploratory pathways. They do not imply acceptance, endorsement, or funding unless explicitly stated.",
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

function renderCard(track, locale) {
  const desc = track.desc[locale] ?? track.desc.en;
  const link = track.href
    ? `<p class="validation-track-link"><a class="btn btn-ghost" href="${escapeHtml(
        track.href,
      )}" target="_blank" rel="noopener noreferrer">${escapeHtml(
        track.linkLabel[locale] ?? track.linkLabel.en,
      )}</a></p>`
    : "";
  return `
          <article class="validation-track-card">
            <p class="validation-track-status">${escapeHtml(track.status)}</p>
            <h3>${escapeHtml(track.title)}</h3>
            <p>${escapeHtml(desc)}</p>
            ${link}
          </article>`;
}

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;
  const cards = tracks.map((track) => renderCard(track, locale)).join("");

  return `
      <section id="validation-tracks" class="section validation-tracks-section" aria-labelledby="validation-tracks-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="validation-tracks-title">${escapeHtml(t.title)}</h2>
          <p class="validation-tracks-intro">${escapeHtml(t.intro)}</p>
          <div class="validation-tracks-grid">${cards}
          </div>
          <p class="validation-tracks-disclaimer">${escapeHtml(t.disclaimer)}</p>
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
  if (html.includes(".validation-tracks-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="validation-tracks"')) return html;

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

console.log(`Injected validation tracks section into ${files.length} page(s).`);
