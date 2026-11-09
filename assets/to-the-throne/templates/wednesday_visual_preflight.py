#!/usr/bin/env python3
"""Strict preflight for Wednesday visual production; never publishes.
Prevents synthetic maps, missing approved master, missing full Scripture,
and release of visually unapproved layered drafts.
"""
import argparse, json
from pathlib import Path
from reference_integrity import SPEC, verify

def check(payload, repository_root=None):
    root = Path(repository_root) if repository_root else Path(__file__).resolve().parents[3]
    errors = []
    if payload.get("format") != "wednesday":
        errors.append("Expected Wednesday Intercession Update format")
    if not payload.get("edition") or not payload.get("date_label"):
        errors.append("Edition and report date are required")
    matters = payload.get("matters", [])
    if not 1 <= len(matters) <= 5:
        errors.append("Wednesday requires 1–5 material developments, never padding")
    if not payload.get("source_names"):
        errors.append("Source footer requires actual relied-on organizations")
    for i, matter in enumerate(matters, 1):
        for field in ("location", "heading", "summary", "prayer_focus"):
            if not matter.get(field):
                errors.append(f"Matter {i}: missing {field}")
        scripture = matter.get("scripture") or {}
        if not scripture.get("reference") or not scripture.get("text"):
            errors.append(f"Matter {i}: complete, distinct WEB/WEBU Scripture required")
        map_path = matter.get("map_file")
        if not (map_path and matter.get("map_verified") is True and matter.get("map_source")):
            errors.append(f"Matter {i}: verified sourced map image required; blank rectangle forbidden")
        elif not Path(map_path).is_file():
            errors.append(f"Matter {i}: supplied map file does not exist")
    verses = [(m.get("scripture") or {}).get("reference") for m in matters]
    if len(set(verses)) != len(verses):
        errors.append("Scripture references must be unique")
    try:
        verify("wednesday", root / SPEC["wednesday"]["path"])
    except Exception as exc:
        errors.append("Original locked Wednesday artwork integrity failed: " + str(exc))
    return {"pass": not errors, "errors": errors,
            "visual_approval": False, "publication_authorized": False,
            "next_step": "Human side-by-side visual signoff required; draft rendering alone is insufficient"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("payload")
    p.add_argument("--out")
    a=p.parse_args()
    result=check(json.loads(Path(a.payload).read_text(encoding="utf-8")))
    output=json.dumps(result,indent=2)+"\n"
    if a.out: Path(a.out).write_text(output,encoding="utf-8")
    print(output)
    return 0 if result["pass"] else 1

if __name__=="__main__":
    raise SystemExit(main())
