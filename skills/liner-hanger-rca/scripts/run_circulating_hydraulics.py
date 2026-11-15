"""Strict offline JSON entry point for restricted LH-CALC-03 hydraulics.

Example:
python scripts/run_circulating_hydraulics.py examples/synthetic_laminar_circuit.json
No standpipe pressure is calculated by this restricted model.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from circulating_hydraulics import (
    FlowSegment, HydraulicsUnavailable, NewtonianFluid, circulation_friction
)

FLUID_FIELDS = {"density_kg_m3", "dynamic_viscosity_pa_s", "rheology"}
SEGMENT_FIELDS = {
    "name", "kind", "length_m", "outer_diameter_m",
    "inner_diameter_m", "flow_leg"
}


def run_payload(payload):
    if not isinstance(payload, dict) or set(payload) != {
        "fluid", "flow_m3_s", "segments"
    }:
        raise HydraulicsUnavailable("exact top-level fields required")
    raw_fluid = payload["fluid"]
    if not isinstance(raw_fluid, dict) or set(raw_fluid) != FLUID_FIELDS:
        raise HydraulicsUnavailable("exact fluid fields required")
    raw_segments = payload["segments"]
    if not isinstance(raw_segments, list) or not raw_segments:
        raise HydraulicsUnavailable("nonempty segment list required")
    if any(not isinstance(s, dict) or set(s) != SEGMENT_FIELDS
           for s in raw_segments):
        raise HydraulicsUnavailable("exact segment fields required")
    try:
        fluid = NewtonianFluid(**raw_fluid)
        segments = [FlowSegment(**s) for s in raw_segments]
    except TypeError as exc:
        raise HydraulicsUnavailable("invalid typed hydraulics input") from exc
    return circulation_friction(fluid, segments, payload["flow_m3_s"])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Restricted Newtonian laminar friction, NOT standpipe pressure"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_payload(json.loads(args.input.read_text(encoding="utf-8")))
        encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        return 0
    except (OSError, ValueError, HydraulicsUnavailable) as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
