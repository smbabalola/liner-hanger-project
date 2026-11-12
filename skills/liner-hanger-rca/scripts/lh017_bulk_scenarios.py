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
        samples = c.get("surface_samples")
        if not isinstance(samples, list) or len(samples) != 6:
            raise BatchError("each case needs six typed synthetic surface samples")
        if len({(x["source_id"], x["source_row"]) for x in samples}) != 6:
            raise BatchError("duplicate sample source and row")
        if len({x["source_id"] for x in samples}) != 2:
            raise BatchError("each case needs two distinct surface channels")
        if len(c.get("assessment_rationales", [])) != 2 or len(c.get("required_evidence", [])) != 2:
            raise BatchError("family-specific rationale/evidence missing")
        for sample in samples:
            if not sample["source_id"].startswith("SYNTHETIC-") or not sample["channel_id"]:
                raise BatchError("sample source identity missing")
            if not isinstance(sample["value"], (int, float)) or isinstance(sample["value"], bool):
                raise BatchError("synthetic sample numeric value required")
            if not sample["unit"] or not sample["domain"] or not sample["source_revision"]:
                raise BatchError("sample units, domain and revision required")
            if sample["clock_verified"] != c["clock_verified"]:
                raise BatchError("sample clock quality inconsistent with case")

    return cases

def run_case(case):
    """Return draft and diagnostic packets; no field advice or success verdict."""
    case_id = case["case_id"]
    kind = case["scenario_class"]
    if case["identity"]["manufacturer_id"] != "baker_hughes":
        raise BatchError("case manufacturer not enabled")
    if case["identity"]["documentation_status"] != "mechanism_described_only":
        raise BatchError("source-gate status mismatch")
    if any(case["identity"][field] is not None for field in ("model", "size", "revision", "configuration_id")):
        raise BatchError("synthetic case cannot claim an approved OEM configuration")
    if not case["observation_source_id"].startswith("SYNTHETIC-"):
        raise BatchError("synthetic case requires synthetic source identity")
    if kind not in KINDS:
        raise BatchError("invalid scenario class")
    if kind == "ambiguous" and case["clock_verified"]:
        raise BatchError("ambiguous synthetic case cannot claim verified alignment")
    if kind != "ambiguous" and not case["clock_verified"]:
        raise BatchError("case requires verified fixture clock")
    samples = case.get("surface_samples")
    if not isinstance(samples, list) or len(samples) != 6:
        raise BatchError("six typed samples required for case")
    events = []
    for n, sample in enumerate(samples):
        if sample["clock_verified"] != case["clock_verified"]:
            raise BatchError("sample clock quality inconsistent with case")
        if not sample["source_id"].startswith("SYNTHETIC-"):
            raise BatchError("non-synthetic sample rejected")
        if not isinstance(sample["value"], (int, float)) or isinstance(sample["value"], bool):
            raise BatchError("sample must have a numeric recorded value")
        usable = (sample["clock_verified"] and sample["channel_mapping_verified"]
                  and sample["units_verified"])
        if usable != (kind != "ambiguous"):
            raise BatchError("case quality state does not match sample provenance")
        event = timeline_engine.EvidenceEvent(
            event_id=case_id + "-S" + str(n+1), case_id=case_id,
            kind="measured_observation" if usable else "evidence_gap",
            summary=("Synthetic recorded " if usable else "Unverified raw synthetic source record for ")
                    + sample["parameter"] + "; no tool-state inference",
            source_ids=(sample["source_id"],),
            time_state="verified" if usable else "unknown",
            timestamp=sample["source_sample_time"] if usable else None,
            source_sample_time=sample["source_sample_time"],
            time_basis="Fictional aligned UTC source clocks" if usable else None,
            related_channel_id=sample["channel_id"],
            reasons=() if usable else ("source clock, channel identity and units not independently verified",),
            source_locations={sample["source_id"]: {
                "channel":sample["channel_id"], "location":"fictional CSV row " + str(sample["source_row"]),
                "revision":sample["source_revision"]}},
            measurement_details={
                "parameter":sample["parameter"], "value":str(sample["value"]),
                "unit":sample["unit"], "domain":sample["domain"],
                "basis":sample["basis"],
                "provenance":"fictional-aligned-sample" if usable else "unverified-raw-sample",
            },
        ).validate()
        events.append(event)
    reported = timeline_engine.EvidenceEvent(
        event_id=case_id + "-DAILY", case_id=case_id, kind="reported_event",
        summary=case["reported_log_summary"],
        source_ids=("SYNTHETIC-DAILY-LOG",), time_state="reported_approximate",
        time_basis="Date only — cannot position among verified events",
    ).validate()
    events.append(reported)
    if kind == "anomalous":
        events.append(timeline_engine.EvidenceEvent(
            event_id=case_id + "-ALTERNATIVE", case_id=case_id,
            kind="engineer_annotation",
            summary="Synthetic competing interpretation: " + case["assessment_rationales"][1],
            source_ids=(samples[0]["source_id"], samples[1]["source_id"],
                        "SYNTHETIC-ASSESSMENT-NOTE"),
            time_state="reported_approximate", timestamp=None,
            time_basis="Assessor annotation time not independently established",
        ).validate())
    hypotheses = []
    if kind != "normal":
        for i, question in enumerate(case["hypothesis_questions"]):
            assessments = []
            if kind == "anomalous":
                # These are context links. No supported mechanism or contradiction
                # can be established without authorised tool-specific evidence.
                assessments.append(hypothesis_engine.EvidenceAssessment(
                    event_id=events[2+i].event_id, relation="context",
                    rationale=case["assessment_rationales"][i],
                    assessor="synthetic assessor", review_status="draft"))
                assessments.append(hypothesis_engine.EvidenceAssessment(
                    event_id=reported.event_id, relation="unresolved",
                    rationale="Job note is date-only and cannot prove the claimed mechanism",
                    assessor="synthetic assessor", review_status="draft"))
            else:
                assessments.append(hypothesis_engine.EvidenceAssessment(
                    event_id=events[i].event_id, relation="unresolved",
                    rationale=case["assessment_rationales"][i]
                    + " Clock, mapping and unit provenance is not verified.",
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
                    required_evidence=case["required_evidence"][i]),),
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
            "surface_sample_count":sum(
                e["measurement_details"] is not None for e in report["evidence_register"]),
            "verified_event_count":len(report["chronology"]["ordered_event_ids"]),
            "unplaced_event_count":len(report["chronology"]["unplaced_event_ids"]),
            "screening_rules_evaluated":len(report["screening_findings"]),
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
