import fs from "node:fs";
import path from "node:path";

const pages = [
  {
    rel: "index.html",
    eyebrow: "Pre-execution safety layer · Open-source · Apache-2.0",
    headline: "Stop risky AI-agent actions before they execute.",
    icp: "For teams deploying AI agents that can change code, infrastructure, money, or governance workflows.",
    subtitle:
      "PythiaLabs is an open-source pre-execution safety gate that evaluates proposed agent actions and returns ALLOW / BLOCK / ESCALATE with reviewer-facing evidence.",
    proofTitle: "Current proof",
    runDemo: "Run demo",
    requestReview: "Request paid review",
    viewGithub: "View GitHub",
    cards: [
      "Open-source MVP",
      "Real-engine demo",
      "SHA-256 evidence verification",
      "Deterministic ALLOW / BLOCK / ESCALATE decisions",
      "Research roadmap: LTP + CML",
    ],
  },
  {
    rel: "ru/index.html",
    eyebrow: "Pre-execution safety layer · Open-source · Apache-2.0",
    headline: "Останавливайте рискованные действия AI-агентов до выполнения.",
    icp: "Для команд, внедряющих AI-агентов, которые могут менять код, инфраструктуру, деньги или governance-процессы.",
    subtitle:
      "PythiaLabs — open-source pre-execution safety gate: оценивает предлагаемые действия агента и возвращает ALLOW / BLOCK / ESCALATE с evidence для ревьюеров.",
    proofTitle: "Текущие proof-сигналы",
    runDemo: "Запустить демо",
    requestReview: "Запросить платный разбор",
    viewGithub: "Открыть GitHub",
    cards: [
      "Open-source MVP",
      "Демо на реальном движке",
      "Проверка evidence по SHA-256",
      "Детерминированные решения ALLOW / BLOCK / ESCALATE",
      "Исследовательский roadmap: LTP + CML",
    ],
  },
  {
    rel: "zh/index.html",
    eyebrow: "Pre-execution safety layer · Open-source · Apache-2.0",
    headline: "Stop risky AI-agent actions before they execute.",
    icp: "For teams deploying AI agents that can change code, infrastructure, money, or governance workflows.",
    subtitle:
      "PythiaLabs is an open-source pre-execution safety gate that evaluates proposed agent actions and returns ALLOW / BLOCK / ESCALATE with reviewer-facing evidence.",
    proofTitle: "Current proof",
    runDemo: "Run demo",
    requestReview: "Request paid review",
    viewGithub: "View GitHub",
    cards: [
      "Open-source MVP",
      "Real-engine demo",
      "SHA-256 evidence verification",
      "Deterministic ALLOW / BLOCK / ESCALATE decisions",
      "Research roadmap: LTP + CML",
    ],
  },
];

for (const page of pages) {
  const file = path.join("dist", page.rel);
  if (!fs.existsSync(file)) continue;
  let html = fs.readFileSync(file, "utf8");

  const heroSection = `
      <section class="hero">
        <div class="container">
          <p class="eyebrow">${page.eyebrow}</p>
          <h1 class="hero-headline">${page.headline}</h1>
          <p class="hero-icp-line">${page.icp}</p>
          <p class="hero-subtitle">${page.subtitle}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="#demo-proof">${page.runDemo}</a>
            <a class="btn btn-secondary" href="#paid-review">${page.requestReview}</a>
            <a class="btn btn-ghost" href="https://github.com/safal207/pythiaLabs" target="_blank" rel="noopener noreferrer">${page.viewGithub}</a>
          </div>
        </div>
      </section>`;

  html = html.replace(/\n\s*<section class="hero">[\s\S]*?<\/section>/, `\n${heroSection}`);

  const currentProofSection = `
      <section id="current-proof" class="section section-alt" aria-labelledby="current-proof-title">
        <div class="container">
          <h2 id="current-proof-title">${page.proofTitle}</h2>
          <div class="card-grid">
            ${page.cards.map((c) => `<article class="card"><p>${c}</p></article>`).join("\n            ")}
          </div>
        </div>
      </section>
`;

  if (!html.includes('id="current-proof"')) {
    html = html.replace('<section id="demo-proof"', `${currentProofSection}\n      <section id="demo-proof"`);
  }

  fs.writeFileSync(file, html);
}
