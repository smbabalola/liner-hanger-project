"""LH-CALC-02 initial soft-string straight-section torque/drag model.

Offline, NON-OPERATIONAL planning illustration. No curved wellbores, bending
stiffness, tension-induced dogleg contact, pressure-end effects, axial/rotary
combined motion, or OEM limits. Requires source-qualified existing section.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from decimal import Decimal
from math import cos, radians, sin, isfinite

from planned_job_section import PlannedSection, PlannedSectionError, SourcedNumber
from engineering_primitives import LENGTH_M, _number, PrimitiveError

COEFFICIENT = {"1": Decimal("1")}
FORCE_N = {"N": Decimal("1"), "kN": Decimal("1000"), "lbf": Decimal("4.4482216152605")}


class TorqueDragError(ValueError):
    """Source, physical-applicability or numerical validation failure."""


@dataclass(frozen=True)
class StraightTorqueDragInputs:
    """Load boundary and measured friction values; no implicit defaults."""
    section: PlannedSection
    axial_friction: SourcedNumber
    rotational_friction: SourcedNumber
    contact_radius: SourcedNumber
    bottom_tension: SourcedNumber

    def validate(self):
        try:
            self.section.validate()
            surveys = self.section.survey_stations
            if len(surveys) != 2:
                raise TorqueDragError("exactly two survey stations required for straight model")
            first, last = surveys
            inclination = _number(first.inclination_deg, "inclination_deg")
            end_inclination = _number(last.inclination_deg, "inclination_deg")
            first_azi = _number(first.azimuth_deg, "azimuth_deg")
            end_azi = _number(last.azimuth_deg, "azimuth_deg")
            if inclination != end_inclination or first_azi != end_azi:
                raise TorqueDragError("curvature or turn is unsupported; no dogleg model")
            if not Decimal("0") <= inclination <= Decimal("90"):
                raise TorqueDragError("only 0..90 degree downward straight wellbore supported")
            mu_ax = self.axial_friction.si(COEFFICIENT, "axial_friction", positive=False)
            mu_rot = self.rotational_friction.si(COEFFICIENT, "rotational_friction", positive=False)
            if mu_ax < 0 or mu_rot < 0:
                raise TorqueDragError("friction coefficients must be nonnegative")
            radius = self.contact_radius.si(LENGTH_M, "contact_radius")
            pipe_od = self.section.pipe_outer_diameter.si(LENGTH_M, "pipe_outer_diameter")
            if radius < pipe_od / 2:
                raise TorqueDragError("contact radius cannot be smaller than pipe OD/2")
            bottom = self.bottom_tension.si(FORCE_N, "bottom_tension", positive=False)
            if bottom < 0:
                raise TorqueDragError("negative downhole tension/compression is unsupported")
        except (PlannedSectionError, PrimitiveError) as exc:
            raise TorqueDragError(str(exc)) from exc
        return self


def predict_straight_section(case: StraightTorqueDragInputs) -> dict:
    """Return nominal forces and pure-rotation friction torque, SI decimal strings.

    Straight, uniform, fully flooded/pressure-balanced string. Apparent weight W
    is the *metal buoyed* section gravity load from LH-CALC-01. Inclination i
    is from vertical. Low-side normal N=abs(W)*sin(i), axial gravity W*cos(i).
    At the top:
      pickup = Tbottom + Wcos(i) + mu_ax*N
      slackoff = Tbottom + Wcos(i) - mu_ax*N
      rotating axial = Tbottom + Wcos(i)  (pure rotation, NO axial travel)
      rotating contact torque = mu_rot*N*radius.
    Force balance ignores string stiffness and tangential curvature contact.
    """
    case.validate()
    section = case.section.calculate()
    incl = _number(case.section.survey_stations[0].inclination_deg, "inclination_deg")
    angle = radians(float(incl))
    if not isfinite(angle):
        raise TorqueDragError("non-finite inclination")
    cosine = Decimal("0") if incl == 90 else Decimal(str(cos(angle)))
    sine = Decimal("0") if incl == 0 else Decimal(str(sin(angle)))
    apparent_weight = Decimal(section["results"]["open_flooded_apparent_weight_n"])
    if apparent_weight < 0:
        raise TorqueDragError("negative apparent weight / floating section unsupported")
    normal_force = apparent_weight * sine
    axial_component = apparent_weight * cosine
    axial_mu = case.axial_friction.si(COEFFICIENT, "axial_friction", positive=False)
    rotary_mu = case.rotational_friction.si(COEFFICIENT, "rotational_friction", positive=False)
    bottom = case.bottom_tension.si(FORCE_N, "bottom_tension", positive=False)
    radius = case.contact_radius.si(LENGTH_M, "contact_radius")
    drag = axial_mu * normal_force
    pickup = bottom + axial_component + drag
    slackoff = bottom + axial_component - drag
    rotating = bottom + axial_component
    torque = rotary_mu * normal_force * radius
    if slackoff < 0:
        raise TorqueDragError("predicted slackoff would be compressive; buckling unsupported")
    def prov(n):
        v = getattr(case, n)
        return {"value": str(v.value), "unit": v.unit,
                "source_id": v.source_id, "source_location": v.source_location,
                "source_revision": v.source_revision, "review_status": v.review_status}
    sources = {n: prov(n) for n in (
        "axial_friction", "rotational_friction", "contact_radius", "bottom_tension"
    )}
    reviewed = section["status"] == "numeric_candidate_only" and all(
        s["review_status"] == "reviewed" for s in sources.values())
    return {
        "case_id": case.section.case_id,
        "section_id": case.section.section_id,
        "model": "straight-constant-inclination-soft-string-v0.1",
        "status": "numeric_candidate_only" if reviewed else "unreviewed_inputs",
        "results": {
            "top_pickup_tension_n": str(pickup),
            "top_slackoff_tension_n": str(slackoff),
            "top_pure_rotation_tension_n": str(rotating),
            "off_bottom_contact_torque_nm": str(torque),
            "low_side_normal_force_n": str(normal_force),
            "axial_drag_force_n": str(drag),
            "buoyed_section_weight_n": str(apparent_weight),
            "bottom_boundary_tension_n": str(bottom),
        },
        "sources": {"section": section["sources"], "torque_drag_inputs": sources},
        "assumptions": [
            "one uniform and straight section, exactly two constant-angle survey stations",
            "inclination in [0,90] degrees, no curvature/dogleg contact",
            "pure rotation and pure axial movement evaluated separately, not simultaneously",
            "open fully flooded pressure-balanced pipe; positive apparent gravity load",
            "Coulomb friction at low-side normal load only; no bending stiffness",
            "bottom boundary tension is provided independently, not inferred from hookload",
        ],
        "warning": "Section-top tensions are NOT rig hookload or validated liner-hanger force; no OEM or operating approval.",
    }


def friction_sensitivity(case: StraightTorqueDragInputs, *, axial_candidates, rotational_candidates):
    """Hypothetical friction scenarios only; NEVER manufacturer-approved values.

    Input candidate values are deliberately marked 'unreviewed' with a separate
    source identity, so a sensitivity envelope cannot masquerade as approved.
    """
    if not isinstance(axial_candidates, (tuple, list)) or not axial_candidates:
        raise TorqueDragError("axial_candidates must be a nonempty list")
    if not isinstance(rotational_candidates, (tuple, list)) or not rotational_candidates:
        raise TorqueDragError("rotational_candidates must be a nonempty list")
    out = []
    for ax in axial_candidates:
        for rot in rotational_candidates:
            scenario = replace(case,
                axial_friction=SourcedNumber(str(ax), "1", "SENSITIVITY-NOT-SOURCED",
                  "hypothetical axial friction", "unapproved", "unreviewed"),
                rotational_friction=SourcedNumber(str(rot), "1", "SENSITIVITY-NOT-SOURCED",
                  "hypothetical rotational friction", "unapproved", "unreviewed"))
            out.append(predict_straight_section(scenario))
    return out
