#!/usr/bin/env python3
"""Reference-based draft layout compositor for Praise, Persecuted Church, Faith Friday.

Uses approved original PNGs. Never redesigns the emblem, masthead, decorative
frame or footer. Content panels are *reconstructed draft overlays*: the final
artwork is blocked until visually approved against each locked PNG.
"""
import argparse,json,re,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from reference_integrity import verify as verify_master
SIZES={"praise":(1086,1448),"persecuted":(1122,1402),"faith":(1087,1446)}
NAVY="#10224a";GOLD="#b78134";GREEN="#075138";BRONZE="#aa5624";PAPER="#fff0d4"
def font(size,bold=False,serif=False):
    roots=["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"]
    if not serif:roots.reverse()
    for p in roots:
        if Path(p).is_file():return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def t(draw,txt,x,y,w,font_size=21,color=NAVY,max_lines=3,leading=26,bold=False,serif=False):
    f=font(font_size,bold,serif)
    lines=[];line=""
    for word in str(txt).split():
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=f)[2]<=w:line=test
        else:
            if not line:raise ValueError("Single word too wide: "+word)
            lines.append(line);line=word
    if line:lines.append(line)
    if len(lines)>max_lines:raise ValueError("Text exceeds approved panel. Shorten text; never crop: "+str(txt)[:90])
    for item in lines:
        draw.text((x,y),item,font=f,fill=color)
        y+=leading
    return y
