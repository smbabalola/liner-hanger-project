#!/usr/bin/env python3
"""Retrospective, auditable procedure comparison against sampled rig telemetry.

Important: only approved job-specific rules with VERIFIED source units and time
alignment may yield a 'deviation'. Otherwise the checker returns 'unverifiable'.
This is NOT an equipment-control, well-control, or diagnosis system.
"""
import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

ALLOWED = {'<', '<=', '>', '>=', 'between'}
UNIT_CHANNELS = {'rpm': 'rpm', 'torque': 'ft-lbs'}  # known from this uploaded file's headers
CHANNELS = {'hookload','pressure','flow','spm','rpm','torque','block','slips',
            'pressure_peak','rpm_peak','torque_peak'}
FMT = '%Y-%m-%dT%H:%M:%S'

def parse_time(s):
    try: return datetime.fromisoformat(s)
    except (ValueError, TypeError): return None

def valid_number(x):
    try: return math.isfinite(float(x))
    except (TypeError, ValueError): return False

def compare(x, rule):
    op = rule['operator']
    v = float(rule['value'])
    if op == '<': return x < v
    if op == '<=': return x <= v
    if op == '>': return x > v
    if op == '>=': return x >= v
    if op == 'between': return v <= x <= float(rule['upper'])
    raise ValueError('unsupported operator')

def load_samples(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        out = list(csv.DictReader(f))
    for a in out: a['_time'] = parse_time(a.get('t'))
    return out

def evaluate(rulebook, rows):
    proc = rulebook.get('procedure', {})
    channel_units = rulebook.get('channel_units', {})
    aligned = rulebook.get('telemetry_clock_alignment_verified') is True
    full_approval = proc.get('approved') is True and bool(proc.get('revision')) and bool(proc.get('approval_reference'))
    results=[]
    for r in rulebook.get('rules', []):
        item = {'id':r.get('id','?'), 'step':r.get('step','Unspecified'), 'description':r.get('description',''),
                'source_reference':r.get('source_reference',''), 'channel':r.get('channel',''),
                'status':'unverifiable', 'instances':[], 'reasons':[]}
        errs=item['reasons']; ch=r.get('channel')
        if not full_approval: errs.append('An approved job-specific procedure, revision and approval reference are required')
        if r.get('approved') is not True: errs.append('Rule has not been approved by a competent engineer')
        if not r.get('source_reference'): errs.append('Rule lacks a procedure page/section reference')
        if not aligned: errs.append('Procedure-event and telemetry clock alignment is not verified')
        if ch not in CHANNELS: errs.append('Channel is missing or unsupported')
        if r.get('operator') not in ALLOWED or not valid_number(r.get('value')) or (r.get('operator')=='between' and not valid_number(r.get('upper'))):
            errs.append('Invalid comparator or numeric value')
        expected_unit=channel_units.get(ch) or UNIT_CHANNELS.get(ch)
        if not expected_unit or not r.get('unit') or r.get('unit') != expected_unit:
            errs.append(f'Engineering units not verified (telemetry: {expected_unit or "unknown"}; rule: {r.get("unit") or "unknown"})')
        w=r.get('window') or {}; a=parse_time(w.get('start')); b=parse_time(w.get('end'))
        if not a or not b or b<=a: errs.append('Need a valid verified start/end event window')
        if errs: results.append(item); continue
        inwindow=[row for row in rows if row['_time'] is not None and a<=row['_time']<b]
        observed=[row for row in inwindow if valid_number(row.get(ch))]
        coverage=len(observed)/len(inwindow) if inwindow else 0
        item['data_coverage']=round(coverage,3)
        if not inwindow or coverage < float(r.get('min_coverage',0.8)):
            errs.append(f'Insufficient valid signal data in approved time window ({len(observed)}/{len(inwindow)} points)')
            results.append(item);continue
        failing=[row for row in observed if not compare(float(row[ch]),r)]
        if not failing:
            item['status']='met'; item['observed_range']=[min(float(x[ch]) for x in observed),max(float(x[ch]) for x in observed)]
            results.append(item);continue
        # Group failures in contiguous observed sequence, accounting for real timestamp gaps.
        timed=sorted(observed,key=lambda x:x['_time'])
        intervals=[];group=[];step_minutes=float(r.get('max_gap_minutes',5.2))
        for row in timed:
            failed=not compare(float(row[ch]),r)
            if not failed:
                if group: intervals.append(group);group=[]
                continue
            if group and (row['_time']-group[-1]['_time']).total_seconds()/60 > step_minutes:
                intervals.append(group);group=[]
            group.append(row)
        if group: intervals.append(group)
        duration=float(r.get('min_duration_minutes',0))
        for group in intervals:
            start,end=group[0]['_time'],group[-1]['_time']
            count_minutes=(end-start).total_seconds()/60 + float(r.get('sample_interval_minutes',5))
            if count_minutes < duration:continue
            item['instances'].append({'start':start.isoformat(timespec='minutes'),
                                      'last_failed_sample':end.isoformat(timespec='minutes'),
                                      'n_points':len(group), 'approx_duration_minutes':round(count_minutes,2),
                                      'observed_min':min(float(x[ch]) for x in group),
                                      'observed_max':max(float(x[ch]) for x in group)})
        item['status']='deviation' if item['instances'] else 'met'
        results.append(item)
    return {'job_id':rulebook.get('job_id',''), 'rules_evaluated':len(results),
            'deviation_count':sum(len(r['instances']) for r in results if r['status']=='deviation'),
            'not_verifiable_rules':sum(r['status']=='unverifiable' for r in results),
            'results':results, 'notice':'Retrospective checks only. Engineers must review source authenticity, sensor integrity and each apparent deviation.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rules',required=True);ap.add_argument('--telemetry',required=True);ap.add_argument('--output')
    args=ap.parse_args();result=evaluate(json.loads(Path(args.rules).read_text(encoding='utf-8')),load_samples(args.telemetry))
    out=json.dumps(result,indent=2)
    if args.output:Path(args.output).write_text(out,encoding='utf-8')
    else: print(out)
if __name__=='__main__':main()
