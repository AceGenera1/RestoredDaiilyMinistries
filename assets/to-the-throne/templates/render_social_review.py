#!/usr/bin/env python3
"""Render original vs reconstructed editable social SVG candidates for visual QA.
No generated imagery, only original locked reference and self-contained layered SVG.
"""
import argparse,json,io
from pathlib import Path
import cairosvg
from PIL import Image,ImageOps,ImageDraw
from reference_integrity import SPEC,verify
KINDS=("monday-social","wednesday-social","praise-social","persecuted-social")
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
def build(folder):
    folder=Path(folder)
    report={"published":False,"approved":False,"family":[]}
    contact=Image.new("RGB",(4*620,650),"#f7eedf")
    draw=ImageDraw.Draw(contact)
    for i,kind in enumerate(KINDS):
        original=REPO/SPEC[kind]["path"]
        verify(kind,original)
        svg=folder/(kind+"-editable-DRAFT.svg")
        if not svg.is_file():raise ValueError("Missing editable "+kind)
        png=cairosvg.svg2png(url=str(svg))
        candidate=Image.open(io.BytesIO(png)).convert("RGB")
        reference=Image.open(original).convert("RGB")
        if candidate.size!=reference.size:raise ValueError(kind+" canvas dimensions differ")
        candidate.save(folder/(kind+"-editable-preview-DRAFT.png"))
        for j,im in enumerate((reference,candidate)):
            thumb=ImageOps.contain(im,(285,565))
            x=i*620+j*310+(310-thumb.width)//2
            contact.paste(thumb,(x,45))
        draw.text((i*620+12,15),kind.upper()+"  ORIGINAL / DRAFT",fill="#7e1a1a")
        report["family"].append({"id":kind,"reference_size":reference.size,"editable_preview":kind+"-editable-preview-DRAFT.png","visually_approved":False})
    draw.text((15,622),"SYNTHETIC, NOT VERIFIED MINISTRY REPORTS. DO NOT PUBLISH ANY DRAFT.",fill="#7e1a1a")
    contact.save(folder/"social-four-original-vs-editable-DRAFT.png")
    (folder/"social-visual-review.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--folder",required=True)
    a=p.parse_args();build(a.folder)
