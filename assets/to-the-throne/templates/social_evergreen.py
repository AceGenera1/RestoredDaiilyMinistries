#!/usr/bin/env python3
"""Stage the FOUR already-approved, evergreen To The Throne social graphics.

They contain no week-specific claims, dates, figures or headlines that must be
re-rendered. Reuse their exact approved PNG bytes instead of redesigning.
This tool *never posts* and writes only to a review/staging directory.
"""
import argparse,json,shutil
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from reference_integrity import SPEC,verify,git_blob_id

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
KINDS=("monday-social","wednesday-social","praise-social","persecuted-social")
def stage(destination):
    destination=Path(destination).resolve()
    if any(x in destination.parts for x in ("weekly-graphics","weekly-documents")):
        raise ValueError("Cannot write directly into published weekly assets")
    destination.mkdir(parents=True,exist_ok=True)
    manifest={"schema":"ttt-evergreen-social-master-v1","approved_originals":4,
       "copies":{},"social_media_published":False,"caption_status":"NOT CREATED: verify weekly content separately"}
    thumbnails=[]
    for kind in KINDS:
        spec=SPEC[kind]
        path=REPO/spec["path"]
        verify(kind,path)
        original=path.read_bytes()
        output=destination/(kind+"-APPROVED-ORIGINAL.png")
        output.write_bytes(original)
        if output.read_bytes()!=original or git_blob_id(output.read_bytes())!=spec["git_blob_sha1"]:
            raise ValueError("Master changed during staging: "+kind)
        with Image.open(output) as im:
            thumbnail=ImageOps.contain(im.convert("RGB"),(460,250))
            size=im.size
        thumbnails.append((kind,thumbnail))
        manifest["copies"][kind]={"file":output.name,"bytes":len(original),"size":size,
           "master_git_sha":spec["git_blob_sha1"],"pixel_identical":True,"editable":False}
    sheet=Image.new("RGB",(1000,670),"#fbf3e5")
    draw=ImageDraw.Draw(sheet)
    for i,(kind,image) in enumerate(thumbnails):
        x=(i%2)*500+(500-image.width)//2
        y=(i//2)*320+34+(250-image.height)//2
        sheet.paste(image,(x,y))
        draw.text(((i%2)*500+20,(i//2)*320+11),kind.upper()+" - LOCKED APPROVED PNG",fill="#17284e")
    draw.text((18,648),"All four images are exact approved originals. Weekly post captions remain separate and require approval.",fill="#17284e")
    sheet.save(destination/"social-evergreen-master-review.png")
    (destination/"social-evergreen-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return manifest
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(stage(a.out),indent=2))
