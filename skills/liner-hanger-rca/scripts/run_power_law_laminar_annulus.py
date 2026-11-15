"""Strict offline JSON runner for bounded laminar power-law concentric annulus."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from circulating_hydraulics import FlowSegment, HydraulicsUnavailable
from power_law_laminar_pipe import PowerLawFluid
from power_law_laminar_annulus import power_law_laminar_annulus_pressure_loss

TOP={"fluid","segment","flow_m3_s",
     "laminar_regime_independently_confirmed","regime_evidence_id"}
FLUID={"density_kg_m3","consistency_pa_s_n","flow_behavior_index","rheology"}
SEGMENT={"name","kind","length_m","outer_diameter_m","inner_diameter_m","flow_leg"}


def run_payload(payload):
    if not isinstance(payload,dict) or set(payload)!=TOP:
        raise HydraulicsUnavailable("exact power-law annulus schema required")
    if not isinstance(payload["fluid"],dict) or set(payload["fluid"])!=FLUID:
        raise HydraulicsUnavailable("exact power-law fluid fields required")
    if not isinstance(payload["segment"],dict) or set(payload["segment"])!=SEGMENT:
        raise HydraulicsUnavailable("exact annulus geometry fields required")
    try:
        fluid=PowerLawFluid(**payload["fluid"])
        section=FlowSegment(**payload["segment"])
    except TypeError as exc:
        raise HydraulicsUnavailable("invalid typed power-law annulus inputs") from exc
    return power_law_laminar_annulus_pressure_loss(
        fluid,section,payload["flow_m3_s"],
        laminar_regime_independently_confirmed=payload[
            "laminar_regime_independently_confirmed"],
        regime_evidence_id=payload["regime_evidence_id"])


def main(argv=None):
    parser=argparse.ArgumentParser(
        description="Research-only power-law concentric laminar annulus, NOT rig SPP")
    parser.add_argument("input",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args(argv)
    try:
        result=run_payload(json.loads(args.input.read_text(encoding="utf-8")))
        encoded=json.dumps(result,indent=2,allow_nan=False)+"\n"
        if args.output:
            args.output.write_text(encoded,encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        return 0
    except (OSError,ValueError,HydraulicsUnavailable) as exc:
        print(f"unavailable: {exc}",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
