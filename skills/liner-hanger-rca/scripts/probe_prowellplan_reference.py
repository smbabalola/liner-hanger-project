"""Audit a pinned *external* public torque/drag example without importing it into the skill.

Research-only benchmark discovery; does not compare our force model or imply
engineering acceptance. Run in an isolated job with exact upstream revisions.
DO NOT use this as part of the portable skill's required dependencies.
"""
from __future__ import annotations

import copy
import json
import math
import sys

from torque_drag import calc
from well_profile import load


TORQUE_DRAG_COMMIT = "701cfff5990e33b495f45e082364d608ee65db87"
WELL_PROFILE_COMMIT = "43375df82eaa53a890b5539808ed33d3d57f0817"
FIXTURE = (
    "https://raw.githubusercontent.com/pro-well-plan/well_profile/"
    + WELL_PROFILE_COMMIT
    + "/well_profile/tests/trajectory1.xlsx"
)
DOCUMENTED_FIRST_FORCE_KN = {
    "lowering": 372.2971700118521,
    "static": 422.85963348870627,
    "hoisting": 486.97807188086904,
}
DOCUMENTED_FIRST_TORQUE_KNM = {
    "lowering": 52.88965056700336,
    "static": 53.24879605055506,
    "hoisting": 53.66437608286427,
}


def main() -> int:
    well = load(FIXTURE)
    data = well.trajectory
    if not data:
        raise RuntimeError("external survey fixture missing")
    inclinations = [float(row["inc"]) for row in data]
    azimuths = [float(row["azi"]) for row in data]
    if not all(math.isfinite(x) for x in inclinations + azimuths):
        raise RuntimeError("nonfinite external survey values")
    dimensions = {"pipe": {"od": 4.5, "id": 4, "shoe": 3000}, "odAnn": 5}
    result = calc(data, dimensions, case="all", torque_calc=True, wob=50, tbit=50)
    explicit_default = calc(copy.deepcopy(data), dimensions, case="all", torque_calc=True,
                            wob=50, tbit=50, fric=[0.24] * len(data))
    actual = {"force": {k: float(result.force[k][0]) for k in DOCUMENTED_FIRST_FORCE_KN},
              "torque": {k: float(result.torque[k][0]) for k in DOCUMENTED_FIRST_TORQUE_KNM}}
    if not all(math.isfinite(v) for group in actual.values() for v in group.values()):
        raise RuntimeError("external source returned nonfinite outputs")
    explicit_default_first = {
        "force": {k: float(explicit_default.force[k][0]) for k in DOCUMENTED_FIRST_FORCE_KN},
        "torque": {k: float(explicit_default.torque[k][0]) for k in DOCUMENTED_FIRST_TORQUE_KNM},
    }
    default_vs_explicit = {
        group: {k: math.isclose(actual[group][k], v, rel_tol=1e-11, abs_tol=1e-9)
                for k, v in values.items()}
        for group, values in explicit_default_first.items()
    }
    deviations = {
        "force_kN": {k: actual["force"][k] - v for k, v in DOCUMENTED_FIRST_FORCE_KN.items()},
        "torque_kNm": {k: actual["torque"][k] - v for k, v in DOCUMENTED_FIRST_TORQUE_KNM.items()},
    }
    matches = {
        "force": {
            k: math.isclose(actual["force"][k], value, rel_tol=1e-5, abs_tol=1e-4)
            for k, value in DOCUMENTED_FIRST_FORCE_KN.items()
        },
        "torque": {
            k: math.isclose(actual["torque"][k], value, rel_tol=1e-5, abs_tol=1e-4)
            for k, value in DOCUMENTED_FIRST_TORQUE_KNM.items()
        },
    }
    documents_match = all(
        ok for group in matches.values() for ok in group.values()
    )
    report = {
        "status": "source_documentation_reproduced" if documents_match else "source_documentation_mismatch",
        "classification": "independent_upstream_software_reproduction_not_physical_validation",
        "engineering_acceptance": False,
        "upstream_torque_drag_commit": TORQUE_DRAG_COMMIT,
        "upstream_well_profile_commit": WELL_PROFILE_COMMIT,
        "survey_fixture": FIXTURE,
        "survey_points": len(data),
        "inclination_range_deg": [min(inclinations), max(inclinations)],
        "azimuth_range_deg": [min(azimuths), max(azimuths)],
        "contains_inclination_variation": max(inclinations)-min(inclinations) > 1e-6,
        "contains_azimuth_variation": max(azimuths)-min(azimuths) > 1e-6,
        "output_first": actual,
        "explicit_list_friction_024_first": explicit_default_first,
        "default_equals_explicit_list_friction_024": default_vs_explicit,
        "executed_minus_documented": deviations,
        "matches_upstream_documentation": matches,
        "source_law_warnings": [
            "This third-party package defaults to friction=0.24 for any non-list argument.",
            "The upstream buoyancy and string boundary conditions require equivalence review.",
            "The documented outputs may be from a different package/source revision.",
            "No comparison with our soft-string solver, field data or OEM limitations is made.",
        ],
    }
    print(json.dumps(report, indent=2, allow_nan=False))
    # This probe always refuses engineering acceptance. A documented-output
    # mismatch is evidence of version drift, not a reason to tune values.
    if not report["contains_inclination_variation"] or not report["contains_azimuth_variation"]:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
