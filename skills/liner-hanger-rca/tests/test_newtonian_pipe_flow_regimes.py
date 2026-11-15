"""USDA-NRCS Darcy-Weisbach and independently derived Colebrook checks."""
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from newtonian_pipe_flow_regimes import newtonian_pipe_pressure_by_regime
from circulating_hydraulics import NewtonianFluid,FlowSegment,HydraulicsUnavailable,segment_pressure_loss


def setup(re,eps=0):
    fluid=NewtonianFluid(1000,.001)
    section=FlowSegment("synthetic_pipe","pipe",10,.1)
    q=re*math.pi*.001*.1/(4*1000)
    r=newtonian_pipe_pressure_by_regime(
        fluid,section,q,absolute_roughness_m=eps,
        roughness_source_id="SYNTHETIC-ROUGHNESS-NOT-MEASURED")
    return r,fluid,section,q


def test_100000_re_smooth_pipe_friction_matches_independent_moody_blasius_limit():
    r,fluid,sec,q=setup(100000)
    # Smooth-pipe Blasius f=0.3164/Re**0.25, accepted source-limited
    # independent approximation; Colebrook predicts close (few %).
    blasius=.3164/(100000**.25)
    assert r["darcy_friction_factor"]==pytest.approx(blasius,rel=.05)
    assert r["regime"]=="turbulent_colebrook"
    v=q/(math.pi*.1**2/4)
    expected=r["darcy_friction_factor"]*(sec.length_m/.1)*1000*v*v/2
    assert r["pressure_loss_pa"]==pytest.approx(expected,rel=1e-13)
    assert r["standpipe_pressure_pa"] is None


def test_nonzero_roughness_matches_independent_swamee_jain_approximation():
    re=50000
    eps=.00002
    r,_,_,_=setup(re,eps)
    independent=.25/(math.log10(eps/(3.7*.1)+5.74/(re**.9))**2)
    assert r["darcy_friction_factor"]==pytest.approx(independent,rel=.05)
    assert r["engineering_acceptance"] is False


def test_laminar_circular_pipe_reduces_to_existing_exact_poisseuille():
    r,fluid,section,q=setup(1500)
    expected=segment_pressure_loss(fluid,section,q)
    assert r["pressure_loss_pa"]==pytest.approx(expected["pressure_loss_pa"])
    assert r["darcy_friction_factor"]==pytest.approx(64/1500)
    assert r["regime"]=="laminar"


@pytest.mark.parametrize("re",[2200,3000,3999])
def test_transition_not_silently_interpolated(re):
    with pytest.raises(HydraulicsUnavailable,match="transitional"):
        setup(re)


def test_pressure_increases_with_pipe_roughness_in_turbulence():
    smooth=setup(100000,0)[0]
    rough=setup(100000,.0001)[0]
    assert rough["pressure_loss_pa"]>smooth["pressure_loss_pa"]


def test_zero_flow_no_fabricated_friction_factor():
    r,_,_,_=setup(0)
    assert r["pressure_loss_pa"]==0
    assert r["darcy_friction_factor"] is None


def test_reject_annular_geometry_and_unsourced_roughness():
    with pytest.raises(HydraulicsUnavailable,match="circular pipe"):
        newtonian_pipe_pressure_by_regime(
            NewtonianFluid(1000,.001),
            FlowSegment("annulus","concentric_annulus",10,.2,.1),
            .001,absolute_roughness_m=.00001,roughness_source_id="SYNTHETIC")
    with pytest.raises(HydraulicsUnavailable,match="source"):
        newtonian_pipe_pressure_by_regime(
            NewtonianFluid(1000,.001),
            FlowSegment("pipe","pipe",10,.1),
            .001,absolute_roughness_m=.00001,roughness_source_id="")
