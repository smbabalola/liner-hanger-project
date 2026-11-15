"""LH-CALC-03: bounded Newtonian laminar circulating-hydraulics primitives.

SI-only; fictional or independently sourced data. No OEM/field approval.
Hagen-Poiseuille pipe and exact steady fully-developed concentric annulus
solutions, valid ONLY when the calculated Reynolds number is <= 2000.
No eccentricity, cuttings, rotation, temperature effects, non-Newtonian
behavior, fittings, bit nozzles, acceleration, pump efficiency or SPP claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi
from typing import Literal


class HydraulicsUnavailable(ValueError):
    """Unsupported model or invalid input; never return misleading pressure."""


def _finite(value: object, name: str, *, positive: bool = False,
            nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise HydraulicsUnavailable(f"{name}: finite numeric SI value required")
    value = float(value)
    if not isfinite(value) or (positive and value <= 0) or (
        nonnegative and value < 0
    ):
        raise HydraulicsUnavailable(f"{name}: out-of-range finite SI value")
    return value


@dataclass(frozen=True)
class NewtonianFluid:
    density_kg_m3: float
    dynamic_viscosity_pa_s: float
    rheology: str = "newtonian"

    def __post_init__(self):
        if self.rheology != "newtonian":
            raise HydraulicsUnavailable("unsupported rheology; only newtonian")
        _finite(self.density_kg_m3, "density_kg_m3", positive=True)
        _finite(self.dynamic_viscosity_pa_s, "dynamic_viscosity_pa_s", positive=True)


@dataclass(frozen=True)
class FlowSegment:
    name: str
    kind: Literal["pipe", "concentric_annulus"]
    length_m: float
    outer_diameter_m: float
    inner_diameter_m: float = 0.0
    # All dimensions are geometrical FLOW boundaries, not metal OD:
    # pipe uses outer_diameter_m as its FLOW ID and inner_diameter_m=0.
    # annulus uses outer_diameter_m=bore/outer flow boundary and
    # inner_diameter_m=inner tubular outer radius boundary (diameters).
    flow_leg: Literal["downstream", "return"] = "downstream"

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise HydraulicsUnavailable("segment name required")
        if self.kind not in ("pipe", "concentric_annulus"):
            raise HydraulicsUnavailable("unsupported flow geometry")
        if self.flow_leg not in ("downstream", "return"):
            raise HydraulicsUnavailable("invalid circulation leg")
        _finite(self.length_m, "length_m", nonnegative=True)
        outer = _finite(self.outer_diameter_m, "outer_diameter_m", positive=True)
        inner = _finite(self.inner_diameter_m, "inner_diameter_m", nonnegative=True)
        if self.kind == "pipe" and inner != 0:
            raise HydraulicsUnavailable("pipe inner boundary must be zero")
        if self.kind == "concentric_annulus" and not (0 < inner < outer):
            raise HydraulicsUnavailable("annulus must have 0 < inner < outer")


def segment_pressure_loss(fluid: NewtonianFluid, segment: FlowSegment,
                          flow_m3_s: float) -> dict:
    """Evaluate exact laminar solution, rejecting unsupported flow regimes.

    Hagen-Poiseuille circular pipe: dp=128 mu L Q /(pi D^4).
    Concentric annulus: Q=pi dp/(8 mu L) *
      [Ro^4-Ri^4-(Ro^2-Ri^2)^2 / ln(Ro/Ri)].
    The concentric-annulus analytical solution assumes fixed walls and
    fully developed laminar isothermal incompressible Newtonian flow.
    """
    if not isinstance(fluid, NewtonianFluid) or not isinstance(segment, FlowSegment):
        raise HydraulicsUnavailable("validated fluid and segment required")
    q = _finite(flow_m3_s, "flow_m3_s", nonnegative=True)
    rho, mu = fluid.density_kg_m3, fluid.dynamic_viscosity_pa_s
    d_outer = segment.outer_diameter_m
    d_inner = segment.inner_diameter_m
    area = pi * (d_outer*d_outer-d_inner*d_inner)/4.0
    velocity = q/area
    hydraulic_d = d_outer - d_inner
    reynolds = rho*velocity*hydraulic_d/mu
    if not isfinite(reynolds):
        raise HydraulicsUnavailable("nonfinite Reynolds number")
    if q and reynolds > 2000:
        raise HydraulicsUnavailable(
            f"laminar-only model: Reynolds {reynolds:.6g} > 2000; "
            "transition/turbulent unavailable"
        )
    if q == 0 or segment.length_m == 0:
        dp = 0.0
    elif segment.kind == "pipe":
        dp = 128*mu*segment.length_m*q/(pi*d_outer**4)
    else:
        ro, ri = d_outer/2, d_inner/2
        # Scale by Ro**4 to avoid subtracting large/very small powers.
        x = ri/ro
        factor = 1-x**4-(1-x*x)**2/log(1/x)
        if not isfinite(factor) or factor <= 0:
            raise HydraulicsUnavailable(
                "annular gap too narrow for numerically stable evaluation"
            )
        dp = 8*mu*segment.length_m*q/(pi*ro**4*factor)
    if not isfinite(dp) or dp < 0:
        raise HydraulicsUnavailable("nonfinite/nonphysical pressure loss")
    return {
        "name": segment.name,
        "flow_leg": segment.flow_leg,
        "geometry": segment.kind,
        "flow_m3_s": q,
        "flow_area_m2": area,
        "mean_velocity_m_s": velocity,
        "reynolds": reynolds,
        "pressure_loss_pa": dp,
        "pressure_loss_bar": dp/100000,
        "model": "newtonian_fully_developed_laminar",
        "engineering_acceptance": False,
    }


def circulation_friction(fluid: NewtonianFluid, segments: list[FlowSegment],
                         flow_m3_s: float) -> dict:
    """Aggregate modeled straight-segment friction only; NEVER report SPP.

    A total friction estimate is not a rig standpipe pressure: bit nozzles,
    bends, tool restrictions, surface lines, hydrostatic differences and
    reference pressure/boundary conditions can remain unmodeled.
    """
    if not isinstance(segments, (list, tuple)) or not segments:
        raise HydraulicsUnavailable("nonempty validated flow segments required")
    names = [s.name for s in segments if isinstance(s, FlowSegment)]
    if len(names) != len(segments) or len(set(names)) != len(names):
        raise HydraulicsUnavailable("unique validated segment names required")
    results = [segment_pressure_loss(fluid, s, flow_m3_s) for s in segments]
    total = sum(row["pressure_loss_pa"] for row in results)
    if not isfinite(total):
        raise HydraulicsUnavailable("nonfinite total friction")
    return {
        "status": "partial_circuit_friction_only",
        "segments": results,
        "modeled_straight_segment_friction_pa": total,
        "modeled_straight_segment_friction_bar": total/100000,
        "standpipe_pressure_pa": None,
        "engineering_acceptance": False,
        "excluded": [
            "bit_nozzle_and_other_restrictions", "surface_line_minor_losses",
            "hydrostatic_difference", "cuttings_and_rotation",
            "pump_and_pressure_datum", "non_newtonian_rheology",
        ],
    }
