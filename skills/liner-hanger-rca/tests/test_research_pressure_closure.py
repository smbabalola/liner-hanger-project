"""Research pressure identity versus independent hydrostatic/Bernoulli sum."""
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from circulating_hydraulics import NewtonianFluid,FlowSegment,HydraulicsUnavailable
from circulation_restrictions import NozzleOrifice
from circulation_budget import CircuitComponent,partial_circulation_budget
from circulation_hydrostatics import HydrostaticLayer,static_hydrostatic_imbalance
from research_pressure_closure import research_circulation_pressure_closure


def inputs(return_density=1000):
    fluid=NewtonianFluid(1000,.1)
    parts=[
        CircuitComponent(pipe_or_annulus=FlowSegment("pipe","pipe",10,.1,flow_leg="downstream")),
        CircuitComponent(nozzle_orifice=NozzleOrifice("nozzle",.0002,.8,"SYNTHETIC")),
        CircuitComponent(pipe_or_annulus=FlowSegment("return","concentric_annulus",10,.2,.1,"return")),
    ]
    budget=partial_circulation_budget(fluid,parts,1e-4)
    hydro=static_hydrostatic_imbalance([
        HydrostaticLayer("down_head","downstream",0,1000,1000,"SYNTHETIC","RKB-FAKE"),
        HydrostaticLayer("return_head","return",0,1000,return_density,"SYNTHETIC","RKB-FAKE"),
    ])
    return budget,hydro


def close(budget=None,hydro=None,excluded=None,datum="RKB-FAKE",return_pa=30000):
    b,h=inputs() if budget is None or hydro is None else (budget,hydro)
    return research_circulation_pressure_closure(
        b,h,return_surface_backpressure_pa=return_pa,
        return_pressure_source_id="SYNTHETIC-RETURN-PRESSURE",
        common_pressure_datum=datum,
        circuit_completeness_declaration_id="SYNTHETIC-DECLARATION-NOT-ACTUAL-RIG",
        declared_unmodeled_components=[] if excluded is None else excluded)


def test_independent_full_pressure_accounting_identity_at_equal_density():
    b,h=inputs()
    r=close(b,h)
    q=.0001
    ro,ri=.1,.05
    dp_pipe=128*.1*10*q/(math.pi*.1**4)
    dp_ann=8*.1*10*q/(math.pi*(
        ro**4-ri**4-(ro**2-ri**2)**2/math.log(ro/ri)))
    dp_nozzle=1000/2*(q/(.8*.0002))**2
    assert r["research_standpipe_pressure_candidate_pa"]==pytest.approx(
        30000+dp_pipe+dp_ann+dp_nozzle,rel=1e-12)
    assert r["standpipe_pressure_pa"] is None
    assert r["engineering_acceptance"] is False
    assert r["field_validation"]=="not_performed"


def test_static_density_difference_changes_pressure_identity_with_signed_head():
    b,h=inputs(return_density=1100)
    r=close(b,h)
    assert r["signed_static_hydrostatic_contribution_pa"]==pytest.approx(
        100*9.80665*1000)
    assert r["research_standpipe_pressure_candidate_pa"]==pytest.approx(
        r["modeled_component_losses_pa"]+30000+100*9.80665*1000)


def test_unmodeled_restriction_refuses_full_pressure_candidate():
    b,h=inputs()
    with pytest.raises(HydraulicsUnavailable,match="unmodeled"):
        close(b,h,excluded=["missing liner running tool bypass loss"])


def test_pressure_datum_mismatch_refused():
    b,h=inputs()
    with pytest.raises(HydraulicsUnavailable,match="datums"):
        close(b,h,datum="OTHER-DATUM")


def test_component_sum_tampering_refused():
    b,h=inputs()
    b["modeled_component_pressure_losses_pa"]*=1.1
    with pytest.raises(HydraulicsUnavailable,match="reconciled"):
        close(b,h)


def test_component_flow_incompatibility_refused():
    b,h=inputs()
    b["components_in_flow_order"][1]["flow_m3_s"]*=2
    with pytest.raises(HydraulicsUnavailable,match="mass-flow"):
        close(b,h)


def test_field_approved_false_cannot_be_spoofed_true():
    b,h=inputs()
    b["engineering_acceptance"]=True
    with pytest.raises(HydraulicsUnavailable,match="unapproved"):
        close(b,h)


def test_negative_return_pressure_rejected():
    b,h=inputs()
    with pytest.raises(HydraulicsUnavailable,match="return_surface_backpressure_pa"):
        close(b,h,return_pa=-1)
