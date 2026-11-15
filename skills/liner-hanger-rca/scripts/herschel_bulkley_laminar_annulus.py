"""Experimental LH-CALC-03 stationary concentric Herschel-Bulkley annulus.

Research sources: Huilgol & Georgiou, JNNFM 285 (2020) 104401,
doi:10.1016/j.jnnfm.2020.104401, viscoplastic no-slip annular flow,
and 2025 Journal of Petroleum Exploration and Production Technology,
doi:10.1007/s13202-024-01919-z, plug/laminar annular flow.

Exact axial momentum balance: tau(r) = G/2*(r0**2/r-r), G=-dp/dz>0.
Constitutive law: |du/dr|=(max(|tau|-tau_y,0)/K)**(1/n).
The unknown zero-stress r0 is found from equal inner/outer no-slip
velocity rises. The flux is then integrated via the radial first moment.
A second bisection finds G for the user's Q. The plug region is included
automatically where |tau| <= tau_y, never replaced with pipe hydraulics.

NO turbulent/transition/rotating/eccentric/suspension/temperature model.
Regime evidence is caller-declared and NOT validated; field acceptance false.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite,pi
from circulating_hydraulics import FlowSegment,HydraulicsUnavailable,_finite


@dataclass(frozen=True)
class HerschelBulkleyFluid:
    density_kg_m3: float
    consistency_pa_s_n: float
    flow_behavior_index: float
    yield_stress_pa: float
    rheology: str = "herschel_bulkley"

    def __post_init__(self):
        if self.rheology!="herschel_bulkley":
            raise HydraulicsUnavailable("herschel_bulkley rheology required")
        _finite(self.density_kg_m3,"density_kg_m3",positive=True)
        _finite(self.consistency_pa_s_n,"consistency_pa_s_n",positive=True)
        n=_finite(self.flow_behavior_index,"flow_behavior_index",positive=True)
        _finite(self.yield_stress_pa,"yield_stress_pa",nonnegative=True)
        if not .3<=n<=1.5:
            raise HydraulicsUnavailable("annulus index outside research scope 0.3..1.5")


def _simpson(fn,a,b,steps):
    h=(b-a)/steps
    s=fn(a)+fn(b)
    for i in range(1,steps):
        s+=(4 if i%2 else 2)*fn(a+h*i)
    return s*h/3


def _flux_at_gradient(ri,ro,n,k,tau_y,g,steps):
    power=1/n
    def inner_shear(r,r0):
        stress=.5*g*(r0*r0/r-r)
        return (max(0.,stress-tau_y)/k)**power
    def outer_shear(r,r0):
        stress=.5*g*(r-r0*r0/r)
        return (max(0.,stress-tau_y)/k)**power
    def residual(r0):
        return (_simpson(lambda r:inner_shear(r,r0),ri,r0,steps)
                -_simpson(lambda r:outer_shear(r,r0),r0,ro,steps))
    lo,hi=ri,ro
    for _ in range(46):
        mid=(lo+hi)/2
        if residual(mid)>0:
            hi=mid
        else:
            lo=mid
    r0=(lo+hi)/2
    inside=_simpson(lambda r:(r0*r0-r*r)*inner_shear(r,r0),ri,r0,steps)
    outside=_simpson(lambda r:(r*r-r0*r0)*outer_shear(r,r0),r0,ro,steps)
    flux=pi*(inside+outside)
    if not isfinite(flux) or flux<0:
        raise HydraulicsUnavailable("nonfinite annular flux")
    inner_wall=.5*g*(r0*r0/ri-ri)
    outer_wall=.5*g*(ro-r0*r0/ro)
    return flux,r0,inner_wall,outer_wall


def hb_laminar_annulus_pressure_loss(
        fluid:HerschelBulkleyFluid, segment:FlowSegment, flow_m3_s:float, *,
        laminar_regime_independently_confirmed:bool=False,
        regime_evidence_id:str="", quadrature_steps:int=128) -> dict:
    if not isinstance(fluid,HerschelBulkleyFluid) or not isinstance(segment,FlowSegment):
        raise HydraulicsUnavailable("validated Herschel-Bulkley fluid and segment required")
    if segment.kind!="concentric_annulus":
        raise HydraulicsUnavailable("only concentric annular geometry supported")
    if laminar_regime_independently_confirmed is not True:
        raise HydraulicsUnavailable("independent laminar-regime declaration required")
    if not isinstance(regime_evidence_id,str) or not regime_evidence_id.strip() or len(regime_evidence_id)>256:
        raise HydraulicsUnavailable("source-labelled laminar-regime evidence required")
    if type(quadrature_steps) is not int or quadrature_steps<64 or quadrature_steps>1024 or quadrature_steps%2:
        raise HydraulicsUnavailable("quadrature_steps must be even in 64..1024")
    q=_finite(flow_m3_s,"flow_m3_s",nonnegative=True)
    ri,ro=segment.inner_diameter_m/2,segment.outer_diameter_m/2
    if not .2<=ri/ro<=.8:
        raise HydraulicsUnavailable("annular radius ratio outside 0.2..0.8 research scope")
    if q==0 and fluid.yield_stress_pa>0 and segment.length_m>0:
        raise HydraulicsUnavailable("zero-flow yield-stress gradient indeterminate")
    if q==0 or segment.length_m==0:
        g=dp=0.
        r0=None
        inner=outer=None
        err=0.
    else:
        k=fluid.consistency_pa_s_n
        n=fluid.flow_behavior_index
        tau_y=fluid.yield_stress_pa
        lo=0.
        hi=max(1.,10*k*(q/(pi*(ro*ro-ri*ri)))**n/(ro-ri)**(n+1),
               10*tau_y/(ro-ri))
        for _ in range(128):
            computed,_,_,_=_flux_at_gradient(ri,ro,n,k,tau_y,hi,quadrature_steps)
            if computed>=q:
                break
            hi*=2
            if not isfinite(hi):
                raise HydraulicsUnavailable("annular pressure-gradient bracket overflow")
        else:
            raise HydraulicsUnavailable("annular pressure-gradient root unbracketed")
        for _ in range(54):
            mid=(lo+hi)/2
            computed,_,_,_=_flux_at_gradient(ri,ro,n,k,tau_y,mid,quadrature_steps)
            if computed<q:
                lo=mid
            else:
                hi=mid
        g=(lo+hi)/2
        _,r0,inner,outer=_flux_at_gradient(ri,ro,n,k,tau_y,g,quadrature_steps)
        dp=g*segment.length_m
        check,_,_,_=_flux_at_gradient(ri,ro,n,k,tau_y,g,quadrature_steps*2)
        err=abs(check-q)/q
        if not isfinite(err) or err>.005:
            raise HydraulicsUnavailable("annular integration insufficiently converged")
    if not isfinite(dp) or dp<0:
        raise HydraulicsUnavailable("nonfinite annular pressure loss")
    return {
        "name":segment.name,"flow_leg":segment.flow_leg,
        "geometry":"concentric_annulus","rheology":"herschel_bulkley",
        "model":"experimental_laminar_hb_concentric_annulus",
        "flow_m3_s":q,"pressure_loss_pa":dp,
        "pressure_loss_bar":dp/1e5,"pressure_gradient_pa_m":g,
        "zero_stress_radius_m":r0,
        "inner_wall_shear_stress_pa":inner,
        "outer_wall_shear_stress_pa":outer,
        "relative_flux_refinement_difference":err,
        "regime_evidence_id":regime_evidence_id,
        "flow_regime_evidence":"caller_declared_not_authenticated",
        "standpipe_pressure_pa":None,"engineering_acceptance":False,
        "excluded":["eccentricity","rotation","turbulence","transition",
                    "solids","temperature","compressibility","OEM_tool_restrictions"],
    }
