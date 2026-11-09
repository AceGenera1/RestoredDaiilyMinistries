#!/usr/bin/env python3
"""Unified To The Throne DRAFT staging.
One approved-data candidate -> tested PDF drafts, source-matched Monday visual,
optional separately verified Wednesday/Praise/Persecuted/Faith drafts, QA report.
No actual research/Scripture verification or publishing is performed.
"""
import argparse,json,sys,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
from package_qa import build as pdf_package
from reference_integrity import SPEC,verify
from locked_graphics import require as require_regular,monday,wednesday,date_box,ft
from special_graphics import render as special_render
from social_evergreen import stage as stage_social
def render_regular(data,kind,out):
    from PIL import Image,ImageDraw
    ref=REPO/SPEC[kind]["path"]
    verify(kind,ref)
    require_regular(data,True)
    with Image.open(ref) as src: im=src.convert("RGB")
    draw=ImageDraw.Draw(im)
    date_box(draw,data,kind)
    (monday if kind=="monday" else wednesday)(im,draw,data,True)
    draw.rectangle((2,2,im.width-3,38),fill="#FFF5DD")
    draw.text((16,7),"DRAFT / DESIGN RECONSTRUCTION NOT APPROVED",font=ft(18,True),fill="#971322")
    im.save(out,"PNG")
def monday_payload(record):
    names=list(dict.fromkeys(s["outlet"] for m in record["matters"] for s in m["sources"]))
    return {"format":"monday","edition":record["edition"],
      "date_label":record.get("publication_date",record["week_of"]),
      "source_names":names,"approved":False,"publication_authorized":False,
      "closing":record.get("closing","Continue praying for those facing hardship."),
      "matters":[{
          "location":m["location"],"heading":m["headline"],"summary":m["summary"],
          "prayer_focus":m["prayer_focus"],
          "scripture":{"reference":m["scripture_reference"],"text":m["scripture_text"]},
          "status":m["status"],
          "map_file":m.get("approved_map_image",""),
          "map_verified":bool(m.get("map_verified")),
          "map_source":m.get("map_source","")
      } for m in record["matters"]]}
def produce(week,out,other=None):
    out=Path(out).resolve()
    if any(x in out.parts for x in ("weekly-documents","weekly-graphics")):
        raise ValueError("Stage folder must not be a published repository location")
    out.mkdir(parents=True,exist_ok=True)
    docdir=out/"pdfs"
    docs=pdf_package(week,docdir)
    if not docs["pdf_checks"]["recording_brief"]["passed"] or not docs["pdf_checks"]["public_source_sheet"]["passed"]:
        raise ValueError("Document QA failed")
    images=out/"graphics";images.mkdir(exist_ok=True)
    monday_data=monday_payload(week)
    (images/"monday-payload-DRAFT.json").write_text(json.dumps(monday_data,indent=2)+"\n")
    regular_file=images/"monday-DRAFT.png"
    render_regular(monday_data,"monday",regular_file)
    status={"edition":week["edition"],"week_of":week["week_of"],"publication":False,
       "source_links":docs["source_links"],"pdfs":docs["pdf_checks"],
       "rendered_graphics":{"monday":{"file":regular_file.name,"state":"DRAFT"}},
       "missing_components":[],"visual_approval":False,"ready_for_publication":False}
    for kind in ("wednesday","praise","persecuted","faith"):
        path=(other or {}).get(kind)
        if path is None:
            status["missing_components"].append(kind)
            continue
        payload=json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("format")!=kind:raise ValueError(kind+" input format mismatch")
        if payload.get("edition")!=week["edition"]:
            raise ValueError(kind+" edition must match canonical week")
        output=images/(kind+"-DRAFT.png")
        if kind=="wednesday":render_regular(payload,kind,output)
        else:special_render(payload,REPO/SPEC[kind]["path"],output)
        status["rendered_graphics"][kind]={"file":output.name,"state":"DRAFT"}
    social=stage_social(out/"approved-evergreen-social")
    status["evergreen_social"]={"verified_originals":social["approved_originals"],"unchanged":True,
       "caption_status":"Separate; user review required", "publication":False}
    status["missing_components"]+=["approved_clean_background_layers"]
    (out/"QA-INTEGRATED-DRAFT.json").write_text(json.dumps(status,indent=2)+"\n")
    return status
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("week");a.add_argument("--out",required=True)
    for kind in ("wednesday","praise","persecuted","faith"):a.add_argument("--"+kind)
    args=a.parse_args()
    data=json.loads(Path(args.week).read_text(encoding="utf-8"))
    opts={k:getattr(args,k) for k in ("wednesday","praise","persecuted","faith")}
    print(json.dumps(produce(data,args.out,opts),indent=2))
