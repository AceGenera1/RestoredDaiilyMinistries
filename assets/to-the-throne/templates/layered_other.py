#!/usr/bin/env python3
"""Self-contained SVG draft templates: Monday, Wednesday, Praise, Faith Friday.
Original brand artwork is embedded from exact Git-locked masters, and every
date, summary, prayer, source and Scripture is an independent SVG text field.
The map images are independently replaceable ONLY with verified provenance.
No release authorization or automatic publication.
"""
import argparse,base64,html,io,json
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image,ImageDraw,ImageOps
from layered_persecuted import wrapped, textured_panel
from reference_integrity import SPEC,verify
from locked_graphics import require as require_weekly
from special_graphics import check as require_special
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
PAPER="#faead0";NAVY="#102451";BRONZE="#aa682c";GREEN="#075138"
KINDS=("monday","wednesday","praise","faith")
def base_art(kind,ref):
    with Image.open(ref) as img:base=img.convert("RGBA")
    w,h=base.size
    d=ImageDraw.Draw(base)
    if kind=="monday":
        base.paste(textured_panel(1045,781),(35,296))
        base.paste(textured_panel(1031,107),(41,1079))
        d=ImageDraw.Draw(base)
        d.rectangle((785,44,1067,153),fill="#fff0d7",outline="#a5772e",width=2)
        for i in range(1,5):
            y=297+i*155
            d.line((37,y,1070,y),fill=BRONZE,width=2)
    elif kind=="wednesday":
        base.paste(textured_panel(1023,877),(30,344))
        base.paste(textured_panel(1014,49),(31,1222))
        d=ImageDraw.Draw(base)
        d.rectangle((819,38,1004,157),fill="#fff0d7",outline="#a5772e",width=2)
        for i in range(1,5):
            y=344+i*174
            d.line((32,y,1050,y),fill=BRONZE,width=2)
    elif kind=="praise":
        base.paste(textured_panel(989,780),(45,330))
        d=ImageDraw.Draw(base)
        d.rectangle((820,40,1004,182),fill="#fff0d7",outline="#a5772e",width=2)
        d.rectangle((47,331,1014,423),fill=GREEN,outline=BRONZE,width=2)
        d.rectangle((420,439,1011,483),fill=GREEN,outline=BRONZE,width=2)
        d.rectangle((420,735,1011,779),fill=GREEN,outline=BRONZE,width=2)
    elif kind=="faith":
        base.paste(textured_panel(1001,571),(44,426))
        d=ImageDraw.Draw(base)
        d.rectangle((818,39,1008,173),fill="#fff0d7",outline="#a5772e",width=2)
        d.line((217,509,875,509),fill=BRONZE,width=2)
        d.rectangle((140,828,947,969),fill="#f8e6c8",outline=BRONZE,width=3)
    mem=io.BytesIO()
    base.save(mem,format="PNG")
    return base64.b64encode(mem.getvalue()).decode("ascii"),(w,h)
def image_layer(map_data,box):
    x,y,w,h=box
    if map_data.get("map_file"):
        if not map_data.get("map_verified") or not map_data.get("map_source"):
            raise ValueError("Map must be verified, sourced and supplied")
        src=Path(map_data["map_file"])
        if not src.is_file():raise ValueError("Map file not found")
        with Image.open(src) as original:
            tile=ImageOps.fit(original.convert("RGB"),(w,h))
        buf=io.BytesIO()
        tile.save(buf,format="PNG")
        return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode("ascii")}"/>'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#e6d5b9" stroke="#b78134" stroke-width="2"/>'
