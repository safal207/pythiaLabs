import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const email = "safal0645@gmail.com";

const css = `
.pilot-capture-section {
  background: linear-gradient(180deg, rgba(124, 196, 255, 0.06) 0%, transparent 100%);
}

.pilot-capture-layout {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(280px, 1.05fr);
  gap: 1.25rem;
  align-items: start;
  margin-top: 1.5rem;
}

.pilot-capture-intro {
  max-width: 760px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.pilot-capture-checklist {
  margin: 1.15rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.65rem;
}

.pilot-capture-checklist li {
  position: relative;
  padding-left: 1.35rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.pilot-capture-checklist li::before {
  content: "✓";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--allow);
  font-weight: 700;
}

.pilot-capture-card {
  border: 1px solid rgba(124, 196, 255, 0.24);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 1.25rem 1.35rem;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
}

.pilot-capture-card h3 {
  margin: 0 0 0.65rem;
  color: var(--text);
  font-size: 1.08rem;
  line-height: 1.35;
}

.pilot-capture-card p {
  margin: 0 0 1rem;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.pilot-capture-fields {
  display: grid;
  gap: 0.75rem;
}

.pilot-capture-field {
  display: grid;
  gap: 0.3rem;
}

.pilot-capture-field label {
  color: var(--text);
  font-size: 0.88rem;
  font-weight: 650;
}

.pilot-capture-field input,
.pilot-capture-field textarea {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg);
  color: var(--text);
  padding: 0.72rem 0.8rem;
  font: inherit;
  font-size: 0.95rem;
}

.pilot-capture-field textarea {
  min-height: 110px;
  resize: vertical;
}

.pilot-capture-field input::placeholder,
.pilot-capture-field textarea::placeholder {
  color: var(--text-muted);
}

.pilot-capture-actions {
  margin-top: 1rem;
}

.pilot-capture-note {
  margin: 0.75rem 0 0 !important;
  color: var(--text-muted);
  font-size: 0.86rem !important;
  line-height: 1.45 !important;
}

@media (max-width: 860px) {
  .pilot-capture-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .pilot-capture-card {
    padding: 1rem;
  }
}
`;

