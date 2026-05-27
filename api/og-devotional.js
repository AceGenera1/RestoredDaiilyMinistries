const API_URL = "https://script.google.com/macros/s/AKfycbyMpMm_C9r3yF16VVKRmxNQmCmQaiLEDkqezOTSwpSjSsg6CGCuTx1Iw0JfMA5GmnKF/exec";

function esc(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function wrap(text = "", max = 44, lines = 4) {
  const words = String(text).replace(/\s+/g, " ").trim().split(" ");
  const out = [];
  let line = "";

  for (const word of words) {
    if ((line + " " + word).trim().length > max) {
      if (line) out.push(line);
      line = word;
    } else {
      line = (line + " " + word).trim();
    }
    if (out.length >= lines) break;
  }

  if (line && out.length < lines) out.push(line);
  return out;
}

function preview(text = "", limit = 190) {
  const clean = String(text).replace(/\s+/g, " ").trim();
  return clean.length > limit ? clean.slice(0, limit).replace(/\s+\S*$/, "") + "..." : clean;
}

export default async function handler(req, res) {
  const id = String(req.query.id || "").trim();

  let title = "Restored Daily Devotional";
  let description = "Daily biblical encouragement from Restored Daily Ministries.";

  try {
    const response = await fetch(API_URL);
    const data = await response.json();
    const item = (data.devotionals || []).find(d => d.id === id || d.slug === id);

    if (item) {
      title = item.subject || title;
      description = preview(item.message || description);
    }
  } catch (error) {}

  const titleLines = wrap(title, 30, 2);
  const descLines = wrap(description, 52, 4);

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="630" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#101A2E"/>
      <stop offset="52%" stop-color="#13233F"/>
      <stop offset="100%" stop-color="#1F4F46"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="15%" r="70%">
      <stop offset="0%" stop-color="#F8D987" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#F8D987" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#glow)"/>
  <rect x="48" y="48" width="1104" height="534" rx="34" fill="#FFF8EA" opacity="0.96"/>
  <rect x="74" y="74" width="1052" height="482" rx="24" fill="none" stroke="#D7A84F" stroke-width="4"/>

  <text x="600" y="128" text-anchor="middle" font-family="Georgia, serif" font-size="38" font-weight="700" fill="#13233F">
    Restored Daily Ministries
  </text>
  <text x="600" y="166" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="20" font-weight="700" letter-spacing="4" fill="#8A621D">
    DAILY DEVOTIONAL
  </text>

  ${titleLines.map((line, i) => `
  <text x="600" y="${250 + i * 58}" text-anchor="middle" font-family="Georgia, serif" font-size="50" font-weight="700" fill="#101A2E">
    ${esc(line)}
  </text>`).join("")}

  ${descLines.map((line, i) => `
  <text x="600" y="${390 + i * 34}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="25" fill="#2B394F">
    ${esc(line)}
  </text>`).join("")}

  <text x="600" y="535" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" fill="#8A621D">
    Restored by Grace • Renewed Daily • Sent on Mission
  </text>
</svg>`;

  res.setHeader("Content-Type", "image/svg+xml; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=3600, s-maxage=3600");
  res.status(200).send(svg);
}
