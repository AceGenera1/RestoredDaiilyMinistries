# TTT Monday reproducibility — working engineering checkpoint (Nov 9, 2026)

**Do not treat this as production lock or publish the draft PNG.**

A NEW deterministic, non-image-generation renderer was implemented and tested in the conversation's downloadable `TTT-Deterministic-Renderer-Engineering-QA.zip`. It is supplied there as Python source code, exact approved-style reference PNG, TTT-0003 canonical editorial JSON, separate map provenance JSON, geographic shapefile, sample output and QA proof. **The executable source is not yet committed to this GitHub repository**. Next action is to import that reviewed source into the repository rather than rebuilding another renderer from scratch.

## Confirmed local QA

- **Identical inputs => byte-identical PNG outputs.** SHA256 for TTT-0003 draft preview: `7f543549e0bb65988fe3c77e64c076d15991b52b50956c6303543f7e99f84795`.
- A synthetic TTT-0004 fixture changed the date, one matter and map position WITHOUT changing the renderer's layout code. It is labeled SYNTHETIC and NOT a future news report.
- Original approved emblem/masthead, signature, landscape and motto were pixel-preserved.
- Correct approved TTT-0003 matter IDs/order: `yemen-sanaa`, `sudan-shelter`, `gaza-flood`, `florida-brevard`, `ukraine-school`.
- Incorrect edition, altered prayer focuses or Scripture, missing full traditional closing and mismatched per-week map manifest all fail the tests.
- The exact TTT-0003 canonical JSON remains at `assets/to-the-throne/templates/approved/TTT-0003-canonical.json`. The independent release gate in `archive_release_gate.py` continues to block publication.

## Important limitations, no euphemisms

1. **VISUAL NOT YET ACCEPTED.** This technical preview has simpler GIS ink-outline mini-maps; they still do not reproduce the user's richer charcoal/hand-drawn map aesthetic. The candidate is NOT suitable for public release.
2. The approved improved reference is currently flattened (it embeds last week's facts). A clean layered background needs design refinement so the matter area has the same rich parchment texture as the final approved master. Do not try to extract background from lettered pixels, which caused severe ghost-text artifacts.
3. The candidate currently reuses permanent logo/header/footer from the approved reference. Future-date plaque replacement and second-week typography have been machine-tested, not visually signed off.
4. Source code is available via the user-visible conversation download but needs import into GitHub, code review, a fully approved proper clean master art asset and CI tests.
5. This checkpoint is **not proof that two real approved weeks** were produced: TTT-0004 test is explicitly synthetic.
6. Do not invoke image-generation for factual overlays, and do not replace the old generator's code with an untested approximation. Maintain one canonical editorial source of truth.

## User directive

Once a visual design is approved, keep it fixed; change only approved fields. Every future Monday graphics run must pass both **exact-week editorial record matching** and **visual-source protection + no overflow**. The complete closing paragraph is mandatory. No website/social publication without explicit release authorization.
