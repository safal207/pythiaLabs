import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { transform } from "lightningcss";

import { localeOrder, validateLocales } from "./src/i18n.mjs";
import { renderOgSvg } from "./src/og.mjs";
import { renderPage } from "./src/render.mjs";
import { renderRobots, renderSitemap } from "./src/sitemap.mjs";
import { downloadAssets } from "./src/download_assets.mjs";

// lightningcss browser version encoding: major << 16 | minor << 8 | patch
const browserVersion = (major, minor = 0, patch = 0) => (major << 16) | (minor << 8) | patch;

const buildCssFixes = `
/* Build-time rendering fixes */
.step-list {
  list-style: none;
  padding-left: 0;
}

.downloads-section {
  background: linear-gradient(180deg, rgba(124, 196, 255, 0.08) 0%, transparent 100%);
}

.downloads-section .downloads-intro {
  max-width: 780px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.downloads-risk-line {
  max-width: 780px;
  margin: 1rem 0 0;
  padding: 0.9rem 1rem;
  border-left: 3px solid var(--escalate);
  border-radius: 0 var(--radius) var(--radius) 0;
  background: rgba(210, 153, 34, 0.1);
  color: var(--text);
  font-size: 1rem;
}

.download-paths {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.6rem;
  margin: 1.35rem 0 0;
  padding: 0;
  list-style: none;
}

.download-paths li {
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: rgba(22, 27, 34, 0.58);
  color: var(--text-muted);
  font-size: 0.92rem;
  line-height: 1.4;
}

.download-paths strong {
  display: block;
  margin-bottom: 0.15rem;
  color: var(--text);
  font-size: 0.88rem;
}

.downloads-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.download-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.4rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.download-card:first-child {
  border-color: rgba(124, 196, 255, 0.48);
  box-shadow: 0 0 0 1px rgba(124, 196, 255, 0.08), 0 12px 36px rgba(0, 0, 0, 0.18);
}

.download-card-kicker {
  margin: 0 0 0.55rem;
  color: var(--accent);
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.download-card h3 {
  margin: 0 0 0.65rem;
  font-size: 1.05rem;
  line-height: 1.35;
  color: var(--text);
}

.download-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.download-card .btn {
  align-self: flex-start;
}

.download-card-micro {
  margin-top: 0.65rem !important;
  color: var(--text-muted) !important;
  font-family: var(--mono);
  font-size: 0.76rem !important;
  line-height: 1.45 !important;
}

.downloads-note {
  margin-top: 1.25rem;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.support-section .support-intro {
  max-width: 780px;
  color: var(--text-muted);
  font-size: 1.03rem;
}

.support-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.support-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.85rem;
  padding: 1.25rem 1.4rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.support-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
  line-height: 1.35;
  color: var(--text);
}

.support-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.support-card .btn {
  align-self: flex-start;
}

.support-note {
  margin-top: 1.25rem;
  color: var(--text-muted);
  font-size: 0.92rem;
}
`;

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const downloadCopy = {
  en: {
    eyebrow: "10-minute safety review",
    title: "Run a pre-execution safety review before your next risky agent tool call",
    intro:
      "If your agent can touch code, infrastructure, money, or governance, the safety question is no longer “did it answer well?”. The question is: should this action execute?",
    riskLine:
      "Your safety boundary is no longer the prompt. It is the moment before execution.",
    pathTitle: "Choose your path",
    note:
      "No email required. Use these files in your next internal review, security discussion, grant application, or pilot conversation.",
    cards: {
      "ai-agent-pre-execution-safety-checklist.md": {
        kicker: "Start here",
        path: "I am evaluating risk",
        title: "Find your first unsafe agent action in 10 minutes",
        desc:
          "Review one real agent workflow and identify missing authorization, stale evidence, blast radius, and escalation gaps before tools execute.",
        button: "Get the 10-minute checklist",
        micro: "Best first download · No email required",
      },
      "pythialabs-one-page-technical-brief.md": {
        kicker: "Internal buy-in",
        path: "I need to explain this internally",
        title: "Explain PythiaLabs to your CTO or security reviewer",
        desc:
          "A one-page brief you can forward internally: what the gate checks, why post-hoc logs are not enough, and how ALLOW / BLOCK / ESCALATE decisions work.",
        button: "Download the technical brief",
        micro: "Forwardable · Reviewer-friendly",
      },
      "pythialabs-pilot-partner-pack.md": {
        kicker: "Pilot fit",
        path: "I want to test a real workflow",
        title: "See if your team is a fit for a pilot",
        desc:
          "Map one high-risk agent workflow into proposed actions, decision-time evidence, stop reasons, and reviewable outputs.",
        button: "Check pilot fit",
        micro: "For teams with real agent tools",
      },
      "sample-evidence-artifact.json": {
        kicker: "Inspect output",
        path: "I want to inspect the output",
        title: "Inspect what reviewers actually get",
        desc:
          "A sample evidence artifact with checks, stop reasons, decision-time evidence, outcome, and digest metadata. No vibes — inspectable output.",
        button: "View sample artifact",
        micro: "JSON artifact · CI/security ready",
      },
    },
  },
  ru: {
    eyebrow: "10-минутное safety review",
    title: "Проведите pre-execution review до следующего рискованного tool call агента",
    intro:
      "Если агент может трогать код, инфраструктуру, деньги или governance, вопрос безопасности уже не “хорошо ли он ответил?”. Вопрос: должно ли это действие выполниться?",
    riskLine:
      "Граница безопасности уже не в промпте. Она в моменте перед выполнением.",
    pathTitle: "Выберите свой путь",
    note:
      "Email не нужен. Используйте эти файлы для внутреннего review, security-обсуждения, грантовой заявки или разговора о пилоте.",
    cards: {
      "ai-agent-pre-execution-safety-checklist.md": {
        kicker: "Начните здесь",
        path: "Я оцениваю риск",
        title: "Найдите первое небезопасное действие агента за 10 минут",
        desc:
          "Возьмите один реальный agent workflow и проверьте authorization, свежесть evidence, blast radius и escalation gaps до запуска tools.",
        button: "Получить 10-минутный checklist",
        micro: "Лучший первый download · Без email",
      },
      "pythialabs-one-page-technical-brief.md": {
        kicker: "Для внутреннего buy-in",
        path: "Мне нужно объяснить это внутри команды",
        title: "Объясните PythiaLabs CTO или security-ревьюеру",
        desc:
          "One-page brief для пересылки: что проверяет gate, почему post-hoc logs недостаточно и как работают ALLOW / BLOCK / ESCALATE решения.",
        button: "Скачать technical brief",
        micro: "Можно переслать · Удобно для ревьюеров",
      },
      "pythialabs-pilot-partner-pack.md": {
        kicker: "Pilot fit",
        path: "Я хочу протестировать реальный workflow",
        title: "Проверьте, подходит ли команда для пилота",
        desc:
          "Соберите один high-risk agent workflow в proposed actions, decision-time evidence, stop reasons и reviewable outputs.",
        button: "Проверить pilot fit",
        micro: "Для команд с реальными agent tools",
      },
      "sample-evidence-artifact.json": {
        kicker: "Посмотреть output",
        path: "Я хочу увидеть результат",
        title: "Посмотрите, что реально получает ревьюер",
        desc:
          "Sample evidence artifact с checks, stop reasons, decision-time evidence, outcome и digest metadata. Не vibes — проверяемый output.",
        button: "Открыть sample artifact",
        micro: "JSON artifact · Для CI/security",
      },
    },
  },
  zh: {
    eyebrow: "10-minute safety review",
    title: "Run a pre-execution safety review before your next risky agent tool call",
    intro:
      "If your agent can touch code, infrastructure, money, or governance, the safety question is no longer “did it answer well?”. The question is: should this action execute?",
    riskLine:
      "Your safety boundary is no longer the prompt. It is the moment before execution.",
    pathTitle: "Choose your path",
    note:
      "No email required. Use these files in your next internal review, security discussion, grant application, or pilot conversation.",
    cards: {
      "ai-agent-pre-execution-safety-checklist.md": {
        kicker: "Start here",
        path: "I am evaluating risk",
        title: "Find your first unsafe agent action in 10 minutes",
        desc:
          "Review one real agent workflow and identify missing authorization, stale evidence, blast radius, and escalation gaps before tools execute.",
        button: "Get the 10-minute checklist",
        micro: "Best first download · No email required",
      },
      "pythialabs-one-page-technical-brief.md": {
        kicker: "Internal buy-in",
        path: "I need to explain this internally",
        title: "Explain PythiaLabs to your CTO or security reviewer",
        desc:
          "A one-page brief you can forward internally: what the gate checks, why post-hoc logs are not enough, and how ALLOW / BLOCK / ESCALATE decisions work.",
        button: "Download the technical brief",
        micro: "Forwardable · Reviewer-friendly",
      },
      "pythialabs-pilot-partner-pack.md": {
        kicker: "Pilot fit",
        path: "I want to test a real workflow",
        title: "See if your team is a fit for a pilot",
        desc:
          "Map one high-risk agent workflow into proposed actions, decision-time evidence, stop reasons, and reviewable outputs.",
        button: "Check pilot fit",
        micro: "For teams with real agent tools",
      },
      "sample-evidence-artifact.json": {
        kicker: "Inspect output",
        path: "I want to inspect the output",
        title: "Inspect what reviewers actually get",
        desc:
          "A sample evidence artifact with checks, stop reasons, decision-time evidence, outcome, and digest metadata. No vibes — inspectable output.",
        button: "View sample artifact",
        micro: "JSON artifact · CI/security ready",
      },
    },
  },
};

