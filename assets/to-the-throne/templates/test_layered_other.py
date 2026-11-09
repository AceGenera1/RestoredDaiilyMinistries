#!/usr/bin/env python3
"""CI suite for four additional reference-locked layered SVG candidates."""
import json,tempfile,copy
from pathlib import Path
from xml.etree import ElementTree as ET
from layered_other import render
ROOT=Path(__file__).resolve().parent
def main():
    results={}
    ns={"s":"http://www.w3.org/2000/svg"}
    with tempfile.TemporaryDirectory() as tmp:
        for kind in ("monday","wednesday","praise","faith"):
            data=json.loads((ROOT/"samples"/(kind+"-render-test.json")).read_text())
            file=Path(tmp)/(kind+"-editable.svg")
            result=render(data,file)
            groups=ET.parse(file).findall(".//s:g",ns)
            assert [g.get("id") for g in groups]==["locked-art","verified-geography","editable-typography","draft-only"]
            assert groups[0].find("s:image",ns) is not None
            assert len(groups[2].findall("s:text",ns))>=6
            assert result["publication_allowed"] is False
            bad=copy.deepcopy(data);bad["approved"]=True
            try:render(bad,Path(tmp)/"unauthorized.svg")
            except ValueError:pass
            else:raise AssertionError("Approved flag bypassed by "+kind)
            results[kind]={"draft_passed":True,"layers":4,"text_fields":result["editable_text_objects"],"maps":result["individual_map_layers"]}
    print(json.dumps(results,indent=2))
if __name__=="__main__":main()
