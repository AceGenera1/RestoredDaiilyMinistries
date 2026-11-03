# To The Throne — controlled production templates (draft infrastructure)

**Status:** production tooling installed; reconstructed graphic layouts are **NOT YET VISUALLY APPROVED**. Existing approved October 26 PNGs remain the authority. No published image is changed by these files.

## Single-agent architecture
These are assets and scripts for the **existing To The Throne Ministry Agent**, not another automation. Keep all research, approval, publishing and archive work in that agent.

## Approved visual references (immutable)
- Monday letter: `../weekly-graphics/2026-10-26/ttt-0001-weekly-letter.png`
- Wednesday intercession: `../weekly-graphics/2026-10-26/ttt-0001-wednesday-intercession.png`
- Praise: `../weekly-graphics/2026-10-26/ttt-0001-wednesday-praise.png`
- Persecuted Church: `../weekly-graphics/2026-10-26/tttpc-0001-01-thursday-persecuted-church.png`
- Faith Friday: `../weekly-graphics/2026-10-26/To the Throne_ Faith Friday Prayer.png`
- Social variants: the corresponding `*-social-share.png` files in the same folder.

These are **reference PNGs**, not layered source templates. Do not claim the output of this new renderer is pixel-identical to them without visual approval.

## Contents
- `brand-lock.json`: brand/source attribution rules, reference image paths, and protected elements.
- `render.py`: editable, data-driven, six-format HTML renderer; optional screenshot export with Playwright.
- `validate.py`: schema checks for required source attributions, distinct scripture references, status and publication safeguards.
- `samples/*.json`: deliberately NON-PUBLISHABLE example content for each output type.

## How to test
From the repository root:

```bash
python assets/to-the-throne/templates/validate.py assets/to-the-throne/templates/samples/weekly-five.json
python assets/to-the-throne/templates/render.py assets/to-the-throne/templates/samples/weekly-five.json --out /tmp/ttt-preview.html
# Optional PNG preview if Playwright and Chromium are installed:
python assets/to-the-throne/templates/render.py assets/to-the-throne/templates/samples/weekly-five.json --out /tmp/ttt-preview.html --png /tmp/ttt-preview.png
```

All sample payloads are `approved: false`. **The renderer refuses publication-style output to the live weekly-graphics folder and does not commit anything itself**. Approved factual payloads must be explicitly marked, independently verified, and reviewed by Kris. Web deployment requires separate explicit authorization.

## Small changes to approved PNGs
For amendments to *existing* artwork, edit only the specified text region with a deterministic overlay tool, and compare every pixel outside that region to the approved input. Never re-run an image generator on the entire image for a sources-line or color-only edit. If there is insufficient room, stop and ask for a revised layout approval. The template renderer is for creating editable future drafts; it is not a pretext to replace the original designs.

## Remaining release gate
Before enabling production output, compare previews of **all six formats** against their approved October 26 references. Confirm exact emblem/map treatments, footer, signature, heading colors, typography, source note and spacing with Kris. Only then mark a template version approved and connect it to the unified agent.
