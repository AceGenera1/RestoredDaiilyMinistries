# TTT production runner — single unified agent, draft-first

This directory is tooling for the **existing** To The Throne Ministry Agent, not a second agent or a new monitoring task.

## Status
- **Recording Brief PDF generator:** functioning and tested with synthetic input; navy/bronze/ivory locked appearance; five matters; complete Scripture; no coaching/uncertainty fields.
- **Public Source Sheet PDF generator:** functioning and tested with synthetic input; six pages with one matter per page and clickable sources.
- **Graphic pixel-change guard:** functioning; protects every pixel outside an explicitly allowed edit rectangle.
- **Monday heading color guard:** functioning for the existing 1122×1402 approved Monday geometry; rejects a red-colored matter-heading regression.
- **Reconstructed graphic renderer (render.py): NOT PRODUCTION-APPROVED.** It generates editable draft HTML but does not yet reproduce the ornate original PNGs pixel-for-pixel. No automatic publication based on it.

## Local setup and test
From repo root:

```bash
python -m pip install -r assets/to-the-throne/templates/requirements.txt
python assets/to-the-throne/templates/test_pipeline.py
python assets/to-the-throne/templates/package_qa.py assets/to-the-throne/templates/samples/canonical-demo.json --out ./ttt-preview
```

The canonical demo is **fabricated test data, not ministry research**. Never publish it.

The canonical record feeds two drafts plus structured graphic fields and QA status; do not hand-edit the PDFs independently, because that would reintroduce inconsistent facts.

## Before public publishing
1. Verify each factual claim against the precise linked source and approval. Do not treat source count as proof of independence.
2. Verify each Scripture quotation and full verse range against the properly labeled public-domain edition.
3. Confirm the actual image masters match the approved artwork, all maps are accurate, and the source line is legible.
4. Run pixel/color checks for authorized revisions and inspect rendered PDFs for clipping.
5. Only after Kris's explicit publication authorization, publish the approved files at their existing website paths and check the live site.
6. **Do not assume that passing automated structural tests proves factual accuracy or graphic fidelity.**

The original approved artwork stays in `../weekly-graphics/2026-10-26/`. The recording-brief and source-sheet PDF visual references are described in `documents/document-lock.json`. Never overwrite published assets from these scripts.
