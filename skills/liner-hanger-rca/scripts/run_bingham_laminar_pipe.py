"""Offline strict JSON runner for *restricted* Bingham-plastic laminar pipe friction.

Input is a research-only calculation with an independently obtained
flow-regime evidence identifier. The script never computes rig SPP.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bingham_laminar_pipe import BinghamFluid, bingham_pipe_laminar_pressure_loss
from circulating_hydraulics import FlowSegment, HydraulicsUnavailable

TOP = {"fluid", "segment", "flow_m3_s",
       "laminar_regime_independently_confirmed", "regime_evidence_id"}
FLUID = {"density_kg_m3", "plastic_viscosity_pa_s", "yield_stress_pa", "rheology"}
SEGMENT = {"name", "kind", "length_m", "outer_diameter_m",
           "inner_diameter_m", "flow_leg"}


def run_payload(payload):
    if not isinstance(payload, dict) or set(payload) != TOP:
        raise HydraulicsUnavailable("exact Bingham pipe schema required")
    raw_fluid, raw_section = payload["fluid"], payload["segment"]
    if not isinstance(raw_fluid, dict) or set(raw_fluid) != FLUID:
        raise HydraulicsUnavailable("exact Bingham fluid schema required")
    if not isinstance(raw_section, dict) or set(raw_section) != SEGMENT:
        raise HydraulicsUnavailable("exact Bingham pipe schema required")
    evidence = payload["regime_evidence_id"]
    if not isinstance(evidence, str) or not evidence.strip() or len(evidence) > 256:
        raise HydraulicsUnavailable("nonempty source reference for laminar regime required")
    try:
        fluid = BinghamFluid(**raw_fluid)
        section = FlowSegment(**raw_section)
    except TypeError as exc:
        raise HydraulicsUnavailable("invalid Bingham pipe field type") from exc
    result = bingham_pipe_laminar_pressure_loss(
        fluid, section, payload["flow_m3_s"],
        laminar_regime_independently_confirmed=(
            payload["laminar_regime_independently_confirmed"]
        ),
    )
    result["regime_evidence_id"] = evidence
    result["flow_regime_evidence"] = "caller_declared_requires_independent_review"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Research-only Bingham laminar pipe, never rig SPP")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_payload(json.loads(args.input.read_text(encoding="utf-8")))
        encoded = json.dumps(result, indent=2, allow_nan=False)+"\n"
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