const copy = {
  en: {
    eyebrow: "Pilot interest",
    title: "Request a review for one risky agent workflow",
    intro:
      "Not ready for a paid review yet? Send a short description of the workflow. I will look for fit and reply with the next step.",
    checklist: [
      "For agents touching code, infrastructure, money, governance, or production data.",
      "Best fit: teams that can describe one concrete action before tools run.",
      "Output path: risk map, evidence checklist, and ALLOW / BLOCK / ESCALATE criteria.",
    ],
    cardTitle: "Send pilot interest",
    cardIntro:
      "This opens an email draft. No tracking form, no third-party backend, no newsletter signup.",
    emailLabel: "Your email",
    emailPlaceholder: "you@company.com",
    roleLabel: "Company / role",
    rolePlaceholder: "Fintech CTO, security engineer, founder...",
    workflowLabel: "Risky workflow",
    workflowPlaceholder:
      "Example: an agent can approve infra changes, move treasury funds, merge code, or trigger governance actions...",
    button: "Send pilot interest",
    note: "Used only to respond about PythiaLabs pilots or paid reviews. Please do not include secrets, credentials, real customer data, or sensitive production details.",
    subject: "PythiaLabs pilot interest",
  },
  ru: {
    eyebrow: "Интерес к пилоту",
    title: "Запросите разбор одного рискованного agent workflow",
    intro:
      "Если вы ещё не готовы к paid review, отправьте короткое описание workflow. Я проверю fit и отвечу следующим шагом.",
    checklist: [
      "Для агентов, которые трогают код, инфраструктуру, деньги, governance или production data.",
      "Лучший fit: команда может описать одно конкретное действие до запуска tools.",
      "Выход: risk map, evidence checklist и критерии ALLOW / BLOCK / ESCALATE.",
    ],
    cardTitle: "Отправить pilot interest",
    cardIntro:
      "Кнопка откроет email draft. Без tracking form, без third-party backend, без newsletter signup.",
    emailLabel: "Ваш email",
    emailPlaceholder: "you@company.com",
    roleLabel: "Компания / роль",
    rolePlaceholder: "Fintech CTO, security engineer, founder...",
    workflowLabel: "Рискованный workflow",
    workflowPlaceholder:
      "Например: агент может approve infra changes, move treasury funds, merge code или trigger governance actions...",
    button: "Отправить pilot interest",
    note: "Используется только для ответа по PythiaLabs pilots или paid reviews. Не отправляйте secrets, credentials, реальные customer data или sensitive production details.",
    subject: "PythiaLabs pilot interest",
  },
  zh: {
    eyebrow: "Pilot interest",
    title: "Request a review for one risky agent workflow",
    intro:
      "Not ready for a paid review yet? Send a short description of the workflow. I will look for fit and reply with the next step.",
    checklist: [
      "For agents touching code, infrastructure, money, governance, or production data.",
      "Best fit: teams that can describe one concrete action before tools run.",
      "Output path: risk map, evidence checklist, and ALLOW / BLOCK / ESCALATE criteria.",
    ],
    cardTitle: "Send pilot interest",
    cardIntro:
      "This opens an email draft. No tracking form, no third-party backend, no newsletter signup.",
    emailLabel: "Your email",
    emailPlaceholder: "you@company.com",
    roleLabel: "Company / role",
    rolePlaceholder: "Fintech CTO, security engineer, founder...",
    workflowLabel: "Risky workflow",
    workflowPlaceholder:
      "Example: an agent can approve infra changes, move treasury funds, merge code, or trigger governance actions...",
    button: "Send pilot interest",
    note: "Used only to respond about PythiaLabs pilots or paid reviews. Please do not include secrets, credentials, real customer data, or sensitive production details.",
    subject: "PythiaLabs pilot interest",
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
    "Email:",
    "Company / role:",
    "Risky workflow:",
    "What tool/action can the agent execute?",
    "What evidence should be checked before execution?",
    "Current stage: prototype / pilot / production / exploring",
  ].join("\n\n");

  return `mailto:${email}?subject=${encodeURIComponent(t.subject)}&body=${encodeURIComponent(body)}`;
}

function renderSection(locale) {
  const t = copy[locale] ?? copy.en;
  const checklist = t.checklist.map((item) => `<li>${escapeHtml(item)}</li>`).join("");

  return `
      <section id="pilot-interest" class="section pilot-capture-section" aria-labelledby="pilot-interest-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(t.eyebrow)}</p>
          <h2 id="pilot-interest-title">${escapeHtml(t.title)}</h2>
          <p class="pilot-capture-intro">${escapeHtml(t.intro)}</p>
          <div class="pilot-capture-layout">
            <div>
              <ul class="pilot-capture-checklist">${checklist}</ul>
            </div>
            <article class="pilot-capture-card">
              <h3>${escapeHtml(t.cardTitle)}</h3>
              <p>${escapeHtml(t.cardIntro)}</p>
              <div class="pilot-capture-fields" aria-hidden="true">
                <div class="pilot-capture-field">
                  <label>${escapeHtml(t.emailLabel)}</label>
                  <input type="email" placeholder="${escapeHtml(t.emailPlaceholder)}" disabled />
                </div>
                <div class="pilot-capture-field">
                  <label>${escapeHtml(t.roleLabel)}</label>
                  <input type="text" placeholder="${escapeHtml(t.rolePlaceholder)}" disabled />
                </div>
                <div class="pilot-capture-field">
                  <label>${escapeHtml(t.workflowLabel)}</label>
                  <textarea placeholder="${escapeHtml(t.workflowPlaceholder)}" disabled></textarea>
                </div>
              </div>
              <p class="pilot-capture-actions">
                <a class="btn btn-primary" href="${mailto(locale)}" aria-label="${escapeHtml(t.subject)}" rel="noopener noreferrer">${escapeHtml(t.button)} →</a>
              </p>
              <p class="pilot-capture-note">${escapeHtml(t.note)}</p>
            </article>
          </div>
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
  if (html.includes(".pilot-capture-section")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectSection(html, locale) {
  if (html.includes('id="pilot-interest"')) return html;

  const section = renderSection(locale);
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

console.log(`Injected pilot interest capture into ${files.length} page(s).`);
