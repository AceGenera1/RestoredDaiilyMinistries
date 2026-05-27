const API_URL = "https://script.google.com/macros/s/AKfycbyMpMm_C9r3yF16VVKRmxNQmCmQaiLEDkqezOTSwpSjSsg6CGCuTx1Iw0JfMA5GmnKF/exec?type=lessons";
const SITE_URL = "https://restoreddailyministries.org";
const OG_IMAGE = `${SITE_URL}/api/og-lesson?id=${encodeURIComponent(id)}`;

function esc(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function preview(text = "", limit = 220) {
  const clean = String(text).replace(/\s+/g, " ").trim();
  return clean.length > limit ? clean.slice(0, limit).replace(/\s+\S*$/, "") + "..." : clean;
}

function titleFrom(entry = "") {
  const first = String(entry).split(/\r?\n/).map(s => s.trim()).filter(Boolean)[0];
  return first ? preview(first, 90) : "Lessons from a Disciple";
}

export default async function handler(req, res) {
  const id = String(req.query.id || "").trim();
  const targetUrl = `${SITE_URL}/disciple.html#${encodeURIComponent(id)}`;

  let title = "Lessons from a Disciple";
  let description = "Real reflections, lessons, and encouragement from Restored Daily Ministries.";

  try {
    const response = await fetch(API_URL);
    const data = await response.json();
    const item = (data.entries || []).find(entry => entry.id === id || entry.slug === id);

    if (item) {
      title = titleFrom(item.entry);
      description = preview(item.entry || description);
    }
  } catch (error) {}

  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${esc(title)}</title>
  <meta name="description" content="${esc(description)}">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Restored Daily Ministries">
  <meta property="og:title" content="${esc(title)}">
  <meta property="og:description" content="${esc(description)}">
  <meta property="og:image" content="${OG_IMAGE}">
  <meta property="og:url" content="${targetUrl}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${esc(title)}">
  <meta name="twitter:description" content="${esc(description)}">
  <meta name="twitter:image" content="${OG_IMAGE}">

  <meta http-equiv="refresh" content="0;url=${targetUrl}">
</head>
<body>
  <p><a href="${targetUrl}">Open lesson</a></p>
</body>
</html>`);
}
