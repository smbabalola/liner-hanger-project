"""Research-only 3D soft-string profile with sourced tangent-continuous survey joins.

Each two-station interval uses the experimental 3D single-interval solver.
No discontinuous doglegs, stiffness, contact loss/transfer or OEM limits.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

from directional_survey import integrate_minimum_curvature, SurveyError
from engineering_primitives import LENGTH_M, _number
from planned_job_section import PlannedSection, PlannedSectionError, SourcedNumber
from torque_drag_straight import FORCE_N, TorqueDragError
from torque_drag_3d import SpatialCurveInputs, predict_spatial_curve


@dataclass(frozen=True)
class SpatialProfileInterval:
    section: PlannedSection
    axial_friction: SourcedNumber
    rotational_friction: SourcedNumber
    contact_radius: SourcedNumber
    integration_steps: int


@dataclass(frozen=True)
class SpatialProfile:
    intervals_top_to_bottom: tuple[SpatialProfileInterval, ...]
    bottom_tension: SourcedNumber


def _derived(tension, ident, mode):
    return SourcedNumber(str(tension), "N", "MODEL-DERIVED-NOT-OEM",
                         f"spatial:{ident}:bottom-{mode}",
                         "experimental-3d-profile-v0.1", "unreviewed")


def predict_spatial_profile(profile: SpatialProfile) -> dict:
    if not isinstance(profile, SpatialProfile):
        raise TorqueDragError("SpatialProfile required")
    rows = profile.intervals_top_to_bottom
    if not isinstance(rows,(tuple,list)) or not rows:
        raise TorqueDragError("at least one spatial interval required")
    if not all(isinstance(r,SpatialProfileInterval) for r in rows):
        raise TorqueDragError("all rows must be SpatialProfileInterval")
    if not isinstance(profile.bottom_tension,SourcedNumber):
        raise TorqueDragError("source-qualified bottom tension required")
    try:
        start = profile.bottom_tension.si(FORCE_N,"bottom_tension")
    except PlannedSectionError as exc:
        raise TorqueDragError(str(exc)) from exc

    previous = None
    identifiers = set()
    for row in rows:
        s = row.section
        if not isinstance(s,PlannedSection):
            raise TorqueDragError("PlannedSection required for each interval")
        try:
            s.validate()
            if len(s.survey_stations) != 2:
                raise TorqueDragError("exactly two stations required")
            if s.section_id in identifiers:
                raise TorqueDragError("duplicate section_id")
            identifiers.add(s.section_id)
            first,last = s.survey_stations
            az1 = _number(first.azimuth_deg,"azimuth_deg")
            az2 = _number(last.azimuth_deg,"azimuth_deg")
            i1 = _number(first.inclination_deg,"inclination_deg")
            i2 = _number(last.inclination_deg,"inclination_deg")
            top_md = s.top_md.si(LENGTH_M,"top_md",positive=False)
            bottom_md = s.bottom_md.si(LENGTH_M,"bottom_md",positive=False)
            integrated = integrate_minimum_curvature(
                stations=s.survey_stations, depth_unit=s.survey_depth_unit,
                start_tvd=s.first_station_tvd.value,
                start_tvd_unit=s.first_station_tvd.unit, datum=s.datum)
            sig=(s.case_id,s.datum,s.survey_source_id,s.survey_revision)
            if previous:
                old_md,old_tvd,old_i,old_az,old_sig = previous
                if sig != old_sig:
                    raise TorqueDragError("case/datum/survey revision mismatch")
                if top_md != old_md:
                    raise TorqueDragError("section MD gap or overlap")
                if abs(integrated[0].tvd_m-old_tvd)>Decimal("0.000001"):
                    raise TorqueDragError("section TVD discontinuity")
                if i1 != old_i or az1 != old_az:
                    raise TorqueDragError("boundary inclination/azimuth kink unsupported")
            previous=(bottom_md,integrated[-1].tvd_m,i2,az2,sig)
        except (PlannedSectionError,SurveyError,ValueError) as exc:
            if isinstance(exc,TorqueDragError):
                raise
            raise TorqueDragError(str(exc)) from exc

    state={"pickup":start,"slackoff":start,"rotation":start}
    total_torque=Decimal(0)
    record=[]
    for row in reversed(rows):
        s=row.section
        item={"section_id":s.section_id,"modes":{}}
        for mode in ("pickup","slackoff","rotation"):
            bottom=state[mode]
            calc=predict_spatial_curve(SpatialCurveInputs(
                s,row.axial_friction,row.rotational_friction,row.contact_radius,
                _derived(bottom,s.section_id,mode),row.integration_steps))
            result=calc["results"][mode]
            state[mode]=Decimal(result["top_tension_n"])
            item["modes"][mode]={
                "bottom_tension_n":str(bottom),
                "top_tension_n":str(state[mode]),
                "integrated_wall_contact_n":result["integrated_wall_contact_n"],
            }
            if mode=="rotation":
                increment=Decimal(result["contact_torque_nm"])
                total_torque+=increment
                item["incremental_rotation_contact_torque_nm"]=str(increment)
                item["cumulative_rotation_contact_torque_nm"]=str(total_torque)
                item["source_register"]=calc["sources"]
        record.append(item)
    return {
        "case_id":rows[0].section.case_id,
        "model":"experimental-contiguous-3d-soft-string-v0.1",
        "status":"unreviewed_inputs",
        "top_tensions_n":{name:str(t) for name,t in state.items()},
        "total_rotation_contact_torque_nm":str(total_torque),
        "bottom_tension_source":{
            "source_id":profile.bottom_tension.source_id,
            "source_location":profile.bottom_tension.source_location,
            "source_revision":profile.bottom_tension.source_revision,
            "review_status":profile.bottom_tension.review_status,
            "value":str(profile.bottom_tension.value),
            "unit":profile.bottom_tension.unit,
        },
        "sections_top_to_bottom":list(reversed(record)),
        "assumptions":[
            "exact MD/TVD/tangent continuity at every sourced survey station",
            "two stations per segment with fixed angular gradients",
            "three distinct axial movement modes, bottom-to-top force transfer",
            "no discrete kinks, joint loads, tool or bit torque, stiffness or contact transfer",
        ],
        "warning":"Experimental 3D soft-string profile only: NOT field-calibrated, rig hookload, liner hanger setting force, OEM limit or operating guidance.",
    }
