# Monday / Wednesday reference-locked graphic renderer (DRAFT)
- `locked_graphics.py` rebuilds only the editable middle panel and date while preserving the approved monogram masthead and mountain/signature/footer pixels from the exact supplied reference PNG.
- Monday reference: `assets/to-the-throne/weekly-graphics/2026-10-26/ttt-0001-weekly-letter.png` (1122 x 1402).
- Wednesday reference: `assets/to-the-throne/weekly-graphics/2026-10-26/ttt-0001-wednesday-intercession.png` (1086 x 1448).
- Both formats use navy lettering and bronze-orange matter headings, dedicated per-matter map slots, Prayer Focus, Scripture, status colors and source attribution.
- Missing maps in draft mode show a TEST/placeholder block. Real publication must use geographically verified maps; the renderer intentionally cannot generate a final graphic.
- Inputs are JSON per the corresponding `samples/*-render-test.json`. Use only approved accurate content and never publish synthetic samples.
- Requires Python 3 + Pillow and fonts commonly installed in Linux. The code is not a guarantee of exact typography across machines.
- Test: `python locked_graphics.py samples/monday-render-test.json --reference ../weekly-graphics/2026-10-26/ttt-0001-weekly-letter.png --out /tmp/monday-draft.png --draft`
- The original weekly PNGs are untouched; layouts need further visual QA, especially row text density, original source-footer residue and long WEB Scripture passages. No final release without a documented visual signoff.
