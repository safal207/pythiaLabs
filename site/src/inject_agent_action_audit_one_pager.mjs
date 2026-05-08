import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const onePagerDir = path.join(distDir, "agent-action-audit-kit-one-pager");
const onePagerPath = path.join(onePagerDir, "index.html");
const onePagerUrl = "/pythiaLabs/agent-action-audit-kit-one-pager/";
const email = "safal0645@gmail.com";

const css = `
.agent-audit-kit-download-note {
  flex-basis: 100%;
  margin: -0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.86rem;
}
`;

const onePagerHtml = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agent Action Audit Kit — One-Pager</title>
  <meta name="description" content="Agent Action Audit Kit: one workflow, one evidence chain, one trust report." />
  <style>
    :root {
      color-scheme: dark;
      --bg: #05070b;
      --panel: #0d1117;
      --panel-2: #111827;
      --text: #f5f7fb;
      --muted: #aab3c5;
      --line: rgba(148, 163, 184, 0.24);
      --accent: #58c7f3;
      --accent-2: #7c3aed;
      --ok: #34d399;
      --warn: #fbbf24;
      --radius: 22px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background:
        radial-gradient(circle at 12% 0%, rgba(88, 199, 243, 0.18), transparent 32rem),
        radial-gradient(circle at 100% 15%, rgba(124, 58, 237, 0.18), transparent 34rem),
        var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }

    main {
      width: min(1120px, calc(100% - 40px));
      margin: 0 auto;
      padding: 42px 0;
    }

    .sheet {
      min-height: calc(100vh - 84px);
      border: 1px solid var(--line);
      border-radius: 30px;
      background: linear-gradient(180deg, rgba(17, 24, 39, 0.94), rgba(5, 7, 11, 0.98));
      box-shadow: 0 26px 80px rgba(0, 0, 0, 0.38);
      overflow: hidden;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.85fr);
      gap: 28px;
      padding: 44px;
      border-bottom: 1px solid var(--line);
    }

    .eyebrow {
      margin: 0 0 12px;
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      max-width: 780px;
      font-size: clamp(2.3rem, 5vw, 5.1rem);
      line-height: 0.92;
      letter-spacing: -0.065em;
    }

    .subtitle {
      max-width: 760px;
      margin: 24px 0 0;
      color: var(--muted);
      font-size: 1.18rem;
    }

    .hero-card {
      align-self: stretch;
      display: grid;
      align-content: space-between;
      gap: 20px;
      padding: 28px;
      border: 1px solid rgba(88, 199, 243, 0.22);
      border-radius: var(--radius);
      background: rgba(13, 17, 23, 0.72);
    }

    .hero-card strong {
      display: block;
      margin-bottom: 8px;
      color: var(--text);
      font-size: 1.2rem;
    }

    .hero-card p { margin: 0; color: var(--muted); }

    .cta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 26px;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 44px;
      padding: 0 18px;
      border-radius: 999px;
      border: 1px solid var(--line);
      color: var(--text);
      text-decoration: none;
      font-weight: 800;
      cursor: pointer;
      background: rgba(255, 255, 255, 0.05);
    }

    .btn.primary {
      border: 0;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      color: #020617;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
      padding: 28px 44px 0;
    }

    .card {
      min-height: 188px;
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(13, 17, 23, 0.72);
    }

    .card h2 {
      margin: 0 0 12px;
      font-size: 1.08rem;
      letter-spacing: -0.02em;
    }

    .card ul {
      display: grid;
      gap: 9px;
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 0.96rem;
    }

    .chain {
      margin: 28px 44px 0;
      padding: 24px;
      border: 1px solid rgba(88, 199, 243, 0.22);
      border-radius: var(--radius);
      background: linear-gradient(135deg, rgba(88, 199, 243, 0.08), rgba(124, 58, 237, 0.08));
    }

    .chain h2 { margin: 0 0 16px; font-size: 1.1rem; }

    .steps {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .step {
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.76rem;
      background: rgba(5, 7, 11, 0.48);
    }

    .footer {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: end;
      padding: 28px 44px 44px;
    }

    .final {
      max-width: 760px;
      margin: 0;
      color: var(--text);
      font-size: 1.18rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }

    .links {
      display: flex;
      gap: 14px;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .links a { color: var(--accent); text-decoration: none; }

    @media (max-width: 860px) {
      .hero, .grid, .footer { grid-template-columns: 1fr; padding-left: 24px; padding-right: 24px; }
      .chain { margin-left: 24px; margin-right: 24px; }
    }

    @media print {
      @page { size: A4 landscape; margin: 10mm; }
      body { background: #05070b; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      main { width: 100%; padding: 0; }
      .sheet { min-height: auto; box-shadow: none; }
      .no-print { display: none !important; }
      .hero { padding: 30px; }
      .grid { padding: 22px 30px 0; }
      .chain { margin: 22px 30px 0; }
      .footer { padding: 22px 30px 30px; }
    }
  </style>
</head>
<body>
  <main>
    <section class="sheet">
      <div class="hero">
        <div>
          <p class="eyebrow">PythiaLabs · Agent Action Audit Kit</p>
          <h1>One workflow. One evidence chain. One trust report.</h1>
          <p class="subtitle">A focused audit for AI-agent workflows that touch code, CI/CD, infrastructure, internal tools, governance, finance, or customer operations.</p>
          <div class="cta-row no-print">
            <button class="btn primary" type="button" onclick="window.print()">Print / Save as PDF</button>
            <a class="btn" href="mailto:${email}?subject=Agent%20Action%20Audit%20Kit%20inquiry">Request audit</a>
            <a class="btn" href="/pythiaLabs/">Open landing</a>
          </div>
        </div>
        <aside class="hero-card">
          <div>
            <strong>Core question</strong>
            <p>Your AI agent may produce the right output. But can you prove it was allowed to do what it did?</p>
          </div>
          <div>
            <strong>First pilot scope</strong>
            <p>One workflow, one action class, one trace/log sample, one reviewer-ready evidence report.</p>
          </div>
        </aside>
      </div>

      <div class="grid">
        <article class="card">
          <h2>What we audit</h2>
          <ul>
            <li>Coding agent PR/autofix flows</li>
            <li>CI/CD remediation actions</li>
            <li>Incident-response agents</li>
            <li>Internal tool-calling workflows</li>
          </ul>
        </article>
        <article class="card">
          <h2>What we check</h2>
          <ul>
            <li>Was the action allowed?</li>
            <li>What evidence existed before action?</li>
            <li>Was the side effect explicit?</li>
            <li>Can the path be replayed?</li>
          </ul>
        </article>
        <article class="card">
          <h2>What you get</h2>
          <ul>
            <li>Evidence-chain map</li>
            <li>ALLOW / BLOCK / ESCALATE verdict</li>
            <li>Causal-validity findings</li>
            <li>Next controls to harden the workflow</li>
          </ul>
        </article>
      </div>

      <section class="chain">
        <h2>Audit chain</h2>
        <div class="steps" aria-label="Audit chain">
          <span class="step">Signal</span>
          <span class="step">Care-Case</span>
          <span class="step">DRP decision</span>
          <span class="step">DMP consequence</span>
          <span class="step">PythiaLabs gate</span>
          <span class="step">CaPU side effect</span>
          <span class="step">T-Trace / LTP replay</span>
          <span class="step">CML causal audit</span>
          <span class="step">Reviewer report</span>
        </div>
      </section>

      <footer class="footer">
        <p class="final">We do not audit whether the answer looked good. We audit whether the action was allowed, evidenced, replayable, reversible, and causally valid.</p>
        <div class="links">
          <a href="mailto:${email}">${email}</a>
          <a href="https://github.com/safal207/pythiaLabs">GitHub</a>
        </div>
      </footer>
    </section>
  </main>
</body>
</html>`;

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
  if (html.includes(".agent-audit-kit-download-note")) return html;
  return html.replace("</style>", `${css}\n</style>`);
}

function injectDownloadButton(html) {
  if (html.includes(onePagerUrl)) return html;
  const docsButton = /(<a class="btn btn-secondary" href="https:\/\/github\.com\/safal207\/pythiaLabs\/blob\/main\/docs\/AGENT_ACTION_AUDIT_KIT\.md"[^>]*>.*?<\/a>)/s;
  const button = `$1\n            <a class="btn btn-secondary" href="${onePagerUrl}" target="_blank" rel="noopener noreferrer">Open one-page brief</a>\n            <p class="agent-audit-kit-download-note">Open the brief, then use Print / Save as PDF for a clean one-page PDF.</p>`;
  if (docsButton.test(html)) return html.replace(docsButton, button);
  return html;
}

await mkdir(onePagerDir, { recursive: true });
await writeFile(onePagerPath, onePagerHtml);

const files = await htmlFiles(distDir);
await Promise.all(
  files.map(async (file) => {
    const original = await readFile(file, "utf8");
    const updated = injectDownloadButton(injectCss(original));
    await writeFile(file, updated);
  }),
);

console.log(`Injected Agent Action Audit one-pager link into ${files.length} page(s).`);
console.log(`Created ${onePagerPath}.`);
