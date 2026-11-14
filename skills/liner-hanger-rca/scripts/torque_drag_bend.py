"""LH-CALC-02: exact tension-induced contact across an ideal WEIGHTLESS bend.

This is a capstan/rope limit case for a flexible string in continuous contact,
NOT a weighted drilling-string dogleg solver. It is deliberately independent
of the straight-profile model until a weighted-curvature formulation is
validated. No field pressures, setting limits, or hookload are inferred.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, Overflow, localcontext

from engineering_primitives import LENGTH_M
from planned_job_section import SourcedNumber, PlannedSectionError
from torque_drag_straight import FORCE_N, TorqueDragError

ANGLE_RAD = {"rad": Decimal("1"), "deg": Decimal("0.017453292519943295769236907684886127134428718885417")}
COEFFICIENT = {"1": Decimal("1")}
PI = Decimal("3.1415926535897932384626433832795028841971693993751")


@dataclass(frozen=True)
class IdealBendInputs:
    bend_id: str
    bottom_tension: SourcedNumber
    bend_angle: SourcedNumber
    axial_friction: SourcedNumber
    rotational_friction: SourcedNumber
    contact_radius: SourcedNumber
    zero_distributed_weight: bool


def _sourced(value, units, name, *, positive=True):
    if not isinstance(value, SourcedNumber):
        raise TorqueDragError(f"{name}: SourcedNumber required")
    try:
        return value.si(units, name, positive=positive)
    except PlannedSectionError as exc:
        raise TorqueDragError(str(exc)) from exc


def predict_ideal_bend(bend: IdealBendInputs) -> dict:
    """Exact capstan benchmark for a flexible, weightless single bend.

    Let T be bottom tension, theta the total turning angle, mu axial Coulomb
    friction. Then T_up,pickup=T exp(+mu theta), and T_up,slackoff=T exp(-mu
    theta). In pure rotation with no axial travel, axial tension stays T,
    integrated normal contact=T theta and torque=mu_rot*T*theta*r.

    Normal contact while sliding: Npickup=T*(exp(mu theta)-1)/mu;
    Nslackoff=T*(1-exp(-mu theta))/mu. At mu=0 use T theta by continuity.
    The normal reactions differ for each mode; no cross-contamination.
    """
    if not isinstance(bend, IdealBendInputs):
        raise TorqueDragError("IdealBendInputs required")
    if not isinstance(bend.bend_id, str) or not bend.bend_id.strip():
        raise TorqueDragError("bend_id required")
    if bend.zero_distributed_weight is not True:
        raise TorqueDragError("only explicitly weightless bend is implemented")
    bottom = _sourced(bend.bottom_tension, FORCE_N, "bottom_tension")
    angle = _sourced(bend.bend_angle, ANGLE_RAD, "bend_angle", positive=False)
    mu = _sourced(bend.axial_friction, COEFFICIENT, "axial_friction", positive=False)
    mu_rot = _sourced(bend.rotational_friction, COEFFICIENT,
                      "rotational_friction", positive=False)
    radius = _sourced(bend.contact_radius, LENGTH_M, "contact_radius")
    if angle < 0 or angle > PI:
        raise TorqueDragError("bend_angle must be 0..pi radians")
    if mu < 0 or mu_rot < 0:
        raise TorqueDragError("friction coefficients must be nonnegative")
    try:
        with localcontext() as ctx:
            ctx.prec = 34
            # Large exponents are not physically meaningful here. Fail closed
            # before decimal exponentiation can overflow or hide instability.
            exponent = mu * angle
            if exponent > Decimal("50"):
                raise TorqueDragError("excessive friction-angle product unsupported")
            pickup = bottom * exponent.exp()
            slackoff = bottom * (-exponent).exp()
            rotation = bottom
            pure_rot_normal = bottom * angle
            if mu == 0:
                pickup_normal = pure_rot_normal
                slackoff_normal = pure_rot_normal
            else:
                pickup_normal = (pickup - bottom) / mu
                slackoff_normal = (bottom - slackoff) / mu
            pure_rotation_torque = mu_rot * pure_rot_normal * radius
    except (InvalidOperation, Overflow) as exc:
        raise TorqueDragError("non-finite capstan solution") from exc
    inputs = {name: {
        "source_id": getattr(bend, name).source_id,
        "source_location": getattr(bend, name).source_location,
        "source_revision": getattr(bend, name).source_revision,
        "review_status": getattr(bend, name).review_status,
        "value": str(getattr(bend, name).value),
        "unit": getattr(bend, name).unit,
    } for name in ("bottom_tension", "bend_angle", "axial_friction",
                   "rotational_friction", "contact_radius")}
    reviewed = all(v["review_status"] == "reviewed" for v in inputs.values())
    return {
        "bend_id": bend.bend_id,
        "model": "ideal-weightless-capstan-dogleg-v0.1",
        "status": "numeric_candidate_only" if reviewed else "unreviewed_inputs",
        "results": {
            "top_pickup_tension_n": str(pickup),
            "top_slackoff_tension_n": str(slackoff),
            "top_pure_rotation_tension_n": str(rotation),
            "pickup_integrated_contact_normal_n": str(pickup_normal),
            "slackoff_integrated_contact_normal_n": str(slackoff_normal),
            "pure_rotation_integrated_contact_normal_n": str(pure_rot_normal),
            "pure_rotation_contact_torque_nm": str(pure_rotation_torque),
        },
        "sources": inputs,
        "assumptions": [
            "ideal perfectly flexible string in continuous wall contact",
            "zero distributed gravity / buoyed weight within bend",
            "source-supplied positive bottom tension, 0..180 degree total dogleg",
            "Coulomb friction acts against pure axial travel, separate pure rotation",
            "pure rotation has no axial sliding, axial tension unchanged",
            "frictional contact torque only; no bit/tool torque or stiffness",
            "no pressure-end load, buckling, slack, twist, dynamic or transient forces",
        ],
        "warning": "Ideal weightless limiting benchmark ONLY; not a weighted curved well model, rig hookload, OEM specification or operating instruction.",
    }
