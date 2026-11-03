#!/usr/bin/env python3
"""Deterministic To The Throne PDFs. Draft-only CLI; never publishes.
Usage: python documents.py INPUT.json --kind recording_brief|public_source_sheet --out preview.pdf --qa
Requires reportlab; --qa also requires pymupdf.
"""
import argparse,json,re
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
NAVY=colors.HexColor('#111C32')
GOLD=colors.HexColor('#B78730')
PALE=colors.HexColor('#F7EAD5')
WARM=colors.HexColor('#FBF5E9')
INK=colors.HexColor('#1B2B46')
MOTTO='TRUTH BEFORE NARRATIVE  |  PRAYER BEFORE REACTION  |  AS FAST AS TRUTH ALLOWS'
BANNED=['watch / uncertainty','known limitations','suggested opening','suggested transition','scripture verification','ministry focus']
def clean(x):return escape(str(x)).replace('\n','<br/>')
def style(name,size=9,leading=None,color=INK,bold=False,align=TA_LEFT):
    return ParagraphStyle(name,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=leading or size*1.36,textColor=color,alignment=align,spaceAfter=0)
S={'title':style('title',17,20,NAVY,True,TA_CENTER),'subtitle':style('subtitle',12,16,GOLD,True,TA_CENTER),'center':style('center',8,11,INK,False,TA_CENTER),'normal':style('normal',9,12,INK),'small':style('small',8,10,INK),'label':style('label',7.8,11,GOLD,True),'head':style('head',11,14,colors.white,True),'goldhead':style('goldhead',10,13,GOLD,True),'navyhead':style('navyhead',11,14,NAVY,True)}
def P(v,name='normal'):return Paragraph(clean(v),S[name])
def footer(canvas,doc):
    canvas.saveState()
    w,h=letter
    canvas.setStrokeColor(GOLD);canvas.setLineWidth(.5);canvas.line(28,36,w-28,36)
    canvas.setFillColor(NAVY);canvas.setFont('Helvetica-Bold',7)
    canvas.drawCentredString(w/2,23,MOTTO)
    if getattr(doc,'_ttt_draft',True):
        canvas.setFillColor(colors.HexColor('#8A6262'))
        canvas.setFont('Helvetica-Bold',7)
        canvas.drawRightString(w-28,h-17,'DRAFT REVIEW - NOT FOR PUBLICATION')
    canvas.restoreState()
def header(title,edition,week):
    return [P('TO THE THRONE','title'),P(title,'subtitle'),P('Edition: '+edition+'  •  Week of: '+week,'center'),Spacer(1,13)]
def require(v,name):
    if not isinstance(v,str) or not v.strip():raise ValueError('Missing '+name)
    if '[REPLACE' in v.upper() or 'PLACEHOLDER' in v.upper():raise ValueError('Placeholder '+name)
def validate(data,kind):
    if data.get('document_type')!=kind:raise ValueError('document_type must be '+kind)
    for k in ('edition','week_of'):require(data.get(k),k)
    matters=data.get('matters')
    if not isinstance(matters,list) or len(matters)!=5:raise ValueError('Exactly five matters required')
    for n,m in enumerate(matters,1):
        for k in ('headline','location','status'):require(m.get(k),f'Matter {n} {k}')
        if kind=='recording_brief':
            details=m.get('verified_details')
            if not isinstance(details,str) or not details.strip():
                raise ValueError('Matter %d needs a single recording-ready Key Verified Details paragraph, not bullets'%n)
            if any(details.lstrip().startswith(x) for x in ('•','- ','* ')) or '\n•' in details or '\n- ' in details:
                raise ValueError('Matter %d Key Verified Details must be connected prose, not bullets'%n)
            if not isinstance(m.get('prayer_focus'),list) or not m['prayer_focus']:
                raise ValueError('Matter %d needs separate Prayer Focus bullet points'%n)
            for k in ('scripture_reference','scripture_text'):require(m.get(k),f'Matter {n} {k}')
            for field in ('watch','uncertainty','coaching','intro','prayer_script'):
                if field in m:raise ValueError('Forbidden recording field '+field)
        else:
            require(m.get('factual_basis'),f'Matter {n} factual_basis')
            require(m.get('last_verified'),f'Matter {n} last_verified')
            sources=m.get('sources',[])
            if not 1<=len(sources)<=3:raise ValueError('Matter %d needs 1–3 verified sources; flag fewer than 3 for review'%n)
            for j,s in enumerate(sources,1):
                for k in ('outlet','title','published','establishes','url'):require(s.get(k),f'Matter {n} source {j} {k}')
                u=urlsplit(s['url'])
                if u.scheme!='https' or not u.netloc:raise ValueError('Source URLs must be absolute HTTPS')
                if 'reuters.com' in u.netloc.lower():raise ValueError('Public sources cannot link to Reuters')
            for k in ('scripture','prayer_focus','coaching','internal_notes'):
                if k in m:raise ValueError('Forbidden public source field '+k)
    if kind=='recording_brief':
        refs=[m['scripture_reference'].lower().strip() for m in matters]
        if len(refs)!=len(set(refs)):raise ValueError('Scripture references must be unique')
    if data.get('publication_authorized') and not data.get('approved'):raise ValueError('Cannot authorize publication without approval')
    return True
