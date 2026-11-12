#!/usr/bin/env python3
"""Normalize time order of one rig-log CSV and join annotations at exact timestamps.
No interpolation, drilling interpretation, anomaly detection or RCA is performed.
Usage: python build_timeline.py rig.csv timeline.csv [events.csv]
The input timestamp column must be offset-aware ISO 8601. Other columns are preserved.
Optional events CSV must have timestamp and event_text columns.
"""
import csv
import sys
from datetime import datetime
from pathlib import Path


def dt(raw):
    value=datetime.fromisoformat(raw.strip().replace('Z','+00:00'))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('timestamp lacks timezone offset: '+str(raw))
    return value


def load(file):
    with Path(file).open(newline='', encoding='utf-8-sig') as fh:
        reader=csv.DictReader(fh)
        if not reader.fieldnames or 'timestamp' not in reader.fieldnames:
            raise ValueError(f'{file}: timestamp column required')
        return list(reader.fieldnames), list(reader)


def main(rig_path, output_path, events_path=None):
    fields, rows=load(rig_path)
    if not rows: raise ValueError('empty rig log')
    events={}
    if events_path:
        efields, erows=load(events_path)
        if 'event_text' not in efields: raise ValueError('events CSV needs event_text column')
        for event in erows:
            t=dt(event['timestamp']).isoformat()
            events.setdefault(t, []).append(event['event_text'])
    for row in rows:
        row['_normalized_time']=dt(row['timestamp']).isoformat()
    rows.sort(key=lambda x:dt(x['timestamp']))
    if any(dt(a['timestamp'])==dt(b['timestamp']) for a,b in zip(rows,rows[1:])):
        raise ValueError('duplicate rig time samples; review before alignment')
    for row in rows:
        row['event_annotations']=' | '.join(events.pop(row['_normalized_time'], []))
        del row['_normalized_time']
    if events:
        print(f'WARNING: {sum(map(len,events.values()))} event annotations did not match any telemetry timestamp', file=sys.stderr)
    with Path(output_path).open('w',newline='',encoding='utf-8') as fh:
        wr=csv.DictWriter(fh, fieldnames=fields+['event_annotations'])
        wr.writeheader();wr.writerows(rows)
    return len(rows)

if __name__=='__main__':
    if len(sys.argv) not in (3,4):
        raise SystemExit('Usage: build_timeline.py rig.csv timeline.csv [events.csv]')
    print(f'Wrote {main(*sys.argv[1:])} synchronized-order records')
