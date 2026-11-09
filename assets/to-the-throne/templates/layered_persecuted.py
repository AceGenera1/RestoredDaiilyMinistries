#!/usr/bin/env python3
"""Generate a self-contained, layered, EDITABLE Persecuted Church SVG DRAFT.
Original Git-locked masthead, symbol and scenic footer are preserved in an
embedded raster art layer. Dynamic text is actual SVG text, not burned in.
Never authorizes publication and never creates geographic maps.
"""
import argparse,base64,html,io,json
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
from special_graphics import check,textured_panel,original_round_icon,font
from reference_integrity import SPEC,verify
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
W,H=1122,1402
def fit(txt,sz,bold=False,serif=True):
    f=font(sz,bold,serif)
    return lambda s: ImageDraw.Draw(Image.new("RGB",(2,2))).textbbox((0,0),s,font=f)[2]
def wrapped(text,x,y,width,maxlines=5,size=20,leading=25,fill="#10224a",weight="normal",family="Georgia"):
    meas=fit(text,size,weight=="bold","Georgia" in family)
    lines=[];l=""
    for word in str(text).split():
        trial=(l+" "+word).strip()
        if meas(trial)<=width:l=trial
        else:
            if not l:raise ValueError("Unfit single word: "+word)
            lines.append(l);l=word
    if l:lines.append(l)
    if len(lines)>maxlines:raise ValueError("Text exceeds field: "+str(text)[:60])
    esc=lambda s:html.escape(s,quote=False)
    pieces=[f'<tspan x="{x}" dy="{0 if i==0 else leading}">{esc(line)}</tspan>' for i,line in enumerate(lines)]
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-family="{family}" font-weight="{weight}">'+"".join(pieces)+"</text>",y+(len(lines)-1)*leading+size
def make_base(ref):
    with Image.open(ref) as im:base=im.convert("RGBA")
    original=base.copy()
    base.paste(textured_panel(1066,1080),(35,167))
    base.paste(textured_panel(989,34),(110,1213))
    base.paste(textured_panel(385,12),(714,1245))
    d=ImageDraw.Draw(base)
    # The date field is separate editable artwork.
    d.rectangle((833,39,1044,158),fill="#fff0d4",outline="#b78134",width=2)
    # Authentically preserve the approved decorative invitation banner and
    # four original circular prayer-category icons.
    base.paste(original.crop((252,704,849,742)),(252,704))
    rects=((105,744,188,813),(367,744,454,813),
           (624,744,716,813),(904,744,994,813))
    cols=((40,272),(274,535),(536,803),(805,1083))
    for rect,(lo,hi) in zip(rects,cols):
        crop,mask=original_round_icon(original,rect)
        base.paste(crop,((lo+hi-crop.width)//2,744),mask)
    base.paste(original.crop((45,1054,137,1126)),(42,1052))
    d=ImageDraw.Draw(base)
    d.line((42,566,1078,566),fill="#b78134",width=2)
    d.line((40,724,252,724),fill="#b78134",width=2)
    d.line((849,724,1063,724),fill="#b78134",width=2)
    for x in (273,535,803):
        d.line((x,746,x,1038 if x!=803 else 1131),fill="#b78134",width=2)
    d.rectangle((32,1048,803,1124),fill="#f6e4c6",outline="#b78134",width=2)
    d.line((727,1142,1069,1142),fill="#b78134",width=1)
    # Keep public-source and Scripture text entirely OUT of the raster layer.
    buf=io.BytesIO();base.save(buf,"PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")
def build(data,out):
    if check(data)!="persecuted":raise ValueError("This template is only Persecuted Church")
    ref=REPO/SPEC["persecuted"]["path"];verify("persecuted",ref)
    if any(data.get(x) for x in ("approved","publication_authorized")):
        raise ValueError("No release authorization in draft editor")
    if data.get("map",{}).get("map_file"):
        if not data["map"].get("map_verified") or not data["map"].get("map_source"):
            raise ValueError("Map must be verified and attributed")
        raise ValueError("Map-vector layer not yet approved; use the reviewed PNG path")
    baseline=make_base(ref)
    texts=[]
    def add(value,x,y,width,**kw):
        markup,end=wrapped(value,x,y,width,**kw);texts.append(markup);return end
    navy="#10224a";bronze="#aa5624"
    add("THURSDAY",856,67,170,size=20,maxlines=1,weight="bold")
    add(data["date_label"].upper(),850,102,182,size=19,maxlines=2,leading=21,weight="bold")
    add(data["edition"],850,149,180,size=14,maxlines=1,weight="bold")
    country=str(data["country"]).upper()
    width=fit(country,55,True)(country)
    size=min(55,max(24,int(55*456/max(width,1))))
    add(country,43,221,459,size=size,maxlines=1,weight="bold")
    add("REMEMBER OUR BROTHERS",43,291,456,size=26,maxlines=1,weight="bold",fill=bronze)
    add("AND SISTERS IN CHRIST",43,322,456,size=26,maxlines=1,weight="bold",fill=bronze)
    add(data["region"].upper(),120,349,371,size=18,maxlines=2,weight="bold")
    add(data["verified_summary"],43,391,457,size=20,leading=26,maxlines=7)
    add("VERIFIED MAP REQUIRED",529,211,536,size=18,maxlines=1,weight="bold")
    add(data["pastoral_invitation"],44,596,1020,size=20,leading=26,maxlines=5)
    col=((40,272),(274,535),(536,803),(805,1083))
    for i,(l,r) in enumerate(col):
        title=data["prayer_focus"][i]["title"].upper()
        yy=add(title,l+10,837,r-l-20,size=17,maxlines=3,leading=21,weight="bold",fill=bronze)
        end=add(data["prayer_focus"][i]["focus"],l+11,yy+15,r-l-22,size=18,maxlines=12 if i==3 else 8,leading=21)
        if end>(1132 if i==3 else 1038):raise ValueError("Prayer column overflow "+str(i+1))
    add(data["scripture"]["reference"],162,1074,610,size=19,maxlines=1,weight="bold",fill=bronze)
    add(data["scripture"]["text"],162,1093,610,size=16,maxlines=2,leading=19)
    add("REMEMBER THE PERSECUTED CHURCH",111,1152,605,size=19,maxlines=1,weight="bold",fill=bronze)
    add("Keep lifting up our brothers and sisters in Christ.",113,1177,597,size=16,maxlines=2,leading=18)
    add("SOURCES: "+" • ".join(data["source_names"]),732,1157,331,size=14,maxlines=2,leading=18,weight="bold")
    add("Full references: weekly archive.",732,1190,331,size=13,maxlines=1)
    # Layer group labels work in Inkscape; editable text and permanent artwork
    # are separate. A visible draft banner is intentionally non-removable.
    svg=f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
  width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<g id="locked-art" inkscape:groupmode="layer" inkscape:label="LOCKED ART - approved emblem, paper, prayer icons, mountain">
  <image x="0" y="0" width="{W}" height="{H}" href="data:image/png;base64,{baseline}"/>
</g>
<g id="editable-typography" inkscape:groupmode="layer" inkscape:label="EDITABLE TEXT - synthetic review data">
{''.join(texts)}
</g>
<g id="draft-review" inkscape:groupmode="layer" inkscape:label="DRAFT WATERMARK - NOT FOR PUBLICATION">
  <rect x="1" y="1" width="{W-2}" height="37" fill="#fff0d4"/>
  <text x="16" y="28" fill="#971322" font-size="19" font-family="DejaVu Sans" font-weight="bold">DRAFT LAYERED TEMPLATE — NOT APPROVED FOR PUBLICATION</text>
</g>
</svg>'''
    path=Path(out).resolve()
    if any(part in path.parts for part in ("weekly-graphics","weekly-documents")):
        raise ValueError("Cannot write directly to published files")
    if path.suffix.lower()!=".svg":raise ValueError("SVG output required")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(svg,encoding="utf-8")
    ET.parse(path)
    return {"format":"persecuted","output":str(path),"layers":3,"editable_text_fields":len(texts),
      "approved_art_sha":SPEC["persecuted"]["git_blob_sha1"],"draft":True,"publication_allowed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("sample");p.add_argument("--out",required=True)
    a=p.parse_args();print(json.dumps(build(json.loads(Path(a.sample).read_text(encoding="utf-8")),a.out),indent=2))
