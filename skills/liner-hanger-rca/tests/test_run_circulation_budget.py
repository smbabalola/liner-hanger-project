"""Offline bounded Newtonian hydraulic circuit JSON validation."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_circulation_budget import run_payload
from circulating_hydraulics import HydraulicsUnavailable
EXAMPLE=ROOT/"examples"/"synthetic_newtonian_component_budget.json"


def test_valid_fictional_json_budget_reports_only_partial_friction():
    result=run_payload(json.loads(EXAMPLE.read_text()))
    assert result["status"]=="partial_circuit_component_budget_only"
    assert len(result["components_in_flow_order"])==3
    assert result["modeled_component_pressure_losses_pa"]>0
    assert result["standpipe_pressure_pa"] is None
    assert not result["engineering_acceptance"]


@pytest.mark.parametrize("drop",["fluid","flow_m3_s","components_in_flow_order"])
def test_missing_top_level_fields_rejected(drop):
    case=json.loads(EXAMPLE.read_text())
    case.pop(drop)
    with pytest.raises(HydraulicsUnavailable):
        run_payload(case)


def test_unexpected_unsupported_component_fields_rejected():
    case=json.loads(EXAMPLE.read_text())
    case["components_in_flow_order"][1]["made_up_rating_psi"]=5000
    with pytest.raises(HydraulicsUnavailable):
        run_payload(case)


def test_unsupported_turbulent_return_fails_without_partial_result():
    case=json.loads(EXAMPLE.read_text())
    case["flow_m3_s"]=1
    with pytest.raises(HydraulicsUnavailable,match="transition/turbulent"):
        run_payload(case)


def test_cli_json_and_rejection_exit_code(tmp_path):
    script=ROOT/"scripts"/"run_circulation_budget.py"
    ok=subprocess.run([sys.executable,str(script),str(EXAMPLE)],
        capture_output=True,text=True)
    assert ok.returncode==0,ok.stderr
    assert json.loads(ok.stdout)["standpipe_pressure_pa"] is None
    bad=tmp_path/"missing.json"
    bad.write_text("{}")
    fail=subprocess.run([sys.executable,str(script),str(bad)],
        capture_output=True,text=True)
    assert fail.returncode==2
    assert "unavailable" in fail.stderr