def centered(draw,txt,x,y,w,size=23,color=NAVY,bold=False,serif=False):
    f=font(size,bold,serif)
    measure=draw.textbbox((0,0),str(txt),font=f)[2]
    if measure>w:raise ValueError("Centered heading overflow: "+str(txt)[:90])
    draw.text((x+(w-measure)//2,y),str(txt),font=f,fill=color)
def bar(draw,box,color=NAVY):draw.rectangle(box,fill=color,outline=GOLD,width=3)
def map_png(im,draw,m,box):
    file=m.get("map_file")
    if file and Path(file).is_file():
        if not m.get("map_verified") or not m.get("map_source"):
            raise ValueError("Map file requires verified geography and attributable source")
        x,y,X,Y=box
        with Image.open(file) as image: tile=ImageOps.fit(image.convert("RGB"),(X-x-4,Y-y-4))
        im.paste(tile,(x+2,y+2))
    else:
        draw.rectangle(box,fill="#e1d1b4")
        x,y,X,Y=box
        t(draw,"VERIFIED MAP REQUIRED",x+12,y+24,X-x-22,18,NAVY,3,22,True)
    draw.rectangle(box,outline=GOLD,width=3)
def check(data):
    kind=data.get("format")
    if kind not in SIZES:raise ValueError("Unknown format")
    if data.get("approved") or data.get("publication_authorized"):
        raise ValueError("This draft compositor NEVER accepts publication authorization")
    for key in ("date_label","edition","source_names"):
        if not data.get(key):raise ValueError("Missing "+key)
    if not isinstance(data["source_names"],list):raise ValueError("Source names must be a list")
    if kind=="praise":
        for key in ("headline","outcome","verified_changes","prayer_focus","scripture","map"):
            if key=="map":
                if not isinstance(data.get("map"),dict):raise ValueError("Missing Praise map object")
            elif not data.get(key):raise ValueError("Missing Praise field "+key)
        if len(data["verified_changes"])>3 or len(data["prayer_focus"])>3:
            raise ValueError("Praise bullets exceed established panel capacity")
    elif kind=="persecuted":
        for key in ("country","region","verified_summary","pastoral_invitation","prayer_focus","scripture","map"):
            if key=="map":
                if not isinstance(data.get("map"),dict):raise ValueError("Missing Persecuted Church map object")
            elif not data.get(key):raise ValueError("Missing Persecuted Church field "+key)
        if len(data["prayer_focus"])!=4:raise ValueError("Persecuted format expects four prayer categories")
    else:
        for key in ("headline","intro","prayer_request","scripture"):
            if not data.get(key):raise ValueError("Missing Faith Friday field "+key)
    s=data["scripture"]
    if not isinstance(s,dict) or not s.get("reference") or not s.get("text"):raise ValueError("Scripture reference and complete passage text required")
    return kind
def heading(draw,data,kind):
    box=(820,40,1004,182) if kind=="praise" else ((850,35,1045,155) if kind=="persecuted" else (818,39,1008,173))
    x,y,X,Y=box
    draw.rectangle(box,fill=PAPER,outline=GOLD,width=2)
    centered(draw,{"praise":"WEDNESDAY","persecuted":"THURSDAY","faith":"FRIDAY"}[kind],x+6,y+10,X-x-12,20,NAVY,True)
    t(draw,data["date_label"],x+14,y+52,X-x-28,21,NAVY,3,29,True)
    if kind=="persecuted":t(draw,data["edition"],x+9,Y-32,X-x-18,14,NAVY,1,17,True)
def praise(im,d,data):
    # The original green praise title and the lower signed mountain footer remain intact.
    d.rectangle((45,330,1034,1110),fill=PAPER)
    bar(d,(47,331,1014,423),GREEN)
    centered(d,data["headline"].upper(),74,350,918,31,"#fff6d9",True,True)
    centered(d,data["outcome"],67,391,940,18,"#fff0d4",False,True)
    map_png(im,d,data["map"],(47,437,405,975))
    bar(d,(420,439,1011,483),GREEN)
    t(d,"VERIFIED PRAISE / WHAT CHANGED",451,445,550,23,"#fff7e3",1,26,True)
    y=493
    for item in data["verified_changes"]:
        d.ellipse((443,y+8,452,y+17),fill=GREEN)
        y=t(d,item,467,y,519,21,NAVY,4,27)+13
    bar(d,(420,735,1011,779),GREEN)
    t(d,"THANK THE LORD / CONTINUE TO PRAY",448,741,550,21,"#fff7e3",1,25,True)
    y=790
    for item in data["prayer_focus"]:
        d.ellipse((443,y+8,452,y+17),fill=GREEN)
        y=t(d,item,467,y,519,20,NAVY,3,26)+11
    if y>975:raise ValueError("Praise prayer section overflow")
    centered(d,data["scripture"]["reference"],50,991,963,20,NAVY,True,True)
    t(d,data["scripture"]["text"],95,1018,895,19,NAVY,2,23,False,True)
    t(d,"SOURCES: "+" • ".join(data["source_names"]),85,1070,925,16,NAVY,2,19,True)
def persecuted(im,d,data):
    # Leave upper approved TTT masthead and signed mountain footers untouched.
    d.rectangle((35,166,1084,1233),fill=PAPER)
    t(d,data["country"].upper(),44,170,467,58,NAVY,2,64,True,True)
    t(d,"REMEMBER OUR BROTHERS AND SISTERS IN CHRIST",47,286,476,26,BRONZE,3,31,True,True)
    t(d,data["region"].upper(),49,375,459,18,NAVY,2,22,True)
    map_png(im,d,data["map"],(516,174,1078,562))
    t(d,data["verified_summary"],43,435,454,20,NAVY,6,26,False,True)
    d.line((42,570,1079,570),fill=GOLD,width=3)
    t(d,data["pastoral_invitation"],45,582,1030,21,NAVY,5,28,False,True)
    bar(d,(44,722,1077,763),BRONZE)
    centered(d,"LET US TAKE THESE NEEDS BEFORE THE THRONE",67,727,990,24,"#fff5d6",True,True)
    cats=data["prayer_focus"]
    for i,m in enumerate(cats):
        x=40+i*265
        if i:d.line((x,773,x,1035),fill=GOLD,width=2)
        centered(d,m["title"].upper(),x+8,790,245,19,BRONZE,True,True)
        t(d,m["focus"],x+11,838,241,18,NAVY,9,22,False,True)
    d.rectangle((45,1055,1074,1118),fill="#f6e4c6",outline=GOLD,width=2)
    t(d,data["scripture"]["reference"],61,1062,989,21,BRONZE,1,25,True)
    t(d,data["scripture"]["text"],61,1085,989,18,NAVY,2,21)
    t(d,"REMEMBER THE PERSECUTED CHURCH",47,1131,973,23,BRONZE,1,26,True,True)
    t(d,"SOURCES: "+" • ".join(data["source_names"]),47,1169,990,16,NAVY,2,19,True)
def faith(im,d,data):
    # Preserve approved FAITH FRIDAY masthead/banner and scenic lower/footer block.
    d.rectangle((44,426,1045,997),fill=PAPER)
    centered(d,data["headline"],73,448,938,32,NAVY,True,True)
    d.line((217,509,875,509),fill=GOLD,width=2)
    centered(d,data["intro"],61,528,965,23,NAVY,False,True)
    t(d,data["prayer_request"],112,642,866,23,NAVY,8,31,False,True)
    d.rectangle((140,828,947,969),fill="#f8e6c8",outline=GOLD,width=3)
    centered(d,data["scripture"]["reference"],170,844,747,25,BRONZE,True,True)
    t(d,data["scripture"]["text"],173,880,737,21,NAVY,4,25,False,True)
def render(data,reference,out):
    kind=check(data)
    ref=Path(reference)
    if not ref.is_file():raise ValueError("Approved reference not found: no artwork fallback")
    verify_master(kind,ref)
    with Image.open(ref) as source: im=source.convert("RGB")
    if im.size!=SIZES[kind]:raise ValueError("Wrong approved reference dimensions")
    d=ImageDraw.Draw(im)
    heading(d,data,kind)
    {"praise":praise,"persecuted":persecuted,"faith":faith}[kind](im,d,data)
    d.rectangle((2,2,im.width-3,39),fill="#fff0d4")
    t(d,"DRAFT ARTWORK / NO PUBLICATION APPROVAL",17,8,im.width-30,21,BRONZE,1,23,True)
    dst=Path(out)
    if any(p in dst.parts for p in ("weekly-graphics","weekly-documents")):
        raise ValueError("Cannot write to public asset folders")
    dst.parent.mkdir(parents=True,exist_ok=True)
    im.save(dst,"PNG")
    return {"draft":True,"format":kind,"reference_sha256":hashlib.sha256(ref.read_bytes()).hexdigest(),
            "output":str(dst),"public_release_allowed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("json");p.add_argument("--reference",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(render(json.loads(Path(a.json).read_text(encoding="utf-8")),a.reference,a.out),indent=2))
