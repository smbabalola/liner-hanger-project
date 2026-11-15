"""LH-CALC-03: research-only Buckingham-Reiner Bingham-plastic pipe model.

Source: Perry's Chemical Engineers' Handbook (7th ed.), Fluid and
Particle Dynamics, Eq. 6-59; Buckingham-Reiner laminar pipe relation:
Q = pi*D**3*tau_w/(32*mu_p) * (1 - 4*a/3 + a**4/3),
a=tau_y/tau_w, tau_w=delta_P*D/(4*L).

Reference public excerpt:
https://schneider.cheme.cmu.edu/Files/Perry%27s%20Chemical%20Engineers%27%20Handbook%207th%20Edition/6.%20Fluid%20and%20Particle%20Dynamics.pdf

This is a mathematical calculation for independently confirmed, steady,
fully developed, no-slip, isothermal laminar Bingham flow in a *circular
pipe only*. No annulus, turbulence, cuttings, sag, thermal or rig pressure.
The Newtonian-based 'plastic Reynolds' screening is NOT a proven
Bingham transition boundary; flow-regime evidence must be independent.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi

from circulating_hydraulics import FlowSegment, HydraulicsUnavailable, _finite


@dataclass(frozen=True)
class BinghamFluid:
    density_kg_m3: float
    plastic_viscosity_pa_s: float
    yield_stress_pa: float
    rheology: str = "bingham_plastic"

    def __post_init__(self):
        if self.rheology != "bingham_plastic":
            raise HydraulicsUnavailable("bingham_plastic rheology required")
        _finite(self.density_kg_m3, "density_kg_m3", positive=True)
        _finite(self.plastic_viscosity_pa_s, "plastic_viscosity_pa_s", positive=True)
        _finite(self.yield_stress_pa, "yield_stress_pa", nonnegative=True)


def _flow_at_wall_stress(tau_w, tau_y, mu, diameter):
    if tau_w <= tau_y:
        return 0.0
    a = tau_y / tau_w
    # Exact algebraic factorisation; avoids subtractive cancellation
    # when the yielded shear layer is tiny.
    factor = (1-a)**2*(a*a+2*a+3)/3
    return pi*diameter**3*tau_w*factor/(32*mu)


def bingham_pipe_laminar_pressure_loss(
        fluid: BinghamFluid, segment: FlowSegment, flow_m3_s: float,
        *, laminar_regime_independently_confirmed: bool = False) -> dict:
    """Invert the exact Buckingham-Reiner flow relation by bracketing.

    Caller must supply a separately established flow-regime confirmation.
    This boolean is an explicit *assertion*, not independently verified
    evidence; engineering_acceptance remains False. Regime verification,
    including evidence of no transition, remains a human responsibility.
    """
    if not isinstance(fluid, BinghamFluid) or not isinstance(segment, FlowSegment):
        raise HydraulicsUnavailable("Bingham fluid and validated section required")
    if segment.kind != "pipe":
        raise HydraulicsUnavailable("Bingham annular flow is not implemented")
    if type(laminar_regime_independently_confirmed) is not bool or (
            not laminar_regime_independently_confirmed):
        raise HydraulicsUnavailable(
            "independent laminar-regime confirmation required; no Bingham transition model"
        )
    q = _finite(flow_m3_s, "flow_m3_s", nonnegative=True)
    d = segment.outer_diameter_m  # Flow ID, documented in FlowSegment.
    L = segment.length_m
    mu = fluid.plastic_viscosity_pa_s
    tau_y = fluid.yield_stress_pa
    area = pi*d*d/4
    velocity = q/area
    # No claim this plastic Reynolds number determines Bingham transition.
    plastic_re = fluid.density_kg_m3*velocity*d/mu
    if not isfinite(plastic_re):
        raise HydraulicsUnavailable("nonfinite plastic Reynolds number")
    if not q or not L:
        dp = tau = 0.0
    elif tau_y == 0:
        # Exact Newtonian limit, also avoids unnecessary root iteration.
        dp = 128*mu*L*q/(pi*d**4)
        tau = dp*d/(4*L)
    else:
        # Physical root is strictly above tau_y. The unphysical
        # sub-yield root of the quartic is explicitly excluded.
        low = tau_y
        high = max(tau_y*2, 8*mu*velocity/d + tau_y*2)
        for _ in range(1024):
            if _flow_at_wall_stress(high, tau_y, mu, d) >= q:
                break
            high *= 2
            if not isfinite(high):
                raise HydraulicsUnavailable("Bingham bracket overflows")
        else:
            raise HydraulicsUnavailable("Bingham wall-stress root unbracketed")
        for _ in range(150):
            mid = low+(high-low)/2
            if mid <= low or mid >= high:
                break
            if _flow_at_wall_stress(mid,tau_y,mu,d) < q:
                low = mid
            else:
                high = mid
        tau = (low+high)/2
        dp = 4*L*tau/d
    if not (isfinite(dp) and dp >= 0 and isfinite(tau)):
        raise HydraulicsUnavailable("Bingham friction result not finite")
    return {
        "name": segment.name,
        "flow_leg": segment.flow_leg,
        "geometry": "pipe",
        "rheology": "bingham_plastic",
        "flow_m3_s": q,
        "flow_area_m2": area,
        "mean_velocity_m_s": velocity,
        "plastic_reynolds_screen_only": plastic_re,
        "wall_shear_stress_pa": tau,
        "pressure_loss_pa": dp,
        "pressure_loss_bar": dp/1e5,
        "model": "assumed_laminar_buckingham_reiner_pipe",
        "flow_regime_evidence": "caller_asserted_not_independently_verified",
        "standpipe_pressure_pa": None,
        "engineering_acceptance": False,
        "excluded": ["concentric_annulus", "turbulent_transition",
                     "yield_stress_time_dependence", "tool_restrictions",
                     "temperature_and_solid_effects", "pressure_datum"],
    }
