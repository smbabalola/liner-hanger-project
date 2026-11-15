"""LH-CALC-03: research-only concentric power-law annulus laminar solver.

Deterre et al. (2020), Journal of Non-Newtonian Fluid Mechanics 285, 104392,
doi:10.1016/j.jnnfm.2020.104392, steady power-law annulus axial momentum
balance and zero-shear radius (Eqs. 6, 7, 13, 17):
https://www.sciencedirect.com/science/article/pii/S037702572030152X

Exact governing radial stress: |tau(r)| = G/2*|r_m^2/r-r|, where
G=-dp/dz>0 and ri<r_m<ro. Constitutive law is
|dv/dr|=(|tau|/K)**(1/n), with both walls fixed and no slip.

We numerically solve equal velocity rise from each wall to r_m, then
integrate volumetric throughput; pressure gradient scales as Q**n.
No approximate hydraulic-diameter substitution, turbulent prediction,
eccentricity, rotation, yield stress, cuttings, compressibility or SPP.
"""
from __future__ import annotations

from math import isfinite, pi

from circulating_hydraulics import FlowSegment, HydraulicsUnavailable, _finite
from power_law_laminar_pipe import PowerLawFluid


def _simpson(f, a, b, steps):
    h = (b-a)/steps
    total = f(a)+f(b)
    for j in range(1,steps):
        total += (4 if j%2 else 2)*f(a+j*h)
    return total*h/3


def _coefficient(ri, ro, n, steps):
    p=1/n
    def inner_stress(r,rm):
        return max(0.,(rm-r)*(rm+r)/r)
    def outer_stress(r,rm):
        return max(0.,(r-rm)*(r+rm)/r)
    def imbalance(rm):
        a=_simpson(lambda r:inner_stress(r,rm)**p,ri,rm,steps)
        b=_simpson(lambda r:outer_stress(r,rm)**p,rm,ro,steps)
        return a-b
    low,high=ri,ro
    for _ in range(56):
        mid=(low+high)/2
        if imbalance(mid)>0:
            high=mid
        else:
            low=mid
    rm=(low+high)/2
    inner=_simpson(
        lambda r:(rm*rm-r*r)*inner_stress(r,rm)**p,
        ri,rm,steps)
    outer=_simpson(
        lambda r:(r*r-rm*rm)*outer_stress(r,rm)**p,
        rm,ro,steps)
    coeff=pi*(inner+outer)
    if not (isfinite(coeff) and coeff>0 and ri<rm<ro):
        raise HydraulicsUnavailable("annular radial integration not resolved")
    return rm,coeff


def power_law_laminar_annulus_pressure_loss(
        fluid: PowerLawFluid, section: FlowSegment, flow_m3_s: float,
        *, laminar_regime_independently_confirmed: bool = False,
        regime_evidence_id: str = "", quadrature_steps: int = 512) -> dict:
    """Solve stationary no-slip power-law concentric annular flow.

    Result is a research prediction of component friction only. Numerical
    refinement difference is exposed, NOT proof of external physical validity.
    """
    if not isinstance(fluid,PowerLawFluid) or not isinstance(section,FlowSegment):
        raise HydraulicsUnavailable("validated power-law fluid and annulus required")
    if section.kind!="concentric_annulus":
        raise HydraulicsUnavailable("power-law annulus model requires concentric_annulus")
    if type(laminar_regime_independently_confirmed) is not bool or (
            not laminar_regime_independently_confirmed):
        raise HydraulicsUnavailable("independent laminar-regime confirmation required")
    if not isinstance(regime_evidence_id,str) or not regime_evidence_id.strip() or (
            len(regime_evidence_id)>256):
        raise HydraulicsUnavailable("laminar-regime source identifier required")
    if type(quadrature_steps) is not int or not 64<=quadrature_steps<=4096 or (
            quadrature_steps%2):
        raise HydraulicsUnavailable("even quadrature_steps in 64..4096 required")
    q=_finite(flow_m3_s,"flow_m3_s",nonnegative=True)
    ri=section.inner_diameter_m/2
    ro=section.outer_diameter_m/2
    ratio=ri/ro
    # Geometry is deliberately conservative until high-confinement and
    # slender-core quadrature conditioning are independently reviewed.
    if not 0.15<=ratio<=0.85:
        raise HydraulicsUnavailable(
            "annulus radius ratio outside bounded 0.15..0.85 research scope")
    if not 0.3<=fluid.flow_behavior_index<=1.5:
        raise HydraulicsUnavailable(
            "annulus exponent outside bounded 0.3..1.5 research scope")
    if not q or not section.length_m:
        dp=gradient=0.
        # Zero flow has no identified maximum-velocity location; zero
        # length has no distributed developed-flow field to locate.
        rm=None
        rel_error=0.
    else:
        rm,c=_coefficient(ri,ro,fluid.flow_behavior_index,quadrature_steps)
        gradient=2*fluid.consistency_pa_s_n*(q/c)**fluid.flow_behavior_index
        dp=gradient*section.length_m
        _,c_refined=_coefficient(ri,ro,fluid.flow_behavior_index,
                               min(4096,quadrature_steps*2))
        reference=2*fluid.consistency_pa_s_n*(
            q/c_refined)**fluid.flow_behavior_index*section.length_m
        rel_error=abs(dp-reference)/reference
        if (not all(isfinite(x) for x in (dp,reference,rel_error)) or
                rel_error>0.002):
            raise HydraulicsUnavailable(
                "annular integration unstable; insufficient convergence")
    if not (isfinite(dp) and dp>=0 and isfinite(gradient)):
        raise HydraulicsUnavailable("annular pressure nonfinite")
    return {
        "name":section.name,"flow_leg":section.flow_leg,
        "geometry":"concentric_annulus","rheology":"power_law",
        "flow_m3_s":q,
        "pressure_loss_pa":dp,"pressure_loss_bar":dp/1e5,
        "pressure_gradient_pa_m":gradient,
        "zero_shear_radius_m":rm,
        "quadrature_steps":quadrature_steps,
        "relative_refinement_difference":rel_error,
        "model":"experimental_power_law_stationary_concentric_annulus_laminar",
        "regime_evidence_id":regime_evidence_id,
        "flow_regime_evidence":"caller_declared_not_authenticated",
        "standpipe_pressure_pa":None,
        "engineering_acceptance":False,
        "excluded":["eccentricity","rotation","yield_stress",
                    "thermal_rheology","cuttings","transition_or_turbulence",
                    "pressure_datum","OEM_tool_pressure"],
    }
