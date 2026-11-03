#!/usr/bin/env python3
"""Replace one EXACT rectangle of an approved PNG with a prepared complete patch.
Never paints outside the selected rectangle; never publishes.
"""
import argparse,json
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
def apply(image,patch,rect,output):
    src=Image.open(image).convert('RGBA')
    p=Image.open(patch).convert('RGBA')
    x,y,w,h=[int(i) for i in rect.split(',')]
    if x<0 or y<0 or w<=0 or h<=0 or x+w>src.width or y+h>src.height:raise ValueError('Rectangle outside image')
    if p.size!=(w,h):raise ValueError('Complete patch dimensions must match allowed rectangle')
    final=src.copy();final.paste(p,(x,y))
    diff=ImageChops.difference(src,final)
    mask=diff.getchannel('R')
    for ch in ('G','B','A'):mask=ImageChops.lighter(mask,diff.getchannel(ch))
    allowed=Image.new('L',src.size,0)
    ImageDraw.Draw(allowed).rectangle((x,y,x+w-1,y+h-1),fill=255)
    if ImageChops.subtract(mask,allowed).getbbox():raise ValueError('Pixels changed outside approved rectangle')
    out=Path(output)
    if 'weekly-graphics' in out.parts or 'weekly-documents' in out.parts:raise ValueError('Cannot overwrite published folders')
    out.parent.mkdir(parents=True,exist_ok=True)
    final.save(out,'PNG')
    return {'passed':True,'image_size':src.size,'changed_bbox':mask.getbbox(),'allowed_rectangle':[x,y,w,h],'outside_region_identical':True,'published':False}
if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('original');a.add_argument('patch');a.add_argument('--rect',required=True,help='x,y,width,height');a.add_argument('--out',required=True)
    q=a.parse_args()
    print(json.dumps(apply(q.original,q.patch,q.rect,q.out),indent=2))
