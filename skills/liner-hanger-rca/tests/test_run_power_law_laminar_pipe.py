"""Source-typed offline power-law pipe entrypoint and fail-closed schema."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_power_law_laminar_pipe import run_payload
from circulating_hydraulics import HydraulicsUnavailable

EXAMPLE=ROOT/"examples"/"synthetic_power_law_laminar_pipe.json"


def test_example_is_non_field_auditable_result():
    r=run_payload(json.loads(EXAMPLE.read_text()))
    assert r["pressure_loss_pa"]>0
    assert r["model"]=="assumed_laminar_metzner_reed_power_law_pipe"
    assert r["engineering_acceptance"] is False
    assert r["standpipe_pressure_pa"] is None
    assert "SYNTHETIC" in r["regime_evidence_id"]


@pytest.mark.parametrize("name",[
    "fluid","segment","flow_m3_s",
    "laminar_regime_independently_confirmed","regime_evidence_id"])
def test_missing_top_level_input_fails(name):
    d=json.loads(EXAMPLE.read_text())
    del d[name]
    with pytest.raises(HydraulicsUnavailable):
        run_payload(d)


def test_extra_unrecognised_input_fails():
    d=json.loads(EXAMPLE.read_text())
    d["segment"]["assumed_tool_rating_psi"]=5000
    with pytest.raises(HydraulicsUnavailable):
        run_payload(d)


def test_annular_payload_rejected():
    d=json.loads(EXAMPLE.read_text())
    d["segment"]["kind"]="concentric_annulus"
    d["segment"]["inner_diameter_m"]=.05
    with pytest.raises(HydraulicsUnavailable,match="annular"):
        run_payload(d)


def test_cli_success_and_invalid_exit(tmp_path):
    runner=ROOT/"scripts"/"run_power_law_laminar_pipe.py"
    ok=subprocess.run([sys.executable,str(runner),str(EXAMPLE)],capture_output=True,text=True)
    assert ok.returncode==0,ok.stderr
    assert json.loads(ok.stdout)["standpipe_pressure_pa"] is None
    invalid=tmp_path/"bad.json"
    invalid.write_text("{}")
    fail=subprocess.run([sys.executable,str(runner),str(invalid)],
                        capture_output=True,text=True)
    assert fail.returncode==2
    assert "unavailable" in fail.stderr
