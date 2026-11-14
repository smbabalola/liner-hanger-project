"""Portable, offline straight-section soft-string JSON entrypoint.

Example from skill root:
  python scripts/run_torque_drag.py examples/synthetic_torque_drag_straight.json

Never accept source labels or calculated outputs as OEM operating approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from planned_job_section import PlannedSectionError, SourcedNumber
from run_planned_section import from_payload
from torque_drag_straight import (
    StraightTorqueDragInputs, TorqueDragError, predict_straight_section,
    friction_sensitivity,
)

REQUIRED = {"planned_section", "axial_friction", "rotational_friction",
            "contact_radius", "bottom_tension"}


def run_payload(payload):
    if not isinstance(payload, dict) or set(payload) != REQUIRED:
        raise TorqueDragError("required fields: " + ", ".join(sorted(REQUIRED)))
    try:
        section = from_payload(payload["planned_section"])
        values = {}
        for key in sorted(REQUIRED - {"planned_section"}):
            if not isinstance(payload[key], dict):
                raise TorqueDragError(f"{key}: sourced object required")
            values[key] = SourcedNumber(**payload[key])
        return predict_straight_section(StraightTorqueDragInputs(section, **values))
    except (TypeError, KeyError, PlannedSectionError) as exc:
        raise TorqueDragError("invalid sourced torque/drag record") from exc


def main(argv=None):
    ap = argparse.ArgumentParser(description="Offline straight-section torque/drag, not operational approval")
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = run_payload(payload)
        text = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        return 0
    except (OSError, json.JSONDecodeError, TorqueDragError) as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
