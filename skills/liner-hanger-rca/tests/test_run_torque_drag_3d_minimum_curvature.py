"""Portable JSON CLI and strict sourced-input checks for MC soft-string."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_torque_drag_3d_minimum_curvature import run_payload
from torque_drag_straight import TorqueDragError

FIX=ROOT/"examples"/"synthetic_torque_drag_3d.json"


def payload():
    d=json.loads(FIX.read_text(encoding="utf-8"))
    d["planned_section"]["survey_stations"][0]["inclination_deg"]=30
    d["planned_section"]["survey_stations"][1]["inclination_deg"]=60
    return d


def test_combined_build_turn_returns_sourced_mc_diagnostics():
    d=payload()
    r=run_payload(d)
    assert "minimum-curvature" in r["model"]
    assert abs(float(r["minimum_curvature_delta_tvd_m"])-
               float(r["survey_delta_tvd_m"]))<1e-8
    assert r["results"]["rotation"]["contact_torque_nm"]
    assert r["status"]=="unreviewed_inputs"


def test_offline_cli_file(tmp_path):
    source=tmp_path/"input.json"
    dest=tmp_path/"output.json"
    source.write_text(json.dumps(payload()),encoding="utf-8")
    p=subprocess.run([sys.executable,
                      str(ROOT/"scripts"/"run_torque_drag_3d_minimum_curvature.py"),
                      str(source),"--output",str(dest)],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert json.loads(dest.read_text(encoding="utf-8"))["model"].startswith("experimental-3d")


@pytest.mark.parametrize("field",[
    "unexpected","axial_friction","bottom_tension","planned_section",
])
def test_invalid_root_or_source_rejected(field):
    d=payload()
    if field=="unexpected":
        d[field]=True
    elif field=="planned_section":
        d[field]=None
    else:
        d[field]={"value":1,"unit":"1"}
    with pytest.raises(TorqueDragError):
        run_payload(d)


def test_cli_invalid_json_fails_nonzero(tmp_path):
    source=tmp_path/"invalid.json"
    source.write_text("{invalid",encoding="utf-8")
    p=subprocess.run([sys.executable,
                      str(ROOT/"scripts"/"run_torque_drag_3d_minimum_curvature.py"),
                      str(source)],capture_output=True,text=True)
    assert p.returncode==2
    assert "unavailable" in p.stderr
