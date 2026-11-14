"""Offline JSON interface for contiguous co-linear straight multi-section model.

From skill root:
    python scripts/run_torque_drag_profile.py examples/synthetic_torque_drag_profile.json
All input values are case-specific and explicitly source-labelled.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from planned_job_section import SourcedNumber, PlannedSectionError
from run_planned_section import from_payload
from torque_drag_profile import (
    ProfileInterval, StraightProfile, predict_straight_profile,
)
from torque_drag_straight import TorqueDragError

TOP_FIELDS = {"intervals_top_to_bottom", "bottom_tension"}
ROW_FIELDS = {"section", "axial_friction", "rotational_friction", "contact_radius"}
FRICTION_FIELDS = {"axial_friction", "rotational_friction", "contact_radius"}


def _number(raw, name):
    if not isinstance(raw, dict):
        raise TorqueDragError(f"{name}: source-labelled value object required")
    try:
        return SourcedNumber(**raw)
    except (TypeError, KeyError) as exc:
        raise TorqueDragError(f"{name}: invalid sourced value schema") from exc


def run_payload(raw):
    if not isinstance(raw, dict) or set(raw) != TOP_FIELDS:
        raise TorqueDragError("invalid profile fields; require intervals_top_to_bottom and bottom_tension")
    sections = raw["intervals_top_to_bottom"]
    if not isinstance(sections, list) or not sections:
        raise TorqueDragError("intervals_top_to_bottom must be a nonempty JSON list")
    intervals = []
    for i, row in enumerate(sections):
        if not isinstance(row, dict) or set(row) != ROW_FIELDS:
            raise TorqueDragError(f"section {i}: invalid record fields")
        try:
            section = from_payload(row["section"])
        except PlannedSectionError as exc:
            raise TorqueDragError(f"section {i}: invalid plan: {exc}") from exc
        values = {name: _number(row[name], f"section {i} {name}") for name in FRICTION_FIELDS}
        intervals.append(ProfileInterval(section, **values))
    tension = _number(raw["bottom_tension"], "bottom_tension")
    return predict_straight_profile(StraightProfile(tuple(intervals), tension))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline co-linear straight profile (not a curved well model)")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = run_payload(payload)
        output = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except (OSError, json.JSONDecodeError, TorqueDragError) as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
