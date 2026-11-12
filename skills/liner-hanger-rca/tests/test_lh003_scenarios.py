"""LH-003 connected workflow acceptance fixtures. All values are invented TEST data.

These tests exercise the existing components together, not an OEM diagnostic model.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = Path(__file__).parent / "fixtures" / "lh003_synthetic_cases.json"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tally_engine = load("bha_tally")
specs = load("equipment_specs")
limits = load("operating_limit_screen")
timeline = load("evidence_timeline")
hypotheses = load("hypothesis_review")


@pytest.fixture(scope="module")
def cases():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert "ENTIRELY SYNTHETIC" in data["disclaimer"]
    assert len(data["cases"]) == 2
    return {case["case_id"]: case for case in data["cases"]}


def tool():
    return limits.ToolIdentity(
        "baker_hughes", "SYNTHETIC-FAMILY", "SYNTHETIC-MODEL",
        "fictional-size", "fictional-revision", "fictional-config")


def exercise(case):
    """One common replay path, no special-case expected outcomes in the engine."""
    case_id = case["case_id"]
    tally = tally_engine.manual_tally("as_run", case["component_rows"], case["anchor"])
    internal = specs.InternalReference(**case["internal_reference"])
    internal_md = specs.internal_reference_md(tally, internal)
    events = [timeline.event_from_dict(
        dict(case_id=case_id, **event)) for event in case["reported_events"]]
    screen_results = []
    generated_events = {}
    for configured_rule, record in zip(case["rules"], case["observations"]):
        assert record["rule_id"] == configured_rule["rule_id"]
        rule = limits.ApprovedLimit(
            tool=tool(), origin="job",
            source_id="SYNTHETIC-JOB-PROGRAM",
            source_revision="synthetic-rev",
            source_location="fictional-reference",
            approval_reference="SYNTHETIC-REVIEW-ONLY",
            reviewed_by="fixture engineer", reviewed_at="2026-01-01T00:00:00Z",
            authorized_for_case=True, **configured_rule)
        measurement = limits.Observation(
            tool=tool(), stage=rule.stage, parameter=rule.parameter,
            quantity=rule.quantity, unit=rule.unit,
            pressure_basis=rule.pressure_basis,
            measurement_domain=record.get("measurement_domain",
                                          rule.measurement_domain),
            value=record["value"], timestamp=record["timestamp"],
            source_id="SYNTHETIC-RIG-CSV",
            channel_id="synthetic-spp",
            units_verified=record.get("units_verified", True),
            channel_mapping_verified=record.get("channel_mapping_verified", True),
            clock_alignment_verified=record.get("clock_alignment_verified", True),
            measurement_equivalence_verified=record.get(
                "measurement_equivalence_verified", True))
        result = limits.screen(rule, measurement)
        event = timeline.events_from_screen(case_id, rule, measurement, result)
        screen_results.append(result)
        generated_events[rule.rule_id] = event
        events.append(event)
    constructed_hypotheses = []
    for raw in case["hypotheses"]:
        constructed_hypotheses.append(hypotheses.Hypothesis(
            hypothesis_id=raw["hypothesis_id"], case_id=case_id,
            title=raw["title"], mechanism_question=raw["mechanism_question"],
            stage=raw["stage"], source_ref=raw["source_ref"],
            assessments=tuple(hypotheses.EvidenceAssessment(**a)
                              for a in raw["assessments"]),
            checks=tuple(hypotheses.DiscriminatingCheck(**c)
                         for c in raw["checks"])))
    ordered = timeline.build_timeline(case_id, events)
    assessment = hypotheses.assess_case(
        case_id, constructed_hypotheses, events, mode=case["mode"])
    return {
        "case_id": case_id, "tally": tally, "internal_md": internal_md,
        "screen_results": screen_results, "screen_events": generated_events,
        "events": events, "timeline": ordered, "assessment": assessment,
    }


def test_normal_operation_full_replay(cases):
    case = cases["LH003-NORMAL-SYNTH"]
    out = exercise(case)
    assert [r["status"] for r in out["screen_results"]] == case["expected_screen_statuses"]
    assert out["internal_md"] == specs.Decimal("1501.2")
    assert out["timeline"]["earliest_screening_candidate_id"] is None
    assert len(out["timeline"]["ordered_verified_events"]) == 2
    assert len(out["timeline"]["unplaced_events"]) == 1
    assert out["assessment"]["hypotheses"] == []
    assert out["assessment"]["confirmed_failure_mechanism"] is None
    assert out["assessment"]["investigation_conclusion"] == "undetermined"


def test_anomalous_operation_full_replay(cases):
    case = cases["LH003-ANOMALOUS-SYNTH"]
    out = exercise(case)
    assert [r["status"] for r in out["screen_results"]] == case["expected_screen_statuses"]
    assert out["internal_md"] is None
    assert out["tally"].position_m("LH-TEST", "bottom") is None
    assert out["timeline"]["earliest_screening_candidate_id"] == out["screen_events"]["A-02"].event_id
    assert out["screen_events"]["A-03"].kind == "evidence_gap"
    assert out["screen_events"]["A-03"].timestamp is None
    assert len(out["timeline"]["unplaced_events"]) == 2
    assert len(out["assessment"]["hypotheses"]) == 2
    assert out["assessment"]["hypotheses"][0]["balance"] == "mixed_evidence_for_review"
    assert out["assessment"]["confirmed_failure_mechanism"] is None


def test_candidate_is_not_automatically_hypothesis_evidence(cases):
    out = exercise(cases["LH003-ANOMALOUS-SYNTH"])
    candidate_id = out["screen_events"]["A-02"].event_id
    assert candidate_id in out["assessment"]["unlinked_event_ids"]
    assert all(candidate_id not in [i["event_id"] for i in h["evidence_for"]]
               for h in out["assessment"]["hypotheses"])


def test_rig_and_cement_unit_stay_distinct(cases):
    out = exercise(cases["LH003-ANOMALOUS-SYNTH"])
    assert out["screen_events"]["A-03"].kind == "evidence_gap"
    assert any("sensor/measurement domain" in reason
               for reason in out["screen_events"]["A-03"].reasons)
    assert out["screen_results"][-1]["status"] == "unverifiable"


def test_reported_day_only_never_fabricates_clock(cases):
    out = exercise(cases["LH003-ANOMALOUS-SYNTH"])
    report = next(event for event in out["timeline"]["unplaced_events"]
                  if event["event_id"] == "A-REPORT")
    assert report["timestamp"] is None
    assert report["time_state"] == "reported_approximate"


def test_sources_survive_entire_pipeline(cases):
    out = exercise(cases["LH003-ANOMALOUS-SYNTH"])
    assert "SYNTHETIC-JOB-PROGRAM" in out["screen_events"]["A-02"].source_ids
    assert "SYNTHETIC-RIG-CSV" in out["screen_events"]["A-02"].source_ids
    assert out["assessment"]["hypotheses"][0]["evidence_for"][0]["source_ids"] == [
        "SYNTHETIC-HOOKLOAD-CSV"]


def test_normal_screen_is_not_success_proof(cases):
    out = exercise(cases["LH003-NORMAL-SYNTH"])
    assert all(event.kind == "screening_context"
               for event in out["screen_events"].values())
    assert out["assessment"]["investigation_conclusion"] == "undetermined"


def test_alternative_hypotheses_remain_unranked(cases):
    out = exercise(cases["LH003-ANOMALOUS-SYNTH"])
    cards = out["assessment"]["hypotheses"]
    assert [h["hypothesis_id"] for h in cards] == ["H-SEAT", "H-SETTING"]
    assert all(h["independent_evidence_strength"] == "not_assessed" for h in cards)
    assert all("probability" not in h for h in cards)


def test_anomalous_case_contains_actual_contradiction_and_checks(cases):
    out = exercise(cases["LH003-ANOMALOUS-SYNTH"])
    first = out["assessment"]["hypotheses"][0]
    assert len(first["evidence_for"]) == 1
    assert len(first["evidence_against"]) == 1
    assert first["discriminating_checks"][0]["required_evidence"]


def test_evidence_case_isolation(cases):
    out = exercise(cases["LH003-NORMAL-SYNTH"])
    wrong = timeline.event_from_dict(dict(
        out["events"][0].to_dict(), case_id="OTHER"))
    with pytest.raises(timeline.TimelineError, match="different case"):
        timeline.build_timeline(out["case_id"], [wrong])


def test_tally_source_and_datum_retained(cases):
    out = exercise(cases["LH003-NORMAL-SYNTH"])
    assert out["tally"].anchor.datum == "SYNTHETIC-RKB"
    assert all(c.source_ref == "SYNTHETIC-TALLY"
               for c in out["tally"].components)


def test_fixture_is_documented_as_fictional(cases):
    for case in cases.values():
        assert case["case_id"].endswith("-SYNTH")
        assert all("SYNTHETIC" in c["source_ref"]
                   for c in case["component_rows"])
        assert all("SYNTHETIC" in rule["rule_id"] or rule["rule_id"].startswith(("A-", "N-"))
                   for rule in case["rules"])
