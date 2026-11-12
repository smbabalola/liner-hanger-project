import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_procedure import evaluate,parse_time

def samples():
    return [{'t':f'2021-01-01T00:{i:02d}:00','_time':parse_time(f'2021-01-01T00:{i:02d}:00'), 'rpm':r} for i,r in [(0,10),(5,15),(10,48),(15,49),(20,12),(25,8)]]

def rulebook():
    return {'job_id':'SYNTHETIC TEST ONLY','procedure':{'approved':True,'revision':'TEST','approval_reference':'NOT A FIELD APPROVAL'},
            'telemetry_clock_alignment_verified':True,'rules':[
             {'id':'T1','approved':True,'step':'Test','source_reference':'SYNTHETIC TEST', 'channel':'rpm', 'operator':'<=','value':30,'unit':'rpm','window':{'start':'2021-01-01T00:00:00','end':'2021-01-01T00:30:00'}}]}

def test_flags_two_consecutive_samples_as_one_instance():
    out=evaluate(rulebook(),samples());r=out['results'][0]
    assert r['status']=='deviation' and len(r['instances'])==1
    assert r['instances'][0]['observed_max']==49

def test_no_approved_procedure_means_no_violation_claim():
    b=rulebook();b['procedure']['approved']=False
    r=evaluate(b,samples())['results'][0]
    assert r['status']=='unverifiable' and not r['instances']

def test_no_clock_match_prevents_false_claim():
    b=rulebook();b['telemetry_clock_alignment_verified']=False
    assert evaluate(b,samples())['deviation_count']==0

def test_no_unit_prevents_false_claim():
    b=rulebook();b['rules'][0]['unit']='psi'
    assert evaluate(b,samples())['results'][0]['status']=='unverifiable'

def test_pass_compliant():
    b=rulebook();b['rules'][0]['value']=60
    assert evaluate(b,samples())['results'][0]['status']=='met'

def test_missing_coverage():
    b=rulebook();a=samples();a[2]['rpm']=''
    b['rules'][0]['min_coverage']=0.9
    assert evaluate(b,a)['results'][0]['status']=='unverifiable'
