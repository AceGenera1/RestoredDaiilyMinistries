#!/usr/bin/env python3
"""To The Throne weekly release preflight and immutable ZIP packager.

Does not publish, post to social media, or edit the public archive.
Requires explicit per-asset authorization, authentic paths and complete release.
Use: python archive_release_gate.py manifest.json --out /tmp/TTT-REVIEW.zip
     python archive_release_gate.py manifest.json --check-only
"""
import argparse,datetime,hashlib,json,re,sys,zipfile
from pathlib import Path
from urllib.parse import urlsplit
from PIL import Image
import fitz

REQUIRED={
    "weekly_letter":{"type":"pdf","name":"Weekly Intercession Letter"},
    "episode_notes":{"type":"pdf","name":"Episode Recording Notes"},
    "sources_verification":{"type":"pdf","name":"Public Sources & Verification"},
    "intercession_update":{"type":"png","name":"Wednesday Intercession Update"},
    "praise_report":{"type":"png","name":"Friday Praise Report"}
}
BANNED=("synthetic","placeholder","draft","test only","verified map required","example.org")
def error(message):raise ValueError(message)
def sha256(data):return hashlib.sha256(data).hexdigest()
def validate_manifest(manifest):
    if manifest.get("schema")!="ttt-weekly-release-v1":error("Unknown release schema")
    edition=manifest.get("edition","")
    if not re.fullmatch(r"TTT-\d{4}",edition):error("Invalid edition")
    try:datetime.date.fromisoformat(manifest["week_of"])
    except (ValueError,KeyError,TypeError):error("Invalid week_of")
    if manifest.get("approved_by_user") is not True: error("Explicit weekly user approval absent")
    if manifest.get("research_verified") is not True:error("Verified research approval absent")
    if manifest.get("visuals_approved") is not True:error("Visual signoff absent")
    if manifest.get("publication_authorized") is not True:error("Publication not authorized")
    # A design approval or checksum is NOT permission to recycle previous
    # week's facts. Every release must carry a separately verified canonical
    # editorial record, and a traceable render from that exact content.
    editorial=manifest.get("canonical_editorial")
    if not isinstance(editorial,dict):
        error("Release missing canonical editorial and provenance")
    f=editorial.get("path")
    if not isinstance(f,str) or not f.strip():
        error("Canonical editorial source file is required")
    canonical_file=Path(f).resolve()
    if not canonical_file.is_file() or canonical_file.is_symlink():
        error("Approved canonical editorial file missing or symlink")
    actual_hash=sha256(canonical_file.read_bytes())
    if actual_hash!=editorial.get("sha256"):
        error("Approved editorial changed after release approval")
    approved_data=json.loads(canonical_file.read_text(encoding="utf-8"))
    if approved_data.get("edition")!=edition:
        error("Editorial edition differs from release edition")
    if approved_data.get("week_of")!=manifest["week_of"]:
        error("Editorial week differs from release week")
    if edition=="TTT-0003":
        from editorial_lock import check,FIXTURE
        check(approved_data,json.loads(FIXTURE.read_text(encoding="utf-8")))
    if not editorial.get("renderer_payload_verified"):
        error("Weekly graphics renderer must confirm exact approved factual fields")
    if not editorial.get("original_closing_present"):
        error("Complete approved closing paragraph must be present")
    assets=manifest.get("assets")
    if not isinstance(assets,dict) or set(assets)!=set(REQUIRED):
        error("Weekly archive requires exactly five resources: "+", ".join(REQUIRED))
    fingerprints={};detail={}
    for key,kind in REQUIRED.items():
        item=assets[key]
        if not isinstance(item,dict) or item.get("approved") is not True:
            error(key+": approval missing")
        if item.get("edition")!=edition:error(key+": wrong edition")
        if not isinstance(item.get("path"),str) or not item["path"].strip():
            error(key+": missing path")
        path=Path(item["path"]).resolve()
        if not path.is_file() or path.is_symlink():error(key+": source missing or symlink")
        if any(token in path.name.lower() for token in BANNED):error(key+": draft/test filename rejected")
        contents=path.read_bytes()
        digest=sha256(contents)
        if not re.fullmatch("[a-f0-9]{64}",str(item.get("sha256",""))) or digest!=item["sha256"]:
            error(key+": immutable checksum mismatch")
        if kind["type"]=="pdf":
            if not contents.startswith(b"%PDF-"):error(key+": wrong PDF signature")
            try:
                pdf=fitz.open(stream=contents,filetype="pdf")
                if pdf.needs_pass or len(pdf)<1:error(key+": PDF protected or empty")
                text="\n".join(page.get_text() for page in pdf)
                if any(x in text.lower() for x in BANNED):error(key+": draft/test text")
                if edition.lower() not in text.lower():error(key+": edition not present in document")
                if key=="sources_verification":
                    if len(pdf)!=6:error("Public Source Sheet must be 6 pages")
                    urls=[l.get("uri") for pg in pdf for l in pg.get_links() if l.get("uri")]
                    if len(urls)<5:error("Source sheet lacks working clickable source references")
                    if any(urlsplit(u).scheme not in ("https",) for u in urls):
                        error("Source sheet has non-HTTPS hyperlinks")
                if key=="episode_notes":
                    for must in ("KEY VERIFIED DETAILS","PRAYER FOCUS"):
                        if must not in text.upper():error("Recording notes missing "+must)
                    for forbidden in ("WATCH / UNCERTAINTY","SUGGESTED OPENING","SUGGESTED TRANSITION"):
                        if forbidden in text.upper():error("Recording notes include coaching/uncertainty")
                detail[key]={"pages":len(pdf),"bytes":len(contents)}
                pdf.close()
            except (fitz.FileDataError,fitz.EmptyFileError) as e:error(key+": invalid PDF ("+str(e)+")")
        else:
            try:
                with Image.open(path) as img:
                    img.verify()
                with Image.open(path) as img:
                    if min(img.size)<900:error(key+": unusually small graphic")
                    detail[key]={"width":img.width,"height":img.height,"bytes":len(contents)}
            except (OSError,SyntaxError) as e:error(key+": invalid graphic ("+str(e)+")")
        fingerprints[key]={"name":kind["name"],"source_path":str(path),"sha256":digest}
    return {"edition":edition,"week_of":manifest["week_of"],"status":"PRE-FLIGHT PASSED; NO PUBLICATION OCCURRED",
        "count":5,"assets":fingerprints,"validated":detail,
        "important":"Checks file integrity and structure, not the truth of reports or Scripture."}
