#!/usr/bin/env python3
"""Run fail-closed regression checks against two approved master PNGs.
Usage: python test_locked_graphics.py <monday-ttt0001.png> <wednesday-ttt0001.png>
Requires Pillow. All test data are intentionally synthetic.
"""
import json,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parent
RENDER=ROOT/"locked_graphics.py"
def run(data,ref,target,draft=True):
    cmd=[sys.executable,str(RENDER),str(data),"--reference",str(ref),"--out",str(target)]
    if draft:cmd.append("--draft")
    return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
def check(mon,wed):
    status={}
    with tempfile.TemporaryDirectory() as temp:
        for kind,reference in (("monday",mon),("wednesday",wed)):
            sample=ROOT/"samples"/(kind+"-render-test.json")
            output=Path(temp)/(kind+".png")
            result=run(sample,reference,output)
            assert result.returncode==0,result.stderr
            a=Image.open(reference).convert("RGB");b=Image.open(output).convert("RGB")
            assert a.size==b.size
            assert ImageChops.difference(a.crop((65,42,222,164)),b.crop((65,42,222,164))).getbbox() is None,"Emblem changed"
            y=1350 if kind=="monday" else 1390
            assert ImageChops.difference(a.crop((0,y,a.width,a.height)),b.crop((0,y,b.width,b.height))).getbbox() is None,"Bottom motto changed"
            blocked=run(sample,reference,Path(temp)/(kind+"-final.png"),draft=False)
            assert blocked.returncode!=0,"Unapproved final rendering was permitted"
            payload=json.loads(sample.read_text())
            payload["matters"][0]["scripture"]["reference"]=payload["matters"][1]["scripture"]["reference"]
            invalid=Path(temp)/(kind+"-invalid.json");invalid.write_text(json.dumps(payload))
            assert run(invalid,reference,Path(temp)/(kind+"-bad.png")).returncode!=0,"Duplicate Scripture accepted"
            status[kind]={"draft_render":"PASS","original_emblem":"PRESERVED","bottom_motto":"PRESERVED","final_output":"BLOCKED","duplicate_scripture":"BLOCKED"}
    print(json.dumps(status,indent=2))
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit(__doc__)
    check(Path(sys.argv[1]),Path(sys.argv[2]))
