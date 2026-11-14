"""Experimental, minimum-curvature-consistent 3D soft-string interval.

The unit tangent follows the great-circle interpolation of two measured
survey tangents, consistently with directional_survey minimum-curvature TVD.
The contact vector retains the sign convention of the validated planar
research model: -w_perpendicular - T * dt/dMD. No field approval.
"""
from __future__ import annotations

from math import acos, cos, exp, hypot, isfinite, pi, radians, sin, sqrt

from engineering_primitives import LENGTH_M, _number
from planned_job_section import PlannedSection, PlannedSectionError, SourcedNumber
from torque_drag_3d import SpatialCurveInputs, _delta_azimuth
from torque_drag_straight import COEFFICIENT, FORCE_N, TorqueDragError
from torque_drag_weighted_curve import _require


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _scale(a, k):
    return tuple(x*k for x in a)


def _add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _tangent(inclination, azimuth):
    return (sin(inclination)*cos(azimuth),
            sin(inclination)*sin(azimuth),
            cos(inclination))


def _minimum_curvature_frame(t0, t1, beta, u):
    """Unit tangent and derivative d(tangent)/d(fractional MD)."""
    if beta < 1e-10:
        return t0, (0.0, 0.0, 0.0)
    denom = sin(beta)
    tangent = _add(_scale(t0, sin((1-u)*beta)/denom),
                   _scale(t1, sin(u*beta)/denom))
    derivative = _add(
        _scale(t0, -beta*cos((1-u)*beta)/denom),
        _scale(t1, beta*cos(u*beta)/denom),
    )
    return tangent, derivative


def _dynamics(T, s, *, L, w, t0, t1, beta, mu, mu_rot, radius, mode):
    # s is bottom-to-top MD; fraction u is from upper station toward lower.
    tangent, derivative = _minimum_curvature_frame(t0, t1, beta, 1-s/L)
    dtdmd = _scale(derivative, 1/L)
    # g_perp is gravity minus its tangential component.
    gravity_perp = (-w*tangent[2]*tangent[0],
                    -w*tangent[2]*tangent[1],
                    w*(1-tangent[2]*tangent[2]))
    reaction = _add(_scale(gravity_perp, -1), _scale(dtdmd, -T))
    n = sqrt(_dot(reaction, reaction))
    if not isfinite(n):
        raise TorqueDragError("nonfinite minimum-curvature contact")
    dT = w*tangent[2] + mode*mu*n
    dN = n
    dM = mu_rot*n*radius if mode == 0 else 0.
    return dT, dN, dM, n, reaction


def _integrate(bottom, L, w, t0, t1, beta, mu, mu_rot, radius, mode, steps):
    h = L/steps
    T, N, M = bottom, 0., 0.
    neutral = False
    for j in range(steps):
        s = j*h
        stages = []
        a = _dynamics(T, s, L=L,w=w,t0=t0,t1=t1,beta=beta,mu=mu,
                      mu_rot=mu_rot,radius=radius,mode=mode)
        stages.append(a)
        bT = T+h*a[0]/2
        b = _dynamics(bT, s+h/2, L=L,w=w,t0=t0,t1=t1,beta=beta,mu=mu,
                      mu_rot=mu_rot,radius=radius,mode=mode)
        stages.append(b)
        cT = T+h*b[0]/2
        c = _dynamics(cT, s+h/2, L=L,w=w,t0=t0,t1=t1,beta=beta,mu=mu,
                      mu_rot=mu_rot,radius=radius,mode=mode)
        stages.append(c)
        dT = T+h*c[0]
        d = _dynamics(dT, s+h, L=L,w=w,t0=t0,t1=t1,beta=beta,mu=mu,
                      mu_rot=mu_rot,radius=radius,mode=mode)
        stages.append(d)
        if min(T, bT, cT, dT) <= 0:
            raise TorqueDragError("compression or zero tensile state unsupported")
        # A nonstraight, weighted arc with vanishing contact is an unknown
        # contact-loss / wall transfer event, not permission to carry on.
        if beta > 1e-10 and w > 0:
            for stage, stageT in zip(stages, (T,bT,cT,dT)):
                threshold = 1e-10*max(1.,w,stageT*beta/L)
                if stage[3] <= threshold:
                    raise TorqueDragError("near-zero contact on curved segment; wall contact state unsupported")
        T += h*(a[0]+2*b[0]+2*c[0]+d[0])/6
        N += h*(a[1]+2*b[1]+2*c[1]+d[1])/6
        M += h*(a[2]+2*b[2]+2*c[2]+d[2])/6
        if not all(isfinite(v) for v in (T,N,M)) or T <= 0:
            raise TorqueDragError("nonfinite result or unsupported compression")
    return T,N,M