def run(manifest,out=None):
    report=validate_manifest(manifest)
    if out is None:return report
    dst=Path(out).resolve()
    if dst.suffix.lower()!=".zip":error("Output must be .zip")
    if any(p in dst.parts for p in ("weekly-documents","weekly-graphics")):
        error("Cannot write to published repository directories")
    dst.parent.mkdir(parents=True,exist_ok=True)
    packed={"schema":"ttt-weekly-release-review-v1","edition":report["edition"],"week_of":report["week_of"],
       "files":{},"release_gate":"PASS","publication_performed":False}
    for key in REQUIRED:
        p=Path(manifest["assets"][key]["path"])
        packed["files"][key]={"name":key+"."+("pdf" if REQUIRED[key]["type"]=="pdf" else "png"),
            "sha256":report["assets"][key]["sha256"]}
    with zipfile.ZipFile(dst,"w",zipfile.ZIP_DEFLATED) as z:
        for key,val in packed["files"].items():
            z.write(manifest["assets"][key]["path"],arcname=val["name"])
        z.writestr("RELEASE-PREFLIGHT.json",json.dumps(packed,indent=2)+"\n")
    report["review_zip"]=str(dst)
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("manifest");p.add_argument("--out")
    p.add_argument("--check-only",action="store_true");args=p.parse_args()
    if args.check_only and args.out:error("Choose --out OR --check-only")
    if not args.check_only and not args.out:error("Supply --check-only or --out")
    manifest=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    print(json.dumps(run(manifest,None if args.check_only else args.out),indent=2))
if __name__=="__main__":main()
