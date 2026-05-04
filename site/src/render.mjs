import { siteConfig } from "./config.mjs";
import { localeOrder, locales } from "./i18n.mjs";

const escape = (s) =>
  String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const li = (s) => `<li>${escape(s)}</li>`;

function pathsFor(currentId) {
  const fromRoot = (id) => (id === "en" ? "./" : `./${id}/`);
  const fromSub = (id) => (id === "en" ? "../" : id === currentId ? "./" : `../${id}/`);
  const make = currentId === "en" ? fromRoot : fromSub;
  return Object.fromEntries(localeOrder.map((id) => [id, make(id)]));
}

function canonicalFor(id) {
  const base = siteConfig.canonicalOrigin.replace(/\/$/, "");
  return id === "en" ? `${base}/` : `${base}/${id}/`;
}

export function renderPage(currentId, year) {
  const t = locales[currentId];
  const hrefs = pathsFor(currentId);
  const canonical = canonicalFor(currentId);

  const langSwitcher = localeOrder
    .map((id) => {
      const label = locales[id].langLabel;
      const active = id === currentId;
      const ariaCurrent = active ? ` aria-current="page"` : "";
      const cls = active ? "lang-link is-active" : "lang-link";
      return `<a class="${cls}" href="${hrefs[id]}" hreflang="${locales[id].htmlLang}"${ariaCurrent}>${escape(label)}</a>`;
    })
    .join("");

  const hreflangLinks = localeOrder
    .map(
      (id) =>
        `<link rel="alternate" hreflang="${locales[id].htmlLang}" href="${canonicalFor(id)}" />`,
    )
    .concat(`<link rel="alternate" hreflang="x-default" href="${canonicalFor("en")}" />`)
    .join("\n    ");

  return `<!doctype html>
<html lang="${t.htmlLang}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#0b0d10" media="(prefers-color-scheme: dark)" />
    <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
    <title>${escape(t.meta.title)}</title>
    <meta name="description" content="${escape(t.meta.description)}" />
    <meta name="color-scheme" content="dark light" />
    <meta name="robots" content="index, follow" />

    <link rel="canonical" href="${canonical}" />

    <meta property="og:title" content="${escape(t.meta.title)}" />
    <meta property="og:description" content="${escape(t.meta.description)}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="${canonical}" />
    <meta property="og:locale" content="${t.htmlLang.replace("-", "_")}" />
    <meta name="twitter:card" content="summary" />

    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='28'%3E%E2%97%87%3C/text%3E%3C/svg%3E" />

    <link rel="dns-prefetch" href="https://github.com" />
    <link rel="dns-prefetch" href="https://youtu.be" />
    <link rel="preconnect" href="https://github.com" crossorigin />

    ${hreflangLinks}

    <style>__INLINE_CSS__</style>
  </head>
  <body>
    <a class="skip-link" href="#top">Skip to content</a>
    <header class="site-header">
      <div class="container header-row">
        <a class="brand" href="${hrefs[currentId]}" aria-label="PythiaLabs home">
          <span class="brand-mark" aria-hidden="true">◇</span>
          <span class="brand-name">PythiaLabs</span>
        </a>
        <nav class="site-nav" aria-label="Primary">
          <a href="#problem">${escape(t.nav.problem)}</a>
          <a href="#solution">${escape(t.nav.solution)}</a>
          <a href="#use-cases">${escape(t.nav.useCases)}</a>
          <a href="#stage">${escape(t.nav.stage)}</a>
          <a href="#contact">${escape(t.nav.contact)}</a>
        </nav>
        <div class="lang-switcher" role="group" aria-label="Language">${langSwitcher}</div>
      </div>
    </header>

    <main id="top">
      <section class="hero">
        <div class="container">
          <p class="eyebrow">${escape(t.hero.eyebrow)}</p>
          <h1>PythiaLabs</h1>
          <p class="hero-subtitle">${escape(t.hero.subtitle)}</p>
          <p class="hero-text">${escape(t.hero.text)}</p>
          <p class="hero-support">${escape(t.hero.support)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="${siteConfig.repoUrl}">${escape(t.cta.github)}</a>
            <a class="btn btn-secondary" href="${siteConfig.demoUrl}">${escape(t.cta.demo)}</a>
            <a class="btn btn-ghost" href="mailto:${siteConfig.email}">${escape(t.cta.contact)}</a>
          </div>
        </div>
      </section>

      <section id="problem" class="section">
        <div class="container">
          <h2>${escape(t.problem.title)}</h2>
          <p>${escape(t.problem.p1)}</p>
          <p>${escape(t.problem.p2)}</p>
          <blockquote>${escape(t.problem.quote)}</blockquote>
        </div>
      </section>

      <section id="solution" class="section section-alt">
        <div class="container">
          <h2>${escape(t.solution.title)}</h2>
          <p>${escape(t.solution.intro)}</p>
          <div class="two-col">
            <div class="card">
              <h3>${escape(t.solution.checksTitle)}</h3>
              <ul>${t.solution.checks.map(li).join("")}</ul>
            </div>
            <div class="card">
              <h3>${escape(t.solution.returnsTitle)}</h3>
              <ul class="decisions">
                <li><span class="tag tag-allow">ALLOW</span></li>
                <li><span class="tag tag-block">BLOCK</span></li>
                <li><span class="tag tag-escalate">ESCALATE</span></li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section id="output" class="section">
        <div class="container">
          <h2>${escape(t.output.title)}</h2>
          <p>${escape(t.output.intro)}</p>
          <ul class="bullet-grid">${t.output.items.map(li).join("")}</ul>
        </div>
      </section>

      <section id="use-cases" class="section section-alt">
        <div class="container">
          <h2>${escape(t.useCases.title)}</h2>
          <div class="card-grid">
            ${t.useCases.items.map((s) => `<div class="card"><h3>${escape(s)}</h3></div>`).join("")}
          </div>
        </div>
      </section>

      <section id="stage" class="section">
        <div class="container">
          <h2>${escape(t.stage.title)}</h2>
          <p>${escape(t.stage.p1)}</p>
          <p>${escape(t.stage.p2)}</p>
          <p>${escape(t.stage.p3)}</p>
        </div>
      </section>

      <section id="founder" class="section section-alt">
        <div class="container">
          <h2>${escape(t.founder.title)}</h2>
          <div class="founder">
            <p class="founder-name">${escape(siteConfig.founderName)}</p>
            <p class="founder-role">${escape(t.founder.role)}</p>
            <p>${escape(t.founder.exp)}</p>
            <p>${escape(t.founder.focus)}</p>
          </div>
        </div>
      </section>

      <section id="contact" class="section">
        <div class="container">
          <h2>${escape(t.contact.title)}</h2>
          <ul class="contact-list">
            <li><span>${escape(t.contact.labels.github)}</span><a href="${siteConfig.repoUrl}">${escape(siteConfig.repoUrl.replace(/^https?:\/\//, ""))}</a></li>
            <li><span>${escape(t.contact.labels.demo)}</span><a href="${siteConfig.demoUrl}">${escape(siteConfig.demoUrl.replace(/^https?:\/\//, ""))}</a></li>
            <li><span>${escape(t.contact.labels.email)}</span><a href="mailto:${siteConfig.email}">${escape(siteConfig.email)}</a></li>
            <li><span>${escape(t.contact.labels.x)}</span><a href="${siteConfig.xUrl}">${escape(siteConfig.xHandle)}</a></li>
            <li><span>${escape(t.contact.labels.telegram)}</span><a href="${siteConfig.telegramUrl}">${escape(siteConfig.telegramHandle)}</a></li>
          </ul>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="container">
        <p>${escape(t.footer.replace("{year}", String(year)))}</p>
      </div>
    </footer>
  </body>
</html>
`;
}
