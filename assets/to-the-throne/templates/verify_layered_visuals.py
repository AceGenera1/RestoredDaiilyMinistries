#!/usr/bin/env python3
"""Render all five layered SVG candidates and enforce preservation of locked art.

Visual comparison is a draft review, not certification of editorial, geographic,
Scripture or layout fidelity. Tests use only exact SHA-locked approved references.
"""
import argparse,io,json
from pathlib import Path
import cairosvg
from PIL import Image,ImageOps,ImageDraw,ImageChops
from reference_integrity import SPEC,verify
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
KINDS=("monday","wednesday","praise","persecuted","faith")
def check(folder,out):
    folder=Path(folder);out=Path(out)
    if "weekly-graphics" in out.parts or "weekly-documents" in out.parts:
        raise ValueError("No publication to asset folders")
    out.mkdir(parents=True,exist_ok=True)
    report={"release_allowed":False,"format":"locked-art SVG visual fidelity review","families":{}}
    sheet=Image.new("RGB",(5*550,740),"#f8f0e3")
    draw=ImageDraw.Draw(sheet)
    for i,kind in enumerate(KINDS):
        src=REPO/SPEC[kind]["path"]
        verify(kind,src)
        svg=folder/(kind+"-editable-DRAFT.svg")
        if not svg.is_file():raise ValueError("Missing SVG for "+kind)
        with Image.open(src) as im:original=im.convert("RGB")
        png=cairosvg.svg2png(url=str(svg))
        candidate=Image.open(io.BytesIO(png)).convert("RGB")
        if original.size!=candidate.size:raise ValueError(kind+" SVG size differs from approved master")
        w,h=original.size
        # Exact original protection for permanent logo block and final motto.
        # The date plaque is purposely excluded (dynamic), as is the draft ribbon.
        logo_regions={
          "monday":(32,44,225,157),"wednesday":(45,46,220,167),
          "praise":(42,45,214,165),"persecuted":(62,44,262,163),
          "faith":(103,44,274,160)}
        rects={"logo":logo_regions[kind],"bottom_motto":(0,h-40,w,h)}
        for label,rect in rects.items():
            original_part=original.crop(rect)
            candidate_part=candidate.crop(rect)
            # CairoSVG rasterizes a PNG background exactly at the 1:1 image size.
            delta=ImageChops.difference(original_part,candidate_part)
            if delta.getbbox() is not None:
                raise ValueError(kind+" protected "+label+" was changed")
        candidate.save(out/(kind+"-layered-preview-DRAFT.png"))
        for j,image in enumerate((original,candidate)):
            thumb=ImageOps.contain(image,(264,657))
            x=i*550+j*275+(275-thumb.width)//2
            sheet.paste(thumb,(x,58+(657-thumb.height)//2))
        draw.text((i*550+12,17),kind.upper()+"  APPROVED / EDITABLE DRAFT",fill="#1b2b50")
        report["families"][kind]={"master_identity_verified":True,"logo_pixel_exact":True,
            "motto_pixel_exact":True,"visual_accepted":False,
            "draft_preview":kind+"-layered-preview-DRAFT.png"}
    draw.text((14,725),"SYNTHETIC VISUAL QA ONLY. PROTECTED PIXELS PASS; VISUAL RECONSTRUCTION IS NOT YET APPROVED.",fill="#a1261c")
    sheet.save(out/"five-originals-vs-layered-DRAFT.png")
    (out/"five-layered-qa.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--folder",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    check(args.folder,args.out)
