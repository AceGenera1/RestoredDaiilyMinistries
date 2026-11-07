#!/usr/bin/env python3
"""TTT reference-locked Monday / Wednesday DRAFT renderer. Pillow required.
Uses the approved PNG as an immutable masthead/footer, never image generation.
New contents replace baked text in the central region. All outputs are drafts
until visually approved; final output is deliberately blocked.
"""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageChops
from reference_integrity import verify as verify_master
NAVY="#102451";ORANGE="#AE6A27";GOLD="#C18A32";RED="#971322"
REGIONS={"monday":(1122,1402),"wednesday":(1086,1448)}
def ft(n=17,bold=False):
    opts=["/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"]
    for x in opts:
        if Path(x).exists():return ImageFont.truetype(x,n)
    return ImageFont.load_default()
def lines(draw,text,font,width,limit):
    result=[];line=""
    for word in str(text).split():
        new=(line+" "+word).strip()
        if draw.textbbox((0,0),new,font=font)[2]<=width:line=new
        else:
            if line:result.append(line)
            line=word
    if line:result.append(line)
    if len(result)>limit:raise ValueError("Field would clip; reduce wording or revise approved layout: "+str(text)[:85])
    return result
def write(draw,x,y,text,font,color,width,limit,step):
    for line in lines(draw,text,font,width,limit):
        draw.text((x,y),line,font=font,fill=color);y+=step
    return y
def mapslot(im,d,m,box,draft):
    x,y,X,Y=box
    f=m.get("map_file","")
    if f and Path(f).is_file():
        with Image.open(f) as original:
            tile=ImageOps.fit(original.convert("RGB"),(X-x-4,Y-y-4))
        im.paste(tile,(x+2,y+2))
    elif draft:
        d.rectangle(box,fill="#E3D4BA")
        write(d,x+9,y+22,"VERIFIED MAP REQUIRED",ft(14,True),NAVY,X-x-18,2,18)
    else:raise ValueError("Verified geographic map required: "+m["location"])
    d.rectangle(box,outline=GOLD,width=2)
def source(d,data,x,y,width):
    names=data["source_names"]
    label="SOURCES: "+" • ".join(names)+" | Full dated citations in this week's To The Throne archive."
    write(d,x,y,label,ft(15,True),NAVY,width,2,18)
def require(data,draft):
    kind=data.get("format")
    if kind not in REGIONS:raise ValueError("Only monday and wednesday are supported")
    if data.get("approved") or data.get("publication_authorized"):
        raise ValueError("Unapproved renderer refuses approved/publication flag")
    matter=data.get("matters",[])
    if (kind=="monday" and len(matter)!=5) or (kind=="wednesday" and not 1<=len(matter)<=5):
        raise ValueError("Invalid matter count")
    for key in ("edition","date_label","source_names"):
        if not data.get(key):raise ValueError("Missing "+key)
    refs=[]
    for m in matter:
        for key in ("location","heading","summary","prayer_focus","scripture"):
            if not m.get(key):raise ValueError("Missing matter "+key)
        if not isinstance(m["prayer_focus"],list):raise ValueError("Prayer Focus must be a list")
        for k in ("reference","text"):
            if not m["scripture"].get(k):raise ValueError("Incomplete Scripture")
        refs.append(m["scripture"]["reference"].lower())
        if m.get("map_file") and (not m.get("map_verified") or not m.get("map_source")):
            raise ValueError("Map file is not verified and attributed: "+m["location"])
        if not draft and not Path(m.get("map_file","")).is_file():raise ValueError("Missing verified map")
    if len(set(refs))!=len(refs):raise ValueError("Distinct Scripture passages required")
    if not draft:raise ValueError("UNAPPROVED renderer: final output disabled pending visual acceptance")
    return kind
def date_box(d,data,kind):
    box=(785,44,1067,153) if kind=="monday" else (819,38,1004,157)
    x,y,X,Y=box
    d.rectangle(box,fill="#FFF0D7",outline="#A5772E",width=2)
    head="WEEKLY INTERCESSION LETTER" if kind=="monday" else "WEDNESDAY"
    size=17
    while d.textbbox((0,0),head,font=ft(size,True))[2]>X-x-16:size-=1
    d.text((x+9,y+10),head,font=ft(size,True),fill=NAVY)
    d.line((x+16,y+35,X-16,y+35),fill=GOLD,width=2)
    if kind=="monday":
        d.text((x+18,y+43),data["edition"],font=ft(30,True),fill=NAVY)
        date_y=y+79
    else:date_y=y+47
    size=21
    while d.textbbox((0,0),data["date_label"],font=ft(size,True))[2]>X-x-18 and size>12:size-=1
    d.text((x+8,date_y),data["date_label"],font=ft(size,True),fill=NAVY)
