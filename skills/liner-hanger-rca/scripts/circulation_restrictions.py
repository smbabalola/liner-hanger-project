"""LH-CALC-03: bounded incompressible orifice/nozzle differential estimate.

Q = Cd*A*sqrt(2*dP/rho), hence dP=rho/2*(Q/(Cd*A))**2.
Source: Vents and Orifice Flow, CMHC (1995), §2.2, archived at
https://publications.gc.ca/collections/collection_2018/schl-cmhc/nh17/NH17-201-1995-eng.pdf
Also Applied Drilling Circulation Systems: Hydraulics, Calculations and
Models, §2, bit nozzle kinetic pressure loss (source register).

This assumes a *known calibrated* discharge coefficient, constant density,
incompressible single-phase steady flow, a valid orifice/nozzle geometry,
no cavitation and negligible approach-velocity correction. Not valid as an
arbitrary liner-hanger tool restriction or downhole differential limit.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from circulating_hydraulics import HydraulicsUnavailable, _finite


@dataclass(frozen=True)
class NozzleOrifice:
    name: str
    total_flow_area_m2: float
    discharge_coefficient: float
    coefficient_source_id: str
    flow_leg: str = "downstream"
    geometry: str = "orifice_approach_velocity_negligible"

    def __post_init__(self):
        if not isinstance(self.name,str) or not self.name.strip():
            raise HydraulicsUnavailable("nozzle identifier required")
        area = _finite(self.total_flow_area_m2,"total_flow_area_m2",positive=True)
        cd = _finite(self.discharge_coefficient,"discharge_coefficient",positive=True)
        if cd > 1:
            raise HydraulicsUnavailable("nozzle discharge coefficient greater than 1 unsupported")
        if not isinstance(self.coefficient_source_id,str) or not (
                self.coefficient_source_id.strip()):
            raise HydraulicsUnavailable("sourced nozzle discharge coefficient required")
        if len(self.coefficient_source_id)>256:
            raise HydraulicsUnavailable("coefficient source identifier too long")
        if self.flow_leg not in ("downstream","return"):
            raise HydraulicsUnavailable("unsupported nozzle flow leg")
        if self.geometry != "orifice_approach_velocity_negligible":
            raise HydraulicsUnavailable("unsupported nozzle geometry/velocity correction")


def nozzle_orifice_loss(rho_kg_m3:float, nozzle:NozzleOrifice, flow_m3_s:float) -> dict:
    if not isinstance(nozzle,NozzleOrifice):
        raise HydraulicsUnavailable("validated nozzle description required")
    rho = _finite(rho_kg_m3,"density_kg_m3",positive=True)
    q = _finite(flow_m3_s,"flow_m3_s",nonnegative=True)
    velocity=q/nozzle.total_flow_area_m2
    try:
        dp=(rho/2)*(velocity/nozzle.discharge_coefficient)**2
    except OverflowError as exc:
        raise HydraulicsUnavailable("nozzle pressure differential overflow") from exc
    if not isfinite(dp) or not isfinite(velocity):
        raise HydraulicsUnavailable("nonfinite nozzle pressure differential")
    return {
        "name":nozzle.name,
        "flow_leg":nozzle.flow_leg,
        "geometry":nozzle.geometry,
        "flow_m3_s":q,
        "jet_velocity_m_s":velocity,
        "total_flow_area_m2":nozzle.total_flow_area_m2,
        "discharge_coefficient":nozzle.discharge_coefficient,
        "coefficient_source_id":nozzle.coefficient_source_id,
        "pressure_loss_pa":dp,
        "pressure_loss_bar":dp/100000,
        "model":"incompressible_sourced_coefficient_orifice_no_approach_correction",
        "coefficient_evidence":"caller_declared_unverified",
        "standpipe_pressure_pa":None,
        "engineering_acceptance":False,
        "excluded":["cavitation","approach_velocity_correction",
                    "unknown_nozzle_geometry","pressure_datum",
                    "unmodeled_circulation_restrictions"],
    }
