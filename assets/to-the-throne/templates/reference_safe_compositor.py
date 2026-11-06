#!/usr/bin/env python3
"""Deterministic, fail-closed edits of approved To The Throne PNGs.

Manifest:
 {"reference":"master.png","reference_sha256":"<hex>",
  "patches":[{"file":"replacement.png","rect":[x,y,w,h]}],
  "allowed_change_rectangles":[[x,y,w,h]],"output":"DRAFT.png"}
No generated designs, no resizing, and no automatic publication.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageChops

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def compose(m):
    source=Path(m['reference'])
    if digest(source)!=m['reference_sha256']:
        raise ValueError('Reference does not match approved master SHA256')
    with Image.open(source) as src: original=src.convert('RGBA')
    final=original.copy()
    rectangles=[]
    for i,patch in enumerate(m.get('patches',[]),1):
        x,y,w,h=patch['rect']
        if any(not isinstance(v,int) for v in (x,y,w,h)) or w<1 or h<1 or x<0 or y<0 or x+w>final.width or y+h>final.height:
            raise ValueError('Patch geometry invalid: '+str(i))
        with Image.open(patch['file']) as layer0: layer=layer0.convert('RGBA')
        if layer.size!=(w,h):raise ValueError('Patch dimensions do not match region: '+str(i))
        rectangles.append((x,y,x+w,y+h))
        final.paste(layer,(x,y))
    allowed=[]
    for rect in m.get('allowed_change_rectangles',[]):
        x,y,w,h=rect
        if x<0 or y<0 or w<1 or h<1 or x+w>final.width or y+h>final.height:
            raise ValueError('Invalid authorized rectangle')
        allowed.append((x,y,x+w,y+h))
    for x0,y0,x1,y1 in rectangles:
        if not any(l<=x0 and t<=y0 and x1<=r and y1<=b for l,t,r,b in allowed):
            raise ValueError('Patch region not explicitly authorized')
    diff=ImageChops.difference(original,final)
    bands=diff.split()
    changed=bands[0]
    for band in bands[1:]:changed=ImageChops.lighter(changed,band)
    mask=changed.point(lambda v:255 if v else 0)
    bbox=mask.getbbox()
    if bbox:
        px=mask.load()
        for y in range(bbox[1],bbox[3]):
            for x in range(bbox[0],bbox[2]):
                if px[x,y] and not any(l<=x<r and t<=y<b for l,t,r,b in allowed):
                    raise ValueError('Protected pixel changed')
    output=Path(m['output'])
    if 'weekly-graphics' in output.parts or 'weekly-documents' in output.parts:
        raise ValueError('Direct production publication prohibited')
    output.parent.mkdir(parents=True,exist_ok=True)
    final.save(output,'PNG')
    return {'passed':True,'output':str(output),'changed_bbox':bbox,'protected_pixels_unchanged':True,'published':False}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('manifest')
    a=p.parse_args()
    print(json.dumps(compose(json.loads(Path(a.manifest).read_text())),indent=2))
