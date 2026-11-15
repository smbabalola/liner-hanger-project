"""Strict offline JSON for bounded power-law pipe/annulus/nozzle budget."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from circulation_budget import CircuitComponent
from circulating_hydraulics import FlowSegment,HydraulicsUnavailable
from circulation_restrictions import NozzleOrifice
from power_law_laminar_pipe import PowerLawFluid
from power_law_circulation_budget import partial_power_law_circulation_budget

TOP={"fluid","flow_m3_s","components_in_flow_order","laminar_evidence_by_section"}
FLUID={"density_kg_m3","consistency_pa_s_n","flow_behavior_index","rheology"}
GEOMETRY={"type","name","kind","length_m","outer_diameter_m",
          "inner_diameter_m","flow_leg"}
NOZZLE={"type","name","total_flow_area_m2","discharge_coefficient",
        "coefficient_source_id","flow_leg","geometry"}


def run_payload(payload):
    if not isinstance(payload,dict) or set(payload)!=TOP:
        raise HydraulicsUnavailable("exact power-law circuit fields required")
    rawfluid=payload["fluid"]
    if not isinstance(rawfluid,dict) or set(rawfluid)!=FLUID:
        raise HydraulicsUnavailable("exact power-law fluid fields required")
    raw=payload["components_in_flow_order"]
    if not isinstance(raw,list) or not raw:
        raise HydraulicsUnavailable("ordered nonempty component list required")
    try:
        fluid=PowerLawFluid(**rawfluid)
        components=[]
        for row in raw:
            if not isinstance(row,dict):
                raise HydraulicsUnavailable("typed circuit component required")
            if row.get("type")=="pipe_or_annulus" and set(row)==GEOMETRY:
                components.append(CircuitComponent(pipe_or_annulus=FlowSegment(
                    **{key:value for key,value in row.items() if key!="type"})))
            elif row.get("type")=="nozzle_orifice" and set(row)==NOZZLE:
                components.append(CircuitComponent(nozzle_orifice=NozzleOrifice(
                    **{key:value for key,value in row.items() if key!="type"})))
            else:
                raise HydraulicsUnavailable("unsupported circuit component schema")
    except TypeError as exc:
        raise HydraulicsUnavailable("invalid typed circuit value") from exc
    return partial_power_law_circulation_budget(
        fluid,components,payload["flow_m3_s"],
        laminar_evidence_by_section=payload["laminar_evidence_by_section"])


def main(argv=None):
    parser=argparse.ArgumentParser(
        description="Source-asserted power-law laminar partial losses, NOT standpipe pressure")
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
