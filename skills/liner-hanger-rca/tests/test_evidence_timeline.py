"""Synthetic evidence timeline tests: screening is never a proven failure."""
import importlib.util
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


screen_mod = load("operating_limit_screen")
timeline = load("evidence_timeline")


def tool(revision="synthetic-A"):
    return screen_mod.ToolIdentity("baker_hughes", "fictional-family",
                                   "fictional-model", "fictional-size",
                                   revision, "fixture-config")


def rule():
    return screen_mod.ApprovedLimit(
        rule_id="test-rule", tool=tool(), stage="hanger_setting",
        parameter="synthetic_pressure", quantity="pressure", unit="psi",
        pressure_basis="gauge", measurement_domain="rig_standpipe",
        comparator="maximum", lower=None, upper=200,
        origin="job", source_id="SYNTHETIC-JOB-PROGRAM",
        source_revision="test-rev", source_location="synthetic-section",
        approval_reference="test-approval", reviewed_by="test-reviewer",
        reviewed_at="2026-01-01T00:00:00Z", authorized_for_case=True)


def observed(value, when="2026-01-01T00:10:00+00:00", **changes):
    data = dict(
        tool=tool(), stage="hanger_setting", parameter="synthetic_pressure",
        quantity="pressure", value=value, unit="psi", pressure_basis="gauge",
        measurement_domain="rig_standpipe", source_id="SYNTHETIC-RIG-CSV",
        channel_id="synthetic-spp", timestamp=when, units_verified=True,
        channel_mapping_verified=True, clock_alignment_verified=True,
        measurement_equivalence_verified=True)
    data.update(changes)
    return screen_mod.Observation(**data)


def screening_event(value, when="2026-01-01T00:10:00+00:00", **changes):
    limit, obs = rule(), observed(value, when, **changes)
    return timeline.events_from_screen("TEST-CASE", limit, obs,
                                       screen_mod.screen(limit, obs))


def test_outside_limit_links_rule_and_telemetry_not_tool_failure():
    event = screening_event(210)
    assert event.kind == "screening_candidate"
    assert event.source_ids == ("SYNTHETIC-JOB-PROGRAM", "SYNTHETIC-RIG-CSV")
    assert event.related_channel_id == "synthetic-spp"
    assert event.review_status == "unreviewed"
    assert "not a tool-state" in event.summary


def test_within_bounds_is_context_not_confirmed_success():
    event = screening_event(180)
    assert event.kind == "screening_context"
    assert event.screening_status == "within_screening_bounds"


def test_unverified_units_are_unplaced_evidence_gap():
    event = screening_event(300, units_verified=False)
    assert event.kind == "evidence_gap"
    assert event.time_state == "unknown"
    assert event.timestamp is None
    assert any("units" in msg for msg in event.reasons)


def test_cross_oem_incompatibility_is_not_a_deviation():
    obs = observed(300, tool=screen_mod.ToolIdentity(
        "halliburton", "fictional-family", "fictional-model",
        "fictional-size", "synthetic-A", "fixture-config"))
    lim = rule()
    event = timeline.events_from_screen("TEST-CASE", lim, obs,
                                        screen_mod.screen(lim, obs))
    assert event.kind == "evidence_gap"
    assert event.time_state == "unknown"


def test_report_only_day_is_not_silently_ordered():
    approx = timeline.EvidenceEvent(
        event_id="report-1", case_id="TEST-CASE",
        kind="reported_event", summary="Daily log reports running issue",
        source_ids=("DAILY-REPORT",), time_state="reported_approximate",
        timestamp=None, time_basis="Date only; no reliable clock")
    output = timeline.build_timeline(
        "TEST-CASE", [screening_event(220), approx])
    assert len(output["ordered_verified_events"]) == 1
    assert output["unplaced_events"][0]["event_id"] == "report-1"
    assert output["investigation_conclusion"] == "undetermined"


def test_earliest_flag_only_among_supplied_verified_candidates():
    later = screening_event(220, "2026-01-01T00:20:00Z")
    earlier = screening_event(230, "2026-01-01T00:10:00+00:00")
    ok = screening_event(190, "2026-01-01T00:00:00Z")
    result = timeline.build_timeline("TEST-CASE", [later, ok, earlier])
    assert result["ordered_verified_events"][0]["kind"] == "screening_context"
    assert result["earliest_screening_candidate_id"] == earlier.event_id
    assert "not necessarily the first" in result["chronology_warning"]


def test_timezone_aware_ordering_is_in_utc():
    e1 = screening_event(210, "2026-01-01T11:00:00+11:00")
    e2 = screening_event(220, "2026-01-01T00:30:00Z")
    result = timeline.build_timeline("TEST-CASE", [e2, e1])
    assert result["ordered_verified_events"][0]["event_id"] == e1.event_id


def test_naive_clock_is_rejected_if_marked_verified():
    with pytest.raises(timeline.TimelineError, match="offset"):
        screening_event(210, "2026-01-01T00:00:00")


@pytest.mark.parametrize("change", [
    {"source_ids": ()},
    {"case_id": "OTHER-CASE"},
    {"time_state": "verified", "timestamp": None},
])
def test_bad_event_or_case_is_rejected(change):
    event = asdict(screening_event(210))
    event.update(change)
    if event["case_id"] != "TEST-CASE":
        parsed = timeline.event_from_dict(event)
        with pytest.raises(timeline.TimelineError, match="different case"):
            timeline.build_timeline("TEST-CASE", [parsed])
    else:
        with pytest.raises(timeline.TimelineError):
            timeline.event_from_dict(event)


def test_duplicate_event_ids_are_rejected():
    event = screening_event(220)
    with pytest.raises(timeline.TimelineError, match="duplicate"):
        timeline.build_timeline("TEST-CASE", [event, event])


def test_tampered_screen_result_rejected():
    lim, obs = rule(), observed(220)
    wrong = screen_mod.screen(lim, obs)
    wrong["status"] = "within_screening_bounds"
    with pytest.raises(timeline.TimelineError, match="does not match"):
        timeline.events_from_screen("TEST-CASE", lim, obs, wrong)


def test_contract_json_roundtrip():
    e = screening_event(220)
    result = timeline.timeline_from_dict("TEST-CASE", [e.to_dict()])
    assert result["ordered_verified_events"][0]["source_ids"] == ("SYNTHETIC-JOB-PROGRAM", "SYNTHETIC-RIG-CSV")
