"""LH-016 report artifact review: synthetic outputs and explicit limitations."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_synthetic_reports.py"
spec = importlib.util.spec_from_file_location("export_synthetic_reports", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

@pytest.fixture(scope="module")
def exports(tmp_path_factory):
    files = mod.generate(tmp_path_factory.mktemp("lh016-report-review"))
    assert len(files) == 4
    return {p.name: p for p in files}

def test_two_reviewable_reports_written(exports):
    for prefix in ("lh003-normal-synth", "lh003-anomalous-synth"):
        assert (prefix + ".md") in exports
        assert (prefix + ".json") in exports
        report = json.loads(exports[prefix + ".json"].read_text(encoding="utf-8"))
        assert report["status"] == "draft_unapproved"
        assert report["conclusion"]["status"] == "undetermined"
        assert report["engineer_review"]["signoff"] is None
        assert report["scope"]["equipment"]["approved_job_procedure"] is None

def test_normal_report_no_failure_claim(exports):
    text = exports["lh003-normal-synth.md"].read_text(encoding="utf-8")
    assert "No failure mechanism inferred" in text
    assert "none identified" in text
    assert "not proof of hanger setting" in text
    assert "NOT ENGINEER-APPROVED" in text

def test_anomaly_report_evidence_and_contradiction_readable(exports):
    text = exports["lh003-anomalous-synth.md"].read_text(encoding="utf-8")
    assert "H-SEAT" in text and "H-SETTING" in text
    assert "Evidence for: A-OBS" in text
    assert "Evidence against: A-ANNOT" in text
    assert "SYNTHETIC-HOOKLOAD-CSV" in text
    assert "SYNTHETIC-JOB-PROGRAM" in text
    assert "not necessarily the first operational deviation" in text

def test_anomaly_prints_why_cement_measurement_unverifiable(exports):
    text = exports["lh003-anomalous-synth.md"].read_text(encoding="utf-8")
    assert "sensor/measurement domain mismatch" in text
    assert "sensor mapping not verified" in text
    assert "time unverified/unplaced" in text
    assert "Date only" in text

def test_unknown_geometry_not_invented(exports):
    normal = json.loads(exports["lh003-normal-synth.json"].read_text(encoding="utf-8"))
    anomaly = json.loads(exports["lh003-anomalous-synth.json"].read_text(encoding="utf-8"))
    assert normal["scope"]["equipment"]["nominal_internal_reference_md_m"] == "1501.2"
    assert anomaly["scope"]["equipment"]["nominal_internal_reference_md_m"] is None
    assert "unavailable" in exports["lh003-anomalous-synth.md"].read_text(encoding="utf-8")

def test_fixtures_maintain_anomaly_chronology_separation(exports):
    data = json.loads(exports["lh003-anomalous-synth.json"].read_text(encoding="utf-8"))
    assert len(data["chronology"]["unplaced_event_ids"]) == 2
    assert data["chronology"]["earliest_screening_candidate_id"]
    assert any(e["time_basis"] == "Date only" for e in data["evidence_register"])
    assert any(e["reasons"] for e in data["evidence_register"])
