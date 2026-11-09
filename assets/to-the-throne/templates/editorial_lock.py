#!/usr/bin/env python3
"""Fail-closed weekly editorial + template contract.

No OCR or image inference is an acceptable replacement for rendering from the
approved canonical data. This guards DATA before any image/PDF is generated.
It does not certify the rendered pixels or a source's factual accuracy.
"""
import argparse,copy,json,re
from pathlib import Path
from urllib.parse import urlparse

HERE=Path(__file__).resolve().parent
FIXTURE=HERE/"approved/TTT-0003-canonical.json"
LEGACY=("AMIET MARKET","TAGADAYAT","BUNDIBUGYO","TTT-0001",
        "DRONE ATTACKS KILL AND INJURE","TAIZ")
EXPECTED=("yemen-sanaa","sudan-shelter","gaza-flood",
          "florida-brevard","ukraine-school")
def check(record,approved):
    if record.get("schema")!="ttt-canonical-editorial-v1":
        raise ValueError("Wrong canonical editorial schema")
    if (record.get("edition"),record.get("week_of")) != (approved["edition"],approved["week_of"]):
        raise ValueError("Edition/week mismatch. Refusing old-week content")
    if record.get("publication_date")!=approved["publication_date"]:
        raise ValueError("Publication date mismatch")
    actual=record.get("matters")
    if not isinstance(actual,list) or len(actual)!=5:
        raise ValueError("Exactly five current approved matters required")
    if tuple(m.get("id") for m in actual)!=EXPECTED:
        raise ValueError("Incorrect matters or order: historical matters forbidden")
    for index,(m,reference) in enumerate(zip(actual,approved["matters"]),1):
        for field in ("id","location","headline","scripture_reference",
                      "scripture_text","prayer_focus","factual_core","source"):
            if m.get(field)!=reference[field]:
                raise ValueError("Matter %d changed approved field: %s"%(index,field))
        if not m.get("prayer_focus") or not isinstance(m["prayer_focus"],list):
            raise ValueError("Empty prayer focus for matter %d"%index)
        u=urlparse(m["source"])
        if u.scheme!="https" or not u.netloc:
            raise ValueError("Unsafe or missing source URL for matter %d"%index)
    if record.get("mandatory_closing")!=approved["mandatory_closing"]:
        raise ValueError("Full original closing paragraph missing or changed")
    if record.get("closing_tagline")!=approved["closing_tagline"]:
        raise ValueError("Closing prayer tagline missing or changed")
    content=json.dumps(record,ensure_ascii=False).upper()
    for term in LEGACY:
        if term in content:raise ValueError("BANNED historical content in current week: "+term)
    return {"passed":True,"edition":approved["edition"],"matters":list(EXPECTED),
            "full_closing_required":True,"five_unique_verses":True,
            "publication_authorized":False}
def validate_renderer_payload(canonical,payload):
    """Renderers must explicitly bind editorial source values, not free-type them."""
    if payload.get("edition")!=canonical["edition"]:
        raise ValueError("Renderer uses wrong edition")
    if len(payload.get("matters",[]))!=5:
        raise ValueError("Renderer lost one or more matters")
    for i,(data,m) in enumerate(zip(payload["matters"],canonical["matters"]),1):
        expected=(m["location"],m["headline"],m["scripture_reference"],m["scripture_text"])
        verse=data.get("scripture",{})
        actual=(data.get("location"),data.get("heading"),
                verse.get("reference"),verse.get("text"))
        if actual!=expected:
            raise ValueError("Renderer field mismatch at matter %d"%i)
    if payload.get("closing")!=canonical["mandatory_closing"]:
        raise ValueError("Renderer shortened or omitted original closing")
    if payload.get("approved") or payload.get("publication_authorized"):
        raise ValueError("Approved data is NOT automatic publication authorization")
    return True
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidate",default=str(FIXTURE))
    p.add_argument("--renderer-payload")
    a=p.parse_args()
    canonical=json.loads(FIXTURE.read_text(encoding="utf-8"))
    candidate=json.loads(Path(a.candidate).read_text(encoding="utf-8"))
    report=check(candidate,canonical)
    if a.renderer_payload:
        payload=json.loads(Path(a.renderer_payload).read_text(encoding="utf-8"))
        validate_renderer_payload(canonical,payload)
        report["renderer_payload_checked"]=True
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
