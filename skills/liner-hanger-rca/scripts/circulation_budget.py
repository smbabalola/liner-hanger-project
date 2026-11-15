"""LH-CALC-03 research-only auditable Newtonian circuit component budget.

Combines *only* individually supported restricted models: fully developed
Newtonian laminar pipe/concentric annulus and sourced, incompressible nozzle
loss. No hydrostatics, pressure datum, riser, surface hoses, fitting losses,
tool bore steps, branch flow, solids, thermal rheology, well control or SPP.
"""
from __future__ import annotations

from math import isfinite
from dataclasses import dataclass

from circulating_hydraulics import (
    NewtonianFluid, FlowSegment, HydraulicsUnavailable,
    segment_pressure_loss, _finite
)
from circulation_restrictions import NozzleOrifice, nozzle_orifice_loss


@dataclass(frozen=True)
class CircuitComponent:
    """Exactly one supported component, ordered along circulating flow."""
    pipe_or_annulus: FlowSegment | None = None
    nozzle_orifice: NozzleOrifice | None = None

    def __post_init__(self):
        if (self.pipe_or_annulus is None) == (self.nozzle_orifice is None):
            raise HydraulicsUnavailable("exactly one circuit component type required")
        if self.pipe_or_annulus is not None and not isinstance(
                self.pipe_or_annulus,FlowSegment):
            raise HydraulicsUnavailable("pipe_or_annulus must be validated segment")
        if self.nozzle_orifice is not None and not isinstance(
                self.nozzle_orifice,NozzleOrifice):
            raise HydraulicsUnavailable("nozzle_orifice must be validated restriction")

    @property
    def name(self):
        s=self.pipe_or_annulus if self.pipe_or_annulus is not None else self.nozzle_orifice
        return s.name

    @property
    def leg(self):
        s=self.pipe_or_annulus if self.pipe_or_annulus is not None else self.nozzle_orifice
        return s.flow_leg


def partial_circulation_budget(
        fluid: NewtonianFluid,
        components_in_flow_order: list[CircuitComponent],
        flow_m3_s: float) -> dict:
    """Compute strictly partial loss budget; never infer a rig SPP."""
    if not isinstance(fluid,NewtonianFluid):
        raise HydraulicsUnavailable("Newtonian fluid required for this circuit model")
    q=_finite(flow_m3_s,"flow_m3_s",nonnegative=True)
    parts=components_in_flow_order
    if not isinstance(parts,(list,tuple)) or not parts or not all(
            isinstance(s,CircuitComponent) for s in parts):
        raise HydraulicsUnavailable("nonempty typed ordered component list required")
    ids=[s.name for s in parts]
    if len(set(ids))!=len(ids):
        raise HydraulicsUnavailable("unique component identifiers required")
    legs=[s.leg for s in parts]
    if "downstream" not in legs or "return" not in legs:
        raise HydraulicsUnavailable("both downstream and return legs required")
    if legs!=sorted(legs,key={"downstream":0,"return":1}.get):
        raise HydraulicsUnavailable("flow leg order must be downstream then return")
    nozzle_count=sum(p.nozzle_orifice is not None for p in parts)
    if nozzle_count > 1:
        raise HydraulicsUnavailable("multiple restrictions require separate engineering model")
    if nozzle_count:
        nozzle_index=next(i for i,p in enumerate(parts) if p.nozzle_orifice is not None)
        if nozzle_index==0 or nozzle_index==len(parts)-1:
            raise HydraulicsUnavailable("nozzle must be between validated flow path sections")
        if legs[nozzle_index]!="downstream":
            raise HydraulicsUnavailable("nozzle cannot appear in return leg in this model")
    rows=[]
    for s in parts:
        if s.pipe_or_annulus is not None:
            r=segment_pressure_loss(fluid,s.pipe_or_annulus,q)
            r["source_class"]="analytical_newtonian_laminar"
        else:
            r=nozzle_orifice_loss(fluid.density_kg_m3,s.nozzle_orifice,q)
            r["source_class"]="caller_sourced_discharge_coefficient"
        rows.append(r)
    total=sum(v["pressure_loss_pa"] for v in rows)
    if not isfinite(total):
        raise HydraulicsUnavailable("nonfinite component total")
    return {
        "status":"partial_circuit_component_budget_only",
        "components_in_flow_order":rows,
        "modeled_component_pressure_losses_pa":total,
        "modeled_component_pressure_losses_bar":total/1e5,
        "standpipe_pressure_pa":None,
        "engineering_acceptance":False,
        "boundary_coverage":{
            "downstream_leg_described":True,
            "return_leg_described":True,
            "nozzle_included":bool(nozzle_count),
            "rig_pressure_datum_verified":False,
            "actual_all_restrictions_verified":False,
            "hydrostatic_balance_verified":False,
            "actual_field_measurement_validated":False,
        },
        "excluded":["surface_hoses_and_pump","unlisted_tool_restrictions",
                    "branch_flow_and_leaks","hydrostatics_and_return_backpressure",
                    "temperature_solid_cuttings_rotation","non_newtonian_fluid",
                    "operator_pressure_transducer_location","OEM_pressure_limits"],
    }
