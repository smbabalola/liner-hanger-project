"""LH-CALC-03: partial, source-labelled laminar power-law component budget.

Only independently declared laminar circular pipe and stationary concentric
annular straight-section friction, plus an optional calibrated ideal
incompressible nozzle. No field SPP, hydrostatics, surface lines, equipment
restrictions, casing/liner joints, cuttings, eccentricity or turbulence.
"""
from __future__ import annotations
from math import isfinite

from circulation_budget import CircuitComponent
from circulating_hydraulics import HydraulicsUnavailable, _finite
from circulation_restrictions import nozzle_orifice_loss
from power_law_laminar_pipe import (
    PowerLawFluid,power_law_laminar_pipe_pressure_loss)
from power_law_laminar_annulus import power_law_laminar_annulus_pressure_loss


def partial_power_law_circulation_budget(
        fluid: PowerLawFluid, components_in_flow_order: list[CircuitComponent],
        flow_m3_s: float, *, laminar_evidence_by_section: dict[str,str]) -> dict:
    """Compute ONLY an openly partial component pressure-loss ledger.

    Each pipe/annulus segment requires a separate external laminar-regime
    source identity because pressure regime can vary through the circuit.
    Identifiers are caller assertions, never authenticated approvals.
    """
    if not isinstance(fluid,PowerLawFluid):
        raise HydraulicsUnavailable("source-typed power-law fluid required")
    q=_finite(flow_m3_s,"flow_m3_s",nonnegative=True)
    parts=components_in_flow_order
    if not isinstance(parts,(list,tuple)) or not parts or not all(
            isinstance(x,CircuitComponent) for x in parts):
        raise HydraulicsUnavailable("nonempty ordered typed component list required")
    ids=[p.name for p in parts]
    if len(set(ids))!=len(ids):
        raise HydraulicsUnavailable("unique component identifiers required")
    legs=[p.leg for p in parts]
    if "downstream" not in legs or "return" not in legs:
        raise HydraulicsUnavailable("downstream and return legs required")
    if legs!=sorted(legs,key={"downstream":0,"return":1}.get):
        raise HydraulicsUnavailable("components must run downstream before return")
    if not isinstance(laminar_evidence_by_section,dict):
        raise HydraulicsUnavailable("per-section independent regime evidence required")
    geometry_ids={p.name for p in parts if p.pipe_or_annulus is not None}
    if set(laminar_evidence_by_section)!=geometry_ids:
        raise HydraulicsUnavailable("exact per-section laminar evidence keys required")
    if sum(p.nozzle_orifice is not None for p in parts)>1:
        raise HydraulicsUnavailable("multiple nozzle orifices unsupported")
    for j,p in enumerate(parts):
        if p.nozzle_orifice is not None and (
                j==0 or j==len(parts)-1 or p.leg!="downstream"):
            raise HydraulicsUnavailable("nozzle path placement unsupported")
    results=[]
    for p in parts:
        if p.pipe_or_annulus is not None:
            section=p.pipe_or_annulus
            evidence=laminar_evidence_by_section[p.name]
            func=(power_law_laminar_pipe_pressure_loss
                  if section.kind=="pipe" else
                  power_law_laminar_annulus_pressure_loss)
            row=func(
                fluid,section,q,laminar_regime_independently_confirmed=True,
                regime_evidence_id=evidence)
            row["source_class"]="caller_asserted_laminar_governing_model"
        else:
            row=nozzle_orifice_loss(fluid.density_kg_m3,p.nozzle_orifice,q)
            row["source_class"]="caller_asserted_orifice_coefficient"
        results.append(row)
    total=sum(x["pressure_loss_pa"] for x in results)
    if not isfinite(total):
        raise HydraulicsUnavailable("nonfinite component pressure total")
    return {
        "status":"partial_power_law_component_budget_only",
        "components_in_flow_order":results,
        "modeled_component_pressure_losses_pa":total,
        "modeled_component_pressure_losses_bar":total/1e5,
        "standpipe_pressure_pa":None,
        "engineering_acceptance":False,
        "laminar_regime_sources":"caller_asserted_not_independently_authenticated",
        "boundary_coverage":{
            "downstream_leg_described":True,"return_leg_described":True,
            "complete_actual_tool_restrictions":False,
            "pressure_measurement_datum_verified":False,
            "hydrostatic_balance_verified":False,
            "field_telemetry_comparison_verified":False,
        },
        "excluded":["transitional_and_turbulent_flow","actual_mud_rheogram",
                    "temperature_dependency","eccentricity","pipe_rotation",
                    "cuttings","unknown_running_tool_restrictions",
                    "surface_lines","backpressure_and_hydrostatics",
                    "pressure_datum","OEM_operating_limits"],
    }
