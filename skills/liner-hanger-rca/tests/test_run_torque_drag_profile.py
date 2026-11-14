"""Synthetic-only profile JSON CLI, schema and numerical regression checks."""
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_torque_drag_profile import run_payload
from torque_drag_straight import TorqueDragError

FIXTURE = ROOT / "examples" / "synthetic_torque_drag_profile.json"


def load():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_full_two_section_fixture_matches_separately_derived_result():
    result = run_payload(load())
    assert result["status"] == "unreviewed_inputs"
    assert len(result["sections_top_to_bottom"]) == 2
    assert abs(Decimal(result["top_section_tensions_n"]["pickup"])
               - Decimal("28036.19044651989")) < Decimal("0.000001")
    assert abs(Decimal(result["top_section_tensions_n"]["slackoff"])
               - Decimal("23901.019589810734")) < Decimal("0.000001")
    assert abs(Decimal(result["total_friction_contact_torque_nm"])
               - Decimal("155.06890712659325")) < Decimal("0.000001")


def test_json_cli_executes_and_reports_no_approval():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_torque_drag_profile.py"),
         str(FIXTURE)], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert "NOT rig hookload" in result["warning"]


def test_json_cli_writes_result_to_file(tmp_path):
    output = tmp_path / "profile-result.json"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_torque_drag_profile.py"),
         str(FIXTURE), "--output", str(output)], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(output.read_text())["model"] == "contiguous-colinear-straight-profile-v0.1"


@pytest.mark.parametrize("change", [
    {"bottom_tension": None},
    {"intervals_top_to_bottom": []},
    {"intervals_top_to_bottom": "not a list"},
    {"unexpected": True},
])
def test_bad_profile_payloads_rejected(change):
    value = load()
    value.update(change)
    with pytest.raises(TorqueDragError):
        run_payload(value)


def test_bad_interval_payload_rejected():
    value = load()
    value["intervals_top_to_bottom"][0].pop("axial_friction")
    with pytest.raises(TorqueDragError):
        run_payload(value)


def test_invalid_json_file_exits_nonzero(tmp_path):
    corrupted = tmp_path / "bad.json"
    corrupted.write_text("{broken", encoding="utf-8")
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_torque_drag_profile.py"),
         str(corrupted)], capture_output=True, text=True)
    assert run.returncode == 2
    assert "unavailable" in run.stderr
