import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const boardUrl = "https://github.com/safal207/pythiaLabs/issues/105";
const issuesUrl = "https://github.com/safal207/pythiaLabs/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22good%20first%20issue%22";

const css = `
.contributor-roadmap-section {
  background: linear-gradient(180deg, rgba(124, 196, 255, 0.045) 0%, transparent 100%);
}

.contributor-roadmap-section .roadmap-intro {
  max-width: 820px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.roadmap-level-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.9rem;
  margin-top: 1.25rem;
}

.roadmap-level-card {
  padding: 1rem 1.1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.roadmap-level-card h3 {
  margin: 0 0 0.45rem;
  color: var(--text);
  font-size: 1rem;
  line-height: 1.35;
}

.roadmap-level-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.93rem;
  line-height: 1.5;
}

.roadmap-flow {
  margin: 1.1rem 0 0;
  padding: 0.95rem 1rem;
  border: 1px solid rgba(124, 196, 255, 0.22);
  border-radius: var(--radius);
  background: rgba(124, 196, 255, 0.055);
  color: var(--text-muted);
  font-family: var(--mono);
  font-size: 0.86rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.contributor-roadmap-cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

@media (max-width: 700px) {
  .contributor-roadmap-cta .btn {
    width: 100%;
    justify-content: center;
    text-align: center;
  }
}
`;

const copy = {
  en: {
    eyebrow: "Contributor roadmap",
    title: "Want to contribute? Start with the public backlog board",
    intro:
      "PythiaLabs keeps a lightweight roadmap board that connects the landing page, research track, documentation tasks, and contributor entry points.",
    levels: [
      ["Level 1", "Docs-only starter tasks: glossary, architecture diagram, README expected-output links."],
      ["Level 2", "Reviewer and contributor workflow tasks: quickstart, paid-review demo checklist."],
      ["Level 3", "Careful evidence documentation: artifact schema and conservative demo references."],
    ],
    flow: "Backlog → Ready for contributor → In progress → Needs review → Ready to merge → Done",
    board: "Open backlog board",
    issues: "View good first issues",
  },
  ru: {
    eyebrow: "Contributor roadmap",
    title: "Хотите помочь? Начните с публичной backlog-доски",
    intro:
      "У PythiaLabs есть лёгкая roadmap-доска: она связывает лендинг, research track, документацию и входные задачи для contributors.",
    levels: [
      ["Level 1", "Docs-only задачи для первого входа: glossary, architecture diagram, README expected-output links."],
      ["Level 2", "Reviewer/contributor workflow: quickstart и paid-review demo checklist."],
      ["Level 3", "Более внимательная evidence-документация: artifact schema и аккуратные demo references."],
    ],
    flow: "Backlog → Ready for contributor → In progress → Needs review → Ready to merge → Done",
    board: "Открыть backlog board",
    issues: "Смотреть good first issues",
  },
  zh: {
    eyebrow: "Contributor roadmap",
    title: "Want to contribute? Start with the public backlog board",
    intro:
      "PythiaLabs keeps a lightweight roadmap board that connects the landing page, research track, documentation tasks, and contributor entry points.",
    levels: [
      ["Level 1", "Docs-only starter tasks: glossary, architecture diagram, README expected-output links."],
      ["Level 2", "Reviewer and contributor workflow tasks: quickstart, paid-review demo checklist."],
      ["Level 3", "Careful evidence documentation: artifact schema and conservative demo references."],
    ],
    flow: "Backlog → Ready for contributor → In progress → Needs review → Ready to merge → Done",
    board: "Open backlog board",
    issues: "View good first issues",
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

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;
  const levels = t.levels
    .map(
      ([title, desc]) => `
            <article class="roadmap-level-card">
              <h3>${escapeHtml(title)}</h3>
              <p>${escapeHtml(desc)}</p>
            </article>`,
    )
    .join("");

  return `
      <section id="contributor-roadmap" class="section section-alt contributor-roadmap-section" aria-labelledby="contributor-roadmap-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="contributor-roadmap-title">${escapeHtml(t.title)}</h2>
          <p class="roadmap-intro">${escapeHtml(t.intro)}</p>
          <div class="roadmap-level-grid">${levels}
          </div>
          <p class="roadmap-flow">${escapeHtml(t.flow)}</p>
          <p class="contributor-roadmap-cta">
            <a class="btn btn-primary" href="${boardUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.board)} →</a>
            <a class="btn btn-secondary" href="${issuesUrl}" target="_blank" rel="noopener noreferrer">${escapeHtml(t.issues)} →</a>
          </p>
        </div>
      </section>`;
}

function injectCss(html) {
  if (html.includes(".contributor-roadmap-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="contributor-roadmap"')) return html;

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

console.log(`Injected contributor roadmap section into ${files.length} page(s).`);
