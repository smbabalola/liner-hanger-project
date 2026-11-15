"""Strict source-labelled Newtonian circular pipe regime API (research only)."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from circulating_hydraulics import NewtonianFluid,FlowSegment,HydraulicsUnavailable
from newtonian_pipe_flow_regimes import newtonian_pipe_pressure_by_regime

TOP={"fluid","segment","flow_m3_s","absolute_roughness_m","roughness_source_id"}
FLUID={"density_kg_m3","dynamic_viscosity_pa_s","rheology"}
SEG={"name","kind","length_m","outer_diameter_m","inner_diameter_m","flow_leg"}


def run_payload(payload):
    if not isinstance(payload,dict) or set(payload)!=TOP:
        raise HydraulicsUnavailable("exact pipe regime fields required")
    if not isinstance(payload["fluid"],dict) or set(payload["fluid"])!=FLUID:
        raise HydraulicsUnavailable("exact Newtonian fluid fields required")
    if not isinstance(payload["segment"],dict) or set(payload["segment"])!=SEG:
        raise HydraulicsUnavailable("exact pipe section fields required")
    try:
        fluid=NewtonianFluid(**payload["fluid"])
        segment=FlowSegment(**payload["segment"])
    except TypeError as exc:
        raise HydraulicsUnavailable("invalid typed pipe regime input") from exc
    return newtonian_pipe_pressure_by_regime(
        fluid,segment,payload["flow_m3_s"],
        absolute_roughness_m=payload["absolute_roughness_m"],
        roughness_source_id=payload["roughness_source_id"])


def main(argv=None):
    p=argparse.ArgumentParser(description="Research-only Newtonian pipe regime; NOT rig SPP")
    p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args(argv)
    try:
        result=run_payload(json.loads(args.input.read_text(encoding="utf-8")))
        encoded=json.dumps(result,indent=2,allow_nan=False)+"\n"
        if args.output:args.output.write_text(encoded,encoding="utf-8")
        else:sys.stdout.write(encoded)
        return 0
    except (OSError,ValueError,HydraulicsUnavailable) as exc:
        print(f"unavailable: {exc}",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