def table_style(extra=[]):
    return TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]+extra)
def brief(data,out):
    story=header('WEEKLY RECORDING BRIEF',data['edition'],data['week_of'])
    for i,m in enumerate(data['matters'],1):
        band=Table([[P('%02d'%i,'head'),P(m['headline'],'head')]],colWidths=[90,460])
        band.setStyle(table_style([('BACKGROUND',(0,0),(0,0),GOLD),('BACKGROUND',(1,0),(1,0),NAVY)]))
        fields=[('LOCATION',P(m['location'])),('STATUS',P(m['status'])),('KEY VERIFIED DETAILS',P(m['verified_details'])),('PRAYER FOCUS',[P('• '+x) for x in m['prayer_focus']]),('SCRIPTURE',[P(m['scripture_reference'],'goldhead'),P(m['scripture_text'])])]
        rows=[[P(label,'label'),value] for label,value in fields]
        tbl=Table(rows,colWidths=[105,445],hAlign='LEFT')
        tbl.setStyle(table_style([('BACKGROUND',(0,0),(0,-1),PALE),('BACKGROUND',(1,0),(1,-1),colors.white),('LINEBELOW',(0,-1),(-1,-1),.6,GOLD)]))
        story.append(KeepTogether([Spacer(1,8),band,tbl,Spacer(1,14)]))
        if i==2:story.append(PageBreak())
    doc=SimpleDocTemplate(out,pagesize=letter,leftMargin=31,rightMargin=31,topMargin=28,bottomMargin=51,title='TTT '+data['edition']+' Weekly Recording Brief',author='Restored Daily Ministries')
    doc._ttt_draft=not (data.get('approved') and data.get('publication_authorized'))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
def source_cover(data):
    return header('PUBLIC SOURCE SHEET',data['edition'],data['week_of'])+[Spacer(1,24),P('PUBLICATION DATE: '+data.get('publication_date',data['week_of']),'center'),Spacer(1,40),P('PURPOSE','goldhead'),Spacer(1,8),P("This sheet provides the public sources supporting the factual context used in this week's To The Throne intercession letter and video. Each matter below includes the sources used to support the factual information shared with the body of Christ."),Spacer(1,25),P('HOW TO READ IT','goldhead'),Spacer(1,8),P('Each source is paired with a short statement explaining exactly what that source establishes. A source is never treated as supporting a claim beyond what it actually reports or documents.'),Spacer(1,25),P('SOURCE STANDARD','goldhead'),Spacer(1,8),P('Primary and credible local sources are prioritized where available. Consequential claims are independently corroborated when reasonably possible. Copies of the same underlying report are not treated as independent confirmation.'),Spacer(1,75),P('The news cycle may move on, but prayer never ceases.','center'),PageBreak()]
