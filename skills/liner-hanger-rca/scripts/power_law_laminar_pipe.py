"""LH-CALC-03: strict power-law fluid, fully developed laminar circular pipe.

Independent reference: BYU, Non-Newtonian Fluid Math, Eq. (7)-(8),
https://www.et.byu.edu/~wheeler/Non-Newtonian_Fluid_Math.pdf

tau = K * shear_rate**n, K in Pa*s**n, n dimensionless > 0.
DeltaP = (4 L / D) * K * [8 v / D * (3*n+1)/(4*n)]**n.

Steady incompressible isothermal time-independent *power law* and no slip.
Independent proof of laminar regime is required and caller-sourced but is
NOT authenticated by this module. It must never be interpreted as rig SPP,
Bingham/Herschel-Bulkley, annular, turbulent or OEM tool hydraulics.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi

from circulating_hydraulics import FlowSegment, HydraulicsUnavailable, _finite


@dataclass(frozen=True)
class PowerLawFluid:
    density_kg_m3: float
    consistency_pa_s_n: float
    flow_behavior_index: float
    rheology: str = "power_law"

    def __post_init__(self):
        if self.rheology != "power_law":
            raise HydraulicsUnavailable("power_law rheology required")
        _finite(self.density_kg_m3, "density_kg_m3", positive=True)
        _finite(self.consistency_pa_s_n, "consistency_pa_s_n", positive=True)
        _finite(self.flow_behavior_index, "flow_behavior_index", positive=True)
        # Extremely low or high exponent may overflow or be physically
        # unsupported by a measured rheogram; numeric limits are a
        # software applicability guard, not a qualified mud range.
        if not 0.1 <= self.flow_behavior_index <= 2:
            raise HydraulicsUnavailable(
                "power law exponent outside provisional 0.1..2 research range"
            )


def power_law_laminar_pipe_pressure_loss(
        fluid: PowerLawFluid, section: FlowSegment, flow_m3_s: float,
        *, laminar_regime_independently_confirmed: bool = False,
        regime_evidence_id: str = "") -> dict:
    """Published analytical pipe relation; fail closed without regime source.

    Evidence ID identifies caller's separate determination and is not
    independent endorsement or tested regime classification.
    """
    if not isinstance(fluid, PowerLawFluid) or not isinstance(section, FlowSegment):
        raise HydraulicsUnavailable("validated power-law fluid and flow section required")
    if section.kind != "pipe":
        raise HydraulicsUnavailable("power-law annular flow is unavailable")
    if type(laminar_regime_independently_confirmed) is not bool or (
            not laminar_regime_independently_confirmed):
        raise HydraulicsUnavailable("independently confirmed laminar regime required")
    if not isinstance(regime_evidence_id, str) or not regime_evidence_id.strip() or (
            len(regime_evidence_id) > 256):
        raise HydraulicsUnavailable("explicit laminar regime evidence identifier required")
    q = _finite(flow_m3_s, "flow_m3_s", nonnegative=True)
    d = section.outer_diameter_m  # Flow ID, not metallic OD.
    area = pi*d*d/4
    v = q/area
    n = fluid.flow_behavior_index
    k = fluid.consistency_pa_s_n
    shear = (8*v/d)*((3*n+1)/(4*n))
    try:
        wall_stress = k*shear**n
        dp = 4*section.length_m*wall_stress/d
    except OverflowError as exc:
        raise HydraulicsUnavailable("power-law computation overflow") from exc
    if not all(isfinite(x) and x >= 0 for x in (v,shear,wall_stress,dp)):
        raise HydraulicsUnavailable("nonfinite/nonphysical power-law pressure")
    return {
        "name":section.name,
        "flow_leg":section.flow_leg,
        "geometry":"pipe",
        "rheology":"power_law",
        "flow_m3_s":q,
        "mean_velocity_m_s":v,
        "flow_area_m2":area,
        "nominal_wall_shear_rate_s_1":shear,
        "wall_shear_stress_pa":wall_stress,
        "pressure_loss_pa":dp,
        "pressure_loss_bar":dp/100000,
        "model":"assumed_laminar_metzner_reed_power_law_pipe",
        "regime_evidence_id":regime_evidence_id,
        "flow_regime_evidence":"caller_declared_not_authenticated",
        "standpipe_pressure_pa":None,
        "engineering_acceptance":False,
        "excluded":["power_law_annulus","transition_or_turbulent",
                    "yield_stress","temperature_pressure_rheology",
                    "tool_restrictions","pressure_datum"],
    }