const supportCopy = {
  en: {
    eyebrow: "Support the project",
    title: "Fund open-source pre-execution safety for AI agents",
    intro:
      "PythiaLabs is open source. Support helps fund deterministic ALLOW / BLOCK / ESCALATE decisions, structured decision-time evidence, replayable traces, and reviewer-facing artifacts for high-risk agent workflows.",
    note: "All paths use email until payment accounts are configured.",
    cards: [
      {
        title: "Support open-source development",
        desc: "For individuals, builders, and researchers. Helps fund docs, demos, evaluators, integrations, and reviewer-facing artifacts.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20support",
        button: "Support the work",
      },
      {
        title: "Sponsor a deterministic safety showcase",
        desc: "Fund a concrete scenario: AI coding agents before merge, DevOps agents before infra changes, fintech risk, or DAO governance.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20showcase%20sponsor",
        button: "Sponsor a showcase",
      },
      {
        title: "Start a paid pilot",
        desc: "For teams whose agents touch code, infrastructure, money, or governance. Map one high-risk workflow into a pre-execution gate.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20paid%20pilot",
        button: "Discuss a pilot",
      },
      {
        title: "Read the sponsorship doc",
        desc: "Full breakdown of support tiers, paid pilot scope, and what funded work produces.",
        href: "https://github.com/safal207/pythiaLabs/blob/main/docs/SPONSORSHIP.md",
        button: "Open SPONSORSHIP.md",
      },
    ],
  },
  ru: {
    eyebrow: "Поддержать проект",
    title: "Поддержите open-source pre-execution safety для AI-агентов",
    intro:
      "PythiaLabs — open source. Поддержка помогает развивать детерминированные ALLOW / BLOCK / ESCALATE решения, decision-time evidence, replayable traces и артефакты для ревьюеров.",
    note: "Пока все каналы — через email, до настройки платёжных аккаунтов.",
    cards: [
      {
        title: "Поддержать open-source разработку",
        desc: "Для тех, кто хочет, чтобы проект продолжал двигаться: документация, демо, evaluator-улучшения, интеграции.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20support",
        button: "Поддержать",
      },
      {
        title: "Спонсировать showcase",
        desc: "Профинансировать конкретный сценарий: AI coding agents, DevOps, fintech-риски, DAO governance.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20showcase%20sponsor",
        button: "Спонсировать showcase",
      },
      {
        title: "Запустить paid pilot",
        desc: "Для команд, чьи агенты трогают код, инфраструктуру, деньги или governance. Один high-risk workflow → pre-execution gate.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20paid%20pilot",
        button: "Обсудить pilot",
      },
      {
        title: "Полный документ о поддержке",
        desc: "Уровни поддержки, объём paid pilot, что получает спонсор.",
        href: "https://github.com/safal207/pythiaLabs/blob/main/docs/SPONSORSHIP.md",
        button: "Открыть SPONSORSHIP.md",
      },
    ],
  },
  zh: {
    eyebrow: "Support the project",
    title: "Fund open-source pre-execution safety for AI agents",
    intro:
      "PythiaLabs is open source. Support helps fund deterministic ALLOW / BLOCK / ESCALATE decisions, structured decision-time evidence, replayable traces, and reviewer-facing artifacts for high-risk agent workflows.",
    note: "All paths use email until payment accounts are configured.",
    cards: [
      {
        title: "Support open-source development",
        desc: "For individuals, builders, and researchers. Helps fund docs, demos, evaluators, integrations, and reviewer-facing artifacts.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20support",
        button: "Support the work",
      },
      {
        title: "Sponsor a deterministic safety showcase",
        desc: "Fund a concrete scenario: AI coding agents before merge, DevOps agents before infra changes, fintech risk, or DAO governance.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20showcase%20sponsor",
        button: "Sponsor a showcase",
      },
      {
        title: "Start a paid pilot",
        desc: "For teams whose agents touch code, infrastructure, money, or governance. Map one high-risk workflow into a pre-execution gate.",
        href: "mailto:safal0645@gmail.com?subject=PythiaLabs%20paid%20pilot",
        button: "Discuss a pilot",
      },
      {
        title: "Read the sponsorship doc",
        desc: "Full breakdown of support tiers, paid pilot scope, and what funded work produces.",
        href: "https://github.com/safal207/pythiaLabs/blob/main/docs/SPONSORSHIP.md",
        button: "Open SPONSORSHIP.md",
      },
    ],
  },
};

