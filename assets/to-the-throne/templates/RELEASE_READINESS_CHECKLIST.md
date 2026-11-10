# TO THE THRONE — RELEASE READINESS CHECKLIST
**Opened:** November 9, 2026  
**Release focus:** TTT-0003 Monday Weekly Intercession Letter and complete Monday episode kit  
**Control rule:** A checkmark requires the exact evidence listed below. “Built,” “locked,” and “CI green” are **not** substitutes for visual or editorial acceptance.

## Hard rules
1. **Do not create new artwork by image-generating an entire finished weekly letter.**
2. Never take a previous week's *content-filled* PNG and cover it with rectangles. The clean master must have no old weekly facts baked into the dynamic area.
3. The same compiled master/layout/fonts/map treatment must be reused for each week, with fields changed only through an approved typed editorial record.
4. The mandatory complete original closing paragraph and source notice must remain legible, above the signature/mountains/motto.
5. Full WEB text must be checked verbatim, not invented or truncated. Five *distinct* verses must match the approved TTT-0003 record.
6. Do not claim the geographic illustrations are historically, geographically, or artistically verified without evidence.
7. **No public publication without express user publication authorization.** TTT-0003 editorial approval is already recorded, and must not be requested again merely because the artwork failed.
8. Recording brief and sources PDF must not be blocked by illustration work. Wednesday and Friday developments must not be fabricated for a Monday package.

## Evidence ledger — items to close, in this order
**Status vocabulary:** VERIFIED = result + evidence link in the repository; IN PROGRESS = actual file/test exists, but acceptance missing; BLOCKED = missing prerequisite; NOT STARTED = no adequate implementation in repo.

| ID | Requirement | Current state | Completion evidence required |
|---|---|---|---|
| A01 | Inventory user-approved Monday look, all five graphic families, and production code | **VERIFIED** | `approved-master-lock.json`; `visual-design-acceptance-2026-11-09.json`; `DETERMINISTIC_RENDERER_ENGINEERING_HANDOFF.md` |
| A02 | Freeze exactly five approved TTT-0003 matters, prayer focuses, Scripture, source provenance and *full* closing | **VERIFIED — field-validation stage** | `approved/TTT-0003-canonical.json`; passing `test_editorial_lock.py` in GitHub Actions; no release implied |
| A03 | Import actual working deterministic renderer **source** + dependencies from engineering QA ZIP into GitHub, removing reliance on this chat | **IN PROGRESS: recovered ZIP source independently rerun locally; GitHub import pending** | Executable source, geography manifest, asset dependencies, runnable README in repo; reproducible GitHub CI from clean checkout |
| A04 | Produce genuine **clean Monday illustrated artwork layers** (no baked-in former matter text); retain exact emblem, border, signoff, mountains, navy/gold motto | **BLOCKED** | Layered clean master (SVG/design file); original protected-region pixel/diff report; **no flat pasted content rectangle** |
| A05 | Standardize the five charcoal/hand-drawn map slots and independently verify geographic positioning/provenance | **BLOCKED: simplified GIS map draft only** | Five region map assets with data source, bounds, marker coordinates, approved illustrated treatment and no wrong labels |
| A06 | Implement reusable fixed Monday geometry, type scale, colors, status badges, five variable sections, maps, source line and closing paragraph | **IN PROGRESS: draft renderer exists, stylistic acceptance fails** | Layout/render configuration; visual overlay comparing approved aesthetic vs correctly populated TTT-0003; zero clipping/ghost text |
| A07 | Prove output is **deterministic** across identical inputs and correct across two different editions | **IN PROGRESS: local synthetic proof; CI production proof missing** | CI renders TTT-0003 twice with identical SHA-256, then a visibly distinct **SYNTHETIC** second-week fixture with same art; exact input metadata, all checks passing |
| A08 | Automated failure tests for wrong edition, wrong five matters/order, truncated WEB text, missing closing, wrong map manifest, ghost text and overlaps | **IN PROGRESS** | Tests fail for deliberate defects and pass clean data; screenshots + machine-readable QA JSON. Existing editorial negative tests alone don't satisfy visual QA |
| A09 | Complete **real TTT-0003** illustrated Monday PNG and print PDF with exact approved facts and finished visual master | **BLOCKED by A03–A08** | Direct phone-friendly PNG, PDF, visual review, checksum manifest; no synthetic test labels or substitute old matters |
| A10 | Validate Episode Recording Brief and Public Sources PDFs for this approved edition | **IN PROGRESS: generated PDFs previously shared; final package checks pending** | PDFs with correct five matters, 2–3 sentence reportable paragraphs, Prayer Focus, full distinct WEB verses; sources 6 pages, correct date/URLs, clickable links, no internal coaching |
| A11 | Build a complete private **Monday episode package** without invented Wednesday/Friday developments | **IN PROGRESS: previous ZIP exists but illustrated Monday image failed quality** | One ZIP containing exact final Monday letter PNG/PDF, brief, source PDF, manifest; all files open and hashes verify |
| A12 | User's final visual review and approval of the **correctly populated** revised TTT-0003 Monday letter | **BLOCKED by A09** | User reviews actual TTT-0003 result; this is NOT a new request for approval of already-approved Sunday/Monday facts |
| A13 | Website weekly archive + connected archive Sheet deployment | **NOT AUTHORIZED for TTT-0003** | Express publication approval, working deployed individual URLs, correct 5-item resource listing as resources become available, archive sheet matched, screenshots/link test |
| A14 | Wednesday, Persecuted Church, Praise, and Faith Friday production masters | **SEPARATE WORKSTREAM: draft layered candidates exist, not individually production-locked** | Each approved style tested with fresh non-synthetic content and asset provenance; do not confuse Monday clearance with other four clearance |
| A15 | Scheduled agent production handoff | **PARTIALLY IMPLEMENTED** | One existing agent; approved record linked; documented command paths + successful scheduled-run artifact delivery. Hourly checking alone is not proven continuous unattended design production |

