"""LH-CALC-02 experimental planar weighted-curvature soft-string model.

Numerical RK4 integration from bottom to top of ONE uniform, planar interval.
Inclination changes linearly with MD; azimuth is fixed. Distributed apparent
gravity and tension-induced wall contact combine as a SIGNED normal vector.
Independent straight and weightless-capstan limits are mandatory benchmarks.
Not an approved drilling torque/drag, surface hookload or setting-force tool.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, pi, radians, sin

from engineering_primitives import LENGTH_M, _number
from planned_job_section import PlannedSection, PlannedSectionError, SourcedNumber
from torque_drag_straight import (
    COEFFICIENT, FORCE_N, StraightTorqueDragInputs, TorqueDragError,
    predict_straight_section,
)


@dataclass(frozen=True)
class WeightedCurveInputs:
    section: PlannedSection
    axial_friction: SourcedNumber
    rotational_friction: SourcedNumber
    contact_radius: SourcedNumber
    bottom_tension: SourcedNumber
    integration_steps: int


def _require(source, unit_family, name, *, positive=True):
    if not isinstance(source, SourcedNumber):
        raise TorqueDragError(f"{name}: sourced numerical value required")
    try:
        val = source.si(unit_family, name, positive=positive)
    except PlannedSectionError as exc:
        raise TorqueDragError(str(exc)) from exc
    return float(val)


def _state_dynamics(t, s, *, w, i_bottom, k, mu, mode, radius, mu_rot):
    """dT/ds, dN/ds, dM/ds; upward s, positive inclination down MD.

    Section balance in tangent/normal directions, downward MD tangent t,
    left normal n=dt/di. External gravity projection: -w sin(i) along n.
    Contact magnitude per upward MD = abs(w*sin(i) - T*k) N/m.
    Thus build/drop and gravity can reinforce OR oppose each other.
    """
    i = i_bottom - k * s
    contact = abs(w * sin(i) - t * k)
    force = w * cos(i) + mode * mu * contact
    torque_rate = mu_rot * contact * radius if mode == 0 else 0.0
    return force, contact, torque_rate


def _integrate(*, bottom, length, w, i_bottom, k, mu, mu_rot, radius, mode, steps):
    h = length / steps
    tension = bottom
    normal = 0.0
    torque = 0.0
    for j in range(steps):
        s = j * h
        a1 = _state_dynamics(tension, s, w=w, i_bottom=i_bottom, k=k,
                             mu=mu, mode=mode, radius=radius, mu_rot=mu_rot)
        a2 = _state_dynamics(tension + h*a1[0]/2, s+h/2, w=w, i_bottom=i_bottom,
                             k=k, mu=mu, mode=mode, radius=radius, mu_rot=mu_rot)
        a3 = _state_dynamics(tension + h*a2[0]/2, s+h/2, w=w, i_bottom=i_bottom,
                             k=k, mu=mu, mode=mode, radius=radius, mu_rot=mu_rot)
        a4 = _state_dynamics(tension + h*a3[0], s+h, w=w, i_bottom=i_bottom,
                             k=k, mu=mu, mode=mode, radius=radius, mu_rot=mu_rot)
        tension += h*(a1[0]+2*a2[0]+2*a3[0]+a4[0])/6
        normal += h*(a1[1]+2*a2[1]+2*a3[1]+a4[1])/6
        torque += h*(a1[2]+2*a2[2]+2*a3[2]+a4[2])/6
        if not all(isfinite(x) for x in (tension, normal, torque)):
            raise TorqueDragError("non-finite weighted-curvature solution")
        if tension < -1e-9:
            raise TorqueDragError("predicted compression/buckling is unsupported")
    return max(0.0, tension), normal, torque


def predict_weighted_curve(inputs: WeightedCurveInputs) -> dict:
    """Solve a single continuous, constant-mass, constant-friction planar arc.

    Rejects 3D turns, decreasing TVD (inclination >90), pressure-end loads,
    frictional stick/slip, unsupported buckling and undocumented coefficients.
    Designed as a transparent research model with convergence diagnostics.
    """
    if not isinstance(inputs, WeightedCurveInputs):
        raise TorqueDragError("WeightedCurveInputs required")
    sct = inputs.section
    if not isinstance(sct, PlannedSection):
        raise TorqueDragError("PlannedSection required")
    try:
        sct.validate()
    except PlannedSectionError as exc:
        raise TorqueDragError(str(exc)) from exc
    stations = sct.survey_stations
    if len(stations) != 2:
        raise TorqueDragError("exactly two sourced survey stations required")
    try:
        itop = float(_number(stations[0].inclination_deg, "top_inclination_deg"))
        ibot = float(_number(stations[1].inclination_deg, "bottom_inclination_deg"))
        az1 = _number(stations[0].azimuth_deg, "top_azimuth_deg")
        az2 = _number(stations[1].azimuth_deg, "bottom_azimuth_deg")
    except ValueError as exc:
        raise TorqueDragError(str(exc)) from exc
    if az1 != az2:
        raise TorqueDragError("3D azimuth change is unsupported; planar bend only")
    if not (0 <= itop <= 90 and 0 <= ibot <= 90):
        raise TorqueDragError("inclinations must be in 0..90 degrees")
    if type(inputs.integration_steps) is not int or not 8 <= inputs.integration_steps <= 20000:
        raise TorqueDragError("integration_steps must be an integer from 8 to 20000")
    bottom = _require(inputs.bottom_tension, FORCE_N, "bottom_tension")
    mu = _require(inputs.axial_friction, COEFFICIENT, "axial_friction", positive=False)
    mu_rot = _require(inputs.rotational_friction, COEFFICIENT,
                      "rotational_friction", positive=False)
    radius = _require(inputs.contact_radius, LENGTH_M, "contact_radius")
    if mu < 0 or mu_rot < 0:
        raise TorqueDragError("friction must be nonnegative")
    od = float(sct.pipe_outer_diameter.si(LENGTH_M, "pipe_outer_diameter"))
    if radius < od / 2:
        raise TorqueDragError("contact radius must be >= pipe OD/2")
    static = sct.calculate()
    length = float(static["results"]["section_length_md_m"])
    apparent_w = float(static["results"]["open_flooded_apparent_weight_n"])
    if apparent_w < 0:
        raise TorqueDragError("floating/negative buoyed weight unsupported")
    w = apparent_w / length
    i_bottom = radians(ibot)
    k = radians(ibot - itop) / length
    # Extreme friction/turn products can be ill-conditioned and should not
    # return silently overflowed or misleadingly precise tensile answers.
    if mu*abs(k)*length > 30:
        raise TorqueDragError("excessive friction-dogleg product unsupported")
    force = {}
    for mode, name in ((1, "pickup"), (-1, "slackoff"), (0, "rotation")):
        top, contact, friction_torque = _integrate(
            bottom=bottom, length=length, w=w, i_bottom=i_bottom, k=k,
            mu=mu, mu_rot=mu_rot, radius=radius, mode=mode,
            steps=inputs.integration_steps)
        force[name] = {
            "top_tension_n": str(top),
            "integrated_wall_contact_n": str(contact),
        }
        if mode == 0:
            force[name]["contact_torque_nm"] = str(friction_torque)
    sources = {
        n: {"value": str(getattr(inputs, n).value),
            "unit": getattr(inputs, n).unit,
            "source_id": getattr(inputs, n).source_id,
            "source_location": getattr(inputs, n).source_location,
            "source_revision": getattr(inputs, n).source_revision,
            "review_status": getattr(inputs, n).review_status}
        for n in ("bottom_tension", "axial_friction", "rotational_friction", "contact_radius")
    }
    reviewed = static["status"] == "numeric_candidate_only" and all(
        x["review_status"] == "reviewed" for x in sources.values())
    return {
        "case_id": sct.case_id, "section_id": sct.section_id,
        "model": "planar-weighted-soft-string-rk4-v0.1",
        "status": "numeric_candidate_only" if reviewed else "unreviewed_inputs",
        "integration_steps": inputs.integration_steps,
        "results": force,
        "section_buoyed_weight_n": str(apparent_w),
        "signed_curvature_rad_per_m": str(k),
        "sources": {"planned_section": static["sources"], "weighted_curve_inputs": sources},
        "assumptions": [
            "uniform section, buoyed gravity and constant planar curvature",
            "two exact survey stations with constant azimuth, 0..90 degree inclination",
            "soft-string wall reaction combines gravity and signed curvature vector",
            "friction is Coulomb, separate pure pickup/slackoff/pure-rotation modes",
            "continuous modeled wall contact, not stiffness or tool-joint forces",
            "explicit RK4 step count; convergence must be checked by caller",
            "bottom positive tensile boundary, no dynamic pressure-end loads",
        ],
        "warning": "Research-level weighted planar arc only: not field-validated, rig hookload, liner-hanger set/load, 3D dogleg, or OEM instruction.",
    }
