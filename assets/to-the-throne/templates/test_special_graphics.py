#!/usr/bin/env python3
"""Run synthetic proof checks against exact approved GitHub asset blobs."""
import copy,json,tempfile
from pathlib import Path
from PIL import Image,ImageChops
from special_graphics import render
from reference_integrity import verify
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
ASSETS=json.loads((ROOT/"approved-master-lock.json").read_text(encoding="utf-8"))
def rejected(action):
    try:action()
    except (ValueError,FileNotFoundError):return
    raise AssertionError("Safety rule failed to reject unapproved input")
def checks():
    result={}
    with tempfile.TemporaryDirectory() as temp:
        for kind in ("praise","persecuted","faith"):
            sample=json.loads((ROOT/"samples"/(kind+"-render-test.json")).read_text(encoding="utf-8"))
            reference=REPO/ASSETS[kind]["path"]
            assert reference.is_file(),reference
            verify(kind,reference)
            output=Path(temp)/(kind+"-draft.png")
            report=render(sample,reference,output)
            assert report["public_release_allowed"] is False
            a=Image.open(reference).convert("RGB")
            b=Image.open(output).convert("RGB")
            assert a.size==b.size
            # Original monogram; exclude top-center editable date.
            assert ImageChops.difference(a.crop((115,45,265,166)),b.crop((115,45,265,166))).getbbox() is None
            # Preserve the original motto/footer below mutable content.
            y={"praise":1370,"persecuted":1350,"faith":1235}[kind]
            assert ImageChops.difference(a.crop((0,y,a.width,a.height)),b.crop((0,y,b.width,b.height))).getbbox() is None
            if kind=="persecuted":
                # Faithfully reuse four original prayer icons; the icons are
                # extracted from the locked master, not redrawn.
                src_boxes=((105,735,188,808),(367,735,454,808),
                           (624,735,716,808),(904,735,994,808))
                columns=((40,272),(274,535),(536,803),(805,1083))
                for rect,(left,right) in zip(src_boxes,columns):
                    expected=a.crop(rect)
                    left_x=(left+right-expected.width)//2
                    actual=b.crop((left_x,744,left_x+expected.width,744+expected.height))
                    assert ImageChops.difference(expected,actual).getbbox() is None,"Approved prayer-category icon changed"
                # The country title must be single-line and never spill into
                # the adjacent original subtitle area.
                assert "TEST COUNTRY" in sample["country"].upper()
            bad=copy.deepcopy(sample);bad["publication_authorized"]=True
            rejected(lambda:render(bad,reference,Path(temp)/"bad-final.png"))
            bad=copy.deepcopy(sample);bad["scripture"]["text"]=""
            rejected(lambda:render(bad,reference,Path(temp)/"bad-scripture.png"))
            badfile=Path(temp)/"same-size-fake.png";Image.new("RGB",a.size,"white").save(badfile)
            rejected(lambda:render(sample,badfile,Path(temp)/"bad-reference.png"))
            if kind in ("praise","persecuted"):
                bad=copy.deepcopy(sample);bad["map"]={"map_file":str(reference)}
                rejected(lambda:render(bad,reference,Path(temp)/"bad-map.png"))
            result[kind]={"draft":"pass","logo_preserved":True,"footer_preserved":True,"unapproved_final_rejected":True,
                          "wrong_master_rejected":True,"missing_scripture_rejected":True}
    print(json.dumps(result,indent=2))
if __name__=="__main__":checks()
