#!/usr/bin/env python3
"""Canonical weekly record -> DRAFT PDFs, graphic content and QA. Never publishes."""
import argparse,json,sys
from pathlib import Path
from urllib.parse import urlsplit
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"documents"))
from documents import validate as validate_document,brief,source_sheet,qa_pdf
def build(record,output):
    if len(record.get('matters',[]))!=5:raise ValueError('Exactly five matters required')
    for key in ('edition','week_of','publication_date'):
        if not record.get(key):raise ValueError('Missing '+key)
    seen=set();sources=[];notes=[]
    for i,m in enumerate(record['matters'],1):
        for field in ('headline','location','status','summary','verified_details','prayer_focus','scripture_reference','scripture_text','sources'):
            if not m.get(field):raise ValueError('Matter %d missing %s'%(i,field))
        if not isinstance(m['verified_details'],str) or not m['verified_details'].strip():
            raise ValueError('Matter %d requires a concise, recording-ready verified-details paragraph, not a bullet list'%i)
        ref=m['scripture_reference'].strip().lower()
        if ref in seen:raise ValueError('Repeated Scripture: '+ref)
        seen.add(ref)
        if len(m['sources'])<3:notes.append('Matter %d has fewer than 3 corroborating sources; review necessary'%i)
        if not m.get('approved_map_image'):notes.append('Matter %d lacks a verified map; graphic is not approvable'%i)
        for s in m['sources']:
            if urlsplit(s['url']).netloc.lower().endswith('reuters.com'):raise ValueError('Reuters URL forbidden in public source sheet')
            if s['outlet'] not in sources:sources.append(s['outlet'])
    common={k:record[k] for k in ('edition','week_of','publication_date')}
    common.update(approved=bool(record.get('approved')),publication_authorized=bool(record.get('publication_authorized')))
    brief_data={**common,'document_type':'recording_brief','matters':[{k:m[k] for k in ('headline','location','status','verified_details','prayer_focus','scripture_reference','scripture_text')} for m in record['matters']]}
    source_data={**common,'document_type':'public_source_sheet','matters':[{**{k:m[k] for k in ('headline','location','status','sources')},'factual_basis':m['summary'],'last_verified':m.get('last_verified','Not supplied')} for m in record['matters']]}
    validate_document(brief_data,'recording_brief')
    validate_document(source_data,'public_source_sheet')
    output=Path(output).resolve()
    if 'weekly-documents' in output.parts or 'weekly-graphics' in output.parts:raise ValueError('Cannot write into published asset directories')
    output.mkdir(parents=True,exist_ok=True)
    brief_path=output/'recording-brief-DRAFT.pdf'
    source_path=output/'public-source-sheet-DRAFT.pdf'
    brief(brief_data,str(brief_path))
    source_sheet(source_data,str(source_path))
    qa={'recording_brief':qa_pdf(str(brief_path),brief_data,'recording_brief'),'public_source_sheet':qa_pdf(str(source_path),source_data,'public_source_sheet')}
    graphic={'kind':'weekly-five','title':'Weekly Intercession Letter','report_id':record['edition'],'week_of':record['week_of'],'date_label':record['publication_date'],'approved':False,'publication_authorized':False,'introduction':record.get('introduction',''),'matters':[{'location':m['location'],'region':m.get('region',''),'heading':m['headline'],'summary':m['summary'],'prayer_focus':m['prayer_focus'],'scripture':{'reference':m['scripture_reference'],'text':m['scripture_text']},'status':m['status'],'map_image':m.get('approved_map_image','')} for m in record['matters']],'sources':sources,'source_archive_url':'https://restoreddailyministries.org/to-the-throne-weekly.html','closing':record.get('closing',''),'tagline':'The news cycle may move on, but prayer never ceases.'}
    (output/'weekly-graphic-content-DRAFT.json').write_text(json.dumps(graphic,indent=2,ensure_ascii=False),encoding='utf-8')
    sys.path.insert(0,str(HERE))
    try:
        from render import make_html
        (output/'weekly-graphic-layout-DRAFT.html').write_text(make_html(graphic),encoding='utf-8')
    except ImportError: notes.append('Graphic HTML renderer unavailable')
    notes.append('Graphic layout is an UNAPPROVED draft, not pixel-faithful to the original')
    status={'edition':record['edition'],'matters':5,'source_links':sum(len(m['sources']) for m in record['matters']),'pdf_checks':qa,'warnings':notes,'published':False,'production_ready':False,'reason':'Approved pixel-faithful graphic templates not yet validated'}
    (output/'QA-DRAFT.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    return status
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('canonical_json');a.add_argument('--out',required=True)
    args=a.parse_args();print(json.dumps(build(json.loads(Path(args.canonical_json).read_text(encoding='utf-8')),args.out),indent=2))
