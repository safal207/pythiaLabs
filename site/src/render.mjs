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
  "canonicalization": "pythia.canonical_export.v1",
  "checks": {
    "authorization":       "pass",
    "evidence_freshness":  "fail",
    "permission_boundary": "pass",
    "credentials":         "pass",
    "action_risk":         "high"
  },
  "trace_id": "01HXR7Q9P3K4...",
  "digest": {
    "algorithm": "sha256",
    "digest":    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
  }
}`;

const exampleDecisions = {
  en: {
    eyebrow: "Example decision",
    title: "An agent wants to move treasury funds. The gate stops first.",
    actionLabel: "Proposed action",
    action: "Transfer 25,000 USDC from treasury",
    decisionLabel: "Decision",
    decision: "ESCALATE",
    reasonLabel: "Reason",
    reason: "Missing quorum approval and stale policy state",
    evidenceLabel: "Evidence",
    evidence: "Replayable trace, check results, and tamper-checkable digest",
  },
  ru: {
    eyebrow: "Пример решения",
    title: "Агент хочет перевести средства казначейства. Сначала срабатывает шлюз.",
    actionLabel: "Предложенное действие",
    action: "Перевести 25 000 USDC из казначейства",
    decisionLabel: "Решение",
    decision: "ESCALATE",
    reasonLabel: "Причина",
    reason: "Нет кворума подтверждений, а состояние политики устарело",
    evidenceLabel: "Доказательства",
    evidence: "Воспроизводимый trace, результаты проверок и tamper-checkable digest",
  },
  zh: {
    eyebrow: "决策示例",
    title: "Agent 想要转移金库资金。门控会先拦截。",
    actionLabel: "拟执行动作",
    action: "从金库转出 25,000 USDC",
    decisionLabel: "决策",
    decision: "ESCALATE",
    reasonLabel: "原因",
    reason: "缺少 quorum approval，且 policy state 已过期",
    evidenceLabel: "证据",
    evidence: "可重放 trace、检查结果和可校验 digest",
  },
};

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
  const example = exampleDecisions[currentId] || exampleDecisions.en;

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

  const mechanismSteps = t.solution.steps
    .map(
      (s, i) =>
        `<li class="step"><div class="step-num" aria-hidden="true">${i + 1}</div><div class="step-body"><h3>${escape(s.name)}</h3><p>${escape(s.desc)}</p></div></li>`,
    )
    .join("");

  const founderVideoCards = siteConfig.founderVideos
    .map((v) => {
      const card = t.founderVideosBlock.cards[v.labelKey];
      return `<article class="video-card">
        <p class="video-card-eyebrow">${escape(card.name)}</p>
        <h3>${escape(card.headline)}</h3>
        <p class="video-card-desc">${escape(card.desc)}</p>
        <p><a class="btn btn-secondary" href="${utm(v.url, v.campaign)}" rel="noopener noreferrer">${escape(card.cta)} →</a></p>
      </article>`;
    })
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
          <a href="#idea">${escape(t.nav.idea)}</a>
          <a href="#solution">${escape(t.nav.solution)}</a>
          <a href="#integration">${escape(t.nav.integration)}</a>
          <a href="#use-cases">${escape(t.nav.useCases)}</a>
          <a href="#videos">${escape(t.nav.videos)}</a>
          <a href="#faq">${escape(t.nav.faq)}</a>
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
          <p class="hero-text">${escape(t.hero.body)}</p>
          <p class="hero-tagline">${escape(t.hero.tagline)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="${utm(siteConfig.demoUrl, "hero_demo")}" rel="noopener noreferrer">${escape(t.cta.primary)}</a>
            <a class="btn btn-secondary" href="${utm(siteConfig.repoUrl, "hero_github")}" rel="noopener noreferrer">${escape(t.cta.secondary)}</a>
            <a class="btn btn-ghost" href="${pilotHref}" rel="noopener noreferrer">${escape(t.cta.tertiary)}</a>
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

      <section class="example-decision" aria-labelledby="example-decision-title">
        <div class="container example-decision-wrap">
          <div class="example-copy">
            <p class="cta-eyebrow">${escape(example.eyebrow)}</p>
            <h2 id="example-decision-title">${escape(example.title)}</h2>
          </div>
          <dl class="decision-card">
            <div class="decision-row">
              <dt>${escape(example.actionLabel)}</dt>
              <dd>${escape(example.action)}</dd>
            </div>
            <div class="decision-row decision-row-strong">
              <dt>${escape(example.decisionLabel)}</dt>
              <dd><span class="tag tag-escalate">${escape(example.decision)}</span></dd>
            </div>
            <div class="decision-row">
              <dt>${escape(example.reasonLabel)}</dt>
              <dd>${escape(example.reason)}</dd>
            </div>
            <div class="decision-row">
              <dt>${escape(example.evidenceLabel)}</dt>
              <dd>${escape(example.evidence)}</dd>
            </div>
          </dl>
        </div>
      </section>

      <aside class="trust-strip" aria-label="Trust signals">
        <div class="container">
          <ul>${t.trustStrip.map((s) => `<li>${escape(s)}</li>`).join("")}</ul>
        </div>
      </aside>

      <section id="video" class="section section-alt">
        <div class="container">
          <p class="cta-eyebrow">${escape(t.videoBlock.eyebrow)}</p>
          <h2>${escape(t.videoBlock.title)}</h2>
          <p>${escape(t.videoBlock.body)}</p>
          <div class="video-frame">
            <iframe
              src="${siteConfig.demoEmbedUrl}"
              title="PythiaLabs demo"
              loading="lazy"
              allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen
              referrerpolicy="strict-origin-when-cross-origin"></iframe>
          </div>
          <blockquote class="core-message">
            <p class="core-label">${escape(t.videoBlock.coreLabel)}</p>
            <p>${escape(t.videoBlock.core)}</p>
          </blockquote>
          <p><a href="${utm(siteConfig.demoUrl, "video_block_fallback")}" rel="noopener noreferrer">${escape(t.videoBlock.fallback)} →</a></p>
        </div>
      </section>

      <section id="problem" class="section">
        <div class="container">
          <h2>${escape(t.problem.title)}</h2>
          <p>${escape(t.problem.intro)}</p>
          <ul class="bullet-grid">${t.problem.items.map(li).join("")}</ul>
          <blockquote>${escape(t.problem.punchline)}</blockquote>
        </div>
      </section>

      <section id="idea" class="section section-alt">
        <div class="container">
          <p class="cta-eyebrow">${escape(t.bigIdea.eyebrow)}</p>
          <h2>${escape(t.bigIdea.title)}</h2>
          <p>${escape(t.bigIdea.lead)}</p>
          <blockquote class="big-quote">${escape(t.bigIdea.quote)}</blockquote>
          <ul class="not-list">${t.bigIdea.not.map((s) => `<li><span class="not-mark" aria-hidden="true">✕</span>${escape(s)}</li>`).join("")}</ul>
          <p class="but-line"><strong>${escape(t.bigIdea.but)}</strong></p>
        </div>
      </section>

      <section id="solution" class="section">
        <div class="container">
          <h2>${escape(t.solution.title)}</h2>
          <p>${escape(t.solution.intro)}</p>
          <ol class="step-list">${mechanismSteps}</ol>
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

      <section id="artifact" class="section section-alt">
        <div class="container">
          <h2>${escape(t.artifact.title)}</h2>
          <p>${escape(t.artifact.intro)}</p>
          <pre class="code-block" aria-label="Example evidence artifact JSON"><code>${escape(ARTIFACT_JSON)}</code></pre>
        </div>
      </section>

      <section id="integration" class="section">
        <div class="container">
          <h2>${escape(t.integration.title)}</h2>
          <p>${escape(t.integration.intro)}</p>
          <div class="card-grid">${t.integration.items
            .map(
              (item) =>
                `<article class="card"><h3>${escape(item.name)}</h3><p>${escape(item.desc)}</p></article>`,
            )
            .join("")}</div>
          <p class="integration-repo-note">${escape(t.integration.repoNote)}</p>
        </div>
      </section>

      <section id="value" class="section">
        <div class="container">
          <h2>${escape(t.valueStack.title)}</h2>
          <p>${escape(t.valueStack.intro)}</p>
          <ul class="value-stack">${t.valueStack.items.map((s) => `<li><span class="check" aria-hidden="true">✓</span><span>${escape(s)}</span></li>`).join("")}</ul>
          <p class="value-stack-footer"><span class="value-price">${escape(t.valueStack.footer)}</span></p>
        </div>
      </section>

      <section id="use-cases" class="section section-alt">
        <div class="container">
          <h2>${escape(t.useCases.title)}</h2>
          <div class="card-grid">${useCaseCards}</div>
        </div>
      </section>

      <section id="positioning" class="section">
        <div class="container">
          <p class="cta-eyebrow">${escape(t.positioning.eyebrow)}</p>
          <h2>${escape(t.positioning.title)}</h2>
          <ul class="not-list">${t.positioning.negatives.map((s) => `<li><span class="not-mark" aria-hidden="true">✕</span>${escape(s)}</li>`).join("")}</ul>
          <p class="but-line"><strong>${escape(t.positioning.claim)}</strong></p>
          <p class="positioning-tags-label">${escape(t.positioning.tagsLabel)}</p>
          <ul class="positioning-tags">
            ${t.positioning.tags
              .map((tag) => {
                const cls =
                  tag === "ALLOW"
                    ? "tag-allow"
                    : tag === "BLOCK"
                      ? "tag-block"
                      : tag === "ESCALATE"
                        ? "tag-escalate"
                        : "tag-audit";
                return `<li><span class="tag ${cls}">${escape(tag)}</span></li>`;
              })
              .join("")}
          </ul>
        </div>
      </section>

      <section id="comparison" class="section section-alt">
        <div class="container">
          <h2>${escape(t.comparison.title)}</h2>
          <div class="compare-grid">
            <div class="compare-col compare-without">
              <h3><span class="compare-mark" aria-hidden="true">✕</span> ${escape(t.comparison.withoutTitle)}</h3>
              <ul>${t.comparison.withoutItems.map((s) => `<li>${escape(s)}</li>`).join("")}</ul>
            </div>
            <div class="compare-col compare-with">
              <h3><span class="compare-mark" aria-hidden="true">✓</span> ${escape(t.comparison.withTitle)}</h3>
              <ul>${t.comparison.withItems.map((s) => `<li>${escape(s)}</li>`).join("")}</ul>
            </div>
          </div>
        </div>
      </section>

      <section id="authority" class="section">
        <div class="container">
          <p class="cta-eyebrow">${escape(t.authority.eyebrow)}</p>
          <h2>${escape(t.authority.title)}</h2>
          <p>${escape(t.authority.body)}</p>
          <blockquote class="big-quote">${escape(t.authority.pullQuote)}</blockquote>
          <aside class="oracle-quote" aria-labelledby="oracle-quote-label">
            <p class="oracle-quote-eyebrow" id="oracle-quote-label">${escape(t.authority.oracleEyebrow)}</p>
            <blockquote class="oracle-quote-body">
              <p>${escape(t.authority.oracleQuote)}</p>
              <cite class="oracle-quote-source">${escape(t.authority.oracleSource)}</cite>
            </blockquote>
            <p class="oracle-quote-bridge">${escape(t.authority.oracleBridge)}</p>
          </aside>
        </div>
      </section>

      <section id="founder" class="section section-alt">
        <div class="container">
          <h2>${escape(t.founderLetter.title)}</h2>
          <blockquote class="founder-letter">
            <p>${escape(t.founderLetter.body)}</p>
            <footer>
              <p class="founder-name">${escape(siteConfig.founderName)}</p>
              <p class="founder-role">${escape(t.founder.role)} · ${escape(t.founder.exp)}</p>
              <p class="founder-signoff">${escape(t.founderLetter.signoff)}</p>
            </footer>
          </blockquote>
        </div>
      </section>

      <section id="videos" class="section">
        <div class="container">
          <p class="cta-eyebrow">${escape(t.founderVideosBlock.eyebrow)}</p>
          <h2>${escape(t.founderVideosBlock.title)}</h2>
          <div class="card-grid video-cards">${founderVideoCards}</div>
        </div>
      </section>

      <section id="faq" class="section section-alt">
        <div class="container">
          <h2>${escape(t.faq.title)}</h2>
          <div class="faq-list">
            ${t.faq.items
              .map(
                (item) =>
                  `<details class="faq-item"><summary>${escape(item.q)}</summary><p>${escape(item.a)}</p></details>`,
              )
              .join("")}
          </div>
        </div>
      </section>

      <section id="pilot" class="section section-cta">
        <div class="container">
          <p class="cta-eyebrow">${escape(t.finalCta.eyebrow)}</p>
          <h2>${escape(t.finalCta.title)}</h2>
          <p>${escape(t.finalCta.body)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="${utm(siteConfig.demoUrl, "final_demo")}" rel="noopener noreferrer">${escape(t.finalCta.primary)}</a>
            <a class="btn btn-secondary" href="${utm(siteConfig.repoUrl, "final_github")}" rel="noopener noreferrer">${escape(t.finalCta.secondary)}</a>
            <a class="btn btn-ghost" href="${pilotHref}" rel="noopener noreferrer">${escape(t.finalCta.tertiary)}</a>
          </div>
          <p class="cta-reassurance">${escape(t.finalCta.reassurance)}</p>
        </div>
      </section>

      <section id="closer" class="section closer">
        <div class="container">
          <p class="closer-line">${escape(t.closer.title)}</p>
        </div>
      </section>

      <section id="stage" class="section">
        <div class="container">
          <h2>${escape(t.stage.title)}</h2>
          <ul class="bullet-grid">${t.stage.items.map(li).join("")}</ul>
        </div>
      </section>

      <section id="contact" class="section section-alt">
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

    <div class="sticky-bar" role="complementary" aria-label="Pilot CTA">
      <div class="container sticky-bar-row">
        <span class="sticky-bar-label">${escape(t.stickyBar.label)}</span>
        <a class="btn btn-primary btn-compact" href="${pilotHref}" rel="noopener noreferrer">${escape(t.stickyBar.cta)} →</a>
      </div>
    </div>

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
