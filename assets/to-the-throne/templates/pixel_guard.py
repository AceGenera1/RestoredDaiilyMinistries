#!/usr/bin/env python3
"""Check revisions to an existing approved To The Throne PNG.

Examples:
  python pixel_guard.py approved.png updated.png --allow 0,1120,1122,83
  python pixel_guard.py approved.png updated.png --allow 0.04,0.82,0.96,0.05 --relative

Never accepts unlisted changed pixels as an approved micro-edit.
Uses exact RGB pixel values after converting both inputs to RGBA.
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops

def rect_from_text(text, width, height, relative):
    vals = [float(x.strip()) for x in text.split(",")]
    if len(vals) != 4:
        raise ValueError("Expected x,y,width,height")
    x,y,w,h = vals
    if relative:
        if not all(0 <= v <= 1 for v in vals):
            raise ValueError("Relative rectangle values must be 0..1")
        x,y,w,h = x*width,y*height,w*width,h*height
    x,y,w,h = [round(v) for v in (x,y,w,h)]
    if w <= 0 or h <= 0 or x < 0 or y < 0 or x+w > width or y+h > height:
        raise ValueError("Allowed region is empty or outside the image")
    return x,y,x+w,y+h

def verify(original, revised, allowed):
    if original.size != revised.size:
        return {"passed":False,"error":"Dimensions changed", "original":original.size,"revised":revised.size}
    diff=ImageChops.difference(original.convert("RGBA"),revised.convert("RGBA"))
    # RGBA.getbbox() can incorrectly return None when only RGB differs and alpha stays identical.
    rgb_diff=diff.convert("RGB")
    alpha_diff=diff.getchannel("A")
    box=ImageChops.lighter(rgb_diff.convert("L"),alpha_diff).getbbox()
    if box is None:
        return {"passed":True,"changed_pixels":0,"changed_bbox":None,"changed_outside_allow":0,
                "note":"No pixel changes"}
    mask=rgb_diff.point(lambda p: 255 if p else 0).convert("L")
    # RGB difference mask collapsed across channels; alpha is checked separately.
    a_diff=ImageChops.difference(original.getchannel("A"),revised.getchannel("A"))
    from PIL import ImageChops as C
    mask=C.lighter(mask,a_diff.point(lambda p: 255 if p else 0))
    changed=0;outside=0
    pix=mask.load()
    width,height=original.size
    for y in range(height):
        for x in range(width):
            if pix[x,y]:
                changed+=1
                if not any(l<=x<r and t<=y<b for l,t,r,b in allowed):
                    outside+=1
    return {"passed":outside==0,"changed_pixels":changed,"changed_outside_allow":outside,
            "changed_bbox":box,"allowed_rectangles":allowed,
            "note":"Pixel comparison only; approved content/text still requires independent review"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("original")
    parser.add_argument("revised")
    parser.add_argument("--allow",action="append",default=[],help="Allowed rectangle x,y,width,height; repeatable")
    parser.add_argument("--relative",action="store_true",help="Treat allowed rectangles as fractions of width/height")
    parser.add_argument("--report",help="Optional JSON report path")
    args=parser.parse_args()
    with Image.open(args.original) as a0,Image.open(args.revised) as b0:
        a=a0.convert("RGBA")
        b=b0.convert("RGBA")
    allowed=[rect_from_text(x,*a.size,args.relative) for x in args.allow]
    result=verify(a,b,allowed)
    result["original_file"]=str(Path(args.original))
    result["revised_file"]=str(Path(args.revised))
    result["note"]=result.get("note","")+"; never use an allowed rectangle larger than the requested edit"
    output=json.dumps(result,indent=2)
    if args.report:
        Path(args.report).write_text(output+"\n",encoding="utf-8")
    print(output)
    return 0 if result["passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
