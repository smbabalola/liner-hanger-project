"""Experimental 3D profile: split invariance and failure boundaries."""
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_torque_drag_spatial_profile import run_payload
from run_torque_drag_3d import run_payload as single
from torque_drag_straight import TorqueDragError

FIX=ROOT/"examples"/"synthetic_torque_drag_spatial_profile.json"
SINGLE=ROOT/"examples"/"synthetic_torque_drag_3d.json"


def data():
    return json.loads(FIX.read_text(encoding="utf-8"))


def calculate():
    return run_payload(data())


def test_two_3d_sections_reproduce_unsplit_uniform_turn():
    r=calculate()
    full=single(json.loads(SINGLE.read_text(encoding="utf-8")))
    assert len(r["sections_top_to_bottom"])==2
    for mode in ("pickup","slackoff","rotation"):
        assert float(r["top_tensions_n"][mode])==pytest.approx(
            float(full["results"][mode]["top_tension_n"]),rel=1e-9)
    assert float(r["total_rotation_contact_torque_nm"])==pytest.approx(
        float(full["results"]["rotation"]["contact_torque_nm"]),rel=1e-9)


def test_each_3d_tensile_state_connects_at_section_interface():
    upper,lower=calculate()["sections_top_to_bottom"]
    for mode in ("pickup","slackoff","rotation"):
        assert upper["modes"][mode]["bottom_tension_n"] == lower["modes"][mode]["top_tension_n"]


def test_spatial_profile_torque_is_sum_of_interval_torques():
    r=calculate()
    upper,lower=r["sections_top_to_bottom"]
    assert float(r["total_rotation_contact_torque_nm"])==pytest.approx(
        float(upper["incremental_rotation_contact_torque_nm"])
        +float(lower["incremental_rotation_contact_torque_nm"]),rel=1e-12)


def test_weightless_horizontal_3d_split_matches_analytic_capstan():
    p=data()
    for row in p["intervals_top_to_bottom"]:
        row["planned_section"]["dry_linear_mass"]["value"] = (
            1000*math.pi*(.1**2-.08**2)/4)
    r=run_payload(p)
    theta=math.pi/3
    assert float(r["top_tensions_n"]["pickup"])==pytest.approx(
        20000*math.exp(.2*theta),rel=2e-9)
    assert float(r["top_tensions_n"]["slackoff"])==pytest.approx(
        20000*math.exp(-.2*theta),rel=2e-9)


def test_an_unreviewed_derived_interface_cannot_be_approved():
    p=calculate()
    assert p["status"]=="unreviewed_inputs"
    assert p["bottom_tension_source"]["source_id"]
    assert "NOT field-calibrated" in p["warning"]


@pytest.mark.parametrize("change,pattern",[
    ({"top_md":49}, "MD gap"),
    ({"top_md":51}, "MD gap"),
    ({"first_station_tvd":30}, "TVD discontinuity"),
    ({"survey_revision":"incompatible"},"revision mismatch"),
    ({"first_inclination":89},"boundary inclination"),
    ({"first_azimuth":31},"boundary inclination/azimuth"),
])
def test_bad_second_section_boundary_rejected(change,pattern):
    p=data()
    sec=p["intervals_top_to_bottom"][1]["planned_section"]
    if "top_md" in change:
        sec["top_md"]["value"]=change["top_md"]
        sec["survey_stations"][0]["measured_depth"]=change["top_md"]
    if "first_station_tvd" in change:
        sec["first_station_tvd"]["value"]=change["first_station_tvd"]
    if "survey_revision" in change:
        sec["survey_revision"]=change["survey_revision"]
    if "first_inclination" in change:
        sec["survey_stations"][0]["inclination_deg"]=change["first_inclination"]
    if "first_azimuth" in change:
        sec["survey_stations"][0]["azimuth_deg"]=change["first_azimuth"]
    with pytest.raises(TorqueDragError,match=pattern):
        run_payload(p)


def test_duplicate_section_id_rejected():
    p=data()
    p["intervals_top_to_bottom"][1]["planned_section"]["section_id"]=(
        p["intervals_top_to_bottom"][0]["planned_section"]["section_id"])
    with pytest.raises(TorqueDragError,match="duplicate"):
        run_payload(p)


def test_unsupported_long_azimuth_turn_rejected():
    p=data()
    p["intervals_top_to_bottom"][1]["planned_section"]["survey_stations"][1]["azimuth_deg"]=180
    with pytest.raises(TorqueDragError,match="azimuth"):
        run_payload(p)


def test_cli_prints_json_and_output_file(tmp_path):
    runner=ROOT/"scripts"/"run_torque_drag_spatial_profile.py"
    path=tmp_path/"output.json"
    p=subprocess.run([sys.executable,str(runner),str(FIX),"--output",str(path)],
                     capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert json.loads(path.read_text())["model"]=="experimental-contiguous-3d-soft-string-v0.1"


@pytest.mark.parametrize("change",[
    {"intervals_top_to_bottom":[]},
    {"intervals_top_to_bottom":None},
    {"bottom_tension":None},
    {"unexpected":42},
])
def test_root_schema_rejected(change):
    p=data(); p.update(change)
    with pytest.raises(TorqueDragError):
        run_payload(p)


def test_incomplete_source_metadata_rejected():
    p=data()
    p["intervals_top_to_bottom"][0]["axial_friction"]={"value":"0.2","unit":"1"}
    with pytest.raises(TorqueDragError):
        run_payload(p)


def test_bad_json_file_exits_nonzero(tmp_path):
    filename=tmp_path/"bad.json"
    filename.write_text("{broken",encoding="utf-8")
    p=subprocess.run([sys.executable,
        str(ROOT/"scripts"/"run_torque_drag_spatial_profile.py"),
        str(filename)],capture_output=True,text=True)
    assert p.returncode==2
    assert "unavailable" in p.stderr
