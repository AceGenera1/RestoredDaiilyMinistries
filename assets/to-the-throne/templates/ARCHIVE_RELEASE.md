# Complete weekly release preflight — no publishing
Run `archive_release_gate.py` only once the complete approved five-item weekly set has been assembled. A separate `release-manifest.sample.json` documents the required fields.

* It requires explicit weekly research, visual, and publication approval, and individually approved matching-edition assets.
* Rejects missing files, drafts/test content, checksum mismatches, wrong dates/edition, broken PDFs/graphics, a non-six-page public source sheet, missing clickable source links, and incomplete weekly resource count.
* Outputs an immutable review ZIP with a checksum manifest, **not** a website publication or social post.
* Does not verify the factual truth of a report, accessibility of external URLs, a map's real-world accuracy, or the verbatim correctness of Scripture. Human checking is still necessary.
* A successful CI test does not grant user publication permission. Do not set the flags true merely to make a build pass.

Example: `python archive_release_gate.py APPROVED-release.json --check-only` then `python archive_release_gate.py APPROVED-release.json --out /tmp/TTT-0003-REVIEW.zip`.

For a week missing one of the five resources, do not fake it; archive the individual verified resources separately under the established site workflow, never represent them as a complete five-item release. The design renderers remain draft-only until the original art has been faithfully reproduced and visually accepted.
