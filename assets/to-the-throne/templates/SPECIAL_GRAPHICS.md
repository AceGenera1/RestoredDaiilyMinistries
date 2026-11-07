# Remaining three graphic family drafts

`special_graphics.py` adds individual reference-locked, **DRAFT-ONLY** compositors for Praise Report, Persecuted Church Letter and Faith Friday.
All preserve the approved original logo/masthead and lower mountain/motto regions. They replace only relevant content areas with typed data and reject excessive text instead of silently clipping it. Praise and Persecuted require a map, and will display **VERIFIED MAP REQUIRED** in the draft when none is provided.

**These are not approved final layouts.** A flat-color center panel is a temporary editing scaffold. Their rendering cannot be published, converted to final, or substituted for the original approved master; do not present test mockups as production-ready TTT graphics.

Examples:
```bash
python special_graphics.py samples/praise-render-test.json --reference /path/to/approved/ttt-0001-wednesday-praise.png --out /tmp/ttt-praise-DRAFT.png
python special_graphics.py samples/persecuted-render-test.json --reference /path/to/approved/tttpc-0001-01-thursday-persecuted-church.png --out /tmp/ttt-persecuted-DRAFT.png
python special_graphics.py samples/faith-render-test.json --reference "/path/to/approved/To the Throne_ Faith Friday Prayer.png" --out /tmp/ttt-friday-DRAFT.png
```
The data examples are invented *test fixtures*, not ministry content.

To unlock production, recover or reconstruct separate clean editable original design layers, validate faithful map placement, original font and brand mark, proof long Scripture and five-real-matter data sets, and obtain visual acceptance. The user has explicitly suspended social posts for the current week; these drafts must never publish.
