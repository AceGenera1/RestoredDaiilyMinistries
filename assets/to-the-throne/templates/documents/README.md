# To The Throne — document production locks

These two uploaded PDF versions are the **authoritative visual references**:

- **Weekly Recording Brief v1.0 LOCKED:** US Letter, 2 pages, page 1 matters 01–02 and page 2 matters 03–05. Centered masthead, gold subtitle and numbers, navy header panels, pale-ivory label column. The uploaded document shows Location, Status, Key Verified Details and Watch / Uncertainty.
- **Public Source Sheet v1.1 LOCKED:** US Letter, 6 pages: cover + one matter per page. Navy numbered banner, ivory headline panel, factual basis, up to three grounded source blocks (publication/update date, precisely what they establish, actual clickable source URL), public status, last verified, navy/gold motto. Cover includes purpose, how-to-read and source standard.

## Final content decision — LOCKED November 3, 2026
Kris confirmed the latest November 2 recording-brief fields as the authoritative content structure, while preserving the supplied v1.0 PDF's navy/bronze/ivory visual design:

- Exactly five numbered matters with Location, Status, **Key Verified Details**, **Prayer Focus**, and **complete Scripture text plus reference** for each.
- **No Watch / Uncertainty or Known Limitations section.**
- **No coaching**, suggested introductions, transitions, written prayers, or closing invitations.
- Allow pages to grow if full Scripture requires space; never truncate verses, compress to unreadable text, or change the visual identity.
- This supersedes the uploaded PDF's *field placeholders*, not its approved layout and color design.

## Production rules
- Reuse existing unified To The Throne Ministry Agent; no new agent.
- Treat the supplied PDFs as the visual masters, not as content with placeholders to publish.
- No invented source links, summaries, verse text or approval status.
- Public Source Sheet must contain factual support only: no prayer, Scripture, internal uncertainty blocks, editorial advice, or backstage process notes.
- Validate exact matter order and IDs across the Weekly Five graphic, recording brief and source sheet.
- Render PDFs and inspect page images after every change. Check pagination, text overflow, and clickable source links.
- Keep all generated documents in a draft location until both content and publication permission are granted.
- Do not replace existing public PDFs just to establish new templates.

See `document-lock.json` for structural and QC rules. The PDF bytes are currently conversation uploads; their exact originals should be committed into a reference-assets directory separately if binary upload is supported, instead of recreating them by memory.


## Implemented PDF generator (draft-only)
`documents.py` produces actual PDF documents from structured JSON using ReportLab:
- Recording Brief: navy/bronze/ivory panels, 5 matters in order, Key Verified Details, Prayer Focus, and complete Scripture. Begins matter 03 on a new page, preserving the reference two-page arrangement **when content fits**; long full passages expand to additional pages without shortening them.
- Public Source Sheet: front matter plus one page per matter (6 pages total), navy/ivory numbered banner, source publication dates, claim-by-claim attribution and actual clickable HTTPS links.
- `--qa` uses PyMuPDF to check required output text, source hyperlinks, absent banned sections, matter count, and page count. A longer Source Sheet that overflows its approved one-matter-per-page design fails rather than silently shifting pages.

Install `reportlab`, `pymupdf`, and `Pillow`; all tools use ordinary Python 3.

Examples (run from the repository root):

```bash
python assets/to-the-throne/templates/documents/documents.py INPUT-RECORDING.json --kind recording_brief --out /tmp/TTT-recording-DRAFT.pdf --qa
python assets/to-the-throne/templates/documents/documents.py INPUT-SOURCES.json --kind public_source_sheet --out /tmp/TTT-sources-DRAFT.pdf --qa
python assets/to-the-throne/templates/test_pipeline.py
```

## Canonical weekly package
`../package_qa.py` reads one canonical five-matter JSON record and creates draft recording and source PDFs, a structured graphic payload, an HTML graphic preview, and `QA-DRAFT.json`. The graphic HTML preview is *NOT* pixel-faithful and cannot be published until the approved graphic-production layout is fully matched. A successful PDF QA test does not verify that events, sources, or Scripture are factually correct; those still require the locked research/approval process.

```bash
python assets/to-the-throne/templates/package_qa.py CANONICAL-WEEK.json --out /tmp/ttt-draft-package
```

**Safety gates:** no automatic GitHub publishing, no modification of the active automation, no overwriting weekly archive assets, no invented Bible text or source URLs, and no premature claims that reconstructed graphics are production-ready.
