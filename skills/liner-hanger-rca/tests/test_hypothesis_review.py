"""Synthetic, source-registered competing-hypothesis regression.

No field data, BH model setpoints or automatic root-cause claims.
"""
import importlib.util
import sys
from pathlib import Path
from dataclasses import asdict, replace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


timeline = load("evidence_timeline")
review = load("hypothesis_review")


def event(eid, kind="measured_observation", case_id="TEST-CASE",
          time_state="verified", status="unreviewed"):
    return timeline.EvidenceEvent(
        event_id=eid, case_id=case_id, kind=kind,
        summary=f"synthetic {eid}", source_ids=(f"SOURCE-{eid}",),
        time_state=time_state,
        timestamp="2026-01-01T00:00:00Z" if time_state == "verified" else None,
        time_basis="Synthetic verified clock" if time_state == "verified" else None,
        review_status=status)


def link(eid, relation, *, rationale="Engineer says this requires review"):
    return review.EvidenceAssessment(eid, relation, rationale, "synthetic engineer")


def check(cid="check-1"):
    return review.DiscriminatingCheck(cid, "What additional evidence differentiates explanations?",
                                     "Authorized chronological job records")


def hypothesis(hid, assessments=(), checks=()):
    return review.Hypothesis(
        hypothesis_id=hid, case_id="TEST-CASE", title=f"Possibility {hid}",
        mechanism_question="Could the reported mechanism account for observed symptoms?",
        stage="hanger_setting", assessments=tuple(assessments),
        checks=tuple(checks), source_ref="synthetic engineering question")


def pair(first, second=None):
    return [first, second or hypothesis("H-B")]


def test_synthetic_competing_hypotheses_keep_both_sides():
    candidates = pair(hypothesis("H-A", [
        link("OBS-1", "supports"), link("OBS-2", "contradicts"),
        link("GAP-1", "unresolved")], [check()]))
    out = review.assess_case("TEST-CASE", candidates,
        [event("OBS-1"), event("OBS-2"), event("GAP-1", "evidence_gap")])
    card = out["hypotheses"][0]
    assert card["balance"] == "mixed_evidence_for_review"
    assert card["evidence_for"][0]["source_ids"] == ["SOURCE-OBS-1"]
    assert card["evidence_against"][0]["event_id"] == "OBS-2"
    assert card["unknowns"][0]["event_id"] == "GAP-1"
    assert card["discriminating_checks"][0]["check_id"] == "check-1"
    assert out["confirmed_failure_mechanism"] is None
    assert out["investigation_conclusion"] == "undetermined"


def test_no_evidence_never_forces_failure():
    out = review.assess_case("TEST-CASE", pair(hypothesis("H-A")), [])
    assert all(c["balance"] == "insufficient_evidence" for c in out["hypotheses"])
    assert out["confirmed_failure_mechanism"] is None


def test_normal_operation_review_without_hypotheses():
    out = review.assess_case("TEST-CASE", [], [event("OBS-1")],
                             mode="normal_operation_review")
    assert out["hypotheses"] == []
    assert out["unlinked_event_ids"] == ["OBS-1"]
    assert out["investigation_conclusion"] == "undetermined"


def test_fault_mode_requires_two_alternatives():
    with pytest.raises(review.HypothesisError, match="at least two"):
        review.assess_case("TEST-CASE", [hypothesis("H-A")], [])


@pytest.mark.parametrize("kind,relation", [
    ("evidence_gap", "supports"),
    ("evidence_gap", "contradicts"),
    ("screening_context", "supports"),
    ("screening_context", "contradicts"),
    ("screening_candidate", "supports"),
    ("screening_candidate", "contradicts"),
])
def test_screening_prompt_and_gaps_not_converted_to_mechanism_proof(kind, relation):
    with pytest.raises(review.HypothesisError):
        review.assess_case("TEST-CASE",
            pair(hypothesis("H-A", [link("E", relation)])),
            [event("E", kind)])


