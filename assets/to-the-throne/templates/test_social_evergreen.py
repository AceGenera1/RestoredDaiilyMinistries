#!/usr/bin/env python3
"""Pixel-identity tests for four evergreen social-share graphics."""
import tempfile,json
from pathlib import Path
from social_evergreen import stage,KINDS
from reference_integrity import SPEC,git_blob_id
def main():
    with tempfile.TemporaryDirectory() as tmp:
        report=stage(Path(tmp)/"social")
        assert report["approved_originals"]==4 and not report["social_media_published"]
        for kind in KINDS:
            f=Path(tmp)/"social"/(kind+"-APPROVED-ORIGINAL.png")
            assert f.is_file() and git_blob_id(f.read_bytes())==SPEC[kind]["git_blob_sha1"]
        assert (Path(tmp)/"social"/"social-evergreen-master-review.png").is_file()
        print(json.dumps({"passed":True,"original_masters":4,"all_byte_identical":True,"posted":False},indent=2))
if __name__=="__main__":main()
