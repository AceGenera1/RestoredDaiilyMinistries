#!/usr/bin/env python3
"""TTT template payload validation. Standard library only."""
import json
import sys
from pathlib import Path

KINDS = {"weekly-five": 5, "intercession-update": 5, "praise-report": 5,
         "persecuted-church": 1, "faith-friday": 1, "social-share": 1}
REQUIRED = ("kind", "title", "report_id", "week_of", "date_label",
            "approved", "publication_authorized", "introduction", "matters",
            "sources", "source_archive_url", "closing", "tagline")

def issues(data, strict=False):
    errors = []
    for k in REQUIRED:
        if k not in data:
            errors.append("Missing field: " + k)
    if errors:
        return errors
    kind = data["kind"]
    if kind not in KINDS:
        errors.append("Unsupported kind: " + str(kind))
    items = data["matters"]
    if not isinstance(items, list) or not items:
        errors.append("matters must be a nonempty list")
        return errors
    if kind == "weekly-five" and len(items) != 5:
        errors.append("Weekly Five must have exactly 5 matters")
    if kind in KINDS and len(items) > KINDS[kind]:
        errors.append("Too many matters for " + kind)
    if not isinstance(data["sources"], list) or not data["sources"]:
        errors.append("Source footer requires at least one real source")
    if not str(data["source_archive_url"]).startswith("https://"):
        errors.append("An HTTPS public source archive URL is required")
    refs = []
    for i, item in enumerate(items, 1):
        for key in ("location", "heading", "summary", "prayer_focus", "scripture", "status"):
            if not item.get(key):
                errors.append("Matter %d missing %s" % (i, key))
        prayer = item.get("prayer_focus", [])
        if not isinstance(prayer, list) or not prayer:
            errors.append("Matter %d needs prayer requests" % i)
        scripture = item.get("scripture", {})
        if not isinstance(scripture, dict) or not scripture.get("reference") or not scripture.get("text"):
            errors.append("Matter %d needs reference AND complete Scripture" % i)
        else:
            refs.append(scripture["reference"].strip().lower())
    if len(set(refs)) != len(refs):
        errors.append("Scripture references must be distinct within a report")
    if strict:
        if not data["approved"] or not data["publication_authorized"]:
            errors.append("Strict publishing requires BOTH explicit approval and publication authorization")
        raw = json.dumps(data, ensure_ascii=False).lower()
        if "replace with" in raw or '"draft"' in raw:
            errors.append("Placeholder or DRAFT content is not publishable")
        if len(data["sources"]) < 1:
            errors.append("Missing attributed sources")
        if "to-the-throne-weekly" not in data["source_archive_url"]:
            errors.append("Source archive should point to the weekly library")
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py DATA.json [--strict]")
        return 2
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    errs = issues(data, "--strict" in sys.argv)
    if errs:
        for e in errs:
            print("FAIL:", e)
        return 1
    print("PASS:", data["kind"], "(draft validated; NOT publication approval)"
          if not ("--strict" in sys.argv) else "(structural gate only; verify facts and graphic visually)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