def source_sheet(data,out):
    story=source_cover(data)
    for i,m in enumerate(data['matters'],1):
        story.append(P('TO THE THRONE','center'))
        band=Table([[P('%02d'%i,'head'),[P(m['location'],'label'),P(m['headline'],'navyhead')]]],colWidths=[245,305])
        band.setStyle(table_style([('BACKGROUND',(0,0),(0,0),NAVY),('BACKGROUND',(1,0),(1,0),PALE),('TOPPADDING',(0,0),(-1,-1),13),('BOTTOMPADDING',(0,0),(-1,-1),13)]))
        story.extend([Spacer(1,7),band,Spacer(1,14),P('FACTUAL BASIS','goldhead'),Spacer(1,7),P(m['factual_basis']),Spacer(1,16)])
        for j,s in enumerate(m['sources'],1):
            link='<link href="'+escape(s['url'],quote=True)+'" color="#13233F"><u>'+escape(s['url'])+'</u></link>'
            rows=[[P('SOURCE %d'%j,'label'),P(s['outlet']+' — '+s['title'],'small')],[P('Published / Updated','small'),P(s['published'],'small')],[P('Establishes','small'),P(s['establishes'],'small')],[P('Open source','small'),Paragraph(link,S['small'])]]
            tbl=Table(rows,colWidths=[200,350],hAlign='LEFT')
            tbl.setStyle(table_style([('BACKGROUND',(0,0),(-1,0),WARM),('LINEBELOW',(0,-1),(-1,-1),.2,PALE)]))
            story.extend([tbl,Spacer(1,12)])
        story.extend([Spacer(1,5),P('PUBLIC STATUS: '+m['status'],'small'),P('LAST VERIFIED: '+m['last_verified']+' (America/Chicago)','small')])
        if i!=5:story.append(PageBreak())
    doc=SimpleDocTemplate(out,pagesize=letter,leftMargin=31,rightMargin=31,topMargin=29,bottomMargin=52,title='TTT '+data['edition']+' Public Source Sheet',author='Restored Daily Ministries')
    doc._ttt_draft=not (data.get('approved') and data.get('publication_authorized'))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
def qa_pdf(path,data,kind):
    import fitz
    pdf=fitz.open(path)
    if kind=='public_source_sheet' and len(pdf)!=6:raise ValueError('Public Source Sheet must be exactly 6 pages; current count is '+str(len(pdf)))
    text='\n'.join(page.get_text() for page in pdf)
    norm=lambda v:re.sub(r'\s+',' ',v)
    for i,m in enumerate(data['matters'],1):
        if m['headline'] not in text:raise ValueError('Missing headline '+str(i))
        if kind=='recording_brief':
            details=re.sub(r'\\s+',' ',m['verified_details']).strip()
            extracted=re.sub(r'\\s+',' ',text).strip()
            if details not in extracted:
                raise ValueError('Missing or truncated Key Verified Details paragraph for matter '+str(i))
            for key in ('scripture_reference','scripture_text'):
                if norm(m[key]) not in norm(text):raise ValueError('Missing or clipped '+key+' in '+str(i))
        else:
            for s in m['sources']:
                if not any(link.get('uri')==s['url'] for page in pdf for link in page.get_links()):raise ValueError('Missing clickable '+s['url'])
    for forbidden in BANNED:
        if forbidden in text.lower():raise ValueError('Forbidden phrase '+forbidden)
    if kind=='public_source_sheet' and ('PRAYER FOCUS' in text.upper() or 'SCRIPTURE' in text.upper()):raise ValueError('Prayer/Scripture leaked into source sheet')
    return {'pages':len(pdf),'hyperlinks':sum(len(page.get_links()) for page in pdf),'passed':True}
def main():
    a=argparse.ArgumentParser()
    a.add_argument('data');a.add_argument('--out',required=True)
    a.add_argument('--kind',choices=['recording_brief','public_source_sheet'],required=True)
    a.add_argument('--qa',action='store_true')
    args=a.parse_args()
    data=json.loads(Path(args.data).read_text(encoding='utf-8'))
    validate(data,args.kind)
    out=Path(args.out)
    if 'weekly-documents' in out.parts or 'weekly-graphics' in out.parts:raise ValueError('Never write directly into published folders')
    out.parent.mkdir(parents=True,exist_ok=True)
    (brief if args.kind=='recording_brief' else source_sheet)(data,str(out))
    if args.qa:print(json.dumps(qa_pdf(str(out),data,args.kind)))
    print('DRAFT PDF created:',out)
if __name__=='__main__':main()