function renderSupportSection(currentId) {
  const copy = supportCopy[currentId] ?? supportCopy.en;
  const cards = copy.cards
    .map(
      (card) => `
          <article class="support-card">
            <div>
              <h3>${escapeHtml(card.title)}</h3>
              <p>${escapeHtml(card.desc)}</p>
            </div>
            <p><a class="btn btn-secondary" href="${escapeHtml(card.href)}" rel="noopener noreferrer">${escapeHtml(card.button)} →</a></p>
          </article>`,
    )
    .join("");

  return `
      <section id="support" class="section support-section" aria-labelledby="support-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(copy.eyebrow)}</p>
          <h2 id="support-title">${escapeHtml(copy.title)}</h2>
          <p class="support-intro">${escapeHtml(copy.intro)}</p>
          <div class="support-grid">${cards}
          </div>
          <p class="support-note">${escapeHtml(copy.note)}</p>
        </div>
      </section>`;
}

function injectSupportSection(html, currentId) {
  const section = renderSupportSection(currentId);
  const contactMarker = "      <section id=\"contact\"";
  if (html.includes(contactMarker)) {
    return html.replace(contactMarker, `${section}\n\n${contactMarker}`);
  }
  return html.replace("\n    </main>", `\n${section}\n    </main>`);
}

