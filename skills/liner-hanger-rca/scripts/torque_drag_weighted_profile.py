"""Research-only contiguous PLANAR weighted soft-string profile.

Connects source-qualified one-interval RK4 solutions, preserving separate
pickup/slackoff/rotation tensile states. No 3D azimuthal doglegs, discrete
kinks, tool forces, rig hookload, stiff-string mechanics, or OEM approval.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from directional_survey import integrate_minimum_curvature, SurveyError
from engineering_primitives import LENGTH_M, _number
from planned_job_section import PlannedSection, PlannedSectionError, SourcedNumber
from torque_drag_straight import FORCE_N, TorqueDragError
from torque_drag_weighted_curve import WeightedCurveInputs, predict_weighted_curve


@dataclass(frozen=True)
class WeightedProfileInterval:
    section: PlannedSection
    axial_friction: SourcedNumber
    rotational_friction: SourcedNumber
    contact_radius: SourcedNumber
    integration_steps: int


@dataclass(frozen=True)
class WeightedPlanarProfile:
    intervals_top_to_bottom: tuple[WeightedProfileInterval, ...]
    bottom_tension: SourcedNumber


def _derived_tension(value: Decimal, section_id: str, mode: str) -> SourcedNumber:
    return SourcedNumber(
        str(value), "N", "MODEL-DERIVED-NOT-OEM",
        f"section:{section_id}:bottom-{mode}-boundary",
        "weighted-planar-profile-v0.1", "unreviewed",
    )


def predict_weighted_planar_profile(profile: WeightedPlanarProfile) -> dict:
    """Integrate depth-contiguous intervals upward with distinct mode boundaries.

    Each interval must start exactly where the previous ends in MD, TVD,
    inclination and azimuth. The two stations per interval must have a
    constant azimuth; *any* turn at the boundary is rejected.
    """
    if not isinstance(profile, WeightedPlanarProfile):
        raise TorqueDragError("WeightedPlanarProfile required")
    rows = profile.intervals_top_to_bottom
    if not isinstance(rows, (tuple, list)) or not rows:
        raise TorqueDragError("at least one weighted planar interval required")
    if not all(isinstance(row, WeightedProfileInterval) for row in rows):
        raise TorqueDragError("all rows must be WeightedProfileInterval")
    if not isinstance(profile.bottom_tension, SourcedNumber):
        raise TorqueDragError("sourced bottom tension required")
    try:
        bottom = profile.bottom_tension.si(FORCE_N, "bottom_tension")
    except PlannedSectionError as exc:
        raise TorqueDragError(str(exc)) from exc

    seen = set()
    previous = None
    prepared = []
    for row in rows:
        section = row.section
        if not isinstance(section, PlannedSection):
            raise TorqueDragError("source-qualified PlannedSection required")
        try:
            section.validate()
            if len(section.survey_stations) != 2:
                raise TorqueDragError("exactly two survey stations per planar interval required")
            if section.section_id in seen:
                raise TorqueDragError("duplicate section_id")
            seen.add(section.section_id)
            first, last = section.survey_stations
            a1 = _number(first.azimuth_deg, "azimuth_deg")
            a2 = _number(last.azimuth_deg, "azimuth_deg")
            if a1 != a2:
                raise TorqueDragError("3D azimuth turn within interval unsupported")
            i1 = _number(first.inclination_deg, "inclination_deg")
            i2 = _number(last.inclination_deg, "inclination_deg")
            md_start = section.top_md.si(LENGTH_M, "top_md", positive=False)
            md_end = section.bottom_md.si(LENGTH_M, "bottom_md", positive=False)
            integrated = integrate_minimum_curvature(
                stations=section.survey_stations, depth_unit=section.survey_depth_unit,
                start_tvd=section.first_station_tvd.value,
                start_tvd_unit=section.first_station_tvd.unit,
                datum=section.datum,
            )
            signature = (section.case_id, section.datum,
                         section.survey_source_id, section.survey_revision, a1)
            if previous:
                prev_md, prev_tvd, prev_i, prev_az, prev_signature = previous
                if signature != prev_signature:
                    raise TorqueDragError("case/datum/survey revision or azimuth mismatch")
                if md_start != prev_md:
                    raise TorqueDragError("section MD gap or overlap")
                if abs(integrated[0].tvd_m - prev_tvd) > Decimal("0.000001"):
                    raise TorqueDragError("section TVD discontinuity")
                if i1 != prev_i or a1 != prev_az:
                    raise TorqueDragError("boundary inclination/azimuth kink unsupported")
            previous = (md_end, integrated[-1].tvd_m, i2, a2, signature)
            # Pre-validation is performed again for each derived mode boundary,
            # so the downstream physical solver cannot be bypassed.
            prepared.append(row)
        except (PlannedSectionError, SurveyError) as exc:
            raise TorqueDragError(str(exc)) from exc

    state = {"pickup": bottom, "slackoff": bottom, "rotation": bottom}
    accumulated_torque = Decimal("0")
    output_bottom_to_top = []
    unreviewed = profile.bottom_tension.review_status != "reviewed"
    for row in reversed(prepared):
        section = row.section
        record = {"section_id": section.section_id, "modes": {}}
        for mode in ("pickup", "slackoff", "rotation"):
            current = state[mode]
            calculation = predict_weighted_curve(WeightedCurveInputs(
                section, row.axial_friction, row.rotational_friction,
                row.contact_radius,
                _derived_tension(current, section.section_id, mode),
                row.integration_steps,
            ))
            local = calculation["results"][mode]
            state[mode] = Decimal(local["top_tension_n"])
            record["modes"][mode] = {
                "bottom_tension_n": str(current),
                "top_tension_n": str(state[mode]),
                "integrated_wall_contact_n": local["integrated_wall_contact_n"],
                "signed_contact_side": local["signed_contact_side"],
            }
            if mode == "rotation":
                torque = Decimal(local["contact_torque_nm"])
                accumulated_torque += torque
                record["incremental_rotation_contact_torque_nm"] = str(torque)
                record["cumulative_rotation_contact_torque_nm"] = str(accumulated_torque)
                record["sources"] = {
                    "planned_section": calculation["sources"]["planned_section"],
                    "coefficients_and_radius": {
                        key: calculation["sources"]["weighted_curve_inputs"][key]
                        for key in ("axial_friction", "rotational_friction", "contact_radius")
                    },
                }
            unreviewed = unreviewed or calculation["status"] == "unreviewed_inputs"

        output_bottom_to_top.append(record)

    return {
        "case_id": prepared[0].section.case_id,
        "model": "contiguous-planar-weighted-soft-string-v0.1",
        "status": "unreviewed_inputs" if unreviewed else "numeric_candidate_only",
        "top_tensions_n": {mode: str(value) for mode, value in state.items()},
        "total_rotation_contact_torque_nm": str(accumulated_torque),
        "bottom_tension_source": {
            "value": str(profile.bottom_tension.value),
            "unit": profile.bottom_tension.unit,
            "source_id": profile.bottom_tension.source_id,
            "source_location": profile.bottom_tension.source_location,
            "source_revision": profile.bottom_tension.source_revision,
            "review_status": profile.bottom_tension.review_status,
        },
        "sections_top_to_bottom": list(reversed(output_bottom_to_top)),
        "assumptions": [
            "continuous top-to-bottom MD, TVD and tangent direction",
            "single fixed azimuth for entire planar wellpath",
            "uniform mass, fluid and friction inside each interval only",
            "independent pickup, slackoff, and pure rotation boundaries",
            "pure-rotation contact torque summed from deepest boundary",
            "downstream model rejects sampled within-interval contact side changes",
            "no 3D doglegs, point kinks, stiffness, buckling or downhole tool forces",
        ],
        "warning": "Research planar profile; NOT rig hookload, OEM liner-hanger force or approved operating instruction.",
    }