def monday(im,d,data,draft):
    d.rectangle((35,296,1080,1077),fill="#FFF2DB")
    for i,m in enumerate(data["matters"]):
        y=297+i*155
        if i:d.line((37,y,1070,y),fill=GOLD,width=2)
        d.text((28,y+11),f"{i+1:02}",font=ft(47,True),fill=ORANGE)
        mapslot(im,d,m,(98,y+6,302,y+149),draft)
        d.line((668,y+8,668,y+149),fill=GOLD,width=2)
        write(d,320,y+6,m["location"].upper(),ft(20,True),NAVY,339,2,21)
        write(d,320,y+39,m["heading"].upper(),ft(19,True),ORANGE,339,2,21)
        write(d,320,y+79,m["summary"],ft(17),NAVY,339,4,18)
        d.text((678,y+8),"TAKE IT BEFORE THE THRONE",font=ft(18,True),fill=ORANGE)
        offset=y+31
        if len(m["prayer_focus"])>4:raise ValueError("Too many prayer requests for fixed Monday region")
        for prayer in m["prayer_focus"]:
            d.ellipse((683,offset+4,689,offset+10),fill=NAVY)
            offset=write(d,696,offset,prayer,ft(16),NAVY,216,2,16)+1
        sc=m["scripture"]
        write(d,682,max(y+107,offset+1),sc["reference"]+" — "+sc["text"],ft(14),NAVY,380,3,16)
        status=m.get("status","ACTIVE").upper()
        d.rounded_rectangle((924,y+7,1067,y+51),radius=8,fill=RED if status=="ACTIVE" else ORANGE)
        write(d,939,y+18,status,ft(18,True),"white",116,1,19)
    d.rectangle((41,1079,1072,1186),fill="#FFF2DB")
    write(d,49,1088,data.get("closing","Stand in the gap for these families and communities."),ft(17),NAVY,1015,3,19)
    source(d,data,49,1146,1015)
def wednesday(im,d,data,draft):
    d.rectangle((30,344,1053,1221),fill="#FFF2DB")
    for i,m in enumerate(data["matters"]):
        y=344+i*174
        if i:d.line((32,y,1050,y),fill=GOLD,width=2)
        mapslot(im,d,m,(35,y+5,274,y+169),draft)
        d.ellipse((282,y+14,330,y+62),fill=ORANGE)
        d.text((296,y+19),str(i+1),font=ft(29,True),fill="white")
        write(d,339,y+7,m["location"].upper(),ft(21,True),NAVY,339,2,23)
        write(d,339,y+43,m["heading"].upper(),ft(18,True),ORANGE,335,2,20)
        write(d,339,y+89,m["summary"],ft(17),NAVY,334,4,19)
        status=m.get("status","ACTIVE").upper()
        d.rectangle((686,y+3,1046,y+33),fill=RED if status=="ACTIVE" else ORANGE)
        write(d,711,y+7,status+" • INTERCESSION",ft(17,True),"white",320,1,17)
        d.text((705,y+37),"PRAYER FOCUS",font=ft(18,True),fill=ORANGE)
        off=y+64
        if len(m["prayer_focus"])>3:raise ValueError("Too many Wednesday prayer bullets")
        for prayer in m["prayer_focus"]:
            d.ellipse((706,off+6,712,off+12),fill=ORANGE)
            off=write(d,718,off,prayer,ft(15),NAVY,318,2,16)+2
        sc=m["scripture"]
        write(d,699,max(off+1,y+126),sc["reference"]+" — "+sc["text"],ft(14),NAVY,338,3,15)
    d.rectangle((31,1222,1045,1271),fill="#FFF2DB")
    source(d,data,50,1230,990)
def main():
    p=argparse.ArgumentParser();p.add_argument("data");p.add_argument("--reference",required=True)
    p.add_argument("--out",required=True);p.add_argument("--draft",action="store_true")
    a=p.parse_args();data=json.loads(Path(a.data).read_text(encoding="utf-8"));kind=require(data,a.draft)
    reference=Path(a.reference)
    if not reference.exists():raise ValueError("Approved reference missing: no fallback artwork allowed")
    verify_master(kind,reference)
    with Image.open(reference) as ref:im=ref.convert("RGB")
    if im.size!=REGIONS[kind]:raise ValueError("Approved reference dimensions incorrect")
    d=ImageDraw.Draw(im);date_box(d,data,kind)
    (monday if kind=="monday" else wednesday)(im,d,data,a.draft)
    output=Path(a.out)
    if "weekly-graphics" in output.parts or "weekly-documents" in output.parts:raise ValueError("Cannot write into published folders")
    d.rectangle((2,2,im.width-3,38),fill="#FFF5DD")
    d.text((16,7),"DRAFT RECONSTRUCTED LAYOUT — VISUAL APPROVAL REQUIRED",font=ft(18,True),fill=RED)
    output.parent.mkdir(parents=True,exist_ok=True)
    im.save(output,"PNG")
    print(json.dumps({"format":kind,"output":str(output),"reference_sha256":hashlib.sha256(reference.read_bytes()).hexdigest(),
      "size":im.size,"draft":True,"visual_release_approved":False}))
if __name__=="__main__":main()
