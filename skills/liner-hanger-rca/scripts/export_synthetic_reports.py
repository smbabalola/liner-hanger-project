"""Export LH-003 synthetic investigations to JSON and Markdown for LH-016 review.

Development-only adapter deliberately reuses the TEST scenario runner; this is
not a production job-package reader or a real-well evidence ingestion pipeline.
Usage (from skill root): py scripts/export_synthetic_reports.py --output-dir reports/synthetic
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TEST_DIR = SKILL / "tests"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def generate(output_dir):
    # This is a controlled fixture adapter, NOT a production dependency.
    scenarios = load("lh003_scenario_export_adapter", TEST_DIR / "test_lh003_scenarios.py")
    reports = load("investigation_report", SKILL / "scripts" / "investigation_report.py")
    cases = json.loads((TEST_DIR / "fixtures" / "lh003_synthetic_cases.json").read_text(encoding="utf-8"))["cases"]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for case in cases:
        result = scenarios.exercise(case)
        record = reports.compile_report(
            case_id=case["case_id"],
            report_id="SYNTHETIC-REPORT-" + case["case_id"],
            authored_by="synthetic fixture runner",
            equipment={
                "manufacturer_id": "baker_hughes",
                "manufacturer_identity_basis": "synthetic only — not genuine OEM tool identification",
                "tool_model": "SYNTHETIC-MODEL",
                "tool_revision": "fictional-revision",
                "tally_basis": result["tally"].basis,
                "tally_anchor_datum": result["tally"].anchor.datum,
                "nominal_internal_reference_md_m":
                    str(result["internal_md"]) if result["internal_md"] is not None else None,
                "geometry_source": "SYNTHETIC-TALLY; SYNTHETIC-DRAWING",
                "approved_job_procedure": None,
            },
            timeline=result["timeline"],
            hypothesis_review=result["assessment"])
        base = case["case_id"].lower()
        json_path = output_dir / (base + ".json")
        md_path = output_dir / (base + ".md")
        json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path.write_text(reports.render_markdown(record), encoding="utf-8")
        written.extend([json_path, md_path])
    return written

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(SKILL / "reports" / "synthetic"))
    args = parser.parse_args()
    for file in generate(args.output_dir):
        print("Wrote", file)
