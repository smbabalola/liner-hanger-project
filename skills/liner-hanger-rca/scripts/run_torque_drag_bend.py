"""Offline sourced ideal weightless bend capstan benchmark.

python scripts/run_torque_drag_bend.py examples/synthetic_torque_drag_bend.json
This is NOT a weighted wellbore dogleg calculator.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from planned_job_section import SourcedNumber
from torque_drag_bend import IdealBendInputs, predict_ideal_bend
from torque_drag_straight import TorqueDragError

REQUIRED = {"bend_id", "bottom_tension", "bend_angle", "axial_friction",
            "rotational_friction", "contact_radius", "zero_distributed_weight"}
SOURCE_FIELDS = {"bottom_tension", "bend_angle", "axial_friction",
                 "rotational_friction", "contact_radius"}


def run_payload(raw):
    if not isinstance(raw, dict) or set(raw) != REQUIRED:
        raise TorqueDragError("weightless bend: exact required schema fields missing or unexpected")
    args = {k: v for k, v in raw.items() if k not in SOURCE_FIELDS}
    for field in SOURCE_FIELDS:
        value = raw[field]
        if not isinstance(value, dict):
            raise TorqueDragError(f"{field}: sourced value object required")
        try:
            args[field] = SourcedNumber(**value)
        except (TypeError, KeyError) as exc:
            raise TorqueDragError(f"{field}: malformed sourced record") from exc
    return predict_ideal_bend(IdealBendInputs(**args))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Exact weightless capstan bend limit only")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    opts = parser.parse_args(argv)
    try:
        result = run_payload(json.loads(opts.input.read_text(encoding="utf-8")))
        output = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if opts.output:
            opts.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except (OSError, json.JSONDecodeError, TorqueDragError) as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
