import fs from "node:fs";
import path from "node:path";

const targets = ["index.html", "ru/index.html", "zh/index.html"];
const icpLine =
  '<p class="hero-icp-line">For teams deploying AI agents that can change code, infrastructure, money, or governance workflows.</p>';

for (const rel of targets) {
  const file = path.join("dist", rel);
  if (!fs.existsSync(file)) continue;
  let html = fs.readFileSync(file, "utf8");

  if (!html.includes("hero-icp-line")) {
    html = html.replace(
      '<p class="hero-subtitle">',
      `${icpLine}\n          <p class="hero-subtitle">`,
    );
  }

  if (!html.includes('id="current-proof"')) {
    html = html.replace(
      '<section id="demo-proof"',
      '<div id="current-proof"></div>\n\n      <section id="demo-proof"',
    );
  }

  fs.writeFileSync(file, html);
}
