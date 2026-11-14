"""Offline CLI for experimental minimum-curvature 3D torque/drag calculation.

The CLI does not replace the legacy linear-angle 3D runner or approve
operational loads. Input is a strict sourced single-section JSON object.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from planned_job_section import SourcedNumber, PlannedSectionError
from run_planned_section import from_payload
from torque_drag_3d import SpatialCurveInputs
from torque_drag_3d_minimum_curvature import predict_minimum_curvature_curve
from torque_drag_straight import TorqueDragError


FIELDS={"planned_section","axial_friction","rotational_friction",
        "contact_radius","bottom_tension","integration_steps"}
SOURCED=("axial_friction","rotational_friction","contact_radius","bottom_tension")


def run_payload(raw):
    if not isinstance(raw,dict) or set(raw)!=FIELDS:
        raise TorqueDragError("minimum-curvature 3D interval exact schema required")
    try:
        section=from_payload(raw["planned_section"])
    except (TypeError,PlannedSectionError) as exc:
        raise TorqueDragError(f"invalid planned survey/section: {exc}") from exc
    sources={}
    for key in SOURCED:
        if not isinstance(raw[key],dict):
            raise TorqueDragError(f"{key}: source record required")
        try:
            sources[key]=SourcedNumber(**raw[key])
        except (TypeError,KeyError) as exc:
            raise TorqueDragError(f"{key}: malformed source record") from exc
    return predict_minimum_curvature_curve(SpatialCurveInputs(
        section=section,integration_steps=raw["integration_steps"],**sources))


def main(argv=None):
    p=argparse.ArgumentParser(description="Research-only minimum-curvature 3D soft-string")
    p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args(argv)
    try:
        result=run_payload(json.loads(a.input.read_text(encoding="utf-8")))
        message=json.dumps(result,indent=2,allow_nan=False)+"\n"
        if a.output:
            a.output.write_text(message,encoding="utf-8")
        else:
            sys.stdout.write(message)
        return 0
    except (OSError,json.JSONDecodeError,TorqueDragError) as exc:
        print(f"unavailable: {exc}",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
