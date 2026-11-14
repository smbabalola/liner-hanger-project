"""Portable research weighted-planar-arc JSON runner tests, fictional only."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_torque_drag_weighted_curve import run_payload
from torque_drag_straight import TorqueDragError

EXAMPLE = ROOT / "examples" / "synthetic_torque_drag_weighted_curve.json"


def payload():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_example_has_finite_positive_separate_modes():
    result = run_payload(payload())
    assert result["status"] == "unreviewed_inputs"
    assert result["integration_steps"] == 256
    assert result["model"] == "planar-weighted-soft-string-rk4-v0.1"
    tensions = [float(result["results"][mode]["top_tension_n"])
                for mode in ("pickup", "slackoff", "rotation")]
    assert tensions[0] >= tensions[2] >= tensions[1] > 0


def test_cli_produces_json_and_research_warning():
    run = subprocess.run([sys.executable,
        str(ROOT / "scripts" / "run_torque_drag_weighted_curve.py"),
        str(EXAMPLE)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    out = json.loads(run.stdout)
    assert "not field-validated" in out["warning"]


def test_cli_can_write_output_file(tmp_path):
    target = tmp_path / "prediction.json"
    run = subprocess.run([sys.executable,
        str(ROOT / "scripts" / "run_torque_drag_weighted_curve.py"),
        str(EXAMPLE), "--output", str(target)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(target.read_text())["integration_steps"] == 256


@pytest.mark.parametrize("change", [
    {"planned_section": {}},
    {"bottom_tension": None},
    {"rotational_friction": {"unit": "1", "value": "0.3"}},
    {"integration_steps": 0},
    {"integration_steps": True},
    {"extra": "unexpected"},
])
def test_invalid_payload_rejected(change):
    record = payload()
    record.update(change)
    with pytest.raises(TorqueDragError):
        run_payload(record)


def test_invalid_file_returns_nonzero(tmp_path):
    filename = tmp_path / "bad.json"
    filename.write_text("{bad", encoding="utf-8")
    p = subprocess.run([sys.executable,
        str(ROOT / "scripts" / "run_torque_drag_weighted_curve.py"),
        str(filename)], capture_output=True, text=True)
    assert p.returncode == 2
    assert "unavailable" in p.stderr
