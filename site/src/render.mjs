import { localeOrder, locales } from "./i18n.mjs";

const escAttr = (s) =>
  String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

// Body text: keep typographic quotes / dashes intact, escape HTML specials only.
const escText = (s) =>
  String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

const li = (s) => `<li>${escText(s)}</li>`;

/**
 * Build relative paths from the current locale's directory to every other
 * locale. `en` lives at the site root; `ru`, `zh` live in subdirs.
 */
function pathsFor(currentId) {
  const fromRoot = (id) => (id === "en" ? "./" : `./${id}/`);
  const fromSub = (id) => (id === "en" ? "../" : id === currentId ? "./" : `../${id}/`);
  const make = currentId === "en" ? fromRoot : fromSub;
  return Object.fromEntries(localeOrder.map((id) => [id, make(id)]));
}

export function renderPage(currentId, year) {
  const t = locales[currentId];
  const hrefs = pathsFor(currentId);

  const langSwitcher = localeOrder
    .map((id) => {
      const label = locales[id].langLabel;
      const active = id === currentId;
      return active
        ? `<span class="lang-link is-active" aria-current="true">${label}</span>`
        : `<a class="lang-link" href="${hrefs[id]}" hreflang="${locales[id].htmlLang}">${label}</a>`;
    })
    .join("");

  const hreflangLinks = localeOrder
    .map(
      (id) =>
        `<link rel="alternate" hreflang="${locales[id].htmlLang}" href="${hrefs[id]}" />`,
    )
    .concat(`<link rel="alternate" hreflang="x-default" href="${hrefs.en}" />`)
    .join("\n    ");

  return `<!doctype html>
<html lang="${t.htmlLang}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#0b0d10" media="(prefers-color-scheme: dark)" />
    <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
    <title>${escText(t.meta.title)}</title>
    <meta name="description" content="${escAttr(t.meta.description)}" />
    <meta name="color-scheme" content="dark light" />

    <meta property="og:title" content="${escAttr(t.meta.title)}" />
    <meta property="og:description" content="${escAttr(t.meta.description)}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://github.com/safal207/pythiaLabs" />
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
    <header class="site-header">
      <div class="container header-row">
        <a class="brand" href="${hrefs[currentId]}" aria-label="PythiaLabs home">
          <span class="brand-mark" aria-hidden="true">◇</span>
          <span class="brand-name">PythiaLabs</span>
        </a>
        <nav class="site-nav" aria-label="Primary">
          <a href="#problem">${escText(t.nav.problem)}</a>
          <a href="#solution">${escText(t.nav.solution)}</a>
          <a href="#use-cases">${escText(t.nav.useCases)}</a>
          <a href="#stage">${escText(t.nav.stage)}</a>
          <a href="#contact">${escText(t.nav.contact)}</a>
        </nav>
        <div class="lang-switcher" role="group" aria-label="Language">${langSwitcher}</div>
      </div>
    </header>

    <main id="top">
      <section class="hero">
        <div class="container">
          <p class="eyebrow">${escText(t.hero.eyebrow)}</p>
          <h1>PythiaLabs</h1>
          <p class="hero-subtitle">${escText(t.hero.subtitle)}</p>
          <p class="hero-text">${escText(t.hero.text)}</p>
          <p class="hero-support">${escText(t.hero.support)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="https://github.com/safal207/pythiaLabs">${escText(t.cta.github)}</a>
            <a class="btn btn-secondary" href="https://youtu.be/IUk3iO0N4YU">${escText(t.cta.demo)}</a>
            <a class="btn btn-ghost" href="mailto:safal0645@gmail.com">${escText(t.cta.contact)}</a>
          </div>
        </div>
      </section>

      <section id="problem" class="section">
        <div class="container">
          <h2>${escText(t.problem.title)}</h2>
          <p>${escText(t.problem.p1)}</p>
          <p>${escText(t.problem.p2)}</p>
          <blockquote>${escText(t.problem.quote)}</blockquote>
        </div>
      </section>

      <section id="solution" class="section section-alt">
        <div class="container">
          <h2>${escText(t.solution.title)}</h2>
          <p>${escText(t.solution.intro)}</p>
          <div class="two-col">
            <div class="card">
              <h3>${escText(t.solution.checksTitle)}</h3>
              <ul>${t.solution.checks.map(li).join("")}</ul>
            </div>
            <div class="card">
              <h3>${escText(t.solution.returnsTitle)}</h3>
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
          <h2>${escText(t.output.title)}</h2>
          <p>${escText(t.output.intro)}</p>
          <ul class="bullet-grid">${t.output.items.map(li).join("")}</ul>
        </div>
      </section>

      <section id="use-cases" class="section section-alt">
        <div class="container">
          <h2>${escText(t.useCases.title)}</h2>
          <div class="card-grid">
            ${t.useCases.items.map((s) => `<div class="card"><h3>${escText(s)}</h3></div>`).join("")}
          </div>
        </div>
      </section>

      <section id="stage" class="section">
        <div class="container">
          <h2>${escText(t.stage.title)}</h2>
          <p>${escText(t.stage.p1)}</p>
          <p>${escText(t.stage.p2)}</p>
          <p>${escText(t.stage.p3)}</p>
        </div>
      </section>

      <section id="founder" class="section section-alt">
        <div class="container">
          <h2>${escText(t.founder.title)}</h2>
          <div class="founder">
            <p class="founder-name">Aleksei Safonov</p>
            <p class="founder-role">${escText(t.founder.role)}</p>
            <p>${escText(t.founder.exp)}</p>
            <p>${escText(t.founder.focus)}</p>
          </div>
        </div>
      </section>

      <section id="contact" class="section">
        <div class="container">
          <h2>${escText(t.contact.title)}</h2>
          <ul class="contact-list">
            <li><span>${escText(t.contact.labels.github)}</span><a href="https://github.com/safal207/pythiaLabs">github.com/safal207/pythiaLabs</a></li>
            <li><span>${escText(t.contact.labels.demo)}</span><a href="https://youtu.be/IUk3iO0N4YU">youtu.be/IUk3iO0N4YU</a></li>
            <li><span>${escText(t.contact.labels.email)}</span><a href="mailto:safal0645@gmail.com">safal0645@gmail.com</a></li>
            <li><span>${escText(t.contact.labels.x)}</span><a href="https://x.com/lim746048">x.com/lim746048</a></li>
            <li><span>${escText(t.contact.labels.telegram)}</span><a href="https://t.me/Alexfox14">@Alexfox14</a></li>
          </ul>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="container">
        <p>${escText(t.footer.replace("{year}", String(year)))}</p>
      </div>
    </footer>
  </body>
</html>
`;
}
