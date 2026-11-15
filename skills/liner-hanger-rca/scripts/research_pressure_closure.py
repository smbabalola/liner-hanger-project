"""LH-CALC-03: bounded research-only circuit pressure ACCOUNTING, NOT SPP.

Pressure identity for aligned reference elevations, stationary single-phase
closed circulation, with properly supported pressure boundaries:

  upstream_surface_minus_reference = return_backpressure
      + sum(downflow/restriction/return dynamic losses)
      + hydrostatic_return_minus_downstream

This module checks declared algebraic inputs, but cannot prove the physical
completeness of a real tool/rig/liner circuit. It deliberately returns a
*research pressure candidate*, NEVER approved standpipe_pressure_pa.
No field/OEM design/operation use without independent review.
"""
from __future__ import annotations
from math import fsum,isfinite
from circulating_hydraulics import HydraulicsUnavailable,_finite

BUDGET_STATUS={
    "partial_circuit_component_budget_only",
    "partial_power_law_component_budget_only",
}


def research_circulation_pressure_closure(
        component_budget:dict, hydrostatic_balance:dict, *,
        return_surface_backpressure_pa:float,
        return_pressure_source_id:str,
        common_pressure_datum:str,
        circuit_completeness_declaration_id:str,
        declared_unmodeled_components:list[str]) -> dict:
    """Audit explicit mathematical pressure balance without field approval.

    Even an empty declared_unmodeled_components list is an unverified
    *claim* of completeness; it is not independent proof. Missing components
    block calculation rather than silently give zero unmodeled losses.
    """
    if not isinstance(component_budget,dict) or component_budget.get("status") not in BUDGET_STATUS:
        raise HydraulicsUnavailable("supported partial component budget required")
    if not isinstance(hydrostatic_balance,dict) or hydrostatic_balance.get("status")!="static_hydrostatic_contribution_only":
        raise HydraulicsUnavailable("explicit matching hydrostatic balance required")
    for label,value in (
        ("return_pressure_source_id",return_pressure_source_id),
        ("common_pressure_datum",common_pressure_datum),
        ("circuit_completeness_declaration_id",circuit_completeness_declaration_id),
    ):
        if not isinstance(value,str) or not value.strip() or len(value)>256:
            raise HydraulicsUnavailable(f"{label} must be explicitly sourced")
    if common_pressure_datum!=hydrostatic_balance.get("datum"):
        raise HydraulicsUnavailable("hydrostatic and return pressure datums differ")
    if not isinstance(declared_unmodeled_components,list) or any(
            not isinstance(x,str) or not x.strip() for x in declared_unmodeled_components):
        raise HydraulicsUnavailable("explicit list of excluded/unknown losses required")
    if declared_unmodeled_components:
        raise HydraulicsUnavailable("unmodeled circulation loss components prevent pressure closure")
    return_pressure=_finite(
        return_surface_backpressure_pa,"return_surface_backpressure_pa",nonnegative=True)
    rows=component_budget.get("components_in_flow_order")
    if not isinstance(rows,list) or len(rows)<3 or not all(isinstance(x,dict) for x in rows):
        raise HydraulicsUnavailable("ordered component audit trail required")
    names=[x.get("name") for x in rows]
    if any(not isinstance(x,str) or not x.strip() for x in names) or len(names)!=len(set(names)):
        raise HydraulicsUnavailable("unique component identities required")
    legs=[x.get("flow_leg") for x in rows]
    if legs!=sorted(legs,key={"downstream":0,"return":1}.get) or (
            "downstream" not in legs or "return" not in legs):
        raise HydraulicsUnavailable("complete ordered downstream/return legs required")
    rates=[_finite(x.get("flow_m3_s"),"component flow_m3_s",nonnegative=True) for x in rows]
    if not rates or any(q!=rates[0] for q in rates):
        raise HydraulicsUnavailable("incompatible component mass-flow accounting")
    contributions=[
        _finite(x.get("pressure_loss_pa"),"component pressure_loss_pa",nonnegative=True)
        for x in rows]
    recalculated=fsum(contributions)
    declared=_finite(component_budget.get("modeled_component_pressure_losses_pa"),
                     "reported modeled components",nonnegative=True)
    if abs(recalculated-declared)>max(.00001,1e-11*max(1,recalculated)):
        raise HydraulicsUnavailable("component loss subtotal cannot be reconciled")
    if component_budget.get("standpipe_pressure_pa") is not None or component_budget.get("engineering_acceptance") is not False:
        raise HydraulicsUnavailable("component budget must remain unapproved and non-SPP")
    if hydrostatic_balance.get("standpipe_pressure_pa") is not None or hydrostatic_balance.get("engineering_acceptance") is not False:
        raise HydraulicsUnavailable("hydrostatic inputs cannot be operationally approved")
    hydro=_finite(
        hydrostatic_balance.get("downstream_surface_minus_return_surface_hydrostatic_pa"),
        "signed hydrostatic contribution")
    # _finite accepts a signed finite value when neither positivity flag is passed.
    candidate=fsum((return_pressure,recalculated,hydro))
    if not isfinite(candidate):
        raise HydraulicsUnavailable("nonfinite pressure closure")
    return {
        "status":"research_pressure_identity_only_not_field_complete",
        "research_standpipe_pressure_candidate_pa":candidate,
        "research_standpipe_pressure_candidate_bar":candidate/100000,
        "modeled_component_losses_pa":recalculated,
        "signed_static_hydrostatic_contribution_pa":hydro,
        "declared_return_surface_backpressure_pa":return_pressure,
        "return_pressure_source_id":return_pressure_source_id,
        "common_pressure_datum":common_pressure_datum,
        "circuit_completeness_declaration_id":circuit_completeness_declaration_id,
        "flow_m3_s":rates[0],
        "component_source_status":"caller_declared_not_independently_authenticated",
        "standpipe_pressure_pa":None,
        "engineering_acceptance":False,
        "field_validation":"not_performed",
        "excluded":["gauge_calibration","transient_or_dynamic_losses",
                    "unknown_tool_flow_paths","actual_circuit_completeness",
                    "thermal_non_newtonian_model","independent_human_approval"],
    }