def test_screening_candidate_can_be_context_without_inference():
    out = review.assess_case("TEST-CASE",
        pair(hypothesis("H-A", [link("E", "context")])),
        [event("E", "screening_candidate")])
    assert out["hypotheses"][0]["balance"] == "insufficient_evidence"
    assert out["hypotheses"][0]["context"][0]["event_id"] == "E"


def test_unresolved_evidence_not_time_ordered_when_unknown():
    out = review.assess_case("TEST-CASE",
        pair(hypothesis("H-A", [link("E", "unresolved")])),
        [event("E", "reported_event", time_state="unknown")])
    item = out["hypotheses"][0]["unknowns"][0]
    assert item["timestamp"] is None
    assert item["time_state"] == "unknown"


def test_duplicate_hypothesis_identifiers_rejected():
    with pytest.raises(review.HypothesisError, match="duplicate hypothesis"):
        review.assess_case("TEST-CASE", [hypothesis("H-A"), hypothesis("H-A")], [])


def test_duplicate_event_link_on_same_hypothesis_rejected():
    a = hypothesis("H-A", [link("E", "supports"), link("E", "contradicts")])
    with pytest.raises(review.HypothesisError, match="duplicate event linked"):
        review.assess_case("TEST-CASE", pair(a), [event("E")])


def test_unknown_evidence_id_rejected():
    with pytest.raises(review.HypothesisError, match="unknown evidence"):
        review.assess_case("TEST-CASE",
            pair(hypothesis("H-A", [link("not-in-register", "supports")])), [])


def test_other_case_evidence_rejected():
    with pytest.raises(review.HypothesisError, match="different case"):
        review.assess_case("TEST-CASE",
            pair(hypothesis("H-A", [link("E", "supports")])),
            [event("E", case_id="OTHER-CASE")])


def test_other_case_hypothesis_rejected():
    with pytest.raises(review.HypothesisError, match="different case"):
        review.assess_case("TEST-CASE",
            pair(replace(hypothesis("H-A"), case_id="OTHER-CASE")), [])


def test_duplicate_event_register_rejected():
    with pytest.raises(review.HypothesisError, match="duplicate event"):
        review.assess_case("TEST-CASE", pair(hypothesis("H-A")),
                           [event("E"), event("E")])


def test_no_implicit_evidence_independence_or_probability():
    out = review.assess_case("TEST-CASE",
        pair(hypothesis("H-A", [link("E1", "supports"), link("E2", "supports")])),
        [event("E1"), event("E2")])
    card = out["hypotheses"][0]
    assert card["independent_evidence_strength"] == "not_assessed"
    assert "probability" not in card
    assert out["confirmed_failure_mechanism"] is None


def test_json_roundtrip_for_registered_evidence():
    h = hypothesis("H-A", [link("E", "contradicts")], [check()])
    out = review.assess_case_from_dict("TEST-CASE",
        [asdict(h), asdict(hypothesis("H-B"))], [event("E").to_dict()])
    assert out["hypotheses"][0]["evidence_against"][0]["event_id"] == "E"


def test_invalid_assessment_and_check_data_rejected():
    a = hypothesis("H-A", [link("E", "certainly_caused")])
    with pytest.raises(review.HypothesisError, match="invalid evidence relation"):
        review.assess_case("TEST-CASE", pair(a), [event("E")])
    h = hypothesis("H-A", checks=[check(), check()])
    with pytest.raises(review.HypothesisError, match="duplicate check_id"):
        review.assess_case("TEST-CASE", pair(h), [])


def test_unlinked_event_ids_remain_visible():
    out = review.assess_case("TEST-CASE",
        pair(hypothesis("H-A", [link("E-1", "context")])),
        [event("E-1"), event("E-2")])
    assert out["unlinked_event_ids"] == ["E-2"]


def test_event_review_flag_not_upgraded_by_hypothesis():
    out = review.assess_case("TEST-CASE",
        pair(hypothesis("H-A", [link("E", "supports")])),
        [event("E", status="unreviewed")])
    item = out["hypotheses"][0]["evidence_for"][0]
    assert item["event_review_status"] == "unreviewed"
    assert item["assessment"]["review_status"] == "draft"
