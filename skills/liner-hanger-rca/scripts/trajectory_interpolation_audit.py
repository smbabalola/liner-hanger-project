"""Independent 3D trajectory interpolation audit; no torque/drag imports.

Compares a constant-in-MD inclination/shortest-azimuth angle path with
minimum-curvature (great-circle) interpolation of the two end tangents.
Coordinates: north, east, down; azimuth clockwise from north; incl from down.
All inputs in metres/degrees. Research diagnostics, NOT actual well clearance.
"""
from __future__ import annotations

from math import acos, cos, isfinite, pi, radians, sin, sqrt


class TrajectoryAuditError(ValueError):
    pass


def _number(x, name):
    if isinstance(x, bool):
        raise TrajectoryAuditError(f"{name}: finite number required")
    try:
        x = float(x)
    except (TypeError, ValueError, OverflowError) as exc:
        raise TrajectoryAuditError(f"{name}: finite number required") from exc
    if not isfinite(x):
        raise TrajectoryAuditError(f"{name}: finite number required")
    return x


def _tangent(inc, az):
    return (sin(inc)*cos(az), sin(inc)*sin(az), cos(inc))


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _distance(a, b):
    return sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def _add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _scale(a, c):
    return tuple(c*x for x in a)


def _simpson(tangent_at, start, end, steps):
    if end == start:
        return (0.0, 0.0, 0.0)
    h = (end-start)/steps
    total = _add(tangent_at(start), tangent_at(end))
    for j in range(1, steps):
        total = _add(total, _scale(tangent_at(start+j*h), 4 if j%2 else 2))
    return _scale(total, h/3)


def audit_two_station_trajectory(*, length_m, top_inclination_deg,
                                 bottom_inclination_deg, top_azimuth_deg,
                                 bottom_azimuth_deg, steps=512):
    """Compare endpoint and sampled paths using independent Simpson quadrature.

    Great-circle interpolation is compared to linear inclination/azimuth;
    both match endpoint tangents but generally not intermediate trajectory.
    """
    length = _number(length_m, "length_m")
    i0 = _number(top_inclination_deg, "top_inclination_deg")
    i1 = _number(bottom_inclination_deg, "bottom_inclination_deg")
    a0 = _number(top_azimuth_deg, "top_azimuth_deg")
    a1 = _number(bottom_azimuth_deg, "bottom_azimuth_deg")
    if length <= 0 or not (0 <= i0 <= 90 and 0 <= i1 <= 90):
        raise TrajectoryAuditError("positive length and inclination in 0..90 required")
    if not (0 <= a0 < 360 and 0 <= a1 < 360):
        raise TrajectoryAuditError("azimuth in 0..360 required")
    if type(steps) is not int or steps < 8 or steps > 16384 or steps%4:
        raise TrajectoryAuditError("steps must be a multiple of four in 8..16384")
    delta = (a1-a0+180)%360-180
    if abs(delta) >= 180-1e-10:
        raise TrajectoryAuditError("ambiguous 180-degree azimuth change unsupported")
    t0 = _tangent(radians(i0), radians(a0))
    t1 = _tangent(radians(i1), radians(a1))
    beta = acos(max(-1.0, min(1.0, _dot(t0, t1))))
    if beta >= pi-1e-7:
        raise TrajectoryAuditError("undefined 180-degree minimum-curvature dogleg")

    def angular(u):
        return _tangent(radians(i0+(i1-i0)*u), radians(a0+delta*u))

    def minimum_curvature(u):
        if beta < 1e-8:
            return t0
        denom = sin(beta)
        return _add(_scale(t0, sin((1-u)*beta)/denom),
                    _scale(t1, sin(u*beta)/denom))

    points = []
    for q in range(5):
        u = q/4
        n = steps//4*q
        angpos = _scale(_simpson(angular, 0, u, n), length) if n else (0.,0.,0.)
        mcpos = _scale(_simpson(minimum_curvature, 0, u, n), length) if n else (0.,0.,0.)
        points.append({
            "fraction_md": u,
            "linear_angles_north_east_down_m": list(angpos),
            "minimum_curvature_north_east_down_m": list(mcpos),
            "position_difference_m": _distance(angpos, mcpos),
            "tangent_difference_norm": _distance(angular(u), minimum_curvature(u)),
        })
    endpoint = points[-1]
    return {
        "model": "independent-trajectory-interpolation-comparison-v0.1",
        "status": "research_only_not_field_validated",
        "length_m": length,
        "dogleg_rad": beta,
        "signed_azimuth_change_deg": delta,
        "integration_steps": steps,
        "samples": points,
        "endpoint_tvd_difference_m": endpoint["linear_angles_north_east_down_m"][2]-endpoint["minimum_curvature_north_east_down_m"][2],
        "endpoint_position_difference_m": endpoint["position_difference_m"],
        "maximum_sampled_position_difference_m": max(p["position_difference_m"] for p in points),
        "maximum_sampled_tangent_difference_norm": max(p["tangent_difference_norm"] for p in points),
        "warning": "Research-only geometry audit. No torque/drag, friction, wall contact, stiffness or safe operating guidance.",
    }
