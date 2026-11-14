"""Offline source-qualified experimental 3D soft-string single interval CLI."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from planned_job_section import SourcedNumber, PlannedSectionError
from run_planned_section import from_payload
from torque_drag_straight import TorqueDragError
from torque_drag_3d import SpatialCurveInputs, predict_spatial_curve

FIELDS = {"planned_section","axial_friction","rotational_friction",
          "contact_radius","bottom_tension","integration_steps"}
NUMBERS = {"axial_friction","rotational_friction","contact_radius","bottom_tension"}


def run_payload(data):
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise TorqueDragError("3D section: exact schema fields required")
    try:
        section = from_payload(data["planned_section"])
    except (TypeError, PlannedSectionError) as exc:
        raise TorqueDragError("invalid sourced planned section") from exc
    vals = {"section": section, "integration_steps": data["integration_steps"]}
    for name in NUMBERS:
        if not isinstance(data[name], dict):
            raise TorqueDragError(f"{name}: sourced number object required")
        try:
            vals[name] = SourcedNumber(**data[name])
        except (TypeError, KeyError) as exc:
            raise TorqueDragError(f"{name}: incomplete sourced number") from exc
    return predict_spatial_curve(SpatialCurveInputs(**vals))


def main(argv=None):
    p = argparse.ArgumentParser(description="Experimental 3D soft-string interval (NOT field use)")
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args(argv)
    try:
        outcome = run_payload(json.loads(a.input.read_text(encoding="utf-8")))
        out = json.dumps(outcome, indent=2, allow_nan=False)+"\n"
        if a.output:
            a.output.write_text(out,encoding="utf-8")
        else:
            sys.stdout.write(out)
        return 0
    except (OSError, json.JSONDecodeError, TorqueDragError) as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
