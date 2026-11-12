"""LH-016: deterministic, draft-only retrospective engineering report.

Consumes existing case, evidence timeline and hypothesis outputs. Never infers
a physical failure, upgrades review flags or authorises a field operation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Mapping

class ReportError(ValueError):
    pass

def _require(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ReportError(f"{label}: non-empty text required")
    return value.strip()

def _text(value):
    return str(value).replace("\r", " ").replace("\n", " ").strip()

def _list(value, label):
    if not isinstance(value, (list, tuple)):
        raise ReportError(f"{label}: expected list")
    return value

def _event_index(case_id, timeline):
    if not isinstance(timeline, Mapping) or timeline.get("case_id") != case_id:
        raise ReportError("timeline case mismatch")
    records = _list(timeline.get("ordered_verified_events"), "verified events") + _list(
        timeline.get("unplaced_events"), "unplaced events")
    seen = {}
    for event in records:
        if not isinstance(event, Mapping) or event.get("case_id") != case_id:
            raise ReportError("event case mismatch")
        eid = _require(event.get("event_id"), "event ID")
        sources = _list(event.get("source_ids"), "source IDs")
        if not sources or any(not isinstance(s, str) or not s.strip() for s in sources):
            raise ReportError("each event requires real source references")
        if eid in seen:
            raise ReportError("duplicate event IDs")
        if event.get("time_state") != "verified" and event.get("timestamp") is not None:
            # A reported approximate time must never render as a verified event time.
            pass
        seen[eid] = event
    earliest = timeline.get("earliest_screening_candidate_id")
    if earliest is not None and (earliest not in seen or seen[earliest].get("kind") != "screening_candidate"
                                  or seen[earliest].get("time_state") != "verified"):
        raise ReportError("invalid earliest screening candidate")
    return records, seen

def compile_report(*, case_id: str, equipment: Mapping, timeline: Mapping,
                   hypothesis_review: Mapping, authored_by: str,
                   report_id: str, source_register: Mapping | None = None):
    """Return a portable JSON-compatible draft. Missing facts remain unavailable.

    `source_register` may supply descriptions, but it must not contain or
    imply authentication. Events always retain the original source IDs.
    """
    _require(case_id, "case ID")
    _require(report_id, "report ID")
    _require(authored_by, "draft author")
    if not isinstance(equipment, Mapping):
        raise ReportError("equipment section must be a mapping")
    if not isinstance(hypothesis_review, Mapping) or hypothesis_review.get("case_id") != case_id:
        raise ReportError("hypothesis review case mismatch")
    if hypothesis_review.get("investigation_conclusion") != "undetermined" or (
            hypothesis_review.get("confirmed_failure_mechanism") is not None):
        raise ReportError("automatic report cannot accept a confirmed mechanism or conclusion")
    mode = hypothesis_review.get("mode")
    if mode not in {"normal_operation_review", "fault_investigation"}:
        raise ReportError("invalid investigation mode")
    cards = _list(hypothesis_review.get("hypotheses"), "hypotheses")
    if mode == "fault_investigation" and len(cards) < 2:
        raise ReportError("fault investigation requires competing explanations")
    records, index = _event_index(case_id, timeline)
    for card in cards:
        if not isinstance(card, Mapping):
            raise ReportError("invalid hypothesis")
        for field in ("evidence_for", "evidence_against", "context", "unknowns"):
            for link in _list(card.get(field), field):
                event = index.get(link.get("event_id"))
                if event is None:
                    raise ReportError("hypothesis references an unknown event")
                # Never trust the denormalised copy over the original timeline.
                if set(link.get("source_ids", ())) != set(event["source_ids"]):
                    raise ReportError("hypothesis source references disagree with timeline")
                if event.get("kind") in {"screening_candidate", "screening_context", "evidence_gap"} and field in {
                        "evidence_for", "evidence_against"}:
                    raise ReportError("screening/gap event cannot prove a mechanism")
    candidates = [e for e in records if e.get("kind") == "screening_candidate"]
    gaps = [e for e in records if e.get("kind") == "evidence_gap"]
    unplaced = [e for e in records if e.get("time_state") != "verified"]
    if source_register is not None:
        if not isinstance(source_register, Mapping):
            raise ReportError("source register must be a mapping")
        for source_id in {s for record in records for s in record["source_ids"]}:
            if source_id not in source_register:
                raise ReportError(f"unregistered evidence source: {source_id}")
    return {
        "schema_version": "1.0",
        "report_id": report_id,
        "case_id": case_id,
        "status": "draft_unapproved",
        "authored_by": authored_by,
        "engineer_review": {
            "status": "not_completed", "reviewer": None,
            "reviewed_at": None, "signoff": None,
        },
        "scope": {"mode": mode, "equipment": dict(equipment),
                  "equipment_validation": "not_independently_verified"},
        "evidence_register": [
            {"event_id": e["event_id"], "kind": e["kind"],
             "summary": e["summary"], "source_ids": list(e["source_ids"]),
             "time_state": e["time_state"],
             "timestamp": e["timestamp"] if e["time_state"] == "verified" else None,
             "review_status": e["review_status"],
             "related_rule_id": e.get("related_rule_id"),
             "related_channel_id": e.get("related_channel_id"),
             "reasons": list(e.get("reasons", ()))}
            for e in records
        ],
        "chronology": {
            "ordered_event_ids": [e["event_id"] for e in timeline["ordered_verified_events"]],
            "unplaced_event_ids": [e["event_id"] for e in unplaced],
            "earliest_screening_candidate_id": timeline.get("earliest_screening_candidate_id"),
            "warning": timeline.get("chronology_warning", "Chronology incomplete"),
        },
        "screening_findings": [
            {"event_id": e["event_id"], "status": e.get("screening_status"),
             "related_rule_id": e.get("related_rule_id"), "source_ids": list(e["source_ids"])}
            for e in records if e.get("kind") in {
                "screening_candidate", "screening_context", "evidence_gap"}
        ],
        "competing_hypotheses": [
            {"hypothesis_id": card["hypothesis_id"], "title": card["title"],
             "mechanism_question": card["mechanism_question"],
             "balance": card["balance"], "review_status": card["review_status"],
             "evidence_for": [x["event_id"] for x in card["evidence_for"]],
             "evidence_against": [x["event_id"] for x in card["evidence_against"]],
             "context": [x["event_id"] for x in card["context"]],
             "unknowns": [x["event_id"] for x in card["unknowns"]],
             "discriminating_checks": list(card["discriminating_checks"])}
            for card in cards
        ],
        "evidence_gaps": {
            "unverifiable_event_ids": [e["event_id"] for e in gaps],
            "uncertain_time_event_ids": [e["event_id"] for e in unplaced],
            "unlinked_event_ids": list(hypothesis_review.get("unlinked_event_ids", ())),
        },
        "conclusion": {
            "status": "undetermined", "confirmed_failure_mechanism": None,
            "reason": "Insufficient independently verified and reviewed evidence to establish a cause or successful tool state.",
        },
        "limitations": [
            "Retrospective engineering draft only; not operational guidance or OEM certification.",
            "Numeric screening candidates are not verified deviations or proof of mechanism.",
            "Surface signals are not direct confirmation of downhole tool state.",
            "Document revisions, calibration, source rights and reviewer authority require independent checks.",
        ],
    }


def render_markdown(report: Mapping) -> str:
    """Human-readable text; never signs off, even if external input claims review."""
    if report.get("status") != "draft_unapproved" or report.get("conclusion", {}).get("status") != "undetermined":
        raise ReportError("only undetermined, unapproved draft reports may be rendered")
    lines = [
        f"# Retrospective Engineering Investigation — {_text(report['case_id'])}",
        "",
        f"**Report ID:** {_text(report['report_id'])}",
        "**Status:** DRAFT — NOT ENGINEER-APPROVED",
        f"**Draft author:** {_text(report['authored_by'])}",
        "**Engineering sign-off:** NOT COMPLETED",
        "",
        "## 1. Equipment and investigation scope",
        f"- Review mode: {_text(report['scope']['mode'])}",
        "- Equipment identity and configuration (as supplied, not independently verified):",
    ]
    equipment = report["scope"]["equipment"]
    if equipment:
        for key, value in equipment.items():
            lines.append(f"  - {_text(key)}: {_text(value) if value is not None else 'unavailable'}")
    else:
        lines.append("  - Unavailable — equipment detail not supplied")
    lines += ["", "## 2. Evidence register and operational chronology"]
    for e in report["evidence_register"]:
        when = e["timestamp"] if e["time_state"] == "verified" else "time unverified/unplaced"
        lines.append(f"- [{_text(e['event_id'])}] {_text(when)} — {_text(e['kind'])}: "
                     f"{_text(e['summary'])} (sources: {_text(', '.join(e['source_ids']))}; "
                     f"review: {_text(e['review_status'])})")
    lines += ["", "## 3. Screening findings and first candidate"]
    for f in report["screening_findings"]:
        lines.append(f"- [{_text(f['event_id'])}] {_text(f['status'])}; "
                     f"rule: {_text(f['related_rule_id'])}")
    earliest = report["chronology"]["earliest_screening_candidate_id"]
    lines.append(f"- Earliest eligible *screening candidate*: {_text(earliest) if earliest else 'none identified'}")
    lines.append(f"- {_text(report['chronology']['warning'])}")
    lines += ["", "## 4. Competing mechanisms and contradictory evidence"]
    if not report["competing_hypotheses"]:
        lines.append("- No failure mechanism inferred (normal-operation review).")
    for h in report["competing_hypotheses"]:
        lines += [
            f"### {_text(h['title'])} [{_text(h['hypothesis_id'])}]",
            f"- Question: {_text(h['mechanism_question'])}",
            f"- Organisational assessment: {_text(h['balance'])} (not a root-cause verdict)",
            f"- Evidence for: {_text(', '.join(h['evidence_for'])) or 'none'}",
            f"- Evidence against: {_text(', '.join(h['evidence_against'])) or 'none'}",
            f"- Context: {_text(', '.join(h['context'])) or 'none'}",
            f"- Unresolved: {_text(', '.join(h['unknowns'])) or 'none'}",
        ]
        for check in h["discriminating_checks"]:
            lines.append(f"- Further check: {_text(check['question'])} — "
                         f"required: {_text(check['required_evidence'])}")
    lines += ["", "## 5. Evidence gaps and limitations"]
    for name, ids in report["evidence_gaps"].items():
        lines.append(f"- {_text(name)}: {_text(', '.join(ids)) if ids else 'none recorded'}")
    for warning in report["limitations"]:
        lines.append(f"- {_text(warning)}")
    lines += [
        "", "## 6. Conclusion and engineering review",
        "**Conclusion: UNDETERMINED — no confirmed root cause or tool state.**",
        f"- {_text(report['conclusion']['reason'])}",
        "- Review/sign-off status: NOT COMPLETED.",
        "",
    ]
    return "\n".join(lines)
