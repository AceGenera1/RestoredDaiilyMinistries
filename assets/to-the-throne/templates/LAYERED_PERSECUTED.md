# Persecuted Church layered template — working SVG DRAFT

`layered_persecuted.py` produces a self-contained SVG with:
* A background image layer reconstructed from the exact Git-verified approved original, preserving its emblem and scenic footer, the approved four prayer icons and ornamental heading.
* Independent editable SVG text objects for date/edition, country, regional summary, four prayer columns, Scripture and sources. They can be opened in Inkscape without modifying the original artwork.
* A conspicuous draft-only watermark layer.

`test_layered_persecuted.py` checks that all layers and editable field nodes exist and prohibits final authorization flags. Tests never treat mock prayers or synthetic Scripture as publishable.

This is NOT a pixel-faithful recreation yet. Full editable approved map insertion, precise typography, complete Scripture overflow and visual signoff remain pending. Reuse the original reference PNG or stop; never create generic logo artwork. The SVG format is intended as a path toward reproducible design, NOT authorization to publish.

Example:
```bash
python assets/to-the-throne/templates/layered_persecuted.py assets/to-the-throne/templates/samples/persecuted-render-test.json --out /tmp/persecuted-layered-DRAFT.svg
```
