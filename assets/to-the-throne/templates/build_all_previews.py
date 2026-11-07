#!/usr/bin/env python3
"""Build local, SYNTHETIC, UNPUBLISHABLE preview package for all five TTT families.
Copies approved social-share assets ONLY for visual comparison, not production.
"""
import argparse,json,subprocess,sys,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFont
from reference_integrity import verify
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
MASTERS=json.loads((ROOT/"approved-master-lock.json").read_text())
FAMILIES={"monday":"locked_graphics.py","wednesday":"locked_graphics.py",
          "praise":"special_graphics.py","persecuted":"special_graphics.py","faith":"special_graphics.py"}
SOCIAL=["monday-social","wednesday-social","praise-social","persecuted-social"]
def generate(out):
    out=Path(out).resolve()
    if "weekly-graphics" in out.parts or "weekly-documents" in out.parts:
        raise ValueError("Never write previews to publication folders")
    out.mkdir(parents=True,exist_ok=True)
    report={"status":"SYNTHETIC / DRAFT / DO NOT PUBLISH","rendered":{},"social_master_comparisons":{}}
    tiles=[]
    for kind,script in FAMILIES.items():
        master=REPO/MASTERS[kind]["path"]
        verify(kind,master)
        sample=ROOT/"samples"/f"{kind}-render-test.json"
        file=out/f"{kind}-DRAFT.png"
        cmd=[sys.executable,str(ROOT/script),str(sample),"--reference",str(master),"--out",str(file)]
        if script=="locked_graphics.py":cmd.append("--draft")
        result=subprocess.run(cmd,text=True,capture_output=True)
        if result.returncode:raise RuntimeError(f"{kind} failed: {result.stderr.strip()}")
        with Image.open(file) as img:
            size=img.size
            tile=ImageOps.contain(img.convert("RGB"),(420,550))
        tiles.append((kind,tile))
        report["rendered"][kind]={"file":file.name,"size":size,"approved":False,"master_git_blob_sha1":MASTERS[kind]["git_blob_sha1"]}
    for kind in SOCIAL:
        master=REPO/MASTERS[kind]["path"]
        verify(kind,master)
        with Image.open(master) as img: size=img.size
        report["social_master_comparisons"][kind]={"master_path":MASTERS[kind]["path"],"size":size,
              "verified":True,"reusable_editable_template_ready":False}
    contact=Image.new("RGB",(5*440,640),"#eee5d5")
    d=ImageDraw.Draw(contact)
    for i,(kind,img) in enumerate(tiles):
        x=i*440+10
        contact.paste(img,(x+(420-img.width)//2,50))
        d.text((x+8,20),kind.upper()+" — DRAFT ONLY",fill="#8d271c")
    d.text((16,611),"NO ACTUAL MATTERS OR SCRIPTURE — VISUAL QA ONLY. SOCIAL SHARE MASTERS VALIDATED, NOT YET RECONSTRUCTED.",fill="#8d271c")
    contact.save(out/"all-five-contact-sheet-DRAFT.png")
    (out/"preview-audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True)
    args=ap.parse_args();generate(args.out)
