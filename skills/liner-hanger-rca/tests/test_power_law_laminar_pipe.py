"""Independent published power-law pipe equation and fail-closed bounds."""
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from power_law_laminar_pipe import PowerLawFluid,power_law_laminar_pipe_pressure_loss
from circulating_hydraulics import NewtonianFluid,FlowSegment,segment_pressure_loss,HydraulicsUnavailable


def pipe(length=10,diameter=.1):
    return FlowSegment("synthetic", "pipe", length, diameter)


def solve(n=0.6,k=.1,q=1e-4,length=10,diameter=.1,flag=True,evidence="SYNTHETIC-ASSUMED"):
    return power_law_laminar_pipe_pressure_loss(
        PowerLawFluid(1000,k,n),pipe(length,diameter),q,
        laminar_regime_independently_confirmed=flag,regime_evidence_id=evidence)


@pytest.mark.parametrize("n", [0.3,0.6,1.0,1.5])
def test_independent_published_metzner_reed_pipe_formula(n):
    # BYU Non-Newtonian Fluid Math Eqs 7-8, independently evaluated
    # using volumetric flow/radius and wall shear stress.
    k,q,d,L=.2,1e-4,.1,10
    result=solve(n=n,k=k,q=q)
    gamma=(3*n+1)/(4*n)*32*q/(math.pi*d**3)
    expected=4*L/d*k*gamma**n
    assert result["pressure_loss_pa"]==pytest.approx(expected,rel=1e-13)
    assert result["nominal_wall_shear_rate_s_1"]==pytest.approx(gamma)
    assert result["engineering_acceptance"] is False
    assert result["standpipe_pressure_pa"] is None


@pytest.mark.parametrize("q", [0,1e-6,1e-5,1e-4])
def test_n_one_is_exact_independent_newtonian_limit(q):
    result=solve(n=1,k=.1,q=q)
    benchmark=segment_pressure_loss(NewtonianFluid(1000,.1),pipe(),q)
    assert result["pressure_loss_pa"]==pytest.approx(
        benchmark["pressure_loss_pa"],rel=1e-12,abs=1e-12)


@pytest.mark.parametrize("n", [0.3,.6,1.,1.5])
def test_pressure_ratio_for_double_flow_is_two_to_n(n):
    a=solve(n=n,q=1e-4)
    b=solve(n=n,q=2e-4)
    assert b["pressure_loss_pa"]/a["pressure_loss_pa"]==pytest.approx(
        2**n,rel=1e-12)


def test_zero_flow_and_zero_length_report_zero_distributed_friction():
    assert solve(q=0)["pressure_loss_pa"]==0
    assert solve(length=0)["pressure_loss_pa"]==0


@pytest.mark.parametrize("bad", [0,-.1,True,float("nan"),float("inf"),.05,3.])
def test_bad_power_exponent_rejected(bad):
    with pytest.raises(HydraulicsUnavailable):
        PowerLawFluid(1000,.1,bad)


@pytest.mark.parametrize("bad", [0,-.1,True,float("nan"),float("inf")])
def test_bad_consistency_rejected(bad):
    with pytest.raises(HydraulicsUnavailable):
        PowerLawFluid(1000,bad,.7)


@pytest.mark.parametrize("bad", [False,0,"yes",None])
def test_no_inferred_laminar_regime(bad):
    with pytest.raises(HydraulicsUnavailable,match="laminar regime"):
        solve(flag=bad)


@pytest.mark.parametrize("bad", [""," ",123,None,"x"*257])
def test_unreviewed_or_missing_regime_identity_fails(bad):
    with pytest.raises(HydraulicsUnavailable,match="evidence identifier"):
        solve(evidence=bad)


@pytest.mark.parametrize("bad", [-1,float("nan"),float("inf"),True,"0.1"])
def test_invalid_flow_fails_closed(bad):
    with pytest.raises(HydraulicsUnavailable):
        solve(q=bad)


def test_power_law_annulus_fails_closed():
    annulus=FlowSegment("return","concentric_annulus",10,.2,.1,"return")
    with pytest.raises(HydraulicsUnavailable,match="annular"):
        power_law_laminar_pipe_pressure_loss(
            PowerLawFluid(1000,.1,.7),annulus,1e-4,
            laminar_regime_independently_confirmed=True,
            regime_evidence_id="SYNTHETIC")
