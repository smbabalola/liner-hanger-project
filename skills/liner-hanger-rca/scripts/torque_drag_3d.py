"""Experimental 3D inclined/azimuthal soft-string section, research only.

The Johancsik-type normal force is resolved in inclination and azimuth
directions: n=sqrt((w sin(i)-T di/dMD)^2 +
                    (T sin(i) da/dMD)^2).
The sign convention deliberately matches the existing signed *planar* module.
Two sourced stations, fixed angular gradients, no stiffness or contact-loss
model. Not rig hookload, field engineering, or OEM setting instructions.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, isfinite, pi, radians, sin

from engineering_primitives import LENGTH_M, _number
from planned_job_section import PlannedSection, PlannedSectionError, SourcedNumber
from torque_drag_straight import COEFFICIENT, FORCE_N, TorqueDragError
from torque_drag_weighted_curve import (
    WeightedCurveInputs, _require, predict_weighted_curve,
)


@dataclass(frozen=True)
class SpatialCurveInputs:
    section: PlannedSection
    axial_friction: SourcedNumber
    rotational_friction: SourcedNumber
    contact_radius: SourcedNumber
    bottom_tension: SourcedNumber
    integration_steps: int


def _delta_azimuth(a, b):
    """Shortest signed turn, rejecting ambiguous exactly 180-degree changes."""
    delta = (b - a + 180.0) % 360.0 - 180.0
    if abs(delta) >= 180.0 - 1e-10:
        raise TorqueDragError("ambiguous 180 degree azimuth turn unsupported")
    return delta


def _normal(t, s, *, w, ib, ab, ki, ka):
    i = ib - ki * s
    return hypot(w * sin(i) - t * ki, t * sin(i) * ka)


def _rhs(t, s, *, w, ib, ab, ki, ka, mu, murot, radius, mode):
    i = ib - ki * s
    n = _normal(t, s, w=w, ib=ib, ab=ab, ki=ki, ka=ka)
    return w*cos(i) + mode*mu*n, n, murot*n*radius if mode == 0 else 0.0


def _solve(bottom, length, w, ib, ab, ki, ka, mu, murot, radius, mode, steps):
    h = length/steps
    T, N, M = bottom, 0.0, 0.0
    for j in range(steps):
        s = j*h
        a = _rhs(T, s, w=w, ib=ib, ab=ab, ki=ki, ka=ka,
                 mu=mu, murot=murot, radius=radius, mode=mode)
        b = _rhs(T+h*a[0]/2, s+h/2, w=w, ib=ib, ab=ab, ki=ki, ka=ka,
                 mu=mu, murot=murot, radius=radius, mode=mode)
        c = _rhs(T+h*b[0]/2, s+h/2, w=w, ib=ib, ab=ab, ki=ki, ka=ka,
                 mu=mu, murot=murot, radius=radius, mode=mode)
        d = _rhs(T+h*c[0], s+h, w=w, ib=ib, ab=ab, ki=ki, ka=ka,
                 mu=mu, murot=murot, radius=radius, mode=mode)
        # A zero-tension RK stage is an unsupported contact/weight regime.
        if min(T, T+h*a[0]/2, T+h*b[0]/2, T+h*c[0]) <= 0:
            raise TorqueDragError("compression or zero intermediate tension unsupported")
        T += h*(a[0]+2*b[0]+2*c[0]+d[0])/6
        N += h*(a[1]+2*b[1]+2*c[1]+d[1])/6
        M += h*(a[2]+2*b[2]+2*c[2]+d[2])/6
        if not all(isfinite(v) for v in (T,N,M)):
            raise TorqueDragError("nonfinite 3D solver result")
        if T <= 0:
            raise TorqueDragError("compression or zero top tension unsupported")
    return T,N,M


def predict_spatial_curve(c: SpatialCurveInputs) -> dict:
    if not isinstance(c, SpatialCurveInputs):
        raise TorqueDragError("SpatialCurveInputs required")
    sec = c.section
    if not isinstance(sec, PlannedSection):
        raise TorqueDragError("PlannedSection required")
    try:
        sec.validate()
    except PlannedSectionError as exc:
        raise TorqueDragError(str(exc)) from exc
    if len(sec.survey_stations) != 2:
        raise TorqueDragError("exactly two sourced survey stations required")
    if type(c.integration_steps) is not int or not 8 <= c.integration_steps <= 20000:
        raise TorqueDragError("integration_steps must be integer in 8..20000")
    first, last = sec.survey_stations
    try:
        i1 = float(_number(first.inclination_deg, "top_inclination"))
        i2 = float(_number(last.inclination_deg, "bottom_inclination"))
        az1 = float(_number(first.azimuth_deg, "top_azimuth"))
        az2 = float(_number(last.azimuth_deg, "bottom_azimuth"))
    except ValueError as exc:
        raise TorqueDragError(str(exc)) from exc
    if not (0 <= i1 <= 90 and 0 <= i2 <= 90):
        raise TorqueDragError("only inclination 0..90 degrees supported")
    turn = _delta_azimuth(az1, az2)
    if abs(turn) > 90:
        raise TorqueDragError("3D azimuth turn >90 degrees per interval unsupported")
    if abs(turn) < 1e-12:
        # Exactly reuse previously validated planar solver, including its
        # fail-closed wall-side transition guard, rather than approximating it.
        p = predict_weighted_curve(WeightedCurveInputs(
            sec, c.axial_friction, c.rotational_friction, c.contact_radius,
            c.bottom_tension, c.integration_steps))
        return {
            **p, "model": "experimental-3d-soft-string-v0.1-planar-limit",
            "warning": "3D research engine planar limiting path; not field/OEM validated.",
        }
    bottom = _require(c.bottom_tension, FORCE_N, "bottom_tension")
    mu = _require(c.axial_friction, COEFFICIENT, "axial_friction", positive=False)
    murot = _require(c.rotational_friction, COEFFICIENT, "rotational_friction", positive=False)
    radius = _require(c.contact_radius, LENGTH_M, "contact_radius")
    if mu < 0 or murot < 0:
        raise TorqueDragError("negative friction unsupported")
    od = float(sec.pipe_outer_diameter.si(LENGTH_M, "pipe_outer_diameter"))
    if radius < od/2:
        raise TorqueDragError("contact radius smaller than pipe OD/2")
    physical = sec.calculate()
    length = float(physical["results"]["section_length_md_m"])
    buoyed_weight = float(physical["results"]["open_flooded_apparent_weight_n"])
    if buoyed_weight < 0:
        raise TorqueDragError("floating negative buoyed weight unsupported")
    w = buoyed_weight/length
    ki = radians(i2-i1)/length
    ka = radians(turn)/length
    if mu * hypot(ki*length, ka*length) > 30:
        raise TorqueDragError("excessive friction-turn product")
    ib, ab = radians(i2), radians(az2)
    result = {}
    for mode,name in ((1,"pickup"),(-1,"slackoff"),(0,"rotation")):
        T,N,M = _solve(bottom,length,w,ib,ab,ki,ka,mu,murot,radius,mode,
                       c.integration_steps)
        result[name] = {
            "top_tension_n": str(T),
            "integrated_wall_contact_n": str(N),
        }
        if mode == 0:
            result[name]["contact_torque_nm"] = str(M)
    sources = {
        field: {
            "value": str(getattr(c,field).value),
            "unit": getattr(c,field).unit,
            "source_id": getattr(c,field).source_id,
            "source_location": getattr(c,field).source_location,
            "source_revision": getattr(c,field).source_revision,
            "review_status": getattr(c,field).review_status,
        }
        for field in ("bottom_tension","axial_friction","rotational_friction",
                      "contact_radius")
    }
    reviewed = physical["status"] == "numeric_candidate_only" and all(
        r["review_status"] == "reviewed" for r in sources.values())
    return {
        "case_id": sec.case_id,
        "section_id": sec.section_id,
        "model": "experimental-3d-soft-string-v0.1",
        "status": "numeric_candidate_only" if reviewed else "unreviewed_inputs",
        "integration_steps": c.integration_steps,
        "results": result,
        "section_buoyed_weight_n": str(buoyed_weight),
        "signed_inclination_change_rad": str(ki*length),
        "signed_azimuth_change_rad": str(ka*length),
        "sources": {"planned_section": physical["sources"],
                    "spatial_curve_inputs": sources},
        "assumptions": [
            "one uniform open flooded segment, two sourced survey stations",
            "inclination and unwrapped azimuth change linearly with MD",
            "Johancsik-type independent curvature-plane normal components",
            "separate axial pickup, slackoff and pure-rotation modes",
            "positive tension, perfect flexible string, no contact loss",
            "no bending stiffness, torque transmission or pressure end loads",
        ],
        "warning": "Experimental 3D mathematical soft-string model; NOT validated with field data, rig hookload, Baker Hughes OEM loads or operational guidance.",
    }
