"""LH-017 fifteen-case synthetic retrospective validation adapter.

Uses the existing evidence timeline, hypotheses and report engines. It contains
NO OEM limits, physical diagnostic model or real well data. Development only.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FIXTURES = SKILL / "tests" / "fixtures" / "lh017_bulk_synthetic_cases.json"

def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

timeline_engine = _load("evidence_timeline", SKILL / "scripts" / "evidence_timeline.py")
hypothesis_engine = _load("hypothesis_review", SKILL / "scripts" / "hypothesis_review.py")
report_engine = _load("investigation_report", SKILL / "scripts" / "investigation_report.py")
KINDS = ("normal", "anomalous", "ambiguous")
FAMILIES = ("ball-seat", "hanger-setting", "running-tool", "cementing", "liner-packer")

class BatchError(ValueError):
    pass

def load_cases():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if "ENTIRELY SYNTHETIC" not in data.get("disclaimer", ""):
        raise BatchError("fixture lacks mandatory synthetic-only disclaimer")
    cases = data["cases"]
    expected = {(family, kind) for family in FAMILIES for kind in KINDS}
    actual = [(c["family_id"], c["scenario_class"]) for c in cases]
    if len(cases) != 15 or len(set(actual)) != 15 or set(actual) != expected:
        raise BatchError("LH-017 fixture must cover each of the five families and three classes exactly once")
    if len({c["case_id"] for c in cases}) != 15:
        raise BatchError("duplicate case IDs")
    for c in cases:
        ident = c["identity"]
        if ident["manufacturer_id"] != "baker_hughes" or ident["documentation_status"] != "mechanism_described_only":
            raise BatchError("unapproved manufacturer or documentation state")
        if any(ident[field] is not None for field in ("model", "size", "revision", "configuration_id")):
            raise BatchError("this synthetic batch must not imply a supported OEM tool")
        if len(c["hypothesis_questions"]) != 2 or len(c["discriminating_checks"]) != 2:
            raise BatchError("each scenario needs two distinct possible mechanisms and checks")
        if c["hypothesis_questions"][0] == c["hypothesis_questions"][1]:
            raise BatchError("hypotheses must differ")
        if not c["observation_source_id"].startswith("SYNTHETIC-"):
            raise BatchError("unexpected synthetic observation source")
    return cases

def run_case(case):
    """Return draft and diagnostic packets; no field advice or success verdict."""
    case_id = case["case_id"]
    kind = case["scenario_class"]
    if case["identity"]["manufacturer_id"] != "baker_hughes":
        raise BatchError("case manufacturer not enabled")
    if case["identity"]["documentation_status"] != "mechanism_described_only":
        raise BatchError("source-gate status mismatch")
    if kind not in KINDS:
        raise BatchError("invalid scenario class")
    if kind == "ambiguous" and case["clock_verified"]:
        raise BatchError("ambiguous synthetic case cannot claim verified alignment")
    if kind != "ambiguous" and not case["clock_verified"]:
        raise BatchError("case requires verified fixture clock")
    base = timeline_engine.EvidenceEvent(
        event_id=case_id + "-SURFACE", case_id=case_id,
        kind="evidence_gap" if kind == "ambiguous" else "measured_observation",
        summary=case["observed_surface_summary"],
        source_ids=(case["observation_source_id"],),
        time_state="unknown" if kind == "ambiguous" else "verified",
        timestamp=None if kind == "ambiguous" else "2026-01-01T08:10:00Z",
        source_sample_time="2026-01-01T08:10:00Z",
        time_basis=None if kind == "ambiguous" else "Synthetic offset-aware clock, fictional alignment flag",
        related_channel_id=case["observed_channel"],
        reasons=("source/channel identity and event timing unverified",) if kind == "ambiguous" else (),
        source_locations={case["observation_source_id"]: {
            "channel":case["observed_channel"], "location":None, "revision":None,
        }},
    ).validate()
    reported = timeline_engine.EvidenceEvent(
        event_id=case_id + "-DAILY", case_id=case_id, kind="reported_event",
        summary=case["reported_log_summary"],
        source_ids=("SYNTHETIC-DAILY-LOG",), time_state="reported_approximate",
        time_basis="Date only — cannot position among verified events",
    ).validate()
    events = [base, reported]
    if kind == "anomalous":
        events.append(timeline_engine.EvidenceEvent(
            event_id=case_id + "-ALTERNATIVE", case_id=case_id,
            kind="engineer_annotation",
            summary="Fictional assessor flags an alternative surface-data interpretation; no physical state inferred",
            source_ids=(case["observation_source_id"], "SYNTHETIC-ASSESSMENT-NOTE"),
            time_state="verified", timestamp="2026-01-01T08:10:00Z",
            time_basis="Synthetic same-clock tie; order cannot be inferred",
        ).validate())
    hypotheses = []
    if kind != "normal":
        for i, question in enumerate(case["hypothesis_questions"]):
            assessments = []
            if kind == "anomalous":
                assessments.append(hypothesis_engine.EvidenceAssessment(
                    event_id=base.event_id,
                    relation="supports" if i == 0 else "contradicts",
                    rationale="Fictional assessor requests correlation; surface signal alone does not prove or disprove this mechanism",
                    assessor="synthetic assessor", review_status="draft"))
                assessments.append(hypothesis_engine.EvidenceAssessment(
                    event_id=events[2].event_id, relation="context",
                    rationale="Alternative interpretation has not been independently verified",
                    assessor="synthetic assessor", review_status="draft"))
            else:
                assessments.append(hypothesis_engine.EvidenceAssessment(
                    event_id=base.event_id, relation="unresolved",
                    rationale="Source and clock provenance insufficient to distinguish this mechanism",
                    assessor="synthetic assessor", review_status="draft"))
            hypotheses.append(hypothesis_engine.Hypothesis(
                hypothesis_id=case_id + "-H" + str(i+1),
                case_id=case_id, title=question,
                mechanism_question="Could " + question.lower() + " explain this reported stage response?",
                stage=case["stage"],
                source_ref="SYNTHETIC-MECHANISM-QUESTIONS",
                assessments=tuple(assessments),
                checks=(hypothesis_engine.DiscriminatingCheck(
                    check_id=case_id + "-CHECK" + str(i+1),
                    question=case["discriminating_checks"][i] + "?",
                    required_evidence="Historical source records and exact as-run configuration, where available"),),
            ))
    mode = "normal_operation_review" if kind == "normal" else "fault_investigation"
    ordered = timeline_engine.build_timeline(case_id, events)
    review = hypothesis_engine.assess_case(case_id, hypotheses, events, mode=mode)
    equipment = {
        **case["identity"],
        "investigation_family":case["family"],
        "stage":case["stage"],
        "scenario_class":kind,
        "approved_procedure":None,
        "original_source_basis":case["source_basis"],
    }
    sources = {s: {"synthetic":True} for event in events for s in event.source_ids}
    draft = report_engine.compile_report(
        case_id=case_id, report_id="SYNTHETIC-LH017-" + case_id,
        authored_by="LH-017 synthetic fixture adapter",
        equipment=equipment, timeline=ordered, hypothesis_review=review,
        source_register=sources)
    return {"case":case, "events":events, "timeline":ordered,
            "hypotheses":review, "report":draft}

def export_batch(output_dir):
    """30 report files plus a manifest; output files are NOT for Git commit."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version":"1.0", "status":"synthetic_only_unapproved",
                "cases":[], "limitations":[
                "Not an OEM performance validation or real failure diagnosis.",
                "No approved Baker Hughes model/size/revision rules or ratings.",
                "Synthetic assessor rationale is not independent engineering signoff."]}
    for case in load_cases():
        run = run_case(case)
        report = run["report"]
        stem = case["case_id"].lower()
        (output_dir / (stem + ".json")).write_text(
            json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
        (output_dir / (stem + ".md")).write_text(
            report_engine.render_markdown(report), encoding="utf-8")
        manifest["cases"].append({
            "case_id":case["case_id"], "family":case["family_id"],
            "class":case["scenario_class"], "status":report["status"],
            "conclusion":report["conclusion"]["status"],
            "hypothesis_count":len(report["competing_hypotheses"]),
            "source_ids":sorted({s for e in report["evidence_register"] for s in e["source_ids"]}),
            "review_status":"not_completed",
            "documentation_status":"mechanism_described_only",
        })
    (output_dir / "validation-manifest.json").write_text(
        json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(SKILL / "reports" / "lh017-bulk"))
    args = parser.parse_args()
    manifest = export_batch(args.output_dir)
    print("Generated", len(manifest["cases"]), "synthetic draft report pairs and a validation manifest")
