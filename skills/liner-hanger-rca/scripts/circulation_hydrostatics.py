"""LH-CALC-03: research-only source-qualified static hydrostatic column balance.

For incompressible homogeneous density per vertical interval,
dP/d(TVD) = rho*g (TVD positive downward). The static pressure difference
between otherwise matching downflow/return surface reference elevations is

    P_down_surface - P_return_surface = g * (
        integral_return rho dTVD - integral_down rho dTVD
    )

before *any* frictional/acceleration/flow restrictions.

This is the hydrostatic *contribution* only, not SPP, ECD, tool pressure,
flowing pressure or an operational circulation envelope. No claim to
temperature/pressure-dependent density, gas influx, cuttings or U-tubing.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import fsum,isfinite

from circulating_hydraulics import HydraulicsUnavailable,_finite

GRAVITY_M_S2 = 9.80665


@dataclass(frozen=True)
class HydrostaticLayer:
    name: str
    leg: str
    top_tvd_m: float
    bottom_tvd_m: float
    density_kg_m3: float
    density_source_id: str
    datum: str

    def __post_init__(self):
        if not isinstance(self.name,str) or not self.name.strip():
            raise HydraulicsUnavailable("hydrostatic layer name required")
        if self.leg not in ("downstream","return"):
            raise HydraulicsUnavailable("hydrostatic leg must be downstream or return")
        top=_finite(self.top_tvd_m,"top_tvd_m",nonnegative=True)
        bottom=_finite(self.bottom_tvd_m,"bottom_tvd_m",positive=True)
        if bottom<=top:
            raise HydraulicsUnavailable("hydrostatic TVD interval must increase downward")
        _finite(self.density_kg_m3,"density_kg_m3",positive=True)
        if not isinstance(self.density_source_id,str) or not self.density_source_id.strip():
            raise HydraulicsUnavailable("source identity required for density")
        if len(self.density_source_id)>256:
            raise HydraulicsUnavailable("hydrostatic density source id too long")
        if not isinstance(self.datum,str) or not self.datum.strip() or len(self.datum)>128:
            raise HydraulicsUnavailable("explicit common vertical datum required")


def static_hydrostatic_imbalance(
        layers: list[HydrostaticLayer], *,
        gravity_m_s2: float = GRAVITY_M_S2) -> dict:
    """Compute separate signed down/return static column contributions.

    Both legs must cover EXACTLY the same continuous vertical range using
    a single explicit datum; this version does not extrapolate missing
    top/bottom layers or shift between unmatched measurement elevations.
    """
    if not isinstance(layers,(list,tuple)) or not layers or not all(
            isinstance(x,HydrostaticLayer) for x in layers):
        raise HydraulicsUnavailable("validated hydrostatic layers required")
    gravity=_finite(gravity_m_s2,"gravity_m_s2",positive=True)
    if abs(gravity-GRAVITY_M_S2)>1e-12:
        raise HydraulicsUnavailable("only standard gravity supported; no arbitrary g")
    ids=[x.name for x in layers]
    if len(set(ids))!=len(ids):
        raise HydraulicsUnavailable("duplicate hydrostatic layer id")
    datums={x.datum for x in layers}
    if len(datums)!=1:
        raise HydraulicsUnavailable("mismatched hydrostatic reference datums")
    legs={}
    for direction in ("downstream","return"):
        rows=sorted((x for x in layers if x.leg==direction),
                    key=lambda x:x.top_tvd_m)
        if not rows:
            raise HydraulicsUnavailable("both vertical flow columns required")
        for previous,current in zip(rows,rows[1:]):
            if current.top_tvd_m!=previous.bottom_tvd_m:
                raise HydraulicsUnavailable("hydrostatic vertical gap or overlap")
        legs[direction]=rows
    downstream,ret=legs["downstream"],legs["return"]
    if (downstream[0].top_tvd_m!=ret[0].top_tvd_m or
            downstream[-1].bottom_tvd_m!=ret[-1].bottom_tvd_m):
        raise HydraulicsUnavailable("legs do not cover the same TVD endpoints")
    contributions=[]
    sums={}
    for direction,rows in legs.items():
        subtotal=[]
        for layer in rows:
            head=layer.density_kg_m3*gravity*(
                layer.bottom_tvd_m-layer.top_tvd_m)
            if not isfinite(head):
                raise HydraulicsUnavailable("nonfinite static hydrostatic term")
            subtotal.append(head)
            contributions.append({
                "name":layer.name,"leg":direction,"datum":layer.datum,
                "top_tvd_m":layer.top_tvd_m,
                "bottom_tvd_m":layer.bottom_tvd_m,
                "density_kg_m3":layer.density_kg_m3,
                "density_source_id":layer.density_source_id,
                "static_column_head_pa":head,
            })
        sums[direction]=fsum(subtotal)
    delta=sums["return"]-sums["downstream"]
    if not isfinite(delta):
        raise HydraulicsUnavailable("nonfinite hydrostatic imbalance")
    return {
        "status":"static_hydrostatic_contribution_only",
        "datum":downstream[0].datum,
        "surface_and_bottom_tvd_endpoints_m":[
            downstream[0].top_tvd_m,downstream[-1].bottom_tvd_m],
        "downstream_static_column_head_pa":sums["downstream"],
        "return_static_column_head_pa":sums["return"],
        "downstream_surface_minus_return_surface_hydrostatic_pa":delta,
        "downstream_surface_minus_return_surface_hydrostatic_bar":delta/1e5,
        "layers":contributions,
        "gravity_m_s2":gravity,
        "standpipe_pressure_pa":None,
        "engineering_acceptance":False,
        "excluded":["friction","nozzle_and_tool_restrictions",
                    "pressure_gauge_location_and_datum",
                    "temperature_pressure_density_variation",
                    "gas_and_cuttings","multiphase","dynamic_u_tubing",
                    "surface_backpressure","flowing_pressure"],
    }
