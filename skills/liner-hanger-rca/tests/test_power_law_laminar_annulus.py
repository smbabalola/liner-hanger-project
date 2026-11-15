"""Independent Newtonian exact / power-law scaling checks for annular flow."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from power_law_laminar_pipe import PowerLawFluid
from power_law_laminar_annulus import power_law_laminar_annulus_pressure_loss
from circulating_hydraulics import NewtonianFluid,FlowSegment,HydraulicsUnavailable,segment_pressure_loss


def annulus(ri=.05,ro=.1):
    return FlowSegment("fictional_annular_return","concentric_annulus",10,2*ro,2*ri,"return")


def solve(n=.7,k=.1,q=1e-4,section=None,steps=512,evidence="SYNTHETIC-NOT-FIELD",flag=True):
    return power_law_laminar_annulus_pressure_loss(
        PowerLawFluid(1000,k,n),section or annulus(),q,
        quadrature_steps=steps,regime_evidence_id=evidence,
        laminar_regime_independently_confirmed=flag)


@pytest.mark.parametrize("ratio", [.2,.5,.8])
def test_n_one_agrees_with_independent_exact_newtonian_annulus(ratio):
    section=annulus(ri=.1*ratio)
    actual=solve(n=1,section=section)
    ref=segment_pressure_loss(NewtonianFluid(1000,.1),section,1e-4)
    assert actual["pressure_loss_pa"]==pytest.approx(
        ref["pressure_loss_pa"],rel=1e-4)
    assert actual["engineering_acceptance"] is False
    assert actual["standpipe_pressure_pa"] is None


@pytest.mark.parametrize("n", [.4,.7,1.,1.4])
def test_power_law_annulus_pressure_scales_as_q_to_n(n):
    a=solve(n=n,q=1e-4)
    b=solve(n=n,q=2e-4)
    assert b["pressure_loss_pa"]/a["pressure_loss_pa"]==pytest.approx(
        2**n,rel=2e-10)
    assert .05<a["zero_shear_radius_m"]<.1
    assert a["relative_refinement_difference"]<.002


def test_annular_quadrature_refinement_is_consistent():
    coarse=solve(n=.6,steps=256)
    fine=solve(n=.6,steps=1024)
    assert coarse["pressure_loss_pa"]==pytest.approx(
        fine["pressure_loss_pa"],rel=5e-4)


def test_zero_flow_zero_distributed_friction():
    r=solve(q=0)
    assert r["pressure_loss_pa"]==0
    assert r["standpipe_pressure_pa"] is None


@pytest.mark.parametrize("ratio", [.01,.9])
def test_geometry_outside_reviewed_research_guard_rejected(ratio):
    with pytest.raises(HydraulicsUnavailable,match="radius ratio"):
        solve(section=annulus(ri=.1*ratio))


@pytest.mark.parametrize("n", [.2,1.8])
def test_exponent_outside_annular_scope_rejected(n):
    with pytest.raises(HydraulicsUnavailable,match="annulus exponent"):
        solve(n=n)


@pytest.mark.parametrize("flag", [False,1,"true",None])
def test_no_silent_laminar_inference(flag):
    with pytest.raises(HydraulicsUnavailable,match="independent laminar"):
        solve(flag=flag)


@pytest.mark.parametrize("bad", ["",None,77,"x"*257])
def test_missing_laminar_provenance_rejected(bad):
    with pytest.raises(HydraulicsUnavailable,match="source identifier"):
        solve(evidence=bad)


@pytest.mark.parametrize("steps", [1,127,True,4098])
def test_bad_quadrature_configuration_rejected(steps):
    with pytest.raises(HydraulicsUnavailable,match="quadrature_steps"):
        solve(steps=steps)


def test_no_power_law_pipe_substituted_for_annulus():
    with pytest.raises(HydraulicsUnavailable,match="concentric_annulus"):
        solve(section=FlowSegment("pipe","pipe",10,.1))
