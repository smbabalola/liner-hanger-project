"""Restricted power-law multi-section CLI synthetic tests."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_power_law_circulation_budget import run_payload
from circulating_hydraulics import HydraulicsUnavailable
EXAMPLE=ROOT/"examples"/"synthetic_power_law_circulation_budget.json"


def test_example_audits_both_regime_sources_and_never_reports_spp():
    result=run_payload(json.loads(EXAMPLE.read_text()))
    assert result["status"]=="partial_power_law_component_budget_only"
    assert len(result["components_in_flow_order"])==3
    assert result["components_in_flow_order"][0]["regime_evidence_id"]=="SYNTHETIC-PIPE-REGIME"
    assert result["components_in_flow_order"][2]["regime_evidence_id"]=="SYNTHETIC-ANNULUS-REGIME"
    assert result["standpipe_pressure_pa"] is None
    assert result["engineering_acceptance"] is False


@pytest.mark.parametrize("key",[
    "fluid","flow_m3_s","components_in_flow_order","laminar_evidence_by_section"])
def test_incomplete_schema_fails(key):
    data=json.loads(EXAMPLE.read_text())
    del data[key]
    with pytest.raises(HydraulicsUnavailable):
        run_payload(data)


def test_missing_annular_regime_evidence_rejected():
    data=json.loads(EXAMPLE.read_text())
    del data["laminar_evidence_by_section"]["synthetic_annulus"]
    with pytest.raises(HydraulicsUnavailable,match="exact per-section"):
        run_payload(data)


def test_unknown_oem_rating_not_permitted():
    data=json.loads(EXAMPLE.read_text())
    data["components_in_flow_order"][0]["oem_setting_pressure"]=5000
    with pytest.raises(HydraulicsUnavailable):
        run_payload(data)


def test_cli_fictional_case_and_fail_closed(tmp_path):
    runner=ROOT/"scripts"/"run_power_law_circulation_budget.py"
    ok=subprocess.run([sys.executable,str(runner),str(EXAMPLE)],
                      capture_output=True,text=True)
    assert ok.returncode==0,ok.stderr
    assert json.loads(ok.stdout)["standpipe_pressure_pa"] is None
    missing=tmp_path/"missing.json"
    missing.write_text("{}")
    no=subprocess.run([sys.executable,str(runner),str(missing)],
                      capture_output=True,text=True)
    assert no.returncode==2
    assert "unavailable" in no.stderr
