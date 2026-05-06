import fs from "node:fs";
import path from "node:path";

const pages = [
  {
    rel: "index.html",
    icp: "For teams deploying AI agents that can change code, infrastructure, money, or governance workflows.",
    subtitle:
      "PythiaLabs is an open-source pre-execution safety gate that evaluates proposed agent actions and returns ALLOW / BLOCK / ESCALATE with reviewer-facing evidence.",
    proofTitle: "Current proof",
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
    icp: "Для команд, внедряющих AI-агентов, которые могут менять код, инфраструктуру, деньги или governance-процессы.",
    subtitle:
      "PythiaLabs — open-source pre-execution safety gate: оценивает предлагаемые действия агента и возвращает ALLOW / BLOCK / ESCALATE с evidence для ревьюеров.",
    proofTitle: "Текущие proof-сигналы",
    cards: [
      "Open-source MVP",
      "Демо на реальном движке",
      "Проверка SHA-256 evidence",
      "Детерминированные решения ALLOW / BLOCK / ESCALATE",
      "Research roadmap: LTP + CML",
    ],
  },
  {
    rel: "zh/index.html",
    icp: "For teams deploying AI agents that can change code, infrastructure, money, or governance workflows.",
    subtitle:
      "PythiaLabs is an open-source pre-execution safety gate that evaluates proposed agent actions and returns ALLOW / BLOCK / ESCALATE with reviewer-facing evidence.",
    proofTitle: "Current proof",
    cards: [
      "Open-source MVP",
      "Real-engine demo",
      "SHA-256 evidence verification",
      "Deterministic ALLOW / BLOCK / ESCALATE decisions",
      "Research roadmap: LTP + CML",
    ],
  },
];

const removeBlocks = [
  /\n\s*<p class="hero-stakes">[\s\S]*?<\/p>/,
  /\n\s*<p class="hero-outcome-line">[\s\S]*?<\/p>/,
  /\n\s*<p class="hero-tagline">[\s\S]*?<\/p>/,
  /\n\s*<p class="hero-start-here">[\s\S]*?<\/p>/,
  /\n\s*<p class="hero-badges">[\s\S]*?<\/p>/,
  /\n\s*<div class="hero-stats"[\s\S]*?<\/div>\n\s*<\/div>/,
];

for (const page of pages) {
  const file = path.join("dist", page.rel);
  if (!fs.existsSync(file)) continue;
  let html = fs.readFileSync(file, "utf8");

  html = html.replace(
    /<h1 class="hero-headline">[\s\S]*?<\/h1>/,
    '<h1 class="hero-headline">Stop risky AI-agent actions before they execute.</h1>',
  );

  html = html.replace(/<p class="hero-subtitle">[\s\S]*?<\/p>/, `<p class="hero-subtitle">${page.subtitle}</p>`);

  if (!html.includes("hero-icp-line")) {
    html = html.replace('<p class="hero-subtitle">', `<p class="hero-icp-line">${page.icp}</p>\n          <p class="hero-subtitle">`);
  }

  for (const pattern of removeBlocks) {
    html = html.replace(pattern, "");
  }

  html = html.replace(
    /<div class="cta-row">[\s\S]*?<\/div>/,
    `<div class="cta-row">\n            <a class="btn btn-primary" href="#demo-proof">Run demo</a>\n            <a class="btn btn-secondary" href="#paid-review">Request paid review</a>\n            <a class="btn btn-ghost" href="https://github.com/safal207/pythiaLabs" target="_blank" rel="noopener noreferrer">View GitHub</a>\n          </div>`,
  );

  const section = `\n      <section id="current-proof" class="section section-alt" aria-labelledby="current-proof-title">\n        <div class="container">\n          <h2 id="current-proof-title">${page.proofTitle}</h2>\n          <div class="proof-grid">\n            ${page.cards.map((c) => `<article class="card"><p>${c}</p></article>`).join("\n            ")}\n          </div>\n        </div>\n      </section>\n`;

  if (!html.includes('id="current-proof"')) {
    html = html.replace('<section id="demo-proof"', `${section}\n      <section id="demo-proof"`);
  }

  fs.writeFileSync(file, html);
}
