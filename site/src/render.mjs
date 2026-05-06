import { siteConfig } from "./config.mjs";
import { localeOrder, locales } from "./i18n.mjs";

const escape = (s) =>
  String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

/** Interprets `…` spans as inline <code> (safe for HTML). */
const inlineCodeToHtml = (s) => {
  const parts = String(s).split(/`([^`]*)`/g);
  let html = "";
  for (let i = 0; i < parts.length; i++) {
    if (i % 2 === 0) {
      html += escape(parts[i]);
    } else {
      html += `<code class="inline-code">${escape(parts[i])}</code>`;
    }
  }
  return html;
};

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

function linkAttrs(url, extra = "") {
  const target = /^https?:\/\//.test(url) ? ` target="_blank"` : "";
  const rel = /^https?:\/\//.test(url) || url.startsWith("mailto:") ? ` target="_blank" rel="noopener noreferrer"` : "";
  return `${target}${rel}${extra}`;
}

function jsonLdGraph(currentId, canonical, buildDate) {
  const t = locales[currentId];
  const base = siteConfig.canonicalOrigin.replace(/\/$/, "");
  const publisher = {
    "@type": "Organization",
    name: "PythiaLabs",
    url: `${base}/`,
    sameAs: [siteConfig.repoUrl, siteConfig.xUrl],
  };

  const softwareApplication = {
    "@type": "SoftwareApplication",
    name: "PythiaLabs",
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Cross-platform",
    description: t.meta.description,
    url: canonical,
    inLanguage: t.htmlLang,
    license: `https://opensource.org/licenses/${siteConfig.license}`,
    codeRepository: siteConfig.repoUrl,
    isAccessibleForFree: true,
    dateModified: buildDate,
    keywords: t.meta.keywords,
    author: {
      "@type": "Person",
      name: siteConfig.founderName,
    },
    publisher,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };

  const webSite = {
    "@type": "WebSite",
    name: "PythiaLabs",
    description: t.meta.description,
    url: `${base}/`,
    inLanguage: localeOrder.map((id) => locales[id].htmlLang),
    publisher,
    potentialAction: {
      "@type": "ReadAction",
      target: `${base}/`,
    },
  };

  const faqPage = {
    "@type": "FAQPage",
    mainEntity: t.faq.items.map((item) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.a,
      },
    })),
  };

  const graphNodes = [softwareApplication, faqPage];
  if (currentId === "en") {
    graphNodes.push(webSite);
  }

  const graph = {
    "@context": "https://schema.org",
    "@graph": graphNodes,
  };

  return `<script type="application/ld+json">${JSON.stringify(graph)}</script>`;
}

