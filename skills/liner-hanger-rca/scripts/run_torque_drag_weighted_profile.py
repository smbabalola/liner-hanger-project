"""Strict offline JSON runner for contiguous weighted planar profile (research).

python scripts/run_torque_drag_weighted_profile.py examples/synthetic_torque_drag_weighted_profile.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from planned_job_section import SourcedNumber, PlannedSectionError
from run_planned_section import from_payload
from torque_drag_straight import TorqueDragError
from torque_drag_weighted_profile import (
    WeightedPlanarProfile, WeightedProfileInterval, predict_weighted_planar_profile,
)

ROOT_FIELDS = {"intervals_top_to_bottom", "bottom_tension"}
INTERVAL_FIELDS = {"planned_section", "axial_friction", "rotational_friction",
                   "contact_radius", "integration_steps"}
SOURCE_FIELDS = {"axial_friction", "rotational_friction", "contact_radius"}


def _source(value, field):
    if not isinstance(value, dict):
        raise TorqueDragError(f"{field}: sourced input object required")
    try:
        return SourcedNumber(**value)
    except (TypeError, KeyError) as exc:
        raise TorqueDragError(f"{field}: invalid source record") from exc


def run_payload(payload):
    if not isinstance(payload, dict) or set(payload) != ROOT_FIELDS:
        raise TorqueDragError("weighted profile: exact fields required")
    sections = payload["intervals_top_to_bottom"]
    if not isinstance(sections, list) or not sections:
        raise TorqueDragError("nonempty intervals_top_to_bottom list required")
    prepared = []
    for index, row in enumerate(sections):
        if not isinstance(row, dict) or set(row) != INTERVAL_FIELDS:
            raise TorqueDragError(f"interval {index}: exact fields required")
        try:
            planned = from_payload(row["planned_section"])
        except (PlannedSectionError, TypeError) as exc:
            raise TorqueDragError(f"interval {index}: invalid source section") from exc
        arguments = {name: _source(row[name], f"interval {index} {name}")
                     for name in SOURCE_FIELDS}
        prepared.append(WeightedProfileInterval(
            section=planned, integration_steps=row["integration_steps"], **arguments))
    return predict_weighted_planar_profile(WeightedPlanarProfile(
        intervals_top_to_bottom=tuple(prepared),
        bottom_tension=_source(payload["bottom_tension"], "bottom_tension"),
    ))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Research-only weighted planar profile")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_payload(json.loads(args.input.read_text(encoding="utf-8")))
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
