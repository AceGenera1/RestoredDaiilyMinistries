#!/usr/bin/env python3
"""Compare reconstructed draft layouts visually against exact approved masters.

Makes side-by-side reference/draft panels, amplified diff thumbnails, JSON scores.
Do NOT treat similarity numbers as publication approval; weekly data differ!
"""
import argparse,json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageChops,ImageStat
from reference_integrity import verify,SPEC
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
KINDS=("monday","wednesday","praise","persecuted","faith")
def compare(drafts,out):
    drafts=Path(drafts);out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    report={"status":"VISUAL QA ONLY—ALL GRAPHICS UNAPPROVED","comparisons":{}}
    panels=[]
    for kind in KINDS:
        original=REPO/SPEC[kind]["path"];verify(kind,original)
        draft=drafts/(kind+"-DRAFT.png")
        if not draft.is_file():raise ValueError("Missing "+str(draft))
        with Image.open(original) as a0,Image.open(draft) as b0:
            a=a0.convert("RGB");b=b0.convert("RGB")
        if a.size!=b.size:raise ValueError("Dimension drift: "+kind)
        diff=ImageChops.difference(a,b)
        hist=diff.convert("L").histogram()
        changed=sum(hist[1:])/max(1,a.width*a.height)
        mae=sum(i*n for i,n in enumerate(hist))/(max(1,sum(hist))*255)
        # Compare invariant lower footer only as a technical preservation guard.
        footer_y=int(a.height*.966)
        invariant=not ImageChops.difference(a.crop((0,footer_y,a.width,a.height)),b.crop((0,footer_y,b.width,b.height))).getbbox()
        if not invariant:raise ValueError("Protected end-of-image footer changed: "+kind)
        # Full-color differences are expected because approved originals feature different factual data.
        thumb_a=ImageOps.contain(a,(420,558))
        thumb_b=ImageOps.contain(b,(420,558))
        thumb_diff=ImageOps.contain(diff.point(lambda v:min(255,v*3)),(420,558))
        w=1260;h=630
        panel=Image.new("RGB",(w,h),"#faf3e8")
        d=ImageDraw.Draw(panel)
        for i,(im,title) in enumerate(zip((thumb_a,thumb_b,thumb_diff),("LOCKED ORIGINAL","DRAFT REBUILD","PIXEL DIFFERENCE (3×)"))):
            x=i*420+(420-im.width)//2
            panel.paste(im,(x,44))
            d.text((i*420+12,12),title,fill="#142c4f")
            if i<2:d.line((420*(i+1),0,420*(i+1),h),fill="#b98c47",width=2)
        d.text((12,609),f"{kind.upper()} — draft is not visually approved; changed luminance fraction {changed:.1%}.",fill="#8c4020")
        file=out/(kind+"-reference-vs-draft.png")
        panel.save(file)
        panels.append(file)
        report["comparisons"][kind]={"comparison_file":file.name,"source_sha":SPEC[kind]["git_blob_sha1"],
              "changed_luminance_fraction":round(changed,4),"mean_absolute_luminance_difference":round(mae,4),
              "protected_footer_unchanged":invariant,"publication_approved":False}
    report["all_renderers_final_approved"]=False
    (out/"VISUAL-QA.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--drafts",required=True);p.add_argument("--out",required=True)
    args=p.parse_args();print(json.dumps(compare(args.drafts,args.out),indent=2))
