"""LH-CALC-02: contiguous CO-LINEAR straight-string sections only.

Propagates independently sourced pickup/slackoff/rotation tensile boundaries
upward from the deepest section. Section orientation MUST remain identical
across boundaries: a dogleg introduces tension-dependent contact not modeled
here. Never interpret output as hookload, field-approved loads or OEM limits.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from directional_survey import integrate_minimum_curvature
from engineering_primitives import LENGTH_M
from planned_job_section import PlannedSection, SourcedNumber
from torque_drag_straight import (
    FORCE_N, StraightTorqueDragInputs, TorqueDragError, predict_straight_section,
)


@dataclass(frozen=True)
class ProfileInterval:
    section: PlannedSection
    axial_friction: SourcedNumber
    rotational_friction: SourcedNumber
    contact_radius: SourcedNumber


@dataclass(frozen=True)
class StraightProfile:
    intervals_top_to_bottom: tuple[ProfileInterval, ...]
    bottom_tension: SourcedNumber


def _boundary(value: Decimal, *, section_id: str, mode: str) -> SourcedNumber:
    return SourcedNumber(str(value), "N", "DERIVED-MODEL-NOT-OEM",
                        f"bottom-of-{section_id}:{mode}",
                        "straight-profile-v0.1", "unreviewed")


def predict_straight_profile(profile: StraightProfile) -> dict:
    """Return depth-ordered section results plus top tensile loads and summed torque.

    For mode q, Ttop(q) = Tbottom(q) + incremental sectional T(q).
    Run distinct tensile states for pickup, slackoff, and pure rotation.
    Assumes no frictional torsional torque at the deepest boundary.
    """
    if not isinstance(profile, StraightProfile):
        raise TorqueDragError("StraightProfile required")
    sections = profile.intervals_top_to_bottom
    if not isinstance(sections, (tuple, list)) or not sections:
        raise TorqueDragError("at least one straight interval required")
    if not all(isinstance(x, ProfileInterval) for x in sections):
        raise TorqueDragError("all intervals must be ProfileInterval")
    try:
        bottom = profile.bottom_tension.si(FORCE_N, "bottom_tension", positive=False)
    except (AttributeError, ValueError) as exc:
        raise TorqueDragError("invalid sourced bottom tensile boundary") from exc
    if bottom < 0:
        raise TorqueDragError("compressive bottom boundary is unsupported")

    prev_bottom = None
    orientation = None
    record_ids = set()
    source_reviewed = profile.bottom_tension.review_status == "reviewed"
    for item in sections:
        section = item.section
        try:
            section.validate()
            top = section.top_md.si(LENGTH_M, "top_md", positive=False)
            lower = section.bottom_md.si(LENGTH_M, "bottom_md", positive=False)
            angle = (Decimal(str(section.survey_stations[0].inclination_deg)),
                     Decimal(str(section.survey_stations[0].azimuth_deg)))
            if section.section_id in record_ids:
                raise TorqueDragError("duplicate section_id is unsupported")
            record_ids.add(section.section_id)
            stations = integrate_minimum_curvature(
                stations=section.survey_stations,
                depth_unit=section.survey_depth_unit,
                start_tvd=section.first_station_tvd.value,
                start_tvd_unit=section.first_station_tvd.unit, datum=section.datum)
        except (ValueError, TypeError, AttributeError) as exc:
            if isinstance(exc, TorqueDragError):
                raise
            raise TorqueDragError("invalid source-qualified profile interval") from exc
        top_tvd = stations[0].tvd_m
        bottom_tvd = stations[-1].tvd_m
        if orientation is None:
            orientation = angle
            case_id = section.case_id
            datum = section.datum
            survey_id = section.survey_source_id
            survey_rev = section.survey_revision
        elif (angle != orientation or section.case_id != case_id
              or section.datum != datum or section.survey_source_id != survey_id
              or section.survey_revision != survey_rev):
            raise TorqueDragError("orientation/datum/survey/case mismatch; dogleg or mixed plan unsupported")
        if prev_bottom is not None:
            prev_md, prev_tvd = prev_bottom
            if top != prev_md:
                raise TorqueDragError("section MD overlap or gap; continuous endpoints required")
            if abs(top_tvd - prev_tvd) > Decimal("0.000001"):
                raise TorqueDragError("TVD discontinuity across section boundary")
        prev_bottom = (lower, bottom_tvd)

        # Validate complete physics inputs without inventing a field bottom load.
        test_case = StraightTorqueDragInputs(
            section, item.axial_friction, item.rotational_friction,
            item.contact_radius, _boundary(bottom, section_id=section.section_id,
                                           mode="validation"))
        test_case.validate()
        # Caller-provided provenance labels do not imply manufacturer approval.
        section_status = section.calculate()["status"]
        source_reviewed = source_reviewed and section_status == "numeric_candidate_only"
        source_reviewed = source_reviewed and all(
            v.review_status == "reviewed" for v in
            (item.axial_friction, item.rotational_friction, item.contact_radius))

    # Three modes are propagated SEPARATELY; otherwise pickup's force
    # boundary would incorrectly contaminate slackoff or rotating tension.
    state = {"pickup": bottom, "slackoff": bottom, "rotation": bottom}
    cumulative_torque = Decimal(0)
    rows_bottom_to_top = []
    for item in reversed(sections):
        record = {"section_id": item.section.section_id}
        physical_row = None
        for mode, key in (
            ("slackoff", "top_slackoff_tension_n"),
            ("pickup", "top_pickup_tension_n"),
            ("rotation", "top_pure_rotation_tension_n"),
        ):
            case = StraightTorqueDragInputs(
                item.section, item.axial_friction, item.rotational_friction,
                item.contact_radius,
                _boundary(state[mode], section_id=item.section.section_id, mode=mode))
            outcome = predict_straight_section(case)
            if physical_row is None:
                physical_row = outcome
            record[f"bottom_{mode}_tension_n"] = str(state[mode])
            state[mode] = Decimal(outcome["results"][key])
            record[key] = str(state[mode])
        local_torque = Decimal(physical_row["results"]["off_bottom_contact_torque_nm"])
        cumulative_torque += local_torque
        record["incremental_contact_torque_nm"] = str(local_torque)
        record["cumulative_contact_torque_nm"] = str(cumulative_torque)
        record["source_register"] = {
            "section": physical_row["sources"]["section"],
            "torque_drag_inputs": {
                key: physical_row["sources"]["torque_drag_inputs"][key]
                for key in ("axial_friction", "rotational_friction", "contact_radius")
            },
        }
        rows_bottom_to_top.append(record)

    return {
        "case_id": sections[0].section.case_id,
        "model": "contiguous-colinear-straight-profile-v0.1",
        "status": "numeric_candidate_only" if source_reviewed else "unreviewed_inputs",
        "top_section_tensions_n": {mode: str(value) for mode, value in state.items()},
        "total_friction_contact_torque_nm": str(cumulative_torque),
        "bottom_tension_source": {
            "value": str(profile.bottom_tension.value),
            "unit": profile.bottom_tension.unit,
            "source_id": profile.bottom_tension.source_id,
            "source_location": profile.bottom_tension.source_location,
            "source_revision": profile.bottom_tension.source_revision,
            "review_status": profile.bottom_tension.review_status,
        },
        "sections_top_to_bottom": list(reversed(rows_bottom_to_top)),
        "assumptions": [
            "all intervals lie on exactly the same straight tangent (no dogleg)",
            "each source-qualified section ends at next section's MD and TVD",
            "separate pickup, slackoff and pure-rotation tensile states",
            "single sourced tension at deepest boundary; zero initial torsional drag",
            "fully flooded/open and pressure-balanced straight sections",
            "no compressive slackoff, no dynamics, no torsional stiffness",
        ],
        "warning": "NOT rig hookload, downhole tool-setting force, OEM limit, or operating guidance.",
    }
