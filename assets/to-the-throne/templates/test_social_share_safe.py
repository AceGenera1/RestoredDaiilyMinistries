#!/usr/bin/env python3
"""Synthetic authorized social-share micro-edit tests; never publish."""
import json,tempfile
from pathlib import Path
from PIL import Image,ImageChops
from reference_integrity import SPEC,verify
from social_share_safe import edit,FAMILIES
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
def denied(action):
    try:action()
    except ValueError:return
    raise AssertionError("Unsafe social-share operation was not blocked")
def main():
    report={}
    with tempfile.TemporaryDirectory() as temp:
        for family in FAMILIES:
            ref=REPO/SPEC[family]["path"]
            verify(family,ref)
            with Image.open(ref) as source:
                size=source.size;original=source.convert("RGBA")
            x=int(size[0]*.45);y=int(size[1]*.5)
            patch=Path(temp)/(family+"-patch.png")
            Image.new("RGBA",(40,20),"#AC702B").save(patch)
            output=Path(temp)/(family+"-DRAFT.png")
            data={"format":family,"reference":str(ref),"output":str(output),
                  "allowed_change_rectangles":[[x,y,40,20]],
                  "patches":[{"file":str(patch),"rect":[x,y,40,20]}]}
            result=edit(data)
            assert result["passed"] and result["protected_pixels_unchanged"]
            with Image.open(output) as edited:
                diff=ImageChops.difference(original.convert("RGB"),edited.convert("RGB"))
                assert diff.getbbox() is not None, "Test patch had no effect"
                assert diff.crop((0,0,size[0],int(size[1]*.2))).getbbox() is None, "Protected masthead changed"
                assert diff.crop((0,int(size[1]*.88),size[0],size[1])).getbbox() is None, "Protected footer changed"
            bad=dict(data);bad["approved"]=True
            denied(lambda:edit(bad))
            bad=dict(data);bad["allowed_change_rectangles"]=[[0,0,40,20]]
            denied(lambda:edit(bad))
            report[family]={"master_verified":True,"approved_region_edit":True,
                            "protected_top_footer":True,"final_output_blocked":True}
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
