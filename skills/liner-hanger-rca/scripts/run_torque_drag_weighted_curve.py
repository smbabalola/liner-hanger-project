"""Run one uniform, planar, weighted soft-string curved interval offline.

Usage: python scripts/run_torque_drag_weighted_curve.py
           examples/synthetic_torque_drag_weighted_curve.json
Research-level model, not an operating recommendation or approved OEM limit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from planned_job_section import SourcedNumber, PlannedSectionError
from run_planned_section import from_payload
from torque_drag_straight import TorqueDragError
from torque_drag_weighted_curve import WeightedCurveInputs, predict_weighted_curve

FIELDS = {"planned_section", "axial_friction", "rotational_friction",
          "contact_radius", "bottom_tension", "integration_steps"}
SOURCED = {"axial_friction", "rotational_friction", "contact_radius", "bottom_tension"}


def run_payload(raw):
    if not isinstance(raw, dict) or set(raw) != FIELDS:
        raise TorqueDragError("weighted curve: exact required schema fields missing or unexpected")
    try:
        section = from_payload(raw["planned_section"])
    except PlannedSectionError as exc:
        raise TorqueDragError("invalid sourced planned section") from exc
    values = {"section": section, "integration_steps": raw["integration_steps"]}
    for field in SOURCED:
        record = raw[field]
        if not isinstance(record, dict):
            raise TorqueDragError(f"{field}: sourced input record required")
        try:
            values[field] = SourcedNumber(**record)
        except (TypeError, KeyError) as exc:
            raise TorqueDragError(f"{field}: invalid sourced record") from exc
    return predict_weighted_curve(WeightedCurveInputs(**values))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Planar weighted soft-string arc, research only")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = run_payload(data)
        rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (OSError, json.JSONDecodeError, TorqueDragError) as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
