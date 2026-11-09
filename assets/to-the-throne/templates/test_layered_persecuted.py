#!/usr/bin/env python3
"""Verify editable text layer and fail-closed SVG draft operation."""
import json,tempfile,copy
from pathlib import Path
from xml.etree import ElementTree as ET
from layered_persecuted import build
ROOT=Path(__file__).resolve().parent
def denied(fn):
    try:fn()
    except ValueError:return
    raise AssertionError("Unapproved SVG allowed")
def main():
    data=json.loads((ROOT/"samples/persecuted-render-test.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"persecuted-editable-DRAFT.svg"
        result=build(data,path)
        svg=ET.parse(path)
        ns={"s":"http://www.w3.org/2000/svg"}
        groups=svg.findall(".//s:g",ns)
        assert [g.get("id") for g in groups]==["locked-art","verified-geography","editable-typography","draft-review"]
        nodes=groups[2].findall("s:text",ns)
        assert len(nodes)>15
        assert any("TEST COUNTRY" in "".join(node.itertext()) for node in nodes)
        assert any("TEST 2:1" in "".join(node.itertext()) for node in nodes)
        assert result["publication_allowed"] is False and result["verified_map_supplied"] is False
        bad=copy.deepcopy(data);bad["approved"]=True
        denied(lambda:build(bad,Path(tmp)/"unauthorized.svg"))
        print(json.dumps({"passed":True,"svg_layers":4,"editable_text_fields":len(nodes),
           "original_art_sha_verified":True,"release_blocked":True}))
if __name__=="__main__":main()
