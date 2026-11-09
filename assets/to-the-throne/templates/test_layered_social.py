#!/usr/bin/env python3
"""Verify four editable social-share families, protected artwork and fail-closed rules."""
import copy,json,tempfile,base64,io
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image,ImageChops
from reference_integrity import SPEC
from layered_social import run,check,KINDS
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
def rejected(call):
    try:call()
    except ValueError:return
    raise AssertionError("Invalid social candidate was accepted")
def test():
    ns={"s":"http://www.w3.org/2000/svg"}
    output={}
    with tempfile.TemporaryDirectory() as temp:
        for family in KINDS:
            data=json.loads((ROOT/"samples"/(family+"-layered-test.json")).read_text(encoding="utf-8"))
            svg=Path(temp)/(family+".svg")
            result=run(data,svg)
            groups=ET.parse(svg).findall(".//s:g",ns)
            assert [a.get("id") for a in groups]==["locked-social-master","editable-copy","mandatory-draft"]
            art=groups[0].find("s:image",ns)
            assert art is not None
            href=art.get("href") or art.get("{http://www.w3.org/1999/xlink}href")
            assert href and href.startswith("data:image/png;base64,")
            embedded=Image.open(io.BytesIO(base64.b64decode(href.split(",",1)[1]))).convert("RGB")
            reference=Image.open(REPO/SPEC[family]["path"]).convert("RGB")
            assert embedded.size==reference.size
            w,h=reference.size
            top=int(h*.26);bottom=int(h*.82)
            for region in ((0,0,w,top),(0,bottom,w,h),(0,top,int(w*.07),bottom),
                           (int(w*.93),top,w,bottom)):
                assert ImageChops.difference(embedded.crop(region),reference.crop(region)).getbbox() is None, (
                    "Locked social art changed outside central editable region",family,region)
            assert len(groups[1].findall("s:text",ns))>=4
            assert result["draft"] and not result["approved"]
            bad=copy.deepcopy(data);bad["approved"]=True
            rejected(lambda:run(bad,Path(temp)/"not-allowed.svg"))
            bad=copy.deepcopy(data);bad["archive_url"]="https://example.org/placeholder"
            rejected(lambda:run(bad,Path(temp)/"not-allowed.svg"))
            if family!="persecuted-social":
                bad=copy.deepcopy(data);bad["scripture"]["text"]=""
                rejected(lambda:run(bad,Path(temp)/"not-allowed.svg"))
            output[family]={"editable":True,"protected_brand_master":True,"outer_art_pixel_exact":True,"no_final_publication":True}
    print(json.dumps(output,indent=2))
if __name__=="__main__":test()
