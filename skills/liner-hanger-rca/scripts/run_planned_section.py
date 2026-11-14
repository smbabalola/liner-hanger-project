"""Run one sourced, uniform synthetic/planned section offline.

Example (from skill root):
  python scripts/run_planned_section.py examples/synthetic_planned_section.json

Output is JSON on stdout. No confidential file uploads or OEM approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from directional_survey import SurveyStation
from planned_job_section import PlannedSection, PlannedSectionError, SourcedNumber


NUMERIC = (
    "first_station_tvd", "top_md", "bottom_md", "bore_diameter",
    "pipe_outer_diameter", "pipe_inner_diameter",
    "dry_linear_mass", "fluid_density",
)
REQUIRED = set(PlannedSection.__dataclass_fields__)


def from_payload(raw):
    """Strictly map a JSON object to the sourced single-section contract."""
    if not isinstance(raw, dict):
        raise PlannedSectionError("job section must be a JSON object")
    missing, extra = REQUIRED - set(raw), set(raw) - REQUIRED
    if missing or extra:
        raise PlannedSectionError(
            "invalid top-level job fields; missing="
            + ",".join(sorted(missing)) + "; unknown=" + ",".join(sorted(extra))
        )
    converted = dict(raw)
    try:
        for key in NUMERIC:
            if not isinstance(raw[key], dict):
                raise PlannedSectionError(f"{key}: sourced object required")
            converted[key] = SourcedNumber(**raw[key])
        if not isinstance(raw["survey_stations"], list):
            raise PlannedSectionError("survey_stations: JSON list required")
        converted["survey_stations"] = tuple(
            SurveyStation(**row) for row in raw["survey_stations"]
        )
        section = PlannedSection(**converted)
        section.validate()
        return section
    except (TypeError, KeyError, AttributeError) as exc:
        raise PlannedSectionError("invalid section record structure") from exc


def run_payload(raw):
    return from_payload(raw).calculate()


def main(argv=None):
    parser = argparse.ArgumentParser(description="One sourced, planned section; offline statics only")
    parser.add_argument("input", type=Path, help="JSON planned-section record")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args(argv)
    try:
        with args.input.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        result = run_payload(payload)
        output = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output is None:
            sys.stdout.write(output)
        else:
            args.output.write_text(output, encoding="utf-8")
        return 0
    except (OSError, json.JSONDecodeError, PlannedSectionError) as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
