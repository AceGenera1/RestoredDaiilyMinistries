#!/usr/bin/env python3
"""Reject red matter headlines on approved 1122x1402 Monday Weekly Five layout.
Ignores legitimate red status badges, prayer prompts and footer outside regions.
"""
import argparse,colorsys,json
from PIL import Image
BOXES=[(316,341,668,370),(316,494,666,536),(316,649,666,693),(316,820,667,865),(316,978,666,1021)]
def check(path):
    im=Image.open(path).convert('RGB')
    if im.size!=(1122,1402):raise ValueError('Unexpected dimensions for this color profile')
    report=[]
    pixels=im.load()
    for n,(x0,y0,x1,y1) in enumerate(BOXES,1):
        red=bronze=total=0
        for y in range(y0,y1):
            for x in range(x0,x1):
                r,g,b=pixels[x,y]
                h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
                if s>.50 and r>105 and r>g+45 and r>b*1.5:
                    total+=1
                    if h<.048:red+=1
                    elif h<.125:bronze+=1
        red_ratio=red/max(total,1)
        bronze_ratio=bronze/max(total,1)
        good=total>=500 and red_ratio<=.12 and bronze_ratio>=.72
        report.append({'matter':n,'red_fraction':round(red_ratio,4),'bronze_fraction':round(bronze_ratio,4),'passed':good})
    return {'passed':all(x['passed'] for x in report),'headlines':report,
       'note':'ROI guard for approved Monday 1122x1402 layout only; human visual review remains required'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('png');args=ap.parse_args()
    result=check(args.png)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
