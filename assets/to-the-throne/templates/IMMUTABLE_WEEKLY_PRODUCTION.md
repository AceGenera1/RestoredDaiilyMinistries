# TTT production correction — NEVER RECREATE AN APPROVED DESIGN

## What was broken
A beautiful flattened graphic was called "locked", while the actual reusable
rendering pipeline remained unrelated to that image. Rebuilding the image with
a generative image model then reproduced the **old TTT-0001 matters** and
removed the **mandatory closing paragraph**. Previous image-size/brand pixel
tests did not catch this.

## Mandatory implementation contract
1. **Two distinct immutable inputs**: a verified, separately editable, clean
   artwork template (no old printed matter text), and this week's approved
   canonical editorial JSON. A finished PNG containing last week's content is
   **NOT** a clean art template and must never be used as the starting layer.
2. **One renderer only** for the Monday letter, operating directly on canonical
   typed fields. It cannot improvise the five matter identities, positions,
   factual synopses, Scriptural texts or source URLs.
3. **Fixed design geometry** from the explicitly approved improved graphic:
   emblem, parchment texture, frame, map style, signature, mountain artwork,
   navy/gold footer, date plaque, status bars and typography.
4. Variable fields are edition/date, FIVE newly approved matters, verified
   attributed charcoal/hand-drawn maps, Scripture, prayer focuses, sources.
5. The complete **original signoff paragraph** above the red prayer tagline
   is a REQUIRED structural field. The entire paragraph must fit, without
   changes, above the original signature and landscape.
6. **Two gates** on every run: first `editorial_lock.py` asserts edition,
   all five matter IDs/order, factual wording, verse references and full
   text, then the visual compositor must prove protected-artwork identity
   and zero clipping/overlap. No output if either fails. Never use image
   generation for factual text replacement.
7. Image-model output cannot be mechanically guaranteed to preserve fixed
   text or layout. It may be used only to create an explicitly reviewed new
   background artwork asset, never as a direct weekly fact/layout renderer.
8. **Do not claim 'production locked' until a true clean layered design
   source is present, this check is integrated into the chosen compositor,
   and two different weeks have been successfully rendered and compared.**

Run:
`python assets/to-the-throne/templates/test_editorial_lock.py`

Current status: the **editorial contract is enforced by tests**; the
previous graphic builder is still **NOT** approved for publishing. The
approved aesthetic exists in a flattened image; a true clean editable
production master must still be finished. No public publishing is implied.
