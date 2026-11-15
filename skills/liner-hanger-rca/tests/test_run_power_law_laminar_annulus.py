"""Offline research power-law annulus schema / CLI tests."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_power_law_laminar_annulus import run_payload
from circulating_hydraulics import HydraulicsUnavailable
EXAMPLE=ROOT/"examples"/"synthetic_power_law_laminar_annulus.json"


def test_synthetic_annulus_runs_without_claiming_field_spp():
    r=run_payload(json.loads(EXAMPLE.read_text()))
    assert r["pressure_loss_pa"]>0
    assert r["geometry"]=="concentric_annulus"
    assert r["standpipe_pressure_pa"] is None
    assert r["engineering_acceptance"] is False
    assert r["flow_regime_evidence"]=="caller_declared_not_authenticated"


@pytest.mark.parametrize("name",[
    "fluid","segment","flow_m3_s",
    "laminar_regime_independently_confirmed","regime_evidence_id"])
def test_missing_field_fails_closed(name):
    d=json.loads(EXAMPLE.read_text())
    del d[name]
    with pytest.raises(HydraulicsUnavailable):
        run_payload(d)


def test_extra_unsupported_oem_field_rejected():
    d=json.loads(EXAMPLE.read_text())
    d["segment"]["approved_setting_psi"]=4000
    with pytest.raises(HydraulicsUnavailable):
        run_payload(d)


def test_pipe_not_silently_treated_as_annulus():
    d=json.loads(EXAMPLE.read_text())
    d["segment"]["kind"]="pipe"
    d["segment"]["inner_diameter_m"]=0
    with pytest.raises(HydraulicsUnavailable,match="concentric_annulus"):
        run_payload(d)


def test_cli_returns_json_and_rejects_invalid(tmp_path):
    runner=ROOT/"scripts"/"run_power_law_laminar_annulus.py"
    ok=subprocess.run([sys.executable,str(runner),str(EXAMPLE)],capture_output=True,text=True)
    assert ok.returncode==0,ok.stderr
    assert json.loads(ok.stdout)["standpipe_pressure_pa"] is None
    bad=tmp_path/"bad.json"
    bad.write_text("{}")
    no=subprocess.run([sys.executable,str(runner),str(bad)],capture_output=True,text=True)
    assert no.returncode==2
    assert "unavailable" in no.stderr
