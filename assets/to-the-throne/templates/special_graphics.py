#!/usr/bin/env python3
"""Reference-based draft layout compositor for Praise, Persecuted Church, Faith Friday.

Uses approved original PNGs. Never redesigns the emblem, masthead, decorative
frame or footer. Content panels are *reconstructed draft overlays*: the final
artwork is blocked until visually approved against each locked PNG.
"""
import argparse,json,re,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
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
def textured_panel(width,height):
    """Deterministic low-contrast parchment inside editable text area only."""
    import random
    rng=random.Random(19026)
    backdrop=Image.new("RGB",(width,height),(250,234,205))
    grain=Image.effect_noise((width,height),11).convert("L")
    tint=Image.new("RGB",(width,height),(213,183,136))
    backdrop=Image.blend(backdrop,Image.composite(tint,backdrop,grain),.08)
    cw=max(2,width//24);ch=max(2,height//24)
    low=Image.new("L",(cw,ch))
    low.putdata([rng.randrange(90,166) for _ in range(cw*ch)])
    low=low.resize((width,height),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(6))
    pale=Image.new("RGB",(width,height),(243,220,186))
    return Image.blend(backdrop,Image.composite(pale,backdrop,low),.13)
def original_round_icon(original,rect):
    """Crop protected original ornament with antialiased alpha around its circle."""
    crop=original.crop(rect)
    w,h=crop.size
    mask_large=Image.new("L",(w*3,h*3),0)
    ImageDraw.Draw(mask_large).ellipse((6,6,(w-2)*3,(h-2)*3),fill=255)
    return crop,mask_large.resize((w,h),Image.Resampling.LANCZOS)

def persecuted(im,d,data):
    """Persecuted Church: preserve approved asymmetrical visual grammar.

    The locked master uses 3 short prayer columns and a taller fourth column
    for those responsible for the attack. The scripture / remember / source
    elements occupy ONLY the first three columns beneath them. This is a
    draft reconstruction, not a pixel-faithful final master.
    """
    # Recover ornamental icon artwork and the original bronze invitation
    # directly from the locked reference, rather than redrawing new symbols.
    # Crop before clearing printed text from the underlying flattened image.
    original=im.copy()
    icon_boxes=((105,744,188,813),(367,744,454,813),
                (624,744,716,813),(904,744,994,813))
    icons=[original_round_icon(original,rect) for rect in icon_boxes]
    banner=original.crop((252,704,849,742))
    # Keep the masthead above y=166 and signed original mountain/footer
    # artwork below y=1233 completely identical to the approved image.
    im.paste(textured_panel(1066,1080),(35,167))
    d=ImageDraw.Draw(im)
    country=data["country"].upper()
    size=57
    while d.textbbox((0,0),country,font=font(size,True,True))[2]>460 and size>26:
        size-=1
    if d.textbbox((0,0),country,font=font(size,True,True))[2]>460:
        raise ValueError("Country title too long for locked Persecuted Church layout")
    d.text((43,173),country,font=font(size,True,True),fill=NAVY)
    t(d,"REMEMBER OUR BROTHERS",43,272,463,26,BRONZE,1,32,True,True)
    t(d,"AND SISTERS IN CHRIST",43,304,463,26,BRONZE,1,32,True,True)
    d.line((43,340,108,340),fill=GOLD,width=2)
    t(d,data["region"].upper(),120,335,372,18,NAVY,2,22,True)
    # Reserved upper-right map / illustration; no unverified borrowed map.
    map_png(im,d,data["map"],(517,172,1080,561))
    t(d,data["verified_summary"],43,373,460,20,NAVY,7,25,False,True)
    d.line((42,566,1078,566),fill=GOLD,width=2)
    t(d,data["pastoral_invitation"],44,577,1030,21,NAVY,5,26,False,True)
    # Bronze decorative bar copied from the approved original. It is a
    # protected design component, not dynamically redrawn typography.
    im.paste(banner,(252,704))
    d.line((40,724,252,724),fill=GOLD,width=2)
    d.line((849,724,1063,724),fill=GOLD,width=2)
    cols=((40,272),(274,535),(536,803),(805,1083))
    end_short=1045
    for i,col in enumerate(cols):
        x0,x1=col
        if i:
            d.line((x0,746,x0,1050 if i<3 else 1131),fill=GOLD,width=2)
        # Preserve precisely the approved prayer-category icon, rather than
        # turning it into a generic emoji or newly drawn religious emblem.
        icon,mask=icons[i]
        ox=(x0+x1-icon.width)//2
        im.paste(icon,(ox,744),mask)
        title=data["prayer_focus"][i]["title"].upper()
        hfont=font(18,True,True)
        words=[]
        for word in title.split():
            cand=(" ".join(words[-1:])+" "+word).strip() if words else word
            words.append(word)
        yy=t(d,title,x0+10,825,x1-x0-20,18,BRONZE,3,21,True,True)
        d.line((x0+14,yy+1,x1-12,yy+1),fill=GOLD,width=1)
        focus=data["prayer_focus"][i]["focus"]
        max_lines=12 if i==3 else 8
        y=t(d,focus,x0+11,yy+11,x1-x0-22,18,NAVY,max_lines,21,False,True)
        if y>(1128 if i==3 else 1039):
            raise ValueError("Persecuted Church prayer column overflow; revise wording/layout")
    # Scripture and remembrance only span first THREE columns. The fourth
    # long intercessory column must remain intact down to the lower margin.
    d.rectangle((32,1048,803,1124),fill="#f6e4c6",outline=GOLD,width=2)
    t(d,data["scripture"]["reference"],165,1056,620,21,BRONZE,1,24,True)
    t(d,data["scripture"]["text"],166,1080,621,17,NAVY,2,20,False,True)
    # Reuse the original Scripture book illustration: fixed approved artwork.
    book=original.crop((45,1054,137,1126))
    im.paste(book,(42,1052))
    t(d,"REMEMBER THE PERSECUTED CHURCH",112,1136,610,20,BRONZE,1,23,True)
    t(d,"Keep lifting up our brothers and sisters in Christ.",114,1165,616,16,NAVY,2,18,False,True)
    # Document attribution block occupies right bottom, outside the
    # three-column scripture/closing content.
    d.line((727,1142,1069,1142),fill=GOLD,width=1)
    t(d,"SOURCES: "+" • ".join(data["source_names"]),732,1151,335,15,NAVY,2,19,True)
    t(d,"Full references: weekly archive.",732,1182,331,13,NAVY,1,16)
    # Original artwork is flattened, so uneditable old body/footer words
    # survive just above the permanent signoff. Erase only this narrow,
    # field-specific strip; preserve the authentic In Christ and signature.
    im.paste(textured_panel(989,34),(110,1213))

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
