"""Synthetic portable CLI, strict schema and numeric invariants."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_torque_drag_weighted_profile import run_payload
from torque_drag_straight import TorqueDragError

EXAMPLE = ROOT / "examples" / "synthetic_torque_drag_weighted_profile.json"


def raw():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_two_section_json_fixture_returns_connected_modes():
    output = run_payload(raw())
    assert output["status"] == "unreviewed_inputs"
    assert output["model"] == "contiguous-planar-weighted-soft-string-v0.1"
    assert len(output["sections_top_to_bottom"]) == 2
    assert float(output["top_tensions_n"]["pickup"]) == pytest.approx(34214.05213166, abs=0.002)
    assert float(output["top_tensions_n"]["slackoff"]) == pytest.approx(26217.8377535, abs=0.002)
    assert float(output["top_tensions_n"]["rotation"]) == pytest.approx(29871.99323562, abs=0.002)
    assert float(output["total_rotation_contact_torque_nm"]) == pytest.approx(298.2402339, abs=0.002)


def test_cli_prints_json():
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag_weighted_profile.py"),
                        str(EXAMPLE)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert "NOT rig hookload" in json.loads(p.stdout)["warning"]


def test_cli_output_file(tmp_path):
    out = tmp_path / "output.json"
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag_weighted_profile.py"),
                        str(EXAMPLE), "--output", str(out)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert json.loads(out.read_text())["model"] == "contiguous-planar-weighted-soft-string-v0.1"


@pytest.mark.parametrize("change", [
    {"intervals_top_to_bottom": []},
    {"intervals_top_to_bottom": None},
    {"bottom_tension": None},
    {"unexpected": True},
])
def test_bad_root_payload_rejected(change):
    payload = raw()
    payload.update(change)
    with pytest.raises(TorqueDragError):
        run_payload(payload)


def test_missing_source_rejected():
    payload = raw()
    payload["intervals_top_to_bottom"][0]["contact_radius"] = {"value": "0.05", "unit": "m"}
    with pytest.raises(TorqueDragError):
        run_payload(payload)


def test_malformed_interval_rejected():
    payload = raw()
    payload["intervals_top_to_bottom"][1]["extra"] = 1
    with pytest.raises(TorqueDragError):
        run_payload(payload)


def test_invalid_steps_rejected_by_solver():
    payload = raw()
    payload["intervals_top_to_bottom"][0]["integration_steps"] = 7
    with pytest.raises(TorqueDragError, match="integration_steps"):
        run_payload(payload)


def test_bad_json_file_returns_nonzero(tmp_path):
    f = tmp_path / "broken.json"
    f.write_text("{broken", encoding="utf-8")
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_torque_drag_weighted_profile.py"),
                        str(f)], capture_output=True, text=True)
    assert p.returncode == 2
    assert "unavailable" in p.stderr
