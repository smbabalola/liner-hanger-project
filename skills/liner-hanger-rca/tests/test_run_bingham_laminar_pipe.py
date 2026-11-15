"""Strict offline Bingham pipe runner contract; entirely synthetic input."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_bingham_laminar_pipe import run_payload
from circulating_hydraulics import HydraulicsUnavailable

EXAMPLE = ROOT / "examples" / "synthetic_bingham_laminar_pipe.json"


def test_example_pipe_produces_auditable_non_field_pressure():
    result = run_payload(json.loads(EXAMPLE.read_text()))
    assert result["pressure_loss_pa"] > 0
    assert result["standpipe_pressure_pa"] is None
    assert result["engineering_acceptance"] is False
    assert result["regime_evidence_id"].startswith("SYNTHETIC")


@pytest.mark.parametrize("name", [
    "fluid", "segment", "flow_m3_s",
    "laminar_regime_independently_confirmed", "regime_evidence_id"
])
def test_missing_required_field_fails_closed(name):
    payload=json.loads(EXAMPLE.read_text())
    del payload[name]
    with pytest.raises(HydraulicsUnavailable):
        run_payload(payload)


@pytest.mark.parametrize("evidence", ["", "  ", None, 14, "x"*257])
def test_missing_invalid_regime_source_rejected(evidence):
    payload=json.loads(EXAMPLE.read_text())
    payload["regime_evidence_id"]=evidence
    with pytest.raises(HydraulicsUnavailable):
        run_payload(payload)


def test_no_unsupported_annular_bingham_fallback():
    payload=json.loads(EXAMPLE.read_text())
    payload["segment"]["kind"]="concentric_annulus"
    payload["segment"]["inner_diameter_m"]=0.05
    with pytest.raises(HydraulicsUnavailable,match="annular"):
        run_payload(payload)


def test_cli_stdout_json_and_fail_closed_exit(tmp_path):
    script=ROOT / "scripts" / "run_bingham_laminar_pipe.py"
    result=subprocess.run(
        [sys.executable,str(script),str(EXAMPLE)],
        capture_output=True,text=True,check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["standpipe_pressure_pa"] is None
    invalid=tmp_path / "invalid.json"
    invalid.write_text("{}")
    rejected=subprocess.run(
        [sys.executable,str(script),str(invalid)],
        capture_output=True,text=True,check=False)
    assert rejected.returncode == 2
    assert "unavailable" in rejected.stderr
