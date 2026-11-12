#!/usr/bin/env python3
"""Extract page-referenced review candidates from a procedure PDF.

This only collects text; it NEVER creates an approved operating rule. A human
must identify the exact OEM/tool/job revision, verify tables and approve values.
"""
import argparse
import json
import re
from pathlib import Path

RE = re.compile(r'\b(?:hanger|running tool|release|set(?:ting)?|shear|pressure|circulat(?:e|ion)|ball|plug|pick[ -]?up|slack[ -]?off|hookload|weight|rpm|torque|pump|rate|volume|stroke|hold|test)\b',re.I)

def extract(path):
    try:import pymupdf
    except ImportError:
        try:import fitz as pymupdf
        except ImportError:raise SystemExit('pymupdf is required: pip install pymupdf')
    doc=pymupdf.open(path)
    result=[];gaps=[]
    for page_no,page in enumerate(doc,1):
        lines=[re.sub(r'\s+',' ',s.strip()) for s in page.get_text(sort=True).splitlines()]
        lines=[s for s in lines if s]
        if not lines:
            gaps.append({'page':page_no,'reason':'No extractable text — scanned page or figure; inspect manually'})
            continue
        for j,line in enumerate(lines):
            if not RE.search(line):continue
            result.append({'page':page_no,'line_index':j+1,'source_text':line[:1200],
                           'review_status':'candidate_only','approved':False,
                           'comment':'Review against original PDF, figures/tables, exact tool and revision'})
    return {'source_pdf':Path(path).name,'pages':len(doc),'candidates':result,'data_gaps':gaps,
            'notice':'Text extraction is not rule approval. Verify tables/diagrams and engineer-sign off before comparing telemetry.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('pdf');ap.add_argument('--output');args=ap.parse_args()
    obj=extract(args.pdf);payload=json.dumps(obj,indent=2)
    if args.output:Path(args.output).write_text(payload,encoding='utf-8')
    else:print(payload)
if __name__=='__main__':main()
