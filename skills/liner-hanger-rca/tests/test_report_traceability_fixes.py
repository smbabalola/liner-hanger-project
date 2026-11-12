"""LH-016 regression tests for audited engineer-readable report findings."""
import json
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

adapter = load("lh016_export_review", ROOT / "scripts" / "export_synthetic_reports.py")

def test_screen_ids_do_not_embed_sample_clocks(tmp_path):
    adapter.generate(tmp_path)
    case = json.loads((tmp_path / "lh003-anomalous-synth.json").read_text(encoding="utf-8"))
    gaps = [e for e in case["evidence_register"] if e["kind"] == "evidence_gap"]
    assert len(gaps) == 1
    assert "2026" not in gaps[0]["event_id"]
    assert gaps[0]["timestamp"] is None
    assert gaps[0]["source_sample_time"] == "2026-01-01T08:20:00Z"
    assert gaps[0]["time_state"] == "unknown"

def test_screen_report_contains_numerical_values_but_no_false_comparison(tmp_path):
    adapter.generate(tmp_path)
    case = json.loads((tmp_path / "lh003-anomalous-synth.json").read_text(encoding="utf-8"))
    outside = next(e for e in case["screening_findings"] if e["status"] == "outside_screening_bounds")
    assert outside["screening_details"]["observed"] == "215"
    assert outside["screening_details"]["upper"] == "200"
    assert outside["screening_details"]["limit_unit"] == "psi"
    unverifiable = next(e for e in case["screening_findings"] if e["status"] == "unverifiable")
    assert unverifiable["screening_details"]["observed"] == "220"
    assert unverifiable["screening_details"]["comparison_permitted"] is False
    assert unverifiable["screening_details"]["observed_domain"] == "rig_standpipe"
    assert unverifiable["screening_details"]["expected_domain"] == "cement_unit_discharge"
    text = (tmp_path / "lh003-anomalous-synth.md").read_text(encoding="utf-8")
    assert "215 psi" in text
    assert "maximum: — to 200 psi" in text
    assert "Comparison NOT authorised" in text

def test_hypothesis_rationales_and_assessors_survive(tmp_path):
    adapter.generate(tmp_path)
    case = json.loads((tmp_path / "lh003-anomalous-synth.json").read_text(encoding="utf-8"))
    first = case["competing_hypotheses"][0]
    assessment = next(e for e in first["evidence_assessments"] if e["relation"] == "contradicts")
    assert assessment["event_id"] == "A-ANNOT"
    assert assessment["rationale"] == "Alternative reading of surface signal needs checking"
    assert assessment["assessor"] == "synthetic engineer"
    text = (tmp_path / "lh003-anomalous-synth.md").read_text(encoding="utf-8")
    assert "Alternative reading of surface signal needs checking" in text
    assert "synthetic engineer" in text

def test_source_revision_location_and_missing_sample_locator_explicit(tmp_path):
    adapter.generate(tmp_path)
    case = json.loads((tmp_path / "lh003-anomalous-synth.json").read_text(encoding="utf-8"))
    e = next(e for e in case["evidence_register"] if e["kind"] == "screening_candidate")
    locs = e["source_locations"]
    assert locs["SYNTHETIC-JOB-PROGRAM"]["revision"] == "FICTIONAL-REV-1"
    assert locs["SYNTHETIC-JOB-PROGRAM"]["location"] == "synthetic-rule-page"
    assert locs["SYNTHETIC-RIG-CSV"]["location"] is None
    text = (tmp_path / "lh003-anomalous-synth.md").read_text(encoding="utf-8")
    assert "location=not supplied" in text
    assert "revision=FICTIONAL-REV-1" in text
    assert "listing order is NOT evidence" in text
