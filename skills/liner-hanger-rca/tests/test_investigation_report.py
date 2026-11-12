"""LH-016 report integration tests against existing synthetic case replays."""
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
TESTS = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

reports = load("investigation_report", SKILL / "scripts" / "investigation_report.py")
scenarios = load("test_lh003_scenarios", TESTS / "test_lh003_scenarios.py")
cases = {c["case_id"]: c for c in json.loads(
    (TESTS / "fixtures" / "lh003_synthetic_cases.json").read_text(
        encoding="utf-8"))["cases"]}

def make_report(case_id):
    result = scenarios.exercise(cases[case_id])
    equipment = {
        "manufacturer": "baker_hughes (fictional identity)",
        "model": "SYNTHETIC-MODEL",
        "configuration": "fictional-config",
        "tally_basis": result["tally"].basis,
        "nominal_internal_reference_md_m":
            str(result["internal_md"]) if result["internal_md"] is not None else None,
        "well_design_approved": None,
    }
    report = reports.compile_report(
        case_id=case_id, report_id=f"REPORT-{case_id}",
        authored_by="synthetic test author",
        equipment=equipment, timeline=result["timeline"],
        hypothesis_review=result["assessment"])
    return result, report

def test_normal_case_report_does_not_infer_success():
    _, report = make_report("LH003-NORMAL-SYNTH")
    assert report["scope"]["mode"] == "normal_operation_review"
    assert report["competing_hypotheses"] == []
    assert report["chronology"]["earliest_screening_candidate_id"] is None
    assert report["conclusion"]["status"] == "undetermined"
    assert report["engineer_review"]["signoff"] is None

def test_anomalous_report_retains_two_alternatives_and_contradictions():
    _, report = make_report("LH003-ANOMALOUS-SYNTH")
    cards = report["competing_hypotheses"]
    assert len(cards) == 2
    assert cards[0]["evidence_for"] == ["A-OBS"]
    assert cards[0]["evidence_against"] == ["A-ANNOT"]
    assert cards[0]["discriminating_checks"]
    assert report["conclusion"]["confirmed_failure_mechanism"] is None

def test_report_keeps_unverifiable_cement_source_separate():
    _, report = make_report("LH003-ANOMALOUS-SYNTH")
    assert len(report["evidence_gaps"]["unverifiable_event_ids"]) == 1
    gap = report["evidence_gaps"]["unverifiable_event_ids"][0]
    observation = next(e for e in report["evidence_register"] if e["event_id"] == gap)
    assert observation["kind"] == "evidence_gap"
    assert observation["related_channel_id"] == "synthetic-spp"
    assert any("sensor/measurement domain" in r for r in observation["reasons"])

def test_first_candidate_not_promoted_to_verified_departure():
    _, report = make_report("LH003-ANOMALOUS-SYNTH")
    assert report["chronology"]["earliest_screening_candidate_id"]
    rendered = reports.render_markdown(report)
    assert "Earliest eligible *screening candidate*" in rendered
    assert "not necessarily the first operational deviation" in rendered
    assert "no confirmed root cause" in rendered

def test_uncertain_daily_event_has_no_fabricated_clock():
    _, report = make_report("LH003-ANOMALOUS-SYNTH")
    daily = next(e for e in report["evidence_register"] if e["event_id"] == "A-REPORT")
    assert daily["timestamp"] is None
    assert daily["time_state"] == "reported_approximate"
    assert "A-REPORT" in report["chronology"]["unplaced_event_ids"]

def test_source_ids_remain_in_report_and_markdown():
    _, report = make_report("LH003-ANOMALOUS-SYNTH")
    candidate = next(f for f in report["screening_findings"]
                     if f["status"] == "outside_screening_bounds")
    assert "SYNTHETIC-JOB-PROGRAM" in candidate["source_ids"]
    assert "SYNTHETIC-RIG-CSV" in candidate["source_ids"]
    text = reports.render_markdown(report)
    assert "SYNTHETIC-JOB-PROGRAM" in text
    assert "SYNTHETIC-RIG-CSV" in text

def test_report_is_json_serializable():
    _, report = make_report("LH003-ANOMALOUS-SYNTH")
    assert json.loads(json.dumps(report))["status"] == "draft_unapproved"

def test_unavailable_geometry_is_not_filled_in():
    _, report = make_report("LH003-ANOMALOUS-SYNTH")
    assert report["scope"]["equipment"]["nominal_internal_reference_md_m"] is None
    assert "unavailable" in reports.render_markdown(report)

def test_no_authorized_signoff_can_be_rendered_by_input_mutation():
    _, report = make_report("LH003-NORMAL-SYNTH")
    report["conclusion"]["status"] = "confirmed"
    with pytest.raises(reports.ReportError):
        reports.render_markdown(report)

def test_case_mismatch_rejected():
    result = scenarios.exercise(cases["LH003-NORMAL-SYNTH"])
    with pytest.raises(reports.ReportError, match="timeline case mismatch"):
        reports.compile_report(
            case_id="OTHER-CASE", report_id="R", authored_by="engineer",
            equipment={}, timeline=result["timeline"], hypothesis_review=result["assessment"])

def test_unregistered_source_fails_closed():
    _, report = make_report("LH003-NORMAL-SYNTH")
    result = scenarios.exercise(cases["LH003-NORMAL-SYNTH"])
    with pytest.raises(reports.ReportError, match="unregistered evidence source"):
        reports.compile_report(
            case_id=result["case_id"], report_id="R", authored_by="engineer",
            equipment={}, timeline=result["timeline"], hypothesis_review=result["assessment"],
            source_register={})

def test_hypothesis_cannot_link_unknown_event():
    result = scenarios.exercise(cases["LH003-ANOMALOUS-SYNTH"])
    packet = deepcopy(result["assessment"])
    packet["hypotheses"][0]["evidence_for"][0]["event_id"] = "FAKE-EVENT"
    with pytest.raises(reports.ReportError, match="unknown event"):
        reports.compile_report(
            case_id=result["case_id"], report_id="R", authored_by="engineer",
            equipment={}, timeline=result["timeline"], hypothesis_review=packet)

def test_hypothesis_source_mismatch_rejected():
    result = scenarios.exercise(cases["LH003-ANOMALOUS-SYNTH"])
    packet = deepcopy(result["assessment"])
    packet["hypotheses"][0]["evidence_for"][0]["source_ids"] = ["FORGED-SOURCE"]
    with pytest.raises(reports.ReportError, match="source references disagree"):
        reports.compile_report(
            case_id=result["case_id"], report_id="R", authored_by="engineer",
            equipment={}, timeline=result["timeline"], hypothesis_review=packet)

def test_report_rejects_claimed_confirmed_mechanism():
    result = scenarios.exercise(cases["LH003-ANOMALOUS-SYNTH"])
    packet = deepcopy(result["assessment"])
    packet["confirmed_failure_mechanism"] = "asserted"
    with pytest.raises(reports.ReportError, match="cannot accept a confirmed"):
        reports.compile_report(
            case_id=result["case_id"], report_id="R", authored_by="engineer",
            equipment={}, timeline=result["timeline"], hypothesis_review=packet)
