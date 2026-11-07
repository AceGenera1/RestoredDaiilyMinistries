#!/usr/bin/env python3
"""Strict pixel-bounded draft edits of four ORIGINAL social-share PNG masters.
No new graphic generation; no publication. Use approved, exact-size patch PNGs.
"""
import argparse,json,tempfile,hashlib
from pathlib import Path
from PIL import Image,ImageChops
from reference_integrity import verify
from reference_safe_compositor import compose

FAMILIES=("monday-social","wednesday-social","praise-social","persecuted-social")
def edit(data):
    family=data.get("format")
    if family not in FAMILIES:raise ValueError("Unsupported approved social-share family")
    if data.get("approved") or data.get("publication_authorized"):
        raise ValueError("Social-share micro-editing tool is still DRAFT-ONLY")
    original=Path(data["reference"])
    verify(family,original)
    with Image.open(original) as source:
        w,h=source.size
    patches=data.get("patches",[])
    if not 1<=len(patches)<=12:raise ValueError("Provide 1 to 12 exact reviewed replacement patches")
    allowed=data.get("allowed_change_rectangles",[])
    if not allowed:raise ValueError("Authorized change rectangles must be explicit")
    # Exclude top brand/masthead and bottom motto; do not guess text regions
    # or silently crop approved artwork.
    for x,y,pw,ph in allowed:
        if x<0 or y<round(.20*h) or pw<1 or ph<1 or x+pw>w or y+ph>round(.88*h):
            raise ValueError("Allowed edit overlaps protected masthead/footer or leaves image")
    manifest={"reference":str(original),"reference_sha256":hashlib.sha256(original.read_bytes()).hexdigest(),
             "patches":patches,"allowed_change_rectangles":allowed,"output":data["output"]}
    result=compose(manifest)
    result.update({"social_family":family,"locked_master":True,"approved":False,"publication_authorized":False})
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("manifest",help="Exact approved master, patch files, explicit reviewed rectangles")
    a=parser.parse_args()
    print(json.dumps(edit(json.loads(Path(a.manifest).read_text(encoding="utf-8"))),indent=2))
