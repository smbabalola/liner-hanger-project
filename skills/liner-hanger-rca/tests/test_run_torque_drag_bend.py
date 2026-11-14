"""Portable fictional capstan bend JSON and CLI tests."""
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_torque_drag_bend import run_payload
from torque_drag_straight import TorqueDragError

FIXTURE = ROOT / "examples" / "synthetic_torque_drag_bend.json"


def fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_exact_weightless_bend_reference():
    out = run_payload(fixture())
    assert out["status"] == "unreviewed_inputs"
    assert float(out["results"]["top_pickup_tension_n"]) == pytest.approx(
        10000 * math.exp(.2 * math.pi / 2), rel=1e-12)
    assert float(out["results"]["top_slackoff_tension_n"]) == pytest.approx(
        10000 * math.exp(-.2 * math.pi / 2), rel=1e-12)
    assert float(out["results"]["pure_rotation_contact_torque_nm"]) == pytest.approx(
        .3 * 10000 * math.pi / 2 * .05, rel=1e-12)


def test_cli_outputs_machine_readable_warning():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag_bend.py"),
                           str(FIXTURE)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "weightless" in json.loads(proc.stdout)["warning"]


def test_cli_output_file(tmp_path):
    output = tmp_path / "capstan-report.json"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag_bend.py"),
                           str(FIXTURE), "--output", str(output)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert json.loads(output.read_text())["model"] == "ideal-weightless-capstan-dogleg-v0.1"


@pytest.mark.parametrize("change", [
    {"bend_angle": None},
    {"zero_distributed_weight": False},
    {"extra_field": "unexpected"},
    {"bottom_tension": {"value": 10000, "unit": "N"}},
])
def test_cli_rejects_invalid_source_schema(change):
    p = fixture()
    p.update(change)
    with pytest.raises(TorqueDragError):
        run_payload(p)


def test_cli_rejects_invalid_json_file(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{invalid", encoding="utf-8")
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag_bend.py"),
                           str(path)], capture_output=True, text=True)
    assert proc.returncode == 2
    assert "unavailable" in proc.stderr
