"""Standalone torque/drag input/output and anchored independent known answer."""
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_torque_drag import run_payload
from torque_drag_straight import TorqueDragError

FILE = ROOT / "examples" / "synthetic_torque_drag_straight.json"


def fixture():
    return json.loads(FILE.read_text(encoding="utf-8"))


def test_reference_numerical_values_from_independent_math_force_balance():
    vals = run_payload(fixture())["results"]
    # Independently computed with Newtonian plane equilibrium and cylindrical wall displacement:
    assert float(vals["buoyed_section_weight_n"]) == pytest.approx(11937.210036330625, rel=1e-12)
    assert float(vals["low_side_normal_force_n"]) == pytest.approx(10337.927141772883, rel=1e-12)
    assert float(vals["top_pickup_tension_n"]) == pytest.approx(28036.19044651989, rel=1e-12)
    assert float(vals["top_slackoff_tension_n"]) == pytest.approx(23901.019589810734, rel=1e-12)
    assert float(vals["top_pure_rotation_tension_n"]) == pytest.approx(25968.60501816531, rel=1e-12)
    assert float(vals["off_bottom_contact_torque_nm"]) == pytest.approx(155.06890712659325, rel=1e-12)


def test_cli_runs_and_preserves_no_approval_warning():
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag.py"), str(FILE)],
                         capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result["status"] == "unreviewed_inputs"
    assert "NOT rig hookload" in result["warning"]


def test_cli_output_file(tmp_path):
    dest = tmp_path / "report.json"
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag.py"),
                          str(FILE), "--output", str(dest)],
                         capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
    assert json.loads(dest.read_text())["model"] == "straight-constant-inclination-soft-string-v0.1"


@pytest.mark.parametrize("corruption", [
    {"axial_friction": None},
    {"contact_radius": {"value": 0.05, "unit": "m"}},
    {"bogus": 42},
    {"planned_section": {}},
    {"rotational_friction": "0.3"},
])
def test_json_schema_and_missing_sources_are_rejected(corruption):
    payload = fixture()
    payload.update(corruption)
    with pytest.raises(TorqueDragError):
        run_payload(payload)


def test_malformed_file_is_nonzero(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not-json")
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag.py"), str(path)],
                         capture_output=True, text=True, check=False)
    assert run.returncode == 2
    assert "unavailable:" in run.stderr
