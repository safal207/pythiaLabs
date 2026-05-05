// Generates a 1200x630 SVG OpenGraph card.
// SVG OG images are accepted by most major scrapers (Twitter/X, LinkedIn,
// Telegram, Slack). Inline-fonts are avoided; system sans-serif renders
// adequately when scrapers rasterize.

export function renderOgSvg() {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b0d10"/>
      <stop offset="1" stop-color="#11151a"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="-10%" r="60%">
      <stop offset="0" stop-color="#4ea6ff" stop-opacity="0.25"/>
      <stop offset="1" stop-color="#4ea6ff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#glow)"/>
  <g font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" fill="#e6edf3">
    <text x="80" y="130" font-size="32" fill="#7cc4ff" letter-spacing="2" font-weight="500">◇  PYTHIALABS</text>
    <text x="80" y="260" font-size="64" font-weight="700">Evidence Gates for</text>
    <text x="80" y="340" font-size="64" font-weight="700">AI-Agent Actions</text>
    <text x="80" y="420" font-size="28" fill="#9aa6b2">Open-source policy engine · ALLOW / BLOCK / ESCALATE</text>
    <text x="80" y="460" font-size="28" fill="#9aa6b2">Replayable evidence · Pre-execution · Apache-2.0</text>
  </g>
  <g transform="translate(80, 530)" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="22">
    <rect x="0" y="0" rx="14" ry="14" width="120" height="40" fill="none" stroke="#3fb950" stroke-width="2"/>
    <text x="60" y="27" fill="#3fb950" text-anchor="middle">ALLOW</text>
    <rect x="140" y="0" rx="14" ry="14" width="120" height="40" fill="none" stroke="#f85149" stroke-width="2"/>
    <text x="200" y="27" fill="#f85149" text-anchor="middle">BLOCK</text>
    <rect x="280" y="0" rx="14" ry="14" width="160" height="40" fill="none" stroke="#d29922" stroke-width="2"/>
    <text x="360" y="27" fill="#d29922" text-anchor="middle">ESCALATE</text>
  </g>
  <text x="1120" y="600" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="20" fill="#57606a" text-anchor="end">github.com/safal207/pythiaLabs</text>
</svg>
`;
}
