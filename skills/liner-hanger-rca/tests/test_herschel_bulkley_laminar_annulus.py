"""Independent source-equation limits; synthetic research-only data."""
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from herschel_bulkley_laminar_annulus import (
    HerschelBulkleyFluid,hb_laminar_annulus_pressure_loss)
from circulating_hydraulics import (
    FlowSegment,NewtonianFluid,segment_pressure_loss,HydraulicsUnavailable)
from power_law_laminar_annulus import power_law_laminar_annulus_pressure_loss
from power_law_laminar_pipe import PowerLawFluid


def annulus(ratio=.5):
    return FlowSegment("synthetic","concentric_annulus",10,.2,.2*ratio,"return")


def run(n=1.,k=.1,yield_pa=0.,q=1e-4,ratio=.5,steps=128):
    return hb_laminar_annulus_pressure_loss(
        HerschelBulkleyFluid(1000,k,n,yield_pa),annulus(ratio),q,
        laminar_regime_independently_confirmed=True,
        regime_evidence_id="SYNTHETIC-DECLARATION-NOT-FIELD",
        quadrature_steps=steps)


@pytest.mark.parametrize("ratio", [.25,.5,.75])
def test_independent_exact_newtonian_concentric_annulus_limit(ratio):
    actual=run(ratio=ratio)
    expected=segment_pressure_loss(NewtonianFluid(1000,.1),annulus(ratio),1e-4)
    assert actual["pressure_loss_pa"]==pytest.approx(expected["pressure_loss_pa"],rel=1e-3)
    assert actual["standpipe_pressure_pa"] is None
    assert actual["engineering_acceptance"] is False


def test_zero_yield_nonnewtonian_matches_separate_power_law_solver():
    case=run(n=.7,yield_pa=0)
    other=power_law_laminar_annulus_pressure_loss(
        PowerLawFluid(1000,.1,.7),annulus(),1e-4,
        laminar_regime_independently_confirmed=True,
        regime_evidence_id="SYNTHETIC")
    assert case["pressure_loss_pa"]==pytest.approx(other["pressure_loss_pa"],rel=2e-3)


def test_bingham_positive_yield_increases_required_pressure_at_same_flow():
    no_yield=run(yield_pa=0)
    bingham=run(yield_pa=5)
    assert bingham["pressure_loss_pa"]>no_yield["pressure_loss_pa"]
    assert bingham["inner_wall_shear_stress_pa"]>5
    assert bingham["outer_wall_shear_stress_pa"]>5
    assert .05<bingham["zero_stress_radius_m"]<.1


def test_hb_shear_thinning_positive_yield_increases_over_zero_yield():
    assert run(n=.65,yield_pa=3)["pressure_loss_pa"]>run(n=.65,yield_pa=0)["pressure_loss_pa"]


def test_bingham_flow_rate_monotonic():
    assert run(yield_pa=2,q=2e-4)["pressure_loss_pa"]>run(yield_pa=2,q=1e-4)["pressure_loss_pa"]


def test_static_plug_zero_flow_pressure_is_indeterminate():
    with pytest.raises(HydraulicsUnavailable,match="indeterminate"):
        run(yield_pa=3,q=0)


def test_zero_flow_zero_yield_has_zero_viscous_loss():
    value=run(q=0)
    assert value["pressure_loss_pa"]==0
    assert value["zero_stress_radius_m"] is None


def test_reject_unsupported_casing_gap_or_regime():
    with pytest.raises(HydraulicsUnavailable,match="radius ratio"):
        run(ratio=.9)
    with pytest.raises(HydraulicsUnavailable,match="laminar-regime"):
        hb_laminar_annulus_pressure_loss(
            HerschelBulkleyFluid(1000,.1,1,5),annulus(),1e-4,
            regime_evidence_id="SYNTHETIC")


def test_numerical_flux_refinement_guard_reports_error():
    result=run(n=.8,yield_pa=2,steps=128)
    assert math.isfinite(result["relative_flux_refinement_difference"])
    assert result["relative_flux_refinement_difference"]<.005


@pytest.mark.parametrize("value",[float("nan"),float("inf"),-1,True])
def test_invalid_yield_rejected(value):
    with pytest.raises(HydraulicsUnavailable):
        HerschelBulkleyFluid(1000,.1,1,value)
