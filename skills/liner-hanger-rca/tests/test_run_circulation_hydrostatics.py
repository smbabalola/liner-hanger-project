"""Portable hydrostatic CLI and strict source identity constraints."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_circulation_hydrostatics import run_payload
from circulating_hydraulics import HydraulicsUnavailable
EXAMPLE=ROOT/"examples"/"synthetic_hydrostatic_column_balance.json"


def test_example_returns_only_static_balance_with_source_register():
    r=run_payload(json.loads(EXAMPLE.read_text()))
    assert r["status"]=="static_hydrostatic_contribution_only"
    assert len(r["layers"])==4
    assert r["datum"]=="FICTIONAL-TVD"
    assert r["standpipe_pressure_pa"] is None
    assert r["engineering_acceptance"] is False


@pytest.mark.parametrize("missing",["layers"])
def test_missing_required_schema_rejected(missing):
    d=json.loads(EXAMPLE.read_text())
    d.pop(missing)
    with pytest.raises(HydraulicsUnavailable):
        run_payload(d)


def test_unknown_pressure_field_rejected():
    d=json.loads(EXAMPLE.read_text())
    d["layers"][0]["measured_rig_spp_psi"]=5000
    with pytest.raises(HydraulicsUnavailable):
        run_payload(d)


def test_unmatched_datums_rejected():
    d=json.loads(EXAMPLE.read_text())
    d["layers"][-1]["datum"]="OTHER-DATUM"
    with pytest.raises(HydraulicsUnavailable,match="datums"):
        run_payload(d)


def test_cli_success_and_invalid_exit(tmp_path):
    runner=ROOT/"scripts"/"run_circulation_hydrostatics.py"
    ok=subprocess.run([sys.executable,str(runner),str(EXAMPLE)],
        capture_output=True,text=True)
    assert ok.returncode==0,ok.stderr
    assert json.loads(ok.stdout)["standpipe_pressure_pa"] is None
    bad=tmp_path/"invalid.json"
    bad.write_text("{}")
    no=subprocess.run([sys.executable,str(runner),str(bad)],
        capture_output=True,text=True)
    assert no.returncode==2
    assert "unavailable" in no.stderr