export function renderPage(currentId, year, buildDate) {
  const t = locales[currentId];
  const hrefs = pathsFor(currentId);
  const canonical = canonicalFor(currentId);
  const ogImage = `${siteConfig.canonicalOrigin.replace(/\/$/, "")}${siteConfig.ogImagePath}`;
  const ogLocale = t.ogLocale || t.htmlLang.replace("-", "_");
  const pilotHref = pilotMailto(siteConfig.pilotEmailSubject);
  const example = exampleDecisions[currentId] || exampleDecisions.en;

  const ogAlternateLocales = localeOrder
    .filter((id) => id !== currentId)
    .map(
      (id) =>
        `<meta property="og:locale:alternate" content="${escape(locales[id].ogLocale || locales[id].htmlLang.replace("-", "_"))}" />`,
    )
    .join("\n    ");

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
        `<li class="step"><div class="step-num" aria-hidden="true">${i + 1}</div><div class="step-body"><h3>${escape(s.name)}</h3><p>${inlineCodeToHtml(s.desc)}</p></div></li>`,
    )
    .join("");

  const founderVideoCards = siteConfig.founderVideos
    .map((v) => {
      const card = t.founderVideosBlock.cards[v.labelKey];
      return `<article class="video-card">
        <p class="video-card-eyebrow">${escape(card.name)}</p>
        <h3>${escape(card.headline)}</h3>
        <p class="video-card-desc">${escape(card.desc)}</p>
        <p><a class="btn btn-secondary" href="${utm(v.url, v.campaign)}" target="_blank" rel="noopener noreferrer">${escape(card.cta)}</a></p>
      </article>`;
    })
    .join("");

  const demoSeriesCards = siteConfig.demoSeries
    .map((v) => {
      const card = t.videoBlock.series[v.labelKey];
      return `<article class="demo-series-card">
            <div class="video-frame">
              <iframe
                src="${v.embedUrl}"
                title="${escape(`${card.label}: ${card.title}`)}"
                loading="lazy"
                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen
                referrerpolicy="strict-origin-when-cross-origin"></iframe>
            </div>
            <p class="video-card-eyebrow">${escape(card.label)}</p>
            <h3>${escape(card.title)}</h3>
            <p>${escape(card.desc)}</p>
            <p><a class="btn btn-secondary" href="${utm(v.url, v.campaign)}" target="_blank" rel="noopener noreferrer">${escape(card.cta)}</a></p>
          </article>`;
    })
    .join("");

  return `<!doctype html>
<html lang="${t.htmlLang}" translate="no">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#0b0d10" media="(prefers-color-scheme: dark)" />
    <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
    <title>${escape(t.meta.title)}</title>
    <meta name="description" content="${escape(t.meta.description)}" />
    <meta name="keywords" content="${escape(t.meta.keywords)}" />
    <meta name="author" content="${escape(siteConfig.founderName)}" />
    <meta name="application-name" content="PythiaLabs" />
    <meta
      name="audience"
      content="Developers, security engineers, platform teams, AI product teams, compliance reviewers" />
    <meta name="color-scheme" content="dark light" />
    <meta name="robots" content="index, follow" />
    <meta name="referrer" content="strict-origin-when-cross-origin" />
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data: https://img.shields.io; frame-src https://www.youtube-nocookie.com; connect-src 'self'; font-src 'self'; base-uri 'self'; form-action 'self'" />

    <link rel="canonical" href="${canonical}" />

    <meta property="og:site_name" content="PythiaLabs" />
    <meta property="og:title" content="${escape(t.meta.title)}" />
    <meta property="og:description" content="${escape(t.meta.description)}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="${canonical}" />
    <meta property="og:locale" content="${escape(ogLocale)}" />
    ${ogAlternateLocales}
    <meta property="og:image" content="${ogImage}" />
    <meta property="og:image:alt" content="${escape(t.meta.ogImageAlt)}" />
    <meta property="og:image:type" content="image/svg+xml" />
    <meta property="article:modified_time" content="${escape(buildDate)}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="${escape(siteConfig.twitterSite)}" />
    <meta name="twitter:title" content="${escape(t.meta.title)}" />
    <meta name="twitter:description" content="${escape(t.meta.description)}" />
    <meta name="twitter:image" content="${ogImage}" />
    <meta name="twitter:image:alt" content="${escape(t.meta.ogImageAlt)}" />

    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='28'%3E%E2%97%87%3C/text%3E%3C/svg%3E" />

    <link rel="dns-prefetch" href="https://github.com" />
    <link rel="dns-prefetch" href="https://www.youtube-nocookie.com" />
    <link rel="dns-prefetch" href="https://img.shields.io" />
    <link rel="preconnect" href="https://github.com" crossorigin />

    ${hreflangLinks}

    ${jsonLdGraph(currentId, canonical, buildDate)}

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
          <a href="#solution">${escape(t.nav.solution)}</a>
          <a href="#videos">${escape(t.nav.videos)}</a>
          <a href="#demo-proof">Demo</a>
          <a href="#use-cases">${escape(t.nav.useCases)}</a>
          <a href="#pilot-outcome">${escape(t.nav.pilot)}</a>
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
          <p class="hero-stakes">${escape(t.hero.stakesLine)}</p>
          <p class="hero-text">${escape(t.hero.body)}</p>
          <p class="hero-outcome-line">${inlineCodeToHtml(t.hero.outcomeLine)}</p>
          <p class="hero-tagline">${escape(t.hero.tagline)}</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="${utm(siteConfig.hookUrl, "hero_hook")}" target="_blank" rel="noopener noreferrer">${escape(t.cta.hook)}</a>
            <a class="btn btn-secondary" href="${utm(siteConfig.demoUrl, "hero_demo")}" target="_blank" rel="noopener noreferrer">${escape(t.cta.runDemo)}</a>
            <a class="btn btn-ghost" href="${utm(siteConfig.repoUrl, "hero_github")}" target="_blank" rel="noopener noreferrer">${escape(t.cta.secondary)}</a>
          </div>
          <p class="hero-start-here">
            <a href="#quickstart">${escape(t.hero.startHereLabel)} →</a>
          </p>
          <p class="hero-badges">
            <a href="${siteConfig.repoUrl}/stargazers" class="badge-link" target="_blank" rel="noopener noreferrer">
              <img src="https://img.shields.io/github/stars/${siteConfig.repoSlug}?style=flat-square&label=stars&color=0b0d10" alt="${escape(t.hero.starsAlt)}" loading="lazy" decoding="async" width="90" height="20" />
            </a>
            <a href="${siteConfig.repoUrl}/blob/main/LICENSE" class="badge-link" target="_blank" rel="noopener noreferrer">
              <img src="https://img.shields.io/github/license/${siteConfig.repoSlug}?style=flat-square&color=0b0d10" alt="License" loading="lazy" decoding="async" width="100" height="20" />
            </a>
            <a href="#cursor-ide" class="badge-link">
              <img src="https://img.shields.io/badge/MCP-ready-7cc4ff?style=flat-square&color=0b0d10" alt="${escape(t.hero.mcpBadgeAlt)}" loading="lazy" decoding="async" width="92" height="20" />
            </a>
            <a href="${siteConfig.repoUrl}/actions/workflows/ci.yml" class="badge-link" target="_blank" rel="noopener noreferrer">
              <img src="https://img.shields.io/github/actions/workflow/status/${siteConfig.repoSlug}/ci.yml?branch=main&style=flat-square&label=runnable%20demo&color=0b0d10" alt="Runnable demo CI status" loading="lazy" decoding="async" width="140" height="20" />
            </a>
          </p>
          <div class="hero-stats" role="region" aria-label="${escape(t.heroStats.ariaLabel)}">
            <div class="stat"><span class="stat-value">${siteConfig.showcaseScriptCount}</span><span class="stat-label">${escape(t.heroStats.showcases)}</span></div>
            <div class="stat rule" aria-hidden="true"></div>
            <div class="stat"><span class="stat-value">${siteConfig.testFileCount}</span><span class="stat-label">${escape(t.heroStats.tests)}</span></div>
            <div class="stat rule" aria-hidden="true"></div>
            <div class="stat"><span class="stat-value stat-value--license">${escape(t.heroStats.licenseValue)}</span><span class="stat-label">${escape(t.heroStats.licenseLine)}</span></div>
            <div class="stat rule" aria-hidden="true"></div>
            <div class="stat"><span class="stat-value">0</span><span class="stat-label">${escape(t.heroStats.llmLine)}</span></div>
          </div>
        </div>
      </section>

      <section id="if-you" class="section section-if-you">
        <div class="container">
          <h2>${escape(t.ifYou.title)}</h2>
          <ul class="if-you-list">${t.ifYou.items.map((s) => `<li>${escape(s)}</li>`).join("")}</ul>
        </div>
      </section>

      <section id="if-not-you" class="section section-if-not-you" aria-labelledby="if-not-you-title">
        <div class="container">
          <h2 id="if-not-you-title">${escape(t.ifNotYou.title)}</h2>
          <ul class="not-list">${t.ifNotYou.items.map((s) => `<li><span class="not-mark" aria-hidden="true">✕</span>${escape(s)}</li>`).join("")}</ul>
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

      <section id="pilot-outcome" class="section">
        <div class="container">
          <h2>${escape(t.pilotOutcome.title)}</h2>
          <p>${escape(t.pilotOutcome.intro)}</p>
          <ul class="value-stack pilot-outcome-list">${t.pilotOutcome.items
            .map(
              (s) =>
                `<li><span class="check" aria-hidden="true">✓</span><span>${escape(s)}</span></li>`,
            )
            .join("")}</ul>
          <p class="pilot-outcome-footnote">${escape(t.pilotOutcome.footnote)}</p>
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
          <div class="demo-series-grid">${demoSeriesCards}</div>
          <blockquote class="core-message">
            <p class="core-label">${escape(t.videoBlock.coreLabel)}</p>
            <p>${escape(t.videoBlock.core)}</p>
          </blockquote>
          <p><a href="${utm(siteConfig.demoUrl, "video_block_fallback")}" target="_blank" rel="noopener noreferrer">${escape(t.videoBlock.fallback)} →</a></p>
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
          <ul class="step-list">${mechanismSteps}</ul>
          <div class="two-col">
            <div class="card">
              <h3>${escape(t.solution.checksTitle)}</h3>
              <ul>${t.solution.checks.map(li).join("")}</ul>
            </div>
            <div class="card return-card">
              <h3>${escape(t.solution.returnsTitle)}</h3>
              <ul class="decisions">
                ${t.solution.returns
                  .map(
                    (item) =>
                      `<li class="decision-outcome decision-${escape(item.label.toLowerCase())}">
                        <span class="tag tag-${escape(item.label.toLowerCase())}">${escape(item.label)}</span>
                        <div>
                          <strong>${escape(item.title)}</strong>
                          <p>${escape(item.desc)}</p>
                        </div>
                      </li>`,
                  )
                  .join("")}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section id="artifact" class="section section-alt">
        <div class="container">
          <h2>${escape(t.artifact.title)}</h2>
          <p>${escape(t.artifact.introPlain)}</p>
          <details class="artifact-technical">
            <summary>${escape(t.artifact.technicalSummary)}</summary>
            <p>${inlineCodeToHtml(t.artifact.introTechnical)}</p>
          </details>
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
                `<article class="card"><h3>${escape(item.name)}</h3><p>${inlineCodeToHtml(item.desc)}</p></article>`,
            )
            .join("")}</div>
          <aside
            class="integration-repo-callout"
            aria-labelledby="integration-repo-note-heading">
            <h3 id="integration-repo-note-heading" class="integration-repo-callout-title">
              ${escape(t.integration.repoNoteTitle)}
            </h3>
            <p class="integration-repo-callout-body">${inlineCodeToHtml(t.integration.repoNote)}</p>
          </aside>
        </div>
      </section>

      <section id="cursor-ide" class="section section-alt section-ide-bridge" aria-labelledby="cursor-ide-title">
        <div class="container">
          <h2 id="cursor-ide-title">${escape(t.ideBridge.title)}</h2>
          <p>${inlineCodeToHtml(t.ideBridge.intro)}</p>
          <ul class="ide-bridge-list">${t.ideBridge.items.map((line) => `<li>${inlineCodeToHtml(line)}</li>`).join("")}</ul>
          <p class="ide-bridge-cta">
            <a class="btn btn-secondary" href="${utm(`${siteConfig.repoUrl}/blob/main/${siteConfig.mcpReadmePath}`, "ide_mcp_docs")}" target="_blank" rel="noopener noreferrer">${escape(t.ideBridge.docsCta)}</a>
          </p>
          <p class="ide-bridge-note">${escape(t.ideBridge.note)}</p>
        </div>
      </section>

      <section id="quickstart" class="section">
        <div class="container">
          <h2>${escape(t.quickstart.title)}</h2>
          <p>${escape(t.quickstart.intro)}</p>
          <ul class="step-list quickstart-list">${t.quickstart.steps
            .map(
              (s, i) =>
                `<li class="step"><div class="step-num" aria-hidden="true">${i + 1}</div><div class="step-body"><h3>${escape(s.name)}</h3><p>${inlineCodeToHtml(s.desc)}</p></div></li>`,
            )
            .join("")}</ul>
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

      <section class="section mid-cta" aria-label="Mid-page calls to action">
        <div class="container mid-cta-inner">
          <p class="mid-cta-line">${escape(t.midCta.line)}</p>
          <div class="cta-row cta-row--center">
            <a class="btn btn-primary" href="${pilotHref}" rel="noopener noreferrer">${escape(t.cta.primary)}</a>
            <a class="btn btn-secondary" href="${utm(siteConfig.demoUrl, "mid_demo")}" target="_blank" rel="noopener noreferrer">${escape(t.cta.demo)}</a>
            <a class="btn btn-ghost" href="${utm(siteConfig.repoUrl, "mid_github")}" target="_blank" rel="noopener noreferrer">${escape(t.cta.secondary)}</a>
          </div>
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
          <h3 class="comparison-vs-title">${escape(t.comparison.vsTitle)}</h3>
          <div class="card-grid comparison-vs-grid">${t.comparison.vsItems
            .map(
              (item) =>
                `<article class="card"><h4>${escape(item.name)}</h4><p>${escape(item.desc)}</p></article>`,
            )
            .join("")}</div>
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
              <p class="founder-verify">
                <a href="${siteConfig.founderGithub}" target="_blank" rel="noopener noreferrer">GitHub profile</a>
                · <a href="${siteConfig.repoUrl}/commits/main?author=safal207" target="_blank" rel="noopener noreferrer">Commits</a>
                · <a href="${siteConfig.demoUrl}" target="_blank" rel="noopener noreferrer">Runnable demo</a>
              </p>
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
                  `<details class="faq-item"><summary>${escape(item.q)}</summary><p>${inlineCodeToHtml(item.a)}</p></details>`,
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
            <a class="btn btn-primary" href="${pilotHref}" rel="noopener noreferrer">${escape(t.finalCta.primary)}</a>
            <a class="btn btn-secondary" href="${utm(siteConfig.demoUrl, "final_demo")}" target="_blank" rel="noopener noreferrer">${escape(t.finalCta.demo)}</a>
            <a class="btn btn-ghost" href="${utm(siteConfig.repoUrl, "final_github")}" target="_blank" rel="noopener noreferrer">${escape(t.finalCta.secondary)}</a>
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
          <div class="contact-panel">
            <div>
              <p class="cta-eyebrow">Start here</p>
              <h3>Send one risky agent workflow</h3>
              <p>Share the action your agent wants to take. I will help map it into proposal, evidence, and an ALLOW / BLOCK / ESCALATE trace.</p>
              <p class="contact-actions">
                <a class="btn btn-primary" href="mailto:${siteConfig.email}?subject=${encodeURIComponent(siteConfig.pilotEmailSubject)}" rel="noopener noreferrer">Email PythiaLabs →</a>
                <a class="btn btn-secondary" href="${utm(siteConfig.demoUrl, "contact_demo")}" target="_blank" rel="noopener noreferrer">Watch the demo →</a>
              </p>
            </div>
            <ul class="contact-list">
              <li><span>${escape(t.contact.labels.github)}</span><a href="${siteConfig.repoUrl}" target="_blank" rel="noopener noreferrer">${escape(siteConfig.repoUrl.replace(/^https?:\/\//, ""))}</a></li>
              <li><span>${escape(t.contact.labels.x)}</span><a href="${siteConfig.xUrl}" target="_blank" rel="noopener noreferrer">${escape(siteConfig.xHandle)}</a></li>
              <li><span>${escape(t.contact.labels.telegram)}</span><a href="${siteConfig.telegramUrl}" target="_blank" rel="noopener noreferrer">${escape(siteConfig.telegramHandle)}</a></li>
            </ul>
          </div>
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
        <p class="footer-meta">${escape(siteConfig.license)}-licensed · Open governance · Public roadmap</p>
        <p class="footer-links">
          <a href="${siteConfig.repoUrl}" target="_blank" rel="noopener noreferrer">GitHub</a>
          <a href="${siteConfig.repoUrl}/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">License (${escape(siteConfig.license)})</a>
          <a href="${siteConfig.repoUrl}/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener noreferrer">Contributing</a>
          <a href="${siteConfig.repoUrl}/blob/main/CODE_OF_CONDUCT.md" target="_blank" rel="noopener noreferrer">Code of Conduct</a>
          <a href="${siteConfig.repoUrl}/blob/main/SECURITY.md" target="_blank" rel="noopener noreferrer">Security</a>
          <a href="#milestones">Roadmap</a>
          <a href="${siteConfig.demoUrl}" target="_blank" rel="noopener noreferrer">Demo</a>
        </p>
      </div>
    </footer>
  </body>
</html>
`;
}
