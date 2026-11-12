"""LH-017 first validation batch: deliberately adverse synthetic investigation inputs.

These are negative-controls and source-gating tests, NOT validation of a
Baker Hughes mechanical diagnosis. No OEM-specific numerical limits are used.
"""
import importlib.util
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj

scenarios = load("lh017_lh003", HERE / "test_lh003_scenarios.py")
limits = scenarios.limits
timeline = scenarios.timeline
reports = load("lh017_reports", SCRIPTS / "investigation_report.py")

@pytest.fixture(scope="module")
def cases():
    return {c["case_id"]: c for c in json.loads(
        (HERE / "fixtures" / "lh003_synthetic_cases.json").read_text(
            encoding="utf-8"))["cases"]}

def model():
    return scenarios.tool()

def rule_and_observation(**overrides):
    tool = model()
    rule = limits.ApprovedLimit(
        rule_id="LH017-ONLY-SYNTHETIC", tool=tool,
        stage="hanger_setting", parameter="synthetic_pressure",
        quantity="pressure", unit="psi", pressure_basis="gauge",
        measurement_domain="rig_standpipe", comparator="maximum",
        lower=None, upper=200, origin="job",
        source_id="SYNTHETIC-RULE", source_revision="fictional-rev",
        source_location="fictional-section", approval_reference="SYNTHETIC-ONLY",
        reviewed_by="fictional reviewer", reviewed_at="2026-01-01T00:00:00Z",
        authorized_for_case=True)
    obs = limits.Observation(
        tool=tool, stage="hanger_setting", parameter="synthetic_pressure",
        quantity="pressure", value=215, unit="psi",
        pressure_basis="gauge", measurement_domain="rig_standpipe",
        source_id="SYNTHETIC-CSV", channel_id="rig-spp-1",
        timestamp="2026-01-01T08:00:00Z",
        units_verified=True, channel_mapping_verified=True,
        clock_alignment_verified=True, measurement_equivalence_verified=True)
    return rule, replace(obs, **overrides)

@pytest.mark.parametrize("other", [
    "halliburton", "unknown_oem", "baker_hughes_typo"
])
def test_other_oem_never_inherits_bh_rule(other):
    rule, observation = rule_and_observation()
    alien = replace(model(), manufacturer_id=other)
    result = limits.screen(rule, replace(observation, tool=alien))
    assert result["status"] == "unverifiable"
    assert any("manufacturer" in reason or "identity" in reason for reason in result["reasons"])

@pytest.mark.parametrize("identity_change", [
    {"revision": "unsupported-rev"},
    {"configuration_id": "unsupported-config"},
    {"model": "different-model"},
    {"size": "different-size"},
])
def test_tool_revision_model_size_configuration_must_match(identity_change):
    rule, obs = rule_and_observation()
    altered = replace(model(), **identity_change)
    result = limits.screen(rule, replace(obs, tool=altered))
    assert result["status"] == "unverifiable"
    assert "tool identity/model/size/revision/configuration mismatch" in result["reasons"]

def test_caller_supplied_unapproved_rule_never_screened():
    rule, obs = rule_and_observation()
    result = limits.screen(replace(rule, authorized_for_case=False), obs)
    assert result["status"] == "unverifiable"
    assert "source approval has not been authorized for this case" in result["reasons"]

@pytest.mark.parametrize("change, reason", [
    ({"unit": "bar"}, "quantity or engineering unit mismatch"),
    ({"pressure_basis": "absolute"}, "pressure basis mismatch"),
    ({"measurement_domain": "cement_unit_discharge"}, "sensor/measurement domain mismatch"),
    ({"measurement_equivalence_verified": False}, "measurement not verified as comparable"),
])
def test_noncomparable_measurement_must_not_become_deviation(change, reason):
    rule, obs = rule_and_observation(**change)
    result = limits.screen(rule, obs)
    assert result["status"] == "unverifiable"
    assert any(reason in r for r in result["reasons"])
    event = timeline.events_from_screen("LH017-SYNTH", rule, obs, result)
    assert event.kind == "evidence_gap"
    assert event.time_state == "unknown"
    assert event.timestamp is None
    assert event.screening_details["comparison_permitted"] is False

def test_bad_clock_never_ordered_as_verified():
    rule, obs = rule_and_observation(clock_alignment_verified=False)
    result = limits.screen(rule, obs)
    event = timeline.events_from_screen("LH017-SYNTH", rule, obs, result)
    ordered = timeline.build_timeline("LH017-SYNTH", [event])
    assert ordered["ordered_verified_events"] == []
    assert ordered["earliest_screening_candidate_id"] is None
    assert ordered["unplaced_events"][0]["source_sample_time"] == obs.timestamp

def test_report_is_unapproved_even_when_screen_candidate_exists(cases):
    outcome = scenarios.exercise(cases["LH003-ANOMALOUS-SYNTH"])
    report = reports.compile_report(
        case_id=outcome["case_id"], equipment={}, timeline=outcome["timeline"],
        hypothesis_review=outcome["assessment"],
        authored_by="synthetic author", report_id="LH017-R")
    assert report["chronology"]["earliest_screening_candidate_id"]
    assert report["conclusion"]["confirmed_failure_mechanism"] is None
    assert report["engineer_review"]["status"] == "not_completed"

def test_normal_control_does_not_generate_failing_hypothesis(cases):
    outcome = scenarios.exercise(cases["LH003-NORMAL-SYNTH"])
    report = reports.compile_report(
        case_id=outcome["case_id"], equipment={}, timeline=outcome["timeline"],
        hypothesis_review=outcome["assessment"],
        authored_by="synthetic author", report_id="LH017-N")
    assert report["competing_hypotheses"] == []
    assert report["chronology"]["earliest_screening_candidate_id"] is None
    assert report["conclusion"]["status"] == "undetermined"