def predict_minimum_curvature_curve(inputs: SpatialCurveInputs) -> dict:
    """Solve one sourced section with *one consistent* great-circle trajectory."""
    if not isinstance(inputs, SpatialCurveInputs):
        raise TorqueDragError("SpatialCurveInputs required")
    section = inputs.section
    if not isinstance(section, PlannedSection):
        raise TorqueDragError("source-qualified PlannedSection required")
    try:
        section.validate()
    except PlannedSectionError as exc:
        raise TorqueDragError(str(exc)) from exc
    if len(section.survey_stations) != 2:
        raise TorqueDragError("exactly two sourced survey stations required")
    if type(inputs.integration_steps) is not int or not 8 <= inputs.integration_steps <= 20000:
        raise TorqueDragError("integration_steps integer in 8..20000 required")
    a,b = section.survey_stations
    i0 = float(_number(a.inclination_deg,"top_inclination"))
    i1 = float(_number(b.inclination_deg,"bottom_inclination"))
    az0 = float(_number(a.azimuth_deg,"top_azimuth"))
    az1 = float(_number(b.azimuth_deg,"bottom_azimuth"))
    if not (0 <= i0 <= 90 and 0 <= i1 <= 90):
        raise TorqueDragError("inclinations 0..90 required")
    turn = _delta_azimuth(az0, az1)
    if abs(turn) > 90+1e-10:
        raise TorqueDragError("azimuth change >90 degrees per section unsupported")
    t0,t1 = _tangent(radians(i0),radians(az0)), _tangent(radians(i1),radians(az1))
    beta = acos(max(-1.0,min(1.0,_dot(t0,t1))))
    if beta >= pi-1e-7:
        raise TorqueDragError("180-degree dogleg unsupported")
    bottom = _require(inputs.bottom_tension,FORCE_N,"bottom_tension")
    mu = _require(inputs.axial_friction,COEFFICIENT,"axial_friction",positive=False)
    mu_rot = _require(inputs.rotational_friction,COEFFICIENT,"rotational_friction",positive=False)
    radius = _require(inputs.contact_radius,LENGTH_M,"contact_radius")
    if mu < 0 or mu_rot < 0:
        raise TorqueDragError("negative friction unsupported")
    od = float(section.pipe_outer_diameter.si(LENGTH_M,"pipe_outer_diameter"))
    if radius < od/2:
        raise TorqueDragError("contact radius smaller than pipe OD/2")
    static = section.calculate()
    L = float(static["results"]["section_length_md_m"])
    W = float(static["results"]["open_flooded_apparent_weight_n"])
    if W < 0:
        raise TorqueDragError("negative buoyed weight unsupported")
    if mu*beta > 30:
        raise TorqueDragError("excessive friction-dogleg product")
    w = W/L
    # The minimum-curvature station TVD must agree with the trajectory
    # actually used for force and gravity in this versioned solver.
    rf = 1.0 if beta < 1e-8 else 2.0/beta * (sin(beta/2)/cos(beta/2))
    model_tvd = L*(t0[2]+t1[2])*rf/2
    survey_tvd = float(static["results"]["delta_tvd_m"])
    if abs(model_tvd-survey_tvd) > max(1e-7, 1e-9*abs(survey_tvd)):
        raise TorqueDragError("minimum-curvature TVD inconsistent with sourced survey")
    outputs = {}
    for mode,label in ((1,"pickup"),(-1,"slackoff"),(0,"rotation")):
        T,N,M = _integrate(bottom,L,w,t0,t1,beta,mu,mu_rot,radius,
                           mode,inputs.integration_steps)
        outputs[label] = {
            "top_tension_n":str(T), "integrated_wall_contact_n":str(N)
        }
        if mode == 0:
            outputs[label]["contact_torque_nm"] = str(M)
    src = {name:{
        "value":str(getattr(inputs,name).value),
        "unit":getattr(inputs,name).unit,
        "source_id":getattr(inputs,name).source_id,
        "source_location":getattr(inputs,name).source_location,
        "source_revision":getattr(inputs,name).source_revision,
        "review_status":getattr(inputs,name).review_status
    } for name in ("bottom_tension","axial_friction","rotational_friction","contact_radius")}
    return {
        "case_id":section.case_id, "section_id":section.section_id,
        "model":"experimental-3d-minimum-curvature-soft-string-v0.1",
        "status":"unreviewed_inputs",
        "results":outputs,
        "dogleg_rad":str(beta),
        "section_buoyed_weight_n":str(W),
        "minimum_curvature_delta_tvd_m":str(model_tvd),
        "survey_delta_tvd_m":str(survey_tvd),
        "sources":{"planned_section":static["sources"],"minimum_curvature_inputs":src},
        "assumptions":[
            "one constant-mass and constant-friction two-station section",
            "unit tangent follows minimum-curvature great-circle interpolation",
            "gravity and normal reaction use the same trajectory",
            "independent pure pickup, slackoff, rotation, no combined motion",
            "ideal flexible string, no buckling/stiffness/contact-side state",
        ],
        "warning":"Experimental minimum-curvature 3D soft-string, not field-validated, no liner hanger load or OEM operating approval.",
    }
