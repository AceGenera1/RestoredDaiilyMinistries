#!/usr/bin/env python3
"""Negative-test the archive gate; no synthetic test can publish."""
import copy,json,tempfile
from pathlib import Path
from archive_release_gate import validate_manifest,REQUIRED
def rejected(a):
    try:validate_manifest(a)
    except ValueError:return
    raise AssertionError("An unsafe publication manifest passed preflight")
def test():
    base={"schema":"ttt-weekly-release-v1","edition":"TTT-0003","week_of":"2026-11-09",
      "approved_by_user":False,"research_verified":False,"visuals_approved":False,
      "publication_authorized":False,
      "assets":{k:{"edition":"TTT-0003","approved":False,"path":"/missing/not-real."+v["type"],"sha256":"0"*64} for k,v in REQUIRED.items()}}
    rejected(base)
    for field in ("approved_by_user","research_verified","visuals_approved","publication_authorized"):
        m=copy.deepcopy(base)
        for f in ("approved_by_user","research_verified","visuals_approved","publication_authorized"):m[f]=True
        m[field]=False
        rejected(m)
    m=copy.deepcopy(base)
    for f in ("approved_by_user","research_verified","visuals_approved","publication_authorized"):m[f]=True
    m["assets"].pop("praise_report")
    rejected(m)
    m=copy.deepcopy(base)
    for f in ("approved_by_user","research_verified","visuals_approved","publication_authorized"):m[f]=True
    for item in m["assets"].values():item["approved"]=True
    rejected(m) # Files must actually exist
    print(json.dumps({"passed":True,"negative_tests":7,"publication_performed":False}))
if __name__=="__main__":test()
