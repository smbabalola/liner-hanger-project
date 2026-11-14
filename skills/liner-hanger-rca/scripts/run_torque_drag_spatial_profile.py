"""Research-only 3D multi-section profile JSON runner. Not operational use."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from planned_job_section import SourcedNumber, PlannedSectionError
from run_planned_section import from_payload
from torque_drag_straight import TorqueDragError
from torque_drag_spatial_profile import (
    SpatialProfile, SpatialProfileInterval, predict_spatial_profile,
)

TOP={"intervals_top_to_bottom","bottom_tension"}
ROW={"planned_section","axial_friction","rotational_friction",
     "contact_radius","integration_steps"}
SOURCE={"axial_friction","rotational_friction","contact_radius"}


def _source(r, name):
    if not isinstance(r,dict):
        raise TorqueDragError(f"{name}: sourced number required")
    try:
        return SourcedNumber(**r)
    except (TypeError,KeyError) as exc:
        raise TorqueDragError(f"{name}: malformed sourced number") from exc


def run_payload(raw, *, calculator=predict_spatial_profile):
    if not isinstance(raw,dict) or set(raw)!=TOP:
        raise TorqueDragError("3D profile exact root schema required")
    rows=raw["intervals_top_to_bottom"]
    if not isinstance(rows,list) or not rows:
        raise TorqueDragError("nonempty list of 3D intervals required")
    parsed=[]
    for index,row in enumerate(rows):
        if not isinstance(row,dict) or set(row)!=ROW:
            raise TorqueDragError(f"interval {index}: exact fields required")
        try:
            s=from_payload(row["planned_section"])
        except (PlannedSectionError,TypeError) as exc:
            raise TorqueDragError(f"interval {index}: invalid planned section") from exc
        values={name:_source(row[name],f"interval {index} {name}") for name in SOURCE}
        parsed.append(SpatialProfileInterval(
            s,values["axial_friction"],values["rotational_friction"],
            values["contact_radius"],row["integration_steps"]))
    return calculator(SpatialProfile(
        tuple(parsed),_source(raw["bottom_tension"],"bottom_tension")))


def main(argv=None):
    p=argparse.ArgumentParser(description="Experimental 3D soft string profile; NOT field approved")
    p.add_argument("input",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args(argv)
    try:
        value=run_payload(json.loads(a.input.read_text(encoding="utf-8")))
        rendered=json.dumps(value,indent=2,allow_nan=False)+"\n"
        if a.output:
            a.output.write_text(rendered,encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (OSError,json.JSONDecodeError,TorqueDragError) as exc:
        print(f"unavailable: {exc}",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