def render(data,out):
    kind=data.get("format")
    if kind not in KINDS:raise ValueError("Unsupported family")
    if kind in ("monday","wednesday"):
        require_weekly(data,True)
    else:
        require_special(data)
    if data.get("approved") or data.get("publication_authorized"):
        raise ValueError("All editable graphics are draft-only")
    reference=REPO/SPEC[kind]["path"]
    verify(kind,reference)
    paper,(w,h)=base_art(kind,reference)
    texts=[];map_layers=[]
    def add(content,x,y,width,**kwargs):
        node,end=wrapped(content,x,y,width,**kwargs)
        texts.append(node)
        return end
    if kind=="monday":
        add("WEEKLY INTERCESSION LETTER",791,62,272,size=12,weight="bold",maxlines=1)
    else:
        add({"wednesday":"WEDNESDAY","praise":"WEDNESDAY","faith":"FRIDAY"}[kind],
            831,61,170,size=16,weight="bold",maxlines=1)
    add(data.get("edition",""),810 if kind=="monday" else 832,116 if kind=="monday" else 153,
        220 if kind=="monday" else 171,size=20 if kind=="monday" else 14,weight="bold",maxlines=2)
    add(data["date_label"],800 if kind=="monday" else 832,142 if kind=="monday" else 103,
        260 if kind=="monday" else 170,size=15,weight="bold",maxlines=2)
    names="SOURCES: "+" • ".join(data["source_names"])
    if kind=="monday":
        for i,m in enumerate(data["matters"]):
            y=297+155*i
            add(f"{i+1:02}",28,y+56,64,size=40,weight="bold",fill=BRONZE,maxlines=1)
            map_layers.append(image_layer(m,(98,y+6,204,143)))
            add(m["location"].upper(),319,y+23,338,size=19,weight="bold",maxlines=2)
            add(m["heading"].upper(),319,y+56,338,size=17,weight="bold",fill=BRONZE,maxlines=2)
            add(m["summary"],319,y+92,334,size=15,maxlines=4,leading=17)
            add("TAKE IT BEFORE THE THRONE",678,y+24,246,size=11,weight="bold",fill=BRONZE,maxlines=1)
            end=y+42
            for prayer in m["prayer_focus"]:
                end=add("• "+prayer,683,end+3,234,size=14,leading=16,maxlines=2)
            sc=m["scripture"]
            end=add(sc["reference"]+" — "+sc["text"],682,max(y+123,end+8),355,size=13,maxlines=3,leading=14)
            if end>y+154:raise ValueError("Monday full Scripture collides with next matter")
            add(m.get("status","ACTIVE"),935,y+59,124,size=15,weight="bold",fill=BRONZE,maxlines=1)
        add(data.get("closing","Continue praying for those facing hardship."),45,1111,1015,size=18,maxlines=3,leading=22)
        add(names,49,1162,1015,size=15,maxlines=2,leading=17,weight="bold")
    elif kind=="wednesday":
        for i,m in enumerate(data["matters"]):
            y=344+174*i
            map_layers.append(image_layer(m,(35,y+5,239,164)))
            add(str(i+1),294,y+48,40,size=30,weight="bold",fill=BRONZE,maxlines=1)
            add(m["location"].upper(),339,y+25,333,size=18,weight="bold",maxlines=2)
            add(m["heading"].upper(),339,y+63,331,size=16,weight="bold",fill=BRONZE,maxlines=2)
            add(m["summary"],339,y+103,332,size=15,leading=18,maxlines=4)
            add(m.get("status","ACTIVE").upper()+" • INTERCESSION",713,y+23,324,size=16,weight="bold",maxlines=1)
            add("PRAYER FOCUS",705,y+56,320,size=17,weight="bold",fill=BRONZE,maxlines=1)
            end=y+74
            for prayer in m["prayer_focus"]:
                end=add("• "+prayer,710,end+5,316,size=14,leading=16,maxlines=2)
            sc=m["scripture"]
            end=add(sc["reference"]+" — "+sc["text"],701,max(y+142,end+4),333,size=13,maxlines=3,leading=14)
            if end>y+174:raise ValueError("Wednesday full Scripture collides with next matter")
        add(names,49,1248,988,size=15,maxlines=2,weight="bold",leading=18)
    elif kind=="praise":
        map_layers.append(image_layer(data["map"],(47,437,358,538)))
        add("WEDNESDAY",839,65,153,size=19,weight="bold",maxlines=1)
        add(data["headline"].upper(),80,367,910,size=28,weight="bold",fill="#ffffff",maxlines=1)
        add(data["outcome"],76,404,905,size=17,fill="#ffffff",maxlines=1)
        add("VERIFIED PRAISE / WHAT CHANGED",448,469,547,size=21,fill="#ffffff",weight="bold",maxlines=1)
        y=516
        for v in data["verified_changes"]:
            y=add("• "+v,438,y,536,size=20,maxlines=4,leading=26)+14
        if y>735:raise ValueError("Praise facts overflow")
        add("THANK THE LORD / CONTINUE TO PRAY",446,764,550,size=20,fill="#ffffff",weight="bold",maxlines=1)
        y=811
        for v in data["prayer_focus"]:
            y=add("• "+v,438,y,536,size=19,maxlines=3,leading=25)+9
        if y>983:raise ValueError("Praise prayer overflow")
        add(data["scripture"]["reference"],425,1010,560,size=19,weight="bold",maxlines=1)
        add(data["scripture"]["text"],107,1040,886,size=18,maxlines=2,leading=22)
        add(names,85,1092,925,size=14,maxlines=2,leading=16)
    else:
        add("FRIDAY",845,64,159,size=20,weight="bold",maxlines=1)
        add(data["headline"],133,478,889,size=31,weight="bold",maxlines=1)
        add(data["intro"],132,558,874,size=22,maxlines=2,leading=27)
        add(data["prayer_request"],113,667,868,size=23,leading=31,maxlines=8)
        add(data["scripture"]["reference"],168,861,738,size=22,weight="bold",fill=BRONZE,maxlines=1)
        add(data["scripture"]["text"],170,904,736,size=20,maxlines=4,leading=23)
    layers=f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<g id="locked-art" inkscape:groupmode="layer" inkscape:label="LOCKED TTT BRAND ART"><image x="0" y="0" width="{w}" height="{h}" href="data:image/png;base64,{paper}"/></g>
<g id="verified-geography" inkscape:groupmode="layer" inkscape:label="MAPS — separate, verify provenance">{''.join(map_layers)}</g>
<g id="editable-typography" inkscape:groupmode="layer" inkscape:label="EDITABLE TITLE/FACTS/PRAYER/SCRIPTURE/SOURCES">{''.join(texts)}</g>
<g id="draft-only" inkscape:groupmode="layer" inkscape:label="UNAPPROVED — remove only after verified design acceptance">
<rect x="1" y="1" width="{w-2}" height="37" fill="#fff0d4"/>
<text x="16" y="27" font-family="DejaVu Sans" font-size="18" fill="#971322" font-weight="bold">DRAFT LAYERED TEMPLATE — NOT APPROVED FOR PUBLICATION</text>
</g></svg>'''
    file=Path(out).resolve()
    if file.suffix.lower()!=".svg":raise ValueError("SVG output only")
    if any(x in file.parts for x in ("weekly-graphics","weekly-documents")):raise ValueError("No public output")
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(layers,encoding="utf-8")
    ET.parse(file)
    return {"format":kind,"file":str(file),"layers":4,
      "editable_text_objects":len(texts),"individual_map_layers":len(map_layers),
      "publication_allowed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("json");p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(render(json.loads(Path(a.json).read_text()),a.out),indent=2))
