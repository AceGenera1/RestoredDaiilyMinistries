#!/usr/bin/env python3
"""Four social-share editable SVG layout candidates — UNPUBLISHABLE.
Exact approved GitHub PNG master is embedded as locked artwork; only the
central information zone is reconstructed as independently editable SVG.
No generic logo, map, or final art is synthesized.
"""
import argparse,base64,html,io,json,re
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image,ImageDraw
from reference_integrity import SPEC,verify
from layered_persecuted import wrapped,textured_panel

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
KINDS=("monday-social","wednesday-social","praise-social","persecuted-social")
def safe_url(url):
    if not isinstance(url,str) or not (url.startswith("https://") and " " not in url):
        raise ValueError("Weekly archive URL must be absolute HTTPS")
    if "example.org" in url or "REPLACE" in url.upper():
        raise ValueError("No sample/archive placeholder URLs")
def check(data):
    kind=data.get("format")
    if kind not in KINDS:raise ValueError("Unsupported social-share design")
    if data.get("approved") or data.get("publication_authorized"):
        raise ValueError("Editable social artwork is NOT visually approved")
    for field in ("edition","date_label","headline","prayer_invitation","archive_url"):
        if not isinstance(data.get(field),str) or not data[field].strip():
            raise ValueError("Missing social field: "+field)
    if not re.fullmatch(r"TTT(?:PC)?-[0-9]{4}(?:-[0-9]{2})?",data["edition"]):
        raise ValueError("Invalid TTT edition identifier")
    if any(x in (data["headline"]+" "+data["prayer_invitation"]).lower() for x in ("synthetic test", "verified map required")):
        raise ValueError("Real outputs cannot use synthetic/placeholder text")
    safe_url(data["archive_url"])
    if kind=="persecuted-social":
        for k in ("country","region"):
            if not data.get(k):raise ValueError("Missing persecuted regional context")
    else:
        for k in ("summary","scripture"):
            if not data.get(k):raise ValueError("Missing summary or Scripture")
        if not data["scripture"].get("reference") or not data["scripture"].get("text"):
            raise ValueError("Scripture may not be shortened or silently omitted")
    return kind
def run(data,out):
    kind=check(data)
    master=REPO/SPEC[kind]["path"]
    verify(kind,master)
    with Image.open(master) as im: original=im.convert("RGBA")
    w,h=original.size
    # Flattened approved art is still kept on its own locked raster layer.
    # Changeable fields have a visible separate paper treatment. The region
    # is explicitly restricted to the middle so logo/footer are protected.
    left=int(w*.07);right=int(w*.93)
    top=int(h*.26);bottom=int(h*.82)
    if bottom-top<270:raise ValueError("Social master too short for editable content")
    clean=original.copy()
    region_w=right-left;region_h=bottom-top
    clean.paste(textured_panel(region_w,region_h),(left,top))
    b=io.BytesIO();clean.save(b,format="PNG")
    background=base64.b64encode(b.getvalue()).decode("ascii")
    navy="#102451";bronze="#a96529"
    nodes=[]
    def add(value,x,y,width,**kwargs):
        markup,end=wrapped(value,x,y,width,**kwargs)
        nodes.append(markup);return end
    x=left+int(region_w*.06)
    limit=int(region_w*.88)
    y=top+int(region_h*.09)
    tit=data["headline"].upper()
    # Use a single headline capped by field width; do not crop or silently
    # shorten words to satisfy layout.
    y=add(tit,x,y,limit,size=max(19,int(w*.022)),leading=29,
          maxlines=2,weight="bold",fill=navy)+int(h*.028)
    if kind=="persecuted-social":
        y=add(data["country"].upper()+" • "+data["region"].upper(),x,y,limit,
              size=max(15,int(w*.018)),weight="bold",fill=bronze,maxlines=3,leading=23)+int(h*.024)
    else:
        y=add(data["summary"],x,y,limit,size=max(15,int(w*.016)),leading=23,maxlines=5)+int(h*.021)
    y=add(data["prayer_invitation"],x,y,limit,size=max(17,int(w*.019)),
          leading=26,maxlines=6)+int(h*.020)
    if kind!="persecuted-social":
        verse=data["scripture"]
        y=add(verse["reference"]+" — "+verse["text"],x,y,limit,size=max(14,int(w*.015)),
              leading=22,maxlines=5)+int(h*.017)
    y=add("Full sources and weekly intercession resources:",x,y,limit,
          size=max(12,int(w*.013)),leading=19,maxlines=2,fill=bronze,weight="bold")+8
    y=add(data["archive_url"],x,y,limit,size=max(11,int(w*.012)),leading=17,maxlines=3)
    if y>bottom-15:raise ValueError("Social fields overflow approved editable zone; do NOT clip")
    # Mandatory draft watermark in separate vector layer. No publish routine.
    svg=f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<g id="locked-social-master" inkscape:groupmode="layer" inkscape:label="LOCKED approved social-brand artwork">
<image x="0" y="0" width="{w}" height="{h}" href="data:image/png;base64,{background}"/></g>
<g id="editable-copy" inkscape:groupmode="layer" inkscape:label="EDITABLE verified social headline, prayer and source text">
{''.join(nodes)}</g>
<g id="mandatory-draft" inkscape:groupmode="layer" inkscape:label="DRAFT — cannot release">
<rect x="0" y="0" width="{w}" height="42" fill="#fff1d9"/>
<text x="18" y="29" font-size="19" font-family="DejaVu Sans" font-weight="bold" fill="#951722">DRAFT SOCIAL LAYOUT — NOT APPROVED</text>
</g></svg>'''
    file=Path(out).resolve()
    if file.suffix.lower()!=".svg":raise ValueError("Output must be editable SVG")
    if any(z in file.parts for z in ("weekly-graphics","weekly-documents")):
        raise ValueError("Never overwrite public release assets")
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(svg,encoding="utf-8")
    ET.parse(file)
    return {"format":kind,"draft":True,"approved":False,"reference_sha":SPEC[kind]["git_blob_sha1"],
            "editable_fields":len(nodes),"protected_masthead_until":top,"protected_footer_from":bottom,
            "output":str(file)}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("input");p.add_argument("--out",required=True)
    args=p.parse_args()
    print(json.dumps(run(json.loads(Path(args.input).read_text(encoding="utf-8")),args.out),indent=2))