function downloadHref(currentId, filename) {
  const prefix = currentId === "en" ? "./" : "../";
  return `${prefix}downloads/${filename}`;
}

function renderDownloadsSection(currentId) {
  const copy = downloadCopy[currentId] ?? downloadCopy.en;
  const pathItems = downloadAssets
    .map((asset) => {
      const card = copy.cards[asset.filename] ?? downloadCopy.en.cards[asset.filename];
      return `<li><strong>${escapeHtml(card.path)}</strong>${escapeHtml(card.kicker)} → ${escapeHtml(card.title)}</li>`;
    })
    .join("");

  const cards = downloadAssets
    .map((asset) => {
      const card = copy.cards[asset.filename] ?? downloadCopy.en.cards[asset.filename];
      const href = downloadHref(currentId, asset.filename);
      return `
          <article class="download-card">
            <div>
              <p class="download-card-kicker">${escapeHtml(card.kicker)}</p>
              <h3>${escapeHtml(card.title)}</h3>
              <p>${escapeHtml(card.desc)}</p>
              <p class="download-card-micro">${escapeHtml(card.micro)}</p>
            </div>
            <p><a class="btn btn-secondary" href="${escapeHtml(href)}" download>${escapeHtml(card.button)} →</a></p>
          </article>`;
    })
    .join("");

  return `
      <section id="downloads" class="section section-alt downloads-section" aria-labelledby="downloads-title">
        <div class="container">
          <p class="cta-eyebrow">${escapeHtml(copy.eyebrow)}</p>
          <h2 id="downloads-title">${escapeHtml(copy.title)}</h2>
          <p class="downloads-intro">${escapeHtml(copy.intro)}</p>
          <p class="downloads-risk-line">${escapeHtml(copy.riskLine)}</p>
          <ul class="download-paths" aria-label="${escapeHtml(copy.pathTitle)}">${pathItems}</ul>
          <div class="downloads-grid">${cards}
          </div>
          <p class="downloads-note">${escapeHtml(copy.note)}</p>
        </div>
      </section>`;
}

