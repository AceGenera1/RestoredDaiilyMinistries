const SITE_URL = "https://restoreddailyministries.org";
const API_URL = "https://script.google.com/macros/s/AKfycbyMpMm_C9r3yF16VVKRmxNQmCmQaiLEDkqezOTSwpSjSsg6CGCuTx1Iw0JfMA5GmnKF/exec";

const OG_IMAGE = `${SITE_URL}/social-preview-devotional.png?v=1000`;

function esc(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function preview(text = "", limit = 220) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  return clean.length > limit ? clean.slice(0, limit).replace(/\s+\S*$/, "") + "..." : clean;
}

export default async function handler(req, res) {
  const id = String(req.query.id || "").trim();
  const targetUrl = `${SITE_URL}/devotional.html#${encodeURIComponent(id)}`;
  const shareUrl = `${SITE_URL}/api/share-devotional?id=${encodeURIComponent(id)}&fresh=1000`;

  let title = "Read Today’s Daily Encouragement";
  let description = "Biblical hope, prayer, and encouragement for your walk with Jesus Christ.";

  try {
    const response = await fetch(API_URL);
    const data = await response.json();

    const item = (data.devotionals || []).find(d => {
      return d.id === id || d.slug === id || d.shareSlug === id || d.anchor === id;
    });

    if (item) {
      title = item.subject || title;
      description = preview(item.message || description);
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
<meta property="og:image:secure_url" content="${OG_IMAGE}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="${shareUrl}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(description)}">
<meta name="twitter:image" content="${OG_IMAGE}">

<script>
window.location.replace("${targetUrl}");
</script>
</head>
<body>
<p><a href="${targetUrl}">Open devotional</a></p>
</body>
</html>`);
}
