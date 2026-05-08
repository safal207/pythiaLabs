import { siteConfig } from "./config.mjs";
import { localeOrder, locales } from "./i18n.mjs";

const origin = () => siteConfig.canonicalOrigin.replace(/\/$/, "");

function urlFor(id) {
  return id === "en" ? `${origin()}/` : `${origin()}/${id}/`;
}

const standaloneUrls = [
  {
    loc: `${origin()}/agent-action-audit-kit-one-pager/`,
    changefreq: "monthly",
    priority: "0.9",
  },
];

export function renderSitemap(today = new Date().toISOString().slice(0, 10)) {
  const alternates = (currentId) =>
    localeOrder
      .map(
        (id) =>
          `      <xhtml:link rel="alternate" hreflang="${locales[id].htmlLang}" href="${urlFor(id)}"/>`,
      )
      .concat(`      <xhtml:link rel="alternate" hreflang="x-default" href="${urlFor("en")}"/>`)
      .join("\n");

  const localizedUrls = localeOrder
    .map(
      (id) => `  <url>
    <loc>${urlFor(id)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>${id === "en" ? "1.0" : "0.8"}</priority>
${alternates(id)}
  </url>`,
    )
    .join("\n");

  const standalone = standaloneUrls
    .map(
      (entry) => `  <url>
    <loc>${entry.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${entry.changefreq}</changefreq>
    <priority>${entry.priority}</priority>
  </url>`,
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
${localizedUrls}
${standalone}
</urlset>
`;
}

export function renderRobots() {
  return `User-agent: *
Allow: /

Sitemap: ${origin()}/sitemap.xml
`;
}
