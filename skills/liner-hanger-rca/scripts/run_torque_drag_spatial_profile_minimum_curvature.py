"""Strict offline source-gated multi-interval minimum-curvature 3D research CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from run_torque_drag_spatial_profile import run_payload as _parse_and_run
from torque_drag_spatial_profile import predict_minimum_curvature_profile
from torque_drag_straight import TorqueDragError


def run_payload(data):
    return _parse_and_run(data,calculator=predict_minimum_curvature_profile)


def main(argv=None):
    p=argparse.ArgumentParser(description="Research-only MC-consistent 3D string profile")
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
