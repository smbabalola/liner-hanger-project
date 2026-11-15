"""LH-CALC-03 source-equation budget arithmetic with fictional elements."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from circulating_hydraulics import (
    NewtonianFluid,FlowSegment,HydraulicsUnavailable
)
from circulation_restrictions import NozzleOrifice
from circulation_budget import CircuitComponent,partial_circulation_budget


def components():
    return [
        CircuitComponent(pipe_or_annulus=FlowSegment(
            "fictional_internal","pipe",10,.1,flow_leg="downstream")),
        CircuitComponent(nozzle_orifice=NozzleOrifice(
            "fictional_bit_nozzle",.0002,.8,"SYNTHETIC-NOT-CALIBRATED")),
        CircuitComponent(pipe_or_annulus=FlowSegment(
            "fictional_return","concentric_annulus",10,.2,.1,"return"))
    ]


def test_independent_circuit_budget_matches_three_independent_closed_forms():
    fluid=NewtonianFluid(1000,.1)
    q=1e-4
    r=partial_circulation_budget(fluid,components(),q)
    pipe=128*.1*10*q/(math.pi*.1**4)
    ro,ri=.1,.05
    annulus=8*.1*10*q/(math.pi*(
        ro**4-ri**4-(ro**2-ri**2)**2/math.log(ro/ri)))
    nozzle=1000/2*(q/(.8*.0002))**2
    assert len(r["components_in_flow_order"])==3
    assert r["modeled_component_pressure_losses_pa"]==pytest.approx(
        pipe+annulus+nozzle,rel=1e-12)
    assert r["standpipe_pressure_pa"] is None
    assert r["engineering_acceptance"] is False
    assert r["boundary_coverage"]["rig_pressure_datum_verified"] is False
    assert r["boundary_coverage"]["actual_all_restrictions_verified"] is False


def test_optional_nozzle_still_only_partial_loss():
    c=[components()[0],components()[-1]]
    r=partial_circulation_budget(NewtonianFluid(1000,.1),c,1e-4)
    assert r["boundary_coverage"]["nozzle_included"] is False
    assert r["standpipe_pressure_pa"] is None


def test_zero_flow_circuit_zero_dynamic_and_viscous_loss():
    r=partial_circulation_budget(NewtonianFluid(1000,.1),components(),0)
    assert r["modeled_component_pressure_losses_pa"]==0


def test_unknown_turbulent_component_fails_entire_circuit():
    with pytest.raises(HydraulicsUnavailable,match="transition/turbulent"):
        partial_circulation_budget(NewtonianFluid(1000,.1),components(),1)


def test_no_return_leg_fails_without_partial_result():
    with pytest.raises(HydraulicsUnavailable,match="both downstream and return"):
        partial_circulation_budget(NewtonianFluid(1000,.1),components()[:2],1e-4)


def test_reversed_flow_leg_order_fails():
    c=components()
    with pytest.raises(HydraulicsUnavailable,match="flow leg order"):
        partial_circulation_budget(NewtonianFluid(1000,.1),
            [c[-1],c[0],c[1]],1e-4)


def test_repeated_component_identity_fails():
    c=components()
    with pytest.raises(HydraulicsUnavailable,match="unique"):
        partial_circulation_budget(NewtonianFluid(1000,.1),[c[0],c[0],c[-1]],1e-4)


def test_multiple_restrictions_fail_without_validated_expansion():
    c=components()
    c.insert(2,CircuitComponent(nozzle_orifice=NozzleOrifice(
        "another_nozzle",.0001,.8,"SYNTHETIC")))
    with pytest.raises(HydraulicsUnavailable,match="multiple restrictions"):
        partial_circulation_budget(NewtonianFluid(1000,.1),c,1e-4)


def test_invalid_component_union_rejected():
    with pytest.raises(HydraulicsUnavailable,match="exactly one"):
        CircuitComponent()
    with pytest.raises(HydraulicsUnavailable,match="exactly one"):
        CircuitComponent(pipe_or_annulus=components()[0].pipe_or_annulus,
                         nozzle_orifice=components()[1].nozzle_orifice)