## Closure report template (required every time)
```
ID: A##
STATUS: VERIFIED / IN PROGRESS / BLOCKED / NOT STARTED
WHAT ACTUALLY CHANGED:
PROOF: exact GitHub commit/Action run + downloadable output/test artifact
VISUAL ACCEPTANCE: yes/no/not applicable
FACTUAL/SCRIPTURE ACCEPTANCE: yes/no/not applicable
NEXT BLOCKER:
```
Never mark an item VERIFIED on the basis of an uninspected generated image, a synthetic fixture alone, or an inaccessible old sandbox link.

## Priority sequence for Monday episode delivery
- **Lane 1 (nonblocking now):** A02 → A10 → provide the fully verified Recording Brief and Public Sources PDFs. Preserve approved facts; no republishing without authorization.
- **Lane 2 (visual engineering):** A03 → A04 → A05 → A06 → A07 → A08 → A09 → A12.
- **Lane 3 (integration):** A11 → A13 (only after publication authorization) → A15.
- **After Monday:** A14, one primary design family at a time.

## Current objective evidence
- `assets/to-the-throne/templates/approved/TTT-0003-canonical.json`: five approved matter identities, WEB verse text/reference, and full closing.
- `assets/to-the-throne/templates/editorial_lock.py` and `test_editorial_lock.py`: negative tests on content drift.
- `assets/to-the-throne/templates/approved-master-lock.json`: SHA-locked original PNG refs, *not* clean source layers.
- `assets/to-the-throne/templates/DETERMINISTIC_RENDERER_ENGINEERING_HANDOFF.md`: local two-week **synthetic** test passed, but code absent from repo and map/background appearance not accepted.
- `assets/to-the-throne/templates/archive_release_gate.py`: requires checked canonical editorial record and typed renderer payload before review packaging, not proof of visual quality.
- GitHub Actions template safeguards passed November 9; see repository Actions for actual run and SHA. **Passing tests do not mean the graphic master is finished.**

**Exit condition:** TTT-0003 is NOT "complete" until A03–A12 have acceptable evidence. Nothing is "permanently locked" until a separate genuine future-week content package is rendered through the exact same source without modifying the master. The first real future week is itself a release test; synthetic weekly fixture does not count as that real-world proof.

## Evidence update — recovered and rerun renderer (November 9)
- Recovered exact `TTT-Deterministic-Renderer-Engineering-QA.zip` from the conversation attachment backing files. It contains `render_monday.py` (15,021 bytes), `test_regression.py` (3,356 bytes), TTT-0003 canonical JSON, TTT-0003 map manifest, Natural Earth shapefile bundle and raster visual reference.
- **Reran** `python test_regression.py` in a fresh extracted directory: **PASS**. Identical-output SHA-256: `7f543549e0bb65988fe3c77e64c076d15991b52b50956c6303543f7e99f84795`.
- Source SHA-256: `ed3835b2b10edae909a026c86924fe95341459c3e44b7f69f81f2623b756a45e`; test SHA-256: `0b16788e965c1761f35b4dd3c472ea7f79a3abc5bbf2a0988ab3e714af43f3dd`.
- A self-contained verified engineering ZIP (including machine-readable `RELEASE-READINESS-QA.json`) is available in this project's November 9 chat. **This is not a repository import**. A03 cannot be marked VERIFIED until the source and required reference and geography assets run from a fresh GitHub checkout.
- Current visual acceptance is still **NO** because map treatment is geographic line art rather than approved charcoal artwork and central parchment layer has not been accepted.