function injectDownloadsSection(html, currentId) {
  const section = renderDownloadsSection(currentId);
  const contactMarker = "      <section id=\"contact\"";
  if (html.includes(contactMarker)) {
    return html.replace(contactMarker, `${section}\n\n${contactMarker}`);
  }
  return html.replace("\n    </main>", `\n${section}\n    </main>`);
}

async function main() {
  validateLocales();

  const here = path.dirname(fileURLToPath(import.meta.url));
  const distDir = path.join(here, "dist");
  const cssPath = path.join(here, "src", "styles.css");

  const cssSource = Buffer.concat([await readFile(cssPath), Buffer.from(buildCssFixes)]);
  const { code } = transform({
    filename: "styles.css",
    code: cssSource,
    minify: true,
    sourceMap: false,
    targets: {
      chrome: browserVersion(100),
      firefox: browserVersion(100),
      safari: browserVersion(14),
    },
  });
  const minifiedCss = code.toString();

  await rm(distDir, { recursive: true, force: true });
  await mkdir(distDir, { recursive: true });

  const year = new Date().getFullYear();
  const buildDate = new Date().toISOString();
  let total = 0;

  for (const id of localeOrder) {
    const html = injectSupportSection(
      injectDownloadsSection(
        renderPage(id, year, buildDate).replace("__INLINE_CSS__", minifiedCss),
        id,
      ),
      id,
    );
    const outDir = id === "en" ? distDir : path.join(distDir, id);
    if (id !== "en") await mkdir(outDir, { recursive: true });
    const outPath = path.join(outDir, "index.html");
    await writeFile(outPath, html, "utf8");
    const size = Buffer.byteLength(html);
    total += size;
    const rel = path.relative(distDir, outPath);
    process.stdout.write(`  ${rel.padEnd(20)} ${(size / 1024).toFixed(2)} KB\n`);
  }

  const downloadsDir = path.join(distDir, "downloads");
  await mkdir(downloadsDir, { recursive: true });
  for (const asset of downloadAssets) {
    await writeFile(path.join(downloadsDir, asset.filename), asset.content, "utf8");
  }

  await writeFile(path.join(distDir, "robots.txt"), renderRobots(), "utf8");
  await writeFile(path.join(distDir, "sitemap.xml"), renderSitemap(), "utf8");
  await writeFile(path.join(distDir, "og.svg"), renderOgSvg(), "utf8");

  process.stdout.write(
    `\nbuilt ${localeOrder.length} pages (${(total / 1024).toFixed(2)} KB total) + ${downloadAssets.length} downloads + robots.txt, sitemap.xml, og.svg\n`,
  );
}

main().catch((err) => {
  process.stderr.write(`build failed: ${err?.stack ?? err}\n`);
  process.exit(1);
});
