"""Strict offline JSON for signed two-leg static hydrostatic imbalance.

Research-only; neither full flowing pressure nor standpipe pressure.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from circulation_hydrostatics import HydrostaticLayer,static_hydrostatic_imbalance
from circulating_hydraulics import HydraulicsUnavailable

TOP={"layers"}
LAYER={"name","leg","top_tvd_m","bottom_tvd_m","density_kg_m3",
       "density_source_id","datum"}


def run_payload(payload):
    if not isinstance(payload,dict) or set(payload)!=TOP:
        raise HydraulicsUnavailable("exact hydrostatic input schema required")
    raw=payload["layers"]
    if not isinstance(raw,list) or not raw:
        raise HydraulicsUnavailable("nonempty hydrostatic layers required")
    if any(not isinstance(x,dict) or set(x)!=LAYER for x in raw):
        raise HydraulicsUnavailable("exact hydrostatic layer fields required")
    try:
        layers=[HydrostaticLayer(**x) for x in raw]
    except TypeError as exc:
        raise HydraulicsUnavailable("invalid hydrostatic field type") from exc
    return static_hydrostatic_imbalance(layers)


def main(argv=None):
    parser=argparse.ArgumentParser(
        description="Research-only hydrostatic balance; NOT circulating rig SPP")
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
