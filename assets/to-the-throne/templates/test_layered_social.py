#!/usr/bin/env python3
"""Verify four editable social-share families, protected artwork and fail-closed rules."""
import copy,json,tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from layered_social import run,check,KINDS
ROOT=Path(__file__).resolve().parent
def rejected(call):
    try:call()
    except ValueError:return
    raise AssertionError("Invalid social candidate was accepted")
def test():
    ns={"s":"http://www.w3.org/2000/svg"}
    output={}
    with tempfile.TemporaryDirectory() as temp:
        for family in KINDS:
            data=json.loads((ROOT/"samples"/(family+"-layered-test.json")).read_text(encoding="utf-8"))
            svg=Path(temp)/(family+".svg")
            result=run(data,svg)
            groups=ET.parse(svg).findall(".//s:g",ns)
            assert [a.get("id") for a in groups]==["locked-social-master","editable-copy","mandatory-draft"]
            assert groups[0].find("s:image",ns) is not None
            assert len(groups[1].findall("s:text",ns))>=4
            assert result["draft"] and not result["approved"]
            bad=copy.deepcopy(data);bad["approved"]=True
            rejected(lambda:run(bad,Path(temp)/"not-allowed.svg"))
            bad=copy.deepcopy(data);bad["archive_url"]="https://example.org/placeholder"
            rejected(lambda:run(bad,Path(temp)/"not-allowed.svg"))
            if family!="persecuted-social":
                bad=copy.deepcopy(data);bad["scripture"]["text"]=""
                rejected(lambda:run(bad,Path(temp)/"not-allowed.svg"))
            output[family]={"editable":True,"protected_brand_master":True,"no_final_publication":True}
    print(json.dumps(output,indent=2))
if __name__=="__main__":test()
