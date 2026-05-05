import { siteConfig } from "./config.mjs";
import { localeOrder, locales } from "./i18n.mjs";

const escape = (s) =>
  String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const li = (s) => `<li>${escape(s)}</li>`;

const ARTIFACT_JSON = `{
  "outcome": "BLOCK",
  "stop_reason": "evidence_stale",
  "checks": {
    "authorization":      "pass",
    "evidence_freshness": "fail",
    "permission_boundary": "pass",
    "credentials":        "pass",
    "action_risk":        "high"
  },
  "trace_id": "01HXR7Q9P3K4...",
  "digest":   "sha256:9f86d081884c..."
}`;

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

function pilotMailto(subject) {
  return `mailto:${siteConfig.email}?subject=${encodeURIComponent(subject)}`;
}

function utm(url, campaign) {
  if (!url || url.startsWith("mailto:") || url.startsWith("#")) return url;
  const sep = url.includes("?") ? "&" : "?";
  return `${url}${sep}utm_source=landing&utm_medium=cta&utm_campaign=${encodeURIComponent(campaign)}`;
}

function jsonLd(currentId, canonical) {
  const t = locales[currentId];
  const data = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "PythiaLabs",
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Cross-platform",
    description: t.meta.description,
    url: canonical,
    inLanguage: t.htmlLang,
    license: `https://opensource.org/licenses/${siteConfig.license}`,
    codeRepository: siteConfig.repoUrl,
    author: {
      "@type": "Person",
      name: siteConfig.founderName,
    },
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };
  return `<script type="application/ld+json">${JSON.stringify(data)}</script>`;
}

export function renderPage(currentId, year) {
  const t = locales[currentId];
  const hrefs = pathsFor(currentId);
  const canonical = canonicalFor(currentId);
  const ogImage = `${siteConfig.canonicalOrigin.replace(/\/$/, "")}${siteConfig.ogImagePath}`;
  const pilotHref = pilotMailto(siteConfig.pilotEmailSubject);

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

  const useCaseCards = t.useCases.items
    .map(
      (uc) =>
        `<article class="card use-case"><h3>${escape(uc.name)}</h3><p>${escape(uc.desc)}</p></article>`,
    )
    .join("");

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
    <meta name="referrer" content="strict-origin-when-cross-origin" />
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data: https://img.shields.io; frame-src https://www.youtube-nocookie.com; connect-src 'self'; font-src 'self'; base-uri 'self'; form-action 'self'" />

    <link rel="canonical" href="${canonical}" />

    <meta property="og:title" content="${escape(t.meta.title)}" />
    <meta property="og:description" content="${escape(t.meta.description)}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="${canonical}" />
    <meta property="og:locale" content="${t.htmlLang.replace("-", "_")}" />
    <meta property="og:image" content="${ogImage}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:image" content="${ogImage}" />

    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='28'%3E%E2%97%87%3C/text%3E%3C/svg%3E" />

    <link rel="dns-prefetch" href="https://github.com" />
    <link rel="dns-prefetch" href="https://www.youtube-nocookie.com" />
    <link rel="dns-prefetch" href="https://img.shields.io" />
    <link rel="preconnect" href="https://github.com" crossorigin />

    ${hreflangLinks}

    ${jsonLd(currentId, canonical)}

    <style>__INLINE_CSS__</style>
  </head>
  <body>
    <a class="skip-link" href="#main">${escape(t.skipLink)}</a>
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
          <a href="#demo">${escape(t.nav.demo)}</a>
          <a href="#contact">${escape(t.nav.contact)}</a>
        </nav>
        <div class="lang-switcher" role="group" aria-label="Language">${langSwitcher}</div>
      </div>
    </header>

    <main id="main">
      <section class="hero">
        <div class="container">
          <p class="eyebrow">${escape(t.hero.eyebrow)}</p>
          <h1 class="hero-headline">${escape(t.hero.headline)}</h1>
          <p class="hero-subtitle">${escape(t.hero.subtitle)}</p>
          <p class="hero-audience">${escape(t.hero.audience)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="${utm(siteConfig.demoUrl, "hero_demo")}" rel="noopener noreferrer">${escape(t.cta.primary)}</a>
            <a class="btn btn-secondary" href="${utm(siteConfig.repoUrl, "hero_github")}" rel="noopener noreferrer">${escape(t.cta.secondary)}</a>
          </div>
          <p class="hero-badges">
            <a href="${siteConfig.repoUrl}/stargazers" class="badge-link">
              <img src="https://img.shields.io/github/stars/${siteConfig.repoSlug}?style=flat-square&label=stars&color=0b0d10" alt="${escape(t.hero.starsAlt)}" loading="lazy" decoding="async" width="90" height="20" />
            </a>
            <a href="${siteConfig.repoUrl}/blob/main/LICENSE" class="badge-link">
              <img src="https://img.shields.io/github/license/${siteConfig.repoSlug}?style=flat-square&color=0b0d10" alt="License" loading="lazy" decoding="async" width="100" height="20" />
            </a>
          </p>
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

      <section id="artifact" class="section">
        <div class="container">
          <h2>${escape(t.artifact.title)}</h2>
          <p>${escape(t.artifact.intro)}</p>
          <pre class="code-block" aria-label="Example evidence artifact JSON"><code>${escape(ARTIFACT_JSON)}</code></pre>
        </div>
      </section>

      <section id="demo" class="section section-alt">
        <div class="container">
          <h2>${escape(t.demo.title)}</h2>
          <p>${escape(t.demo.caption)}</p>
          <div class="video-frame">
            <iframe
              src="${siteConfig.demoEmbedUrl}"
              title="PythiaLabs demo"
              loading="lazy"
              allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen
              referrerpolicy="strict-origin-when-cross-origin"></iframe>
          </div>
          <p><a href="${siteConfig.demoUrl}">${escape(t.demo.fallback)} →</a></p>
        </div>
      </section>

      <section id="use-cases" class="section">
        <div class="container">
          <h2>${escape(t.useCases.title)}</h2>
          <div class="card-grid">${useCaseCards}</div>
        </div>
      </section>

      <section id="pilot" class="section section-cta">
        <div class="container">
          <h2>${escape(t.finalCta.title)}</h2>
          <p>${escape(t.finalCta.text)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="${pilotHref}" rel="noopener noreferrer">${escape(t.finalCta.primary)}</a>
            <a class="btn btn-secondary" href="${utm(siteConfig.repoUrl, "pilot_github")}" rel="noopener noreferrer">${escape(t.finalCta.secondary)}</a>
          </div>
        </div>
      </section>

      <section id="stage" class="section">
        <div class="container">
          <h2>${escape(t.stage.title)}</h2>
          <ul class="bullet-grid">${t.stage.items.map(li).join("")}</ul>
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
      <div class="container footer-row">
        <p>${escape(t.footer.copyright.replace("{year}", String(year)))} · ${escape(t.footer.tagline)}</p>
        <p class="footer-links">
          <a href="${siteConfig.repoUrl}">GitHub</a>
          <a href="${siteConfig.repoUrl}/blob/main/LICENSE">License</a>
          <a href="${siteConfig.demoUrl}">Demo</a>
        </p>
      </div>
    </footer>
  </body>
</html>
`;
}
