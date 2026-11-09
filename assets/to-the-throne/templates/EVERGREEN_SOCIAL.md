# Approved evergreen social graphics: no redesign required

The four approved social-share images are **evergreen**, not tied to a particular week's dates or data. They contain a general call to intercession rather than the five matters. The safest production approach is to reuse the **identical Git-verified PNG master bytes** and place weekly reporting details in the accompanying approved social caption / weekly archive link.

Run `python social_evergreen.py --out /tmp/ttt-social-staging`.

This:
- verifies the approved Git blob SHA for each of Monday, Wednesday, Praise and Persecuted Church;
- copies all four ORIGINAL PNG files unchanged;
- produces a small original-only contact sheet and a manifest;
- never posts, never overwrites public files and never authors a weekly claim.

**Decision:** The previously created `layered_social.py` SVG overlays are experimentation-only, **deprecated for weekly social production**. Visual comparison showed those reconstructed social versions overwrite distinctive approved banners and are not faithful. Do not publish them. No social-media publication is scheduled or authorized by this tool.

If the ministry approves a NEW dated or geographically specific social design later, create a distinct reference-locked master, obtain explicit design signoff and test it separately. Do not silently modify these evergreen originals.
