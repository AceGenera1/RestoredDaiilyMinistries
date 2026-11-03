#!/usr/bin/env python3
"""Self-contained TTT production smoke tests. Synthetic content; never publishes."""
import copy,json,tempfile,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"documents"))
from documents import validate,brief,source_sheet,qa_pdf
from graphics_patch import apply
def synthetic(kind):
    matters=[]
    for i in range(5):
        m={'headline':f'SYNTHETIC HEADING {i+1}','location':'TEST LOCATION','status':'ACTIVE',
           'verified_details':'The example agency reported a sample incident on November 2. This is synthetic test information and makes no real-world claim.','prayer_focus':['SAMPLE: prayer focus'],
           'scripture_reference':f'Test {i+1}:1','scripture_text':'SYNTHETIC TEXT FOR TESTS, NOT BIBLE SCRIPTURE.',
           'factual_basis':'SYNTHETIC FACTUAL BASIS. NOT A REAL REPORT.','last_verified':'2026-11-03 10:00',
           'sources':[{'outlet':f'TEST OUTLET {j+1}','title':'SYNTHETIC TITLE','published':'2026-11-03','establishes':'Sample support statement','url':f'https://example.org/test-{i}-{j}'} for j in range(3)]}
        if kind=='recording_brief':
            for k in ('factual_basis','sources','last_verified'):m.pop(k)
        else:
            for k in ('verified_details','prayer_focus','scripture_reference','scripture_text'):m.pop(k)
        matters.append(m)
    return {'document_type':kind,'edition':'TTT-DEMO','week_of':'2026-11-02','publication_date':'2026-11-03','approved':False,'publication_authorized':False,'matters':matters}
def rejected(fn):
    try:fn()
    except ValueError:return
    raise AssertionError('Validation did not reject forbidden input')
def run():
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)
        brief_data=synthetic('recording_brief')
        source_data=synthetic('public_source_sheet')
        validate(brief_data,'recording_brief');validate(source_data,'public_source_sheet')
        brief(brief_data,str(path/'brief.pdf'))
        source_sheet(source_data,str(path/'sources.pdf'))
        b=qa_pdf(str(path/'brief.pdf'),brief_data,'recording_brief')
        s=qa_pdf(str(path/'sources.pdf'),source_data,'public_source_sheet')
        assert b['pages']==2 and s['pages']==6 and s['hyperlinks']==15,(b,s)
        bad=copy.deepcopy(brief_data)
        bad['matters'][0]['scripture_reference']=bad['matters'][1]['scripture_reference']
        rejected(lambda:validate(bad,'recording_brief'))
        bad=copy.deepcopy(brief_data)
        bad['matters'][0]['verified_details']=['This list must be rejected']
        rejected(lambda:validate(bad,'recording_brief'))
        bad=copy.deepcopy(source_data)
        bad['matters'][0]['sources'][0]['url']='https://www.reuters.com/disallowed'
        rejected(lambda:validate(bad,'public_source_sheet'))
        bad=copy.deepcopy(brief_data)
        bad['matters'][0]['watch']='unknown'
        rejected(lambda:validate(bad,'recording_brief'))
        original=path/'original.png'
        patch=path/'patch.png'
        Image.new('RGBA',(60,40),'#ffffff').save(original)
        Image.new('RGBA',(18,12),'#bd7630').save(patch)
        result=apply(original,patch,'5,6,18,12',path/'edited.png')
        assert result['passed'] and result['outside_region_identical']
        print(json.dumps({'passed':True,'recording_brief_pages':b['pages'],
            'source_sheet_pages':s['pages'],'clickable_source_links':s['hyperlinks'],
            'negative_tests':['duplicate scripture','Reuters URL','forbidden uncertainty field','bullet-list verified details'],
            'pixel_guard_passed':True},indent=2))
if __name__=='__main__':run()
