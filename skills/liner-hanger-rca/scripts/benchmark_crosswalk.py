"""Fail-closed, research-only intake of independently sourced torque/drag benchmarks.

Numerical agreement is NOT engineering validation or approval for field use.
No proprietary job data should be placed into a public benchmark manifest.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


class BenchmarkError(ValueError):
    """Missing, ambiguous or physically incomparable benchmark evidence."""


REQUIRED_BASIS = (
    "survey_stations_md_inc_azi_tvd", "survey_interpolation", "wellbore_geometry",
    "pipe_geometry_mass_and_flood_state", "fluid_density", "friction_basis",
    "contact_model_and_regime", "movement_mode", "bottom_boundary_condition",
    "measured_output_location", "unit_system", "gravity_and_buoyancy",
)
REQUIRED_SOURCE = ("title", "public_locator", "exact_table_figure_or_dataset",
                   "independence_statement", "reproduction_permission")
SUPPORTED_OBSERVABLES = {
    "top_pickup_tension_n", "top_slackoff_tension_n",
    "top_rotation_tension_n", "rotation_contact_torque_nm",
}


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _finite_number(value, name, *, nonnegative=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise BenchmarkError(f"{name} must be a finite numeric value (not boolean)")
    if nonnegative and value < 0:
        raise BenchmarkError(f"{name} must not be negative")
    return float(value)


def assess_benchmark(data: dict) -> dict:
    """Check provenance/comparability then compare an independent scalar target.

    All basis fields are text evidence references, *not inferred defaults*.
    This gate cannot authenticate an author, reviewer, paper or OEM authority.
    """
    if not isinstance(data, dict):
        raise BenchmarkError("benchmark JSON object required")
    if data.get("schema_version") != "lh-calc02-benchmark-v1":
        raise BenchmarkError("unsupported schema_version")
    source, basis, comparison = (data.get(k) for k in ("source", "basis", "comparison"))
    if not all(isinstance(v, dict) for v in (source, basis, comparison)):
        raise BenchmarkError("source, basis, comparison objects required")
    missing_source = [k for k in REQUIRED_SOURCE if not _nonempty(source.get(k))]
    missing_basis = [k for k in REQUIRED_BASIS if not _nonempty(basis.get(k))]
    if missing_source or missing_basis:
        raise BenchmarkError("missing source evidence: " + ", ".join(missing_source) +
                             "; missing physical crosswalk: " + ", ".join(missing_basis))
    if source.get("source_type") not in ("published_independent", "qualified_independent"):
        raise BenchmarkError("source_type must be independently published or qualified")
    if source.get("independence_statement", "").strip().lower() in (
        "self-generated", "same solver", "unknown", "none", "n/a"):
        raise BenchmarkError("self-generated or unknown independence is not external evidence")
    if basis.get("contact_model_and_regime", "").strip().lower() in (
        "unknown", "unspecified", "n/a"):
        raise BenchmarkError("contact basis cannot be unknown")
    if comparison.get("observable") not in SUPPORTED_OBSERVABLES:
        raise BenchmarkError("unsupported or ambiguous observable")
    model_units = ("N*m" if comparison["observable"] == "rotation_contact_torque_nm" else "N")
    if comparison.get("unit") != model_units:
        raise BenchmarkError(f"observable must be compared in {model_units} (explicit conversion required)")
    if comparison.get("mode") != basis["movement_mode"]:
        raise BenchmarkError("movement mode differs between crosswalk and comparison")
    if comparison["mode"] not in ("pickup", "slackoff", "rotation"):
        raise BenchmarkError("unknown movement mode")
    expected_mode = ("rotation" if comparison["observable"] in (
        "top_rotation_tension_n", "rotation_contact_torque_nm") else
        "pickup" if comparison["observable"] == "top_pickup_tension_n" else "slackoff")
    if comparison["mode"] != expected_mode:
        raise BenchmarkError("observable incompatible with movement mode")
    if comparison.get("physical_equivalence_review") != "reviewed_comparable":
        raise BenchmarkError("explicit physical-equivalence review required; no auto-assumption")
    if not _nonempty(comparison.get("reviewer_or_basis_reference")):
        raise BenchmarkError("reviewer or documented physical-equivalence rationale required")
    target = _finite_number(comparison.get("reference_value"), "reference_value")
    model = _finite_number(comparison.get("model_value"), "model_value")
    atol = _finite_number(comparison.get("absolute_tolerance"), "absolute_tolerance", nonnegative=True)
    rtol = _finite_number(comparison.get("relative_tolerance"), "relative_tolerance", nonnegative=True)
    if atol == 0 and rtol == 0:
        raise BenchmarkError("at least one nonzero, justified tolerance required")
    if not _nonempty(comparison.get("tolerance_rationale")):
        raise BenchmarkError("tolerance rationale required")
    delta = model - target
    threshold = atol + rtol * abs(target)
    within = abs(delta) <= threshold
    return {
        "status": "numerical_agreement_only" if within else "numerical_disagreement",
        "reference_value": target,
        "model_value": model,
        "difference_model_minus_reference": delta,
        "allowed_absolute_difference": threshold,
        "observable": comparison["observable"],
        "unit": model_units,
        "engineering_acceptance": False,
        "warning": "This checks source-labelled numerical comparability only; no physical/OEM/field sign-off.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="local, authorized benchmark JSON")
    args = parser.parse_args(argv)
    try:
        result = assess_benchmark(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (BenchmarkError, ValueError, OSError) as exc:
        print(json.dumps({"status": "evidence_incomplete", "engineering_acceptance": False,
                          "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "numerical_agreement_only" else 1


if __name__ == "__main__":
    raise SystemExit(main())
