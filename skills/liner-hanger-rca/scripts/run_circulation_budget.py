"""Strict offline fictional Newtonian pipe/annulus/nozzle component budget.

No interpretation as rig standpipe pressure or OEM tool qualification.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from circulation_budget import CircuitComponent, partial_circulation_budget
from circulating_hydraulics import (
    NewtonianFluid, FlowSegment, HydraulicsUnavailable)
from circulation_restrictions import NozzleOrifice

TOP = {"fluid","flow_m3_s","components_in_flow_order"}
FLUID = {"density_kg_m3","dynamic_viscosity_pa_s","rheology"}
PIPE = {"type","name","kind","length_m","outer_diameter_m",
        "inner_diameter_m","flow_leg"}
NOZZLE = {"type","name","total_flow_area_m2","discharge_coefficient",
          "coefficient_source_id","flow_leg","geometry"}


def run_payload(payload):
    if not isinstance(payload,dict) or set(payload)!=TOP:
        raise HydraulicsUnavailable("exact component budget fields required")
    rawfluid=payload["fluid"]
    if not isinstance(rawfluid,dict) or set(rawfluid)!=FLUID:
        raise HydraulicsUnavailable("exact Newtonian fluid fields required")
    rawcomponents=payload["components_in_flow_order"]
    if not isinstance(rawcomponents,list) or not rawcomponents:
        raise HydraulicsUnavailable("nonempty ordered component list required")
    try:
        fluid=NewtonianFluid(**rawfluid)
        components=[]
        for row in rawcomponents:
            if not isinstance(row,dict):
                raise HydraulicsUnavailable("typed component object required")
            if row.get("type")=="pipe_or_annulus" and set(row)==PIPE:
                components.append(CircuitComponent(pipe_or_annulus=FlowSegment(
                    **{key:value for key,value in row.items() if key!="type"})))
            elif row.get("type")=="nozzle_orifice" and set(row)==NOZZLE:
                components.append(CircuitComponent(nozzle_orifice=NozzleOrifice(
                    **{key:value for key,value in row.items() if key!="type"})))
            else:
                raise HydraulicsUnavailable("unsupported component type or fields")
    except TypeError as exc:
        raise HydraulicsUnavailable("invalid component field type") from exc
    return partial_circulation_budget(
        fluid,components,payload["flow_m3_s"])


def main(argv=None):
    parser=argparse.ArgumentParser(description="Restricted partial circulation losses, not rig SPP")
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
