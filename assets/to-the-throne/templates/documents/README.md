# To The Throne — document production locks

These two uploaded PDF versions are the **authoritative visual references**:

- **Weekly Recording Brief v1.0 LOCKED:** US Letter, 2 pages, page 1 matters 01–02 and page 2 matters 03–05. Centered masthead, gold subtitle and numbers, navy header panels, pale-ivory label column. The uploaded document shows Location, Status, Key Verified Details and Watch / Uncertainty.
- **Public Source Sheet v1.1 LOCKED:** US Letter, 6 pages: cover + one matter per page. Navy numbered banner, ivory headline panel, factual basis, up to three grounded source blocks (publication/update date, precisely what they establish, actual clickable source URL), public status, last verified, navy/gold motto. Cover includes purpose, how-to-read and source standard.

## Unresolved instruction conflict — do not silently reconcile
The user's **uploaded Recording Brief v1.0** does **not** contain Prayer Focus or Scripture and includes Watch / Uncertainty. The **current unified agent's November 2 locked text** instead requires Prayer Focus plus complete Scripture and prohibits a Watch / Uncertainty section.

This is a **release blocker for the Recording Brief**, NOT permission to replace the user's uploaded design with an older draft. Confirm with Kris which content structure is final before adding executable document generation.

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
