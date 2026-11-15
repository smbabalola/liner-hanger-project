"""LH-CALC-03: Newtonian circular pipe laminar / turbulent, NO transition.

Source: USDA-NRCS Engineering Field Handbook Part 650 Ch3 (2009),
Darcy-Weisbach eq. 160, Re eq.161, laminar f=64/Re eq.157,
turbulent Colebrook-White eq.158 and comparison Swamee-Jain eq.159.
https://irrigationtoolbox.com/NEH/Part650EngineeringFieldHandbook/Part650Ch03-DRAFT.pdf

Research-only Newtonian single-phase steady, fully developed circular pipe.
Transition (2000<Re<4000) and non-Newtonian/turbulent annulus unavailable.
Roughness must be source-labelled and diameter interpreted as FLOW ID.
"""
from __future__ import annotations
from math import isfinite, log10, pi
from circulating_hydraulics import (
    NewtonianFluid,FlowSegment,HydraulicsUnavailable,_finite,
    segment_pressure_loss)


def newtonian_pipe_pressure_by_regime(
        fluid: NewtonianFluid, section: FlowSegment, flow_m3_s: float, *,
        absolute_roughness_m: float,
        roughness_source_id: str) -> dict:
    if not isinstance(fluid,NewtonianFluid) or not isinstance(section,FlowSegment):
        raise HydraulicsUnavailable("validated Newtonian pipe description required")
    if section.kind!="pipe":
        raise HydraulicsUnavailable("this turbulent correlation only supports circular pipe")
    eps=_finite(absolute_roughness_m,"absolute_roughness_m",nonnegative=True)
    if not isinstance(roughness_source_id,str) or not roughness_source_id.strip() or len(roughness_source_id)>256:
        raise HydraulicsUnavailable("source-labelled absolute roughness required")
    q=_finite(flow_m3_s,"flow_m3_s",nonnegative=True)
    d=section.outer_diameter_m
    if eps/d>.05:
        raise HydraulicsUnavailable("relative roughness >0.05 outside research scope")
    area=pi*d*d/4
    velocity=q/area
    re=fluid.density_kg_m3*velocity*d/fluid.dynamic_viscosity_pa_s
    if not isfinite(re):
        raise HydraulicsUnavailable("nonfinite Newtonian Reynolds")
    if q==0:
        dp=0.
        factor=None
        regime="zero_flow"
    elif re<=2000:
        base=segment_pressure_loss(fluid,section,q)
        dp=base["pressure_loss_pa"]
        factor=64/re
        regime="laminar"
    elif re<4000:
        raise HydraulicsUnavailable("transitional flow 2000 < Re < 4000 unavailable")
    elif re>1e8:
        raise HydraulicsUnavailable("turbulent Re above research range")
    else:
        # y=1/sqrt(f_Darcy); Colebrook: y=-2 log10(eps/(3.7D)+2.51*y/Re).
        def residual(y):
            return y+2*log10(eps/(3.7*d)+2.51*y/re)
        lo,hi=1.,100.
        if residual(lo)>=0 or residual(hi)<=0:
            raise HydraulicsUnavailable("Colebrook root not bracketed")
        for _ in range(72):
            mid=(lo+hi)/2
            if residual(mid)>0:
                hi=mid
            else:
                lo=mid
        factor=1/((lo+hi)/2)**2
        dp=factor*(section.length_m/d)*fluid.density_kg_m3*velocity**2/2
        regime="turbulent_colebrook"
    if not isfinite(dp) or dp<0:
        raise HydraulicsUnavailable("nonphysical/nonfinite pipe loss")
    return {
        "name":section.name,"flow_leg":section.flow_leg,
        "geometry":"pipe","rheology":"newtonian",
        "regime":regime,"reynolds":re,
        "darcy_friction_factor":factor,
        "absolute_roughness_m":eps,
        "roughness_source_id":roughness_source_id,
        "flow_m3_s":q,"mean_velocity_m_s":velocity,
        "pressure_loss_pa":dp,"pressure_loss_bar":dp/100000,
        "standpipe_pressure_pa":None,"engineering_acceptance":False,
        "excluded":["non_newtonian_turbulence","annulus_turbulence",
                    "transitional_flow","tool_restrictions",
                    "fluid_temperature","cuttings","surface_datum"],
    }
