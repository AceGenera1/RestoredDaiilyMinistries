"""Exact git-blob identity check of approved brand masters. No size-only fallbacks."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPEC=json.loads((ROOT/"approved-master-lock.json").read_text(encoding="utf-8"))
def git_blob_id(payload):
    return hashlib.sha1(b"blob "+str(len(payload)).encode("ascii")+b"\0"+payload).hexdigest()
def verify(kind,file):
    data=Path(file).read_bytes()
    if kind not in SPEC:raise ValueError("Unknown approved design family: "+kind)
    actual=git_blob_id(data)
    required=SPEC[kind]["git_blob_sha1"]
    if actual!=required:
        raise ValueError("Reference PNG is NOT the locked GitHub master for "+kind+
                         ". Expected "+required+", received "+actual)
    return required
