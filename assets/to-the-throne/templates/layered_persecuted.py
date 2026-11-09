#!/usr/bin/env python3
"""Generate a self-contained, layered, EDITABLE Persecuted Church SVG DRAFT.
Original Git-locked masthead, symbol and scenic footer are preserved in an
embedded raster art layer. Dynamic text is actual SVG text, not burned in.
Never authorizes publication and never creates geographic maps.
"""
import argparse,base64,html,io,json
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image,ImageDraw,ImageFont,ImageOps
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
    d=ImageDraw.Draw(base)
    # The approved floral horizontal divider is an artwork element, not
    # generic vector decoration; reuse it from the locked source.
    base.paste(original.crop((40,558,1081,574)),(40,558))
    d.line((40,724,252,724),fill="#b78134",width=2)
    d.line((849,724,1063,724),fill="#b78134",width=2)
    for x in (273,535,803):
        d.line((x,746,x,1038 if x!=803 else 1131),fill="#b78134",width=2)
    # The Scripture strip is deliberately wider vertically than the old draft
    # to keep BOTH verse lines inside the framed region.
    d.rectangle((32,1044,803,1131),fill="#f6e4c6",outline="#b78134",width=2)
    base.paste(original.crop((45,1054,137,1126)),(42,1052))
    # The approved remembrance globe and source-document emblems must
    # survive independent text changes, just like the four prayer icons.
    globe,globe_mask=original_round_icon(original,(38,1134,103,1196))
    base.paste(globe,(38,1134),globe_mask)
    doc_icon=original.crop((728,1174,769,1216))
    base.paste(doc_icon,(728,1155))
    d=ImageDraw.Draw(base)
    d.line((727,1142,1069,1142),fill="#b78134",width=1)
    # Keep public-source and Scripture text entirely OUT of the raster layer.
    buf=io.BytesIO();base.save(buf,"PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")
def build(data,out):
    if check(data)!="persecuted":raise ValueError("This template is only Persecuted Church")
    ref=REPO/SPEC["persecuted"]["path"];verify("persecuted",ref)
    if any(data.get(x) for x in ("approved","publication_authorized")):
        raise ValueError("No release authorization in draft editor")
    map_data=data.get("map",{})
    if map_data.get("map_file"):
        if not map_data.get("map_verified") or not map_data.get("map_source"):
            raise ValueError("Map must be verified and attributed")
        if not Path(map_data["map_file"]).is_file():
            raise ValueError("Verified map asset missing")
        with Image.open(map_data["map_file"]) as loaded:
            tile=ImageOps.fit(loaded.convert("RGBA"),(555,385))
            buf=io.BytesIO()
            tile.save(buf,format="PNG")
            map_layer='<image x="521" y="173" width="555" height="385" href="data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode("ascii")+'"/>'
    else:
        map_layer='<rect x="518" y="171" width="562" height="390" fill="#e6d4b7" fill-opacity=".72" stroke="#b78134" stroke-width="2"/>'
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
    if not map_data.get("map_file"):
        add("VERIFIED MAP REQUIRED",529,211,536,size=18,maxlines=1,weight="bold")
    add(data["pastoral_invitation"],44,596,1020,size=20,leading=26,maxlines=5)
    col=((40,272),(274,535),(536,803),(805,1083))
    for i,(l,r) in enumerate(col):
        title=data["prayer_focus"][i]["title"].upper()
        yy=add(title,l+10,837,r-l-20,size=17,maxlines=3,leading=21,weight="bold",fill=bronze)
        end=add(data["prayer_focus"][i]["focus"],l+11,yy+15,r-l-22,size=18,maxlines=12 if i==3 else 8,leading=21)
        if end>(1132 if i==3 else 1038):raise ValueError("Prayer column overflow "+str(i+1))
    # Keep Scripture and the remembrance appeal IN THEIR OWN FIXED PANELS.
    # Fail the build rather than clipping full WEB text or drawing over art.
    reference_end=add(data["scripture"]["reference"],158,1070,618,size=18,maxlines=1,weight="bold",fill=bronze)
    if reference_end>1089:raise ValueError("Scripture reference exceeds approved strip")
    scripture_end=add(data["scripture"]["text"],158,1092,620,size=15,maxlines=2,leading=19)
    if scripture_end>1127:raise ValueError("Full Scripture extends beyond approved strip")
    remembrance_end=add("REMEMBER THE PERSECUTED CHURCH",111,1150,604,size=18,maxlines=1,weight="bold",fill=bronze)
    if remembrance_end>1170:raise ValueError("Remembrance heading overflows")
    appeal_end=add("Keep lifting up our brothers and sisters in Christ.",113,1177,593,size=15,maxlines=2,leading=18)
    if appeal_end>1210:raise ValueError("Remembrance text overflows the footer buffer")
    source_end=add("SOURCES: "+" • ".join(data["source_names"]),782,1163,278,size=12,maxlines=2,leading=16,weight="bold")
    if source_end>1194:raise ValueError("Source attribution overflows")
    add("Full references: weekly archive.",782,1207,278,size=11,maxlines=1)
    # Layer group labels work in Inkscape; editable text and permanent artwork
    # are separate. A visible draft banner is intentionally non-removable.
    svg=f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
  width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<g id="locked-art" inkscape:groupmode="layer" inkscape:label="LOCKED ART - approved emblem, paper, prayer icons, mountain">
  <image x="0" y="0" width="{W}" height="{H}" href="data:image/png;base64,{baseline}"/>
</g>
<g id="verified-geography" inkscape:groupmode="layer" inkscape:label="VERIFIED MAP - separately replaceable">{map_layer}</g>
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
    return {"format":"persecuted","output":str(path),"layers":4,"editable_text_fields":len(texts),"verified_map_supplied":bool(map_data.get("map_file")),
      "approved_art_sha":SPEC["persecuted"]["git_blob_sha1"],"draft":True,"publication_allowed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("sample");p.add_argument("--out",required=True)
    a=p.parse_args();print(json.dumps(build(json.loads(Path(a.sample).read_text(encoding="utf-8")),a.out),indent=2))
