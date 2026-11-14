"""Standalone JSON runner and contract-negative tests (all data synthetic)."""
import json
from decimal import Decimal
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_planned_section import from_payload, run_payload
from planned_job_section import PlannedSectionError


def example():
    return json.loads((ROOT / "examples" / "synthetic_planned_section.json").read_text(encoding="utf-8"))


def test_bundled_example_calculates_candidate_with_unreviewed_sources():
    result = run_payload(example())
    assert result["case_id"] == "SYNTHETIC-CALC01-NOT-A-REAL-WELL"
    assert result["status"] == "unreviewed_inputs"
    assert Decimal(result["results"]["hydrostatic_difference_pa"]) == Decimal("980665")
    assert "No OEM approval" in result["warning"]


def test_runner_cli_stdout():
    cmd = [sys.executable, str(ROOT / "scripts" / "run_planned_section.py"),
           str(ROOT / "examples" / "synthetic_planned_section.json")]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "unreviewed_inputs"
    assert payload["results"]["section_length_md_m"] == "100"


def test_runner_cli_rejects_invalid_json(tmp_path):
    invalid = tmp_path / "bad.json"
    invalid.write_text("{invalid", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_planned_section.py"), str(invalid)],
        capture_output=True, text=True, check=False)
    assert completed.returncode == 2
    assert "unavailable:" in completed.stderr


@pytest.mark.parametrize("change", [
    {"case_id": None},
    {"survey_stations": "not-an-array"},
    {"survey_stations": [{"measured_depth": 0, "inclination_deg": 0,
                          "azimuth_deg": 0, "source_ref": "synthetic"}]},
    {"fluid_density": None},
    {"fluid_density": {"value": 1000, "unit": "kg/m3"}},
    {"extra": "not supported"},
])
def test_job_schema_fails_closed(change):
    raw = example()
    raw.update(change)
    with pytest.raises(PlannedSectionError):
        from_payload(raw)


def test_unknown_nan_fluid_value_is_rejected():
    raw = example()
    raw["fluid_density"]["value"] = float("nan")
    with pytest.raises(PlannedSectionError):
        run_payload(raw)
