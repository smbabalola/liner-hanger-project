"""Research-only HB annulus offline strict JSON checks."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_herschel_bulkley_laminar_annulus import run_payload
from circulating_hydraulics import HydraulicsUnavailable
EXAMPLE=ROOT/"examples"/"synthetic_herschel_bulkley_annulus.json"


def test_bingham_limit_example_returns_auditable_restricted_pressure():
    row=run_payload(json.loads(EXAMPLE.read_text()))
    assert row["pressure_loss_pa"]>0
    assert row["zero_stress_radius_m"]>0
    assert row["model"]=="experimental_laminar_hb_concentric_annulus"
    assert row["standpipe_pressure_pa"] is None
    assert row["engineering_acceptance"] is False


@pytest.mark.parametrize("key",["fluid","segment","flow_m3_s","laminar_regime_independently_confirmed","regime_evidence_id"])
def test_no_required_field_may_be_missing(key):
    data=json.loads(EXAMPLE.read_text())
    data.pop(key)
    with pytest.raises(HydraulicsUnavailable):
        run_payload(data)


def test_caller_cannot_inject_unchecked_oem_pressures():
    data=json.loads(EXAMPLE.read_text())
    data["segment"]["approved_pressure_psi"]=5000
    with pytest.raises(HydraulicsUnavailable):
        run_payload(data)


def test_laminar_regime_assertion_must_be_true():
    data=json.loads(EXAMPLE.read_text())
    data["laminar_regime_independently_confirmed"]=False
    with pytest.raises(HydraulicsUnavailable,match="laminar-regime"):
        run_payload(data)


def test_cli_output_and_error_exit(tmp_path):
    script=ROOT/"scripts"/"run_herschel_bulkley_laminar_annulus.py"
    valid=subprocess.run([sys.executable,str(script),str(EXAMPLE)],capture_output=True,text=True)
    assert valid.returncode==0,valid.stderr
    assert json.loads(valid.stdout)["standpipe_pressure_pa"] is None
    bad=tmp_path/"bad.json"
    bad.write_text("{}")
    invalid=subprocess.run([sys.executable,str(script),str(bad)],capture_output=True,text=True)
    assert invalid.returncode==2
    assert "unavailable" in invalid.stderr
