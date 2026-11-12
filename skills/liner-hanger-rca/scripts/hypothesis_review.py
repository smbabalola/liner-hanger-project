"""Evidence-linked competing-hypothesis register for offline retrospective RCA.

This deterministic module ORGANISES engineering interpretations. It never
infers that a tool set/released, declares a root cause or manufactures tests.
Inputs contain only engineer-authored hypotheses and links to existing evidence
timeline events. No OEM limits or diagnostic rules are embedded.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping, Sequence

RELATIONS = {"supports", "contradicts", "context", "unresolved"}
MODES = {"fault_investigation", "normal_operation_review"}
REVIEW_STATES = {"draft", "review_requested", "engineer_reviewed"}
# A screen outside a limit is a candidate, not proof of a mechanism.
EVIDENCE_KINDS = {
    "reported_event", "measured_observation", "screening_candidate",
    "screening_context", "evidence_gap", "engineer_annotation",
}


class HypothesisError(ValueError):
    """Invalid contract or untraceable engineering interpretation."""


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise HypothesisError(f"{field}: non-empty string required")
    return value.strip()


@dataclass(frozen=True)
class EvidenceAssessment:
    """Engineer-asserted relationship; event fact remains unchanged."""
    event_id: str
    relation: str
    rationale: str
    assessor: str
    review_status: str = "draft"

    def validate(self):
        _text(self.event_id, "event_id")
        if self.relation not in RELATIONS:
            raise HypothesisError("invalid evidence relation")
        _text(self.rationale, "rationale")
        _text(self.assessor, "assessor")
        if self.review_status not in REVIEW_STATES:
            raise HypothesisError("invalid assessment review status")
        return self


@dataclass(frozen=True)
class DiscriminatingCheck:
    """A review question, not a live operating instruction."""
    check_id: str
    question: str
    required_evidence: str
    source_ref: str | None = None

    def validate(self):
        _text(self.check_id, "check_id")
        _text(self.question, "question")
        _text(self.required_evidence, "required_evidence")
        return self


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    case_id: str
    title: str
    mechanism_question: str
    stage: str
    assessments: tuple[EvidenceAssessment, ...] = ()
    checks: tuple[DiscriminatingCheck, ...] = ()
    source_ref: str | None = None
    review_status: str = "draft"

    def validate(self):
        for key in ("hypothesis_id", "case_id", "title", "mechanism_question", "stage"):
            _text(getattr(self, key), key)
        if self.review_status not in REVIEW_STATES:
            raise HypothesisError("invalid hypothesis review status")
        seen = set()
        for assessment in self.assessments:
            assessment.validate()
            if assessment.event_id in seen:
                raise HypothesisError("duplicate event linked to same hypothesis")
            seen.add(assessment.event_id)
        checks = set()
        for check in self.checks:
            check.validate()
            if check.check_id in checks:
                raise HypothesisError("duplicate check_id")
            checks.add(check.check_id)
        return self


def _event_index(case_id, events):
    """Accept EvidenceEvent objects or validated JSON copies."""
    from evidence_timeline import event_from_dict
    index = {}
    for event in events:
        # Revalidate even dataclass objects: neither a forged reference nor an
        # event from another case can be silently accepted.
        record = event_from_dict(event) if isinstance(event, Mapping) else event.validate()
        if record.kind not in EVIDENCE_KINDS:
            raise HypothesisError("unsupported evidence kind")
        if record.case_id != case_id:
            raise HypothesisError("evidence belongs to a different case")
        if record.event_id in index:
            raise HypothesisError("duplicate event in evidence register")
        index[record.event_id] = record
    return index


def assess_case(case_id: str, hypotheses: Sequence[Hypothesis],
                events, *, mode: str = "fault_investigation") -> dict:
    """Produce a traceable, non-diagnostic review packet.

    A fault investigation must include at least two competing hypotheses.
    A normal-operation review may contain no hypotheses without claiming proof
    of success. No scoring, probabilities or root-cause selection are produced.
    """
    _text(case_id, "case_id")
    if mode not in MODES:
        raise HypothesisError("invalid investigation mode")
    if mode == "fault_investigation" and len(hypotheses) < 2:
        raise HypothesisError("fault investigation requires at least two competing hypotheses")
    register = _event_index(case_id, events)
    seen = set()
    cards = []
    for hypothesis in hypotheses:
        hypothesis.validate()
        if hypothesis.case_id != case_id:
            raise HypothesisError("hypothesis belongs to a different case")
        if hypothesis.hypothesis_id in seen:
            raise HypothesisError("duplicate hypothesis_id")
        seen.add(hypothesis.hypothesis_id)
        grouped = {key: [] for key in RELATIONS}
        for link in hypothesis.assessments:
            event = register.get(link.event_id)
            if event is None:
                raise HypothesisError(f"unknown evidence event: {link.event_id}")
            # An evidence gap is never support or contradiction. Likewise, a
            # within-limit screen does not prove a mechanism was absent.
            if event.kind == "evidence_gap" and link.relation != "unresolved":
                raise HypothesisError("evidence gaps may only be linked as unresolved")
            if event.kind == "screening_context" and link.relation in {"supports", "contradicts"}:
                raise HypothesisError("within-bound screen is context, not mechanism evidence")
            if event.kind == "screening_candidate" and link.relation in {"supports", "contradicts"}:
                # A limit-screen finding remains a prompt until a separately
                # reviewed engineer annotation provides an interpretation.
                raise HypothesisError("screening candidate needs independent interpretation")
            grouped[link.relation].append({
                "event_id": event.event_id,
                "kind": event.kind,
                "summary": event.summary,
                "source_ids": list(event.source_ids),
                "event_review_status": event.review_status,
                "assessment": asdict(link),
                "time_state": event.time_state,
                "timestamp": event.timestamp if event.time_state == "verified" else None,
            })
        if grouped["supports"] and grouped["contradicts"]:
            balance = "mixed_evidence_for_review"
        elif grouped["supports"]:
            balance = "support_reported_for_review"
        elif grouped["contradicts"]:
            balance = "contradiction_reported_for_review"
        else:
            balance = "insufficient_evidence"
        # Do not count multiple correlated samples or duplicated source
        # observations as independent votes.
        cards.append({
            "hypothesis_id": hypothesis.hypothesis_id,
            "title": hypothesis.title,
            "mechanism_question": hypothesis.mechanism_question,
            "stage": hypothesis.stage,
            "source_ref": hypothesis.source_ref,
            "review_status": hypothesis.review_status,
            "evidence_for": grouped["supports"],
            "evidence_against": grouped["contradicts"],
            "context": grouped["context"],
            "unknowns": grouped["unresolved"],
            "discriminating_checks": [asdict(c) for c in hypothesis.checks],
            "balance": balance,
            "independent_evidence_strength": "not_assessed",
        })
    return {
        "case_id": case_id,
        "mode": mode,
        "hypotheses": cards,
        "unlinked_event_ids": sorted(set(register) - {
            a.event_id for h in hypotheses for a in h.assessments
        }),
        "investigation_conclusion": "undetermined",
        "confirmed_failure_mechanism": None,
        "review_notice": (
            "Engineer-authored interpretations are review candidates, not causal proof. "
            "Screening prompts and correlated telemetry are not independent confirmation."
        ),
    }


def assess_case_from_dict(case_id: str, hypotheses: Sequence[Mapping],
                          events, *, mode="fault_investigation"):
    try:
        parsed = []
        for raw in hypotheses:
            payload = dict(raw)
            payload["assessments"] = tuple(
                EvidenceAssessment(**a) for a in payload.get("assessments", ()))
            payload["checks"] = tuple(
                DiscriminatingCheck(**c) for c in payload.get("checks", ()))
            parsed.append(Hypothesis(**payload))
        return assess_case(case_id, parsed, events, mode=mode)
    except (KeyError, TypeError) as error:
        raise HypothesisError(f"invalid hypothesis contract: {error}") from error
