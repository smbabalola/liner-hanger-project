"""Independent Buckingham-Reiner pipe checks; fictional research cases."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from bingham_laminar_pipe import BinghamFluid, bingham_pipe_laminar_pressure_loss
from circulating_hydraulics import (
    FlowSegment, HydraulicsUnavailable, NewtonianFluid,
    segment_pressure_loss,
)


def pipe(length=10.0):
    return FlowSegment("fictional_tubular", "pipe", length, 0.1)


def test_independent_published_buckingham_reiner_wall_stress_forward_and_inverse():
    # Independently specified wall stress 20 Pa, yield stress 5 Pa:
    # Perry's Eq. 6-59, Q = pi D^3*tau_w/(32*mu) *
    # (1 - 4 tau_y/(3tau_w) + (tau_y/tau_w)^4/3).
    tau_w, tau_y, D, mu, L = 20., 5., .1, .1, 10.
    a = tau_y/tau_w
    q = math.pi*D**3*tau_w/(32*mu)*(1-4*a/3+a**4/3)
    observed = bingham_pipe_laminar_pressure_loss(
        BinghamFluid(1000, mu, tau_y), pipe(), q,
        laminar_regime_independently_confirmed=True)
    assert observed["wall_shear_stress_pa"] == pytest.approx(tau_w, rel=1e-12)
    assert observed["pressure_loss_pa"] == pytest.approx(
        4*L*tau_w/D, rel=1e-12)
    assert observed["engineering_acceptance"] is False
    assert observed["standpipe_pressure_pa"] is None
    assert observed["flow_regime_evidence"] == "caller_asserted_not_independently_verified"


@pytest.mark.parametrize("q", [0.00001, 0.0001, 0.0002])
def test_zero_yield_reduces_exactly_to_independent_newtonian_pipe(q):
    b = bingham_pipe_laminar_pressure_loss(
        BinghamFluid(1000, 0.1, 0), pipe(), q,
        laminar_regime_independently_confirmed=True)
    n = segment_pressure_loss(NewtonianFluid(1000, 0.1), pipe(), q)
    assert b["pressure_loss_pa"] == pytest.approx(n["pressure_loss_pa"], rel=1e-13)


def test_positive_yield_exceeds_zero_yield_for_same_laminar_flow():
    q=0.00001
    newton = bingham_pipe_laminar_pressure_loss(
        BinghamFluid(1000, .1, 0), pipe(), q,
        laminar_regime_independently_confirmed=True)
    plastic = bingham_pipe_laminar_pressure_loss(
        BinghamFluid(1000, .1, 5), pipe(), q,
        laminar_regime_independently_confirmed=True)
    assert plastic["pressure_loss_pa"] > newton["pressure_loss_pa"]
    assert plastic["wall_shear_stress_pa"] > 5


def test_yielding_near_threshold_still_returns_physical_above_yield_root():
    q = 1e-10
    r = bingham_pipe_laminar_pressure_loss(
        BinghamFluid(1000,.1,5),pipe(),q,
        laminar_regime_independently_confirmed=True)
    assert r["wall_shear_stress_pa"] > 5
    assert r["pressure_loss_pa"] > 4*10*5/.1


@pytest.mark.parametrize("q", [0, 1e-5])
def test_zero_length_has_no_distributed_friction(q):
    r = bingham_pipe_laminar_pressure_loss(
        BinghamFluid(1000,.1,5),pipe(length=0),q,
        laminar_regime_independently_confirmed=True)
    assert r["pressure_loss_pa"] == 0


def test_zero_flow_with_positive_yield_has_indeterminate_pressure():
    # Static plug below yield is compatible with a family of gradients;
    # a zero-flow reading does NOT determine the pressure differential.
    with pytest.raises(HydraulicsUnavailable, match="indeterminate"):
        bingham_pipe_laminar_pressure_loss(
            BinghamFluid(1000,.1,5),pipe(),0,
            laminar_regime_independently_confirmed=True)


def test_zero_flow_with_zero_yield_is_zero_laminar_friction():
    r = bingham_pipe_laminar_pressure_loss(
        BinghamFluid(1000,.1,0),pipe(),0,
        laminar_regime_independently_confirmed=True)
    assert r["pressure_loss_pa"] == 0


@pytest.mark.parametrize("flag", [False, 1, "yes", None])
def test_no_silent_laminar_regime_inference(flag):
    with pytest.raises(HydraulicsUnavailable, match="independent laminar-regime"):
        bingham_pipe_laminar_pressure_loss(
            BinghamFluid(1000,.1,5), pipe(),1e-5,
            laminar_regime_independently_confirmed=flag)


def test_annular_bingham_plastic_fails_closed():
    annulus = FlowSegment("return", "concentric_annulus",10,.2,.1,"return")
    with pytest.raises(HydraulicsUnavailable,match="annular flow"):
        bingham_pipe_laminar_pressure_loss(
            BinghamFluid(1000,.1,5),annulus,1e-5,
            laminar_regime_independently_confirmed=True)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1, True])
def test_unsupported_yield_stress_fails_closed(bad):
    with pytest.raises(HydraulicsUnavailable):
        BinghamFluid(1000,.1,bad)


@pytest.mark.parametrize("q", [float("nan"), float("inf"), -1, True])
def test_unsupported_flow_fails_closed(q):
    with pytest.raises(HydraulicsUnavailable):
        bingham_pipe_laminar_pressure_loss(
            BinghamFluid(1000,.1,5),pipe(),q,
            laminar_regime_independently_confirmed=True)
