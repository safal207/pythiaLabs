import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "../dist");
const onePagerPath = path.join(distDir, "agent-action-audit-kit-one-pager", "index.html");

const origin = "https://safal207.github.io/pythiaLabs";
const url = `${origin}/agent-action-audit-kit-one-pager/`;
const title = "Agent Action Audit Kit One-Pager — PythiaLabs";
const description =
  "One-page brief for auditing AI-agent actions: one workflow, one evidence chain, one trust report. Built for coding agents, CI/CD, incident response, and internal tool-calling workflows.";
const image = `${origin}/og.png`;

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebPage",
      name: title,
      description,
      url,
      isPartOf: {
        "@type": "WebSite",
        name: "PythiaLabs",
        url: origin,
      },
      about: [
        "AI agent safety",
        "agent action audit",
        "pre-execution safety gate",
        "causal audit",
        "AI governance",
      ],
      primaryImageOfPage: {
        "@type": "ImageObject",
        url: image,
      },
    },
    {
      "@type": "Service",
      name: "Agent Action Audit Kit",
      serviceType: "AI agent workflow audit",
      provider: {
        "@type": "Organization",
        name: "PythiaLabs",
        url: origin,
      },
      description:
        "A focused audit for one AI-agent workflow, action class, or trace/log sample. The output is a reviewer-ready evidence chain with ALLOW, BLOCK, or ESCALATE criteria and causal-validity findings.",
      areaServed: "Worldwide",
      audience: {
        "@type": "Audience",
        audienceType:
          "AI safety teams, platform engineering teams, security reviewers, compliance reviewers, and AI governance teams",
      },
    },
  ],
};

const seoHead = `
  <meta name="description" content="${description}" />
  <meta name="author" content="Aleksei Safonov" />
  <meta name="robots" content="index, follow" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <link rel="canonical" href="${url}" />
  <meta property="og:site_name" content="PythiaLabs" />
  <meta property="og:title" content="${title}" />
  <meta property="og:description" content="${description}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="${url}" />
  <meta property="og:image" content="${image}" />
  <meta property="og:image:alt" content="PythiaLabs Agent Action Audit Kit one-page brief" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@lim746048" />
  <meta name="twitter:title" content="${title}" />
  <meta name="twitter:description" content="${description}" />
  <meta name="twitter:image" content="${image}" />
  <script type="application/ld+json">${JSON.stringify(jsonLd)}</script>`;

const html = await readFile(onePagerPath, "utf8");

const withoutOldDescription = html.replace(
  /\n\s*<meta name="description" content="Agent Action Audit Kit: one workflow, one evidence chain, one trust report\." \/>/,
  "",
);

const updatedTitle = withoutOldDescription.replace(
  /<title>Agent Action Audit Kit — One-Pager<\/title>/,
  `<title>${title}</title>`,
);

const updated = updatedTitle.includes("application/ld+json")
  ? updatedTitle
  : updatedTitle.replace("  <style>", `${seoHead}\n  <style>`);

await writeFile(onePagerPath, updated);
console.log("Injected SEO metadata into Agent Action Audit one-pager.");
