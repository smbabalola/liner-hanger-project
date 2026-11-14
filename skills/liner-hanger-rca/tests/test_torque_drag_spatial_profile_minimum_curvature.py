"""MC profile split invariance with true great-circle midpoint, not angle midpoint."""
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_torque_drag_spatial_profile_minimum_curvature import run_payload
from run_torque_drag_3d_minimum_curvature import run_payload as single
from torque_drag_straight import TorqueDragError

PROFILE=ROOT/"examples"/"synthetic_torque_drag_spatial_profile.json"
SEGMENT=ROOT/"examples"/"synthetic_torque_drag_3d.json"


def _tangent(i,a):
    i,a=math.radians(i),math.radians(a)
    return (math.sin(i)*math.cos(a),math.sin(i)*math.sin(a),math.cos(i))


def _middle():
    a,b=_tangent(30,0),_tangent(60,60)
    t=tuple((x+y)/math.sqrt(sum((p+q)**2 for p,q in zip(a,b)))
            for x,y in zip(a,b))
    inc=math.degrees(math.atan2(math.hypot(t[0],t[1]),t[2]))
    az=(math.degrees(math.atan2(t[1],t[0]))+360)%360
    return inc,az


def inputs():
    p=json.loads(PROFILE.read_text(encoding="utf-8"))
    first,second=p["intervals_top_to_bottom"]
    im,am=_middle()
    survey1=first["planned_section"]["survey_stations"]
    survey2=second["planned_section"]["survey_stations"]
    survey1[0]["inclination_deg"],survey1[0]["azimuth_deg"]=30,0
    survey1[1]["inclination_deg"],survey1[1]["azimuth_deg"]=im,am
    survey2[0]["inclination_deg"],survey2[0]["azimuth_deg"]=im,am
    survey2[1]["inclination_deg"],survey2[1]["azimuth_deg"]=60,60
    t0,t1=_tangent(30,0),_tangent(im,am)
    beta=math.acos(sum(x*y for x,y in zip(t0,t1)))
    rf=2*math.tan(beta/2)/beta
    second["planned_section"]["first_station_tvd"]["value"]=(
        50*(t0[2]+t1[2])/2*rf)
    d=json.loads(SEGMENT.read_text(encoding="utf-8"))
    d["planned_section"]["survey_stations"][0]["inclination_deg"]=30
    d["planned_section"]["survey_stations"][0]["azimuth_deg"]=0
    d["planned_section"]["survey_stations"][1]["inclination_deg"]=60
    d["planned_section"]["survey_stations"][1]["azimuth_deg"]=60
    return p,d


def test_true_mc_midpoint_split_reproduces_nonzero_weight_full_section():
    p,d=inputs()
    combined=run_payload(p)
    unsplit=single(d)
    assert combined["status"]=="unreviewed_inputs"
    for mode in ("pickup","slackoff","rotation"):
        assert float(combined["top_tensions_n"][mode])==pytest.approx(
            float(unsplit["results"][mode]["top_tension_n"]),rel=2e-9)
    assert float(combined["total_rotation_contact_torque_nm"])==pytest.approx(
        float(unsplit["results"]["rotation"]["contact_torque_nm"]),rel=2e-9)


def test_weightless_true_mc_split_has_exact_dogleg_capstan():
    p,d=inputs()
    for section in p["intervals_top_to_bottom"]:
        section["planned_section"]["dry_linear_mass"]["value"]=(
            1000*math.pi*(0.1**2-0.08**2)/4)
    a,b=_tangent(30,0),_tangent(60,60)
    beta=math.acos(sum(x*y for x,y in zip(a,b)))
    out=run_payload(p)
    assert float(out["top_tensions_n"]["pickup"])==pytest.approx(
        20000*math.exp(.2*beta),rel=1e-9)
    assert float(out["top_tensions_n"]["slackoff"])==pytest.approx(
        20000*math.exp(-.2*beta),rel=1e-9)


def test_all_mode_boundaries_remain_distinct_and_connected():
    r=run_payload(inputs()[0])
    top,bottom=r["sections_top_to_bottom"]
    for mode in ("pickup","slackoff","rotation"):
        assert top["modes"][mode]["bottom_tension_n"]==bottom["modes"][mode]["top_tension_n"]
    assert float(top["modes"]["pickup"]["bottom_tension_n"]) > float(
        top["modes"]["slackoff"]["bottom_tension_n"])
    assert float(r["total_rotation_contact_torque_nm"])==pytest.approx(
        sum(float(x["incremental_rotation_contact_torque_nm"]) for x in (top,bottom)),
        rel=1e-12)


def test_wrong_second_section_mc_tvd_rejected():
    p,_=inputs()
    p["intervals_top_to_bottom"][1]["planned_section"]["first_station_tvd"]["value"]=0
    with pytest.raises(TorqueDragError,match="TVD discontinuity"):
        run_payload(p)


def test_wrong_angle_midpoint_is_not_tangent_consistent():
    p,_=inputs()
    p["intervals_top_to_bottom"][1]["planned_section"]["survey_stations"][0]["inclination_deg"]=45
    with pytest.raises(TorqueDragError,match="boundary inclination"):
        run_payload(p)


def test_cli_generates_research_output(tmp_path):
    p,_=inputs()
    a=tmp_path/"in.json";b=tmp_path/"out.json"
    a.write_text(json.dumps(p),encoding="utf-8")
    proc=subprocess.run([
        sys.executable,
        str(ROOT/"scripts"/"run_torque_drag_spatial_profile_minimum_curvature.py"),
        str(a),"--output",str(b)
    ],capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    out=json.loads(b.read_text(encoding="utf-8"))
    assert out["model"]=="experimental-contiguous-3d-minimum-curvature-soft-string-v0.1"
    assert "no qualified field" in out["warning"]


@pytest.mark.parametrize("bad", ["intervals_top_to_bottom","bottom_tension"])
def test_invalid_schema_rejected(bad):
    p,_=inputs();p[bad]=None
    with pytest.raises(TorqueDragError):
        run_payload(p)
