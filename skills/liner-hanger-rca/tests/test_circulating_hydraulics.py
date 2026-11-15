"""LH-CALC-03 independent analytical and fail-closed test fixtures.

Synthetic SI input only, not Baker Hughes operational data.
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from circulating_hydraulics import (
    NewtonianFluid, FlowSegment, HydraulicsUnavailable,
    segment_pressure_loss, circulation_friction,
)


def fluid():
    return NewtonianFluid(1000.0, 0.1)


def pipe(length=10.0, diameter=0.1, leg="downstream", name="pipe"):
    return FlowSegment(name, "pipe", length, diameter, flow_leg=leg)


def annulus(length=10.0, outer=0.2, inner=0.1, leg="return", name="annulus"):
    return FlowSegment(name, "concentric_annulus", length, outer, inner, leg)


def test_independent_hagen_poiseuille_known_answer():
    q = 0.0001
    r = segment_pressure_loss(fluid(), pipe(), q)
    # Independent closed-form solution for a single Newtonian laminar tube.
    expected = 8*0.1*10*q/(math.pi*(0.05**4))
    assert r["pressure_loss_pa"] == pytest.approx(expected, rel=1e-13)
    assert r["pressure_loss_bar"] == pytest.approx(expected/1e5)
    assert r["mean_velocity_m_s"] == pytest.approx(q/(math.pi*0.05**2))
    assert r["reynolds"] < 2000
    assert r["engineering_acceptance"] is False


def test_independent_concentric_annulus_known_answer():
    q = 0.0001
    r = segment_pressure_loss(fluid(), annulus(), q)
    ri, ro = 0.05, 0.1
    # Solve the analytical laminar annulus throughput relation for dp.
    geometric = ro**4-ri**4-(ro**2-ri**2)**2/math.log(ro/ri)
    expected = 8*0.1*10*q/(math.pi*geometric)
    assert r["pressure_loss_pa"] == pytest.approx(expected, rel=1e-12)
    assert r["mean_velocity_m_s"] == pytest.approx(
        q/(math.pi*(ro**2-ri**2)))
    assert r["reynolds"] < 2000


@pytest.mark.parametrize("geometry", [pipe(), annulus()])
def test_zero_flow_gives_zero_pressure_loss(geometry):
    r = segment_pressure_loss(fluid(), geometry, 0)
    assert r["reynolds"] == 0
    assert r["pressure_loss_pa"] == 0


@pytest.mark.parametrize("geometry", [pipe(length=0), annulus(length=0)])
def test_zero_length_gives_zero_pressure_loss(geometry):
    assert segment_pressure_loss(fluid(), geometry, 0.0001)["pressure_loss_pa"] == 0


@pytest.mark.parametrize("geometry", [pipe(), annulus()])
def test_laminar_pressure_scales_with_flow_and_length(geometry):
    r1 = segment_pressure_loss(fluid(), geometry, 0.0001)
    r2 = segment_pressure_loss(fluid(), geometry, 0.0002)
    assert r2["pressure_loss_pa"] == pytest.approx(2*r1["pressure_loss_pa"])


def test_pipe_diameter_fourth_power_at_same_flow():
    small = segment_pressure_loss(fluid(), pipe(diameter=0.1), 0.0001)
    large = segment_pressure_loss(fluid(), pipe(diameter=0.2), 0.0001)
    assert small["pressure_loss_pa"] == pytest.approx(16*large["pressure_loss_pa"])


def test_viscosity_scales_pressure_loss_for_fixed_laminar_flow():
    a = segment_pressure_loss(fluid(), pipe(), 0.0001)
    b = segment_pressure_loss(NewtonianFluid(1000, 0.2), pipe(), 0.0001)
    assert b["pressure_loss_pa"] == pytest.approx(2*a["pressure_loss_pa"])


def test_regime_threshold_fail_closed():
    # Re for pipe is rho*4Q/(pi D mu); choose strictly above threshold.
    critical_q = 2000*math.pi*0.1*0.1/(4*1000)
    segment_pressure_loss(fluid(), pipe(), critical_q)
    with pytest.raises(HydraulicsUnavailable, match="transition/turbulent"):
        segment_pressure_loss(fluid(), pipe(), critical_q*1.001)


def test_reject_turbulent_annulus():
    with pytest.raises(HydraulicsUnavailable, match="transition/turbulent"):
        segment_pressure_loss(fluid(), annulus(), 1.0)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1.0, True, "0.1"])
def test_reject_bad_flow(bad):
    with pytest.raises(HydraulicsUnavailable):
        segment_pressure_loss(fluid(), pipe(), bad)


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True])
def test_reject_bad_fluid_density(bad):
    with pytest.raises(HydraulicsUnavailable):
        NewtonianFluid(bad, 0.1)


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True])
def test_reject_bad_viscosity(bad):
    with pytest.raises(HydraulicsUnavailable):
        NewtonianFluid(1000, bad)


def test_reject_unsupported_rheology():
    with pytest.raises(HydraulicsUnavailable, match="rheology"):
        NewtonianFluid(1000, 0.1, "bingham")


@pytest.mark.parametrize("bad", [0, -0.1, float("nan"), float("inf"), True])
def test_reject_invalid_pipe_diameter(bad):
    with pytest.raises(HydraulicsUnavailable):
        pipe(diameter=bad)


@pytest.mark.parametrize("outer,inner", [(0.1, 0.1), (0.1, 0.2), (0.1, 0), (0.1, -0.01)])
def test_reject_invalid_annular_clearance(outer, inner):
    with pytest.raises(HydraulicsUnavailable):
        annulus(outer=outer, inner=inner)


def test_pipe_must_have_zero_inner_boundary():
    with pytest.raises(HydraulicsUnavailable):
        FlowSegment("pipe", "pipe", 10, 0.1, 0.05)


def test_reject_invalid_flow_leg_and_geometry():
    with pytest.raises(HydraulicsUnavailable):
        FlowSegment("x", "ellipse", 10, 0.1)
    with pytest.raises(HydraulicsUnavailable):
        FlowSegment("x", "pipe", 10, 0.1, flow_leg="sideways")


def test_reject_negative_length():
    with pytest.raises(HydraulicsUnavailable):
        pipe(length=-1)


def test_partial_circuit_sums_only_known_straight_friction():
    q = 0.0001
    a, b = pipe(), annulus()
    r = circulation_friction(fluid(), [a, b], q)
    expected = (segment_pressure_loss(fluid(), a, q)["pressure_loss_pa"]
                + segment_pressure_loss(fluid(), b, q)["pressure_loss_pa"])
    assert r["modeled_straight_segment_friction_pa"] == pytest.approx(expected)
    assert r["standpipe_pressure_pa"] is None
    assert r["engineering_acceptance"] is False
    assert r["status"] == "partial_circuit_friction_only"
    assert len(r["segments"]) == 2


def test_reject_incomplete_or_duplicate_segments():
    with pytest.raises(HydraulicsUnavailable):
        circulation_friction(fluid(), [], 0.0001)
    with pytest.raises(HydraulicsUnavailable):
        circulation_friction(fluid(), [pipe(), pipe()], 0.0001)


def test_circuit_rejects_unsupported_member_without_partial_total():
    with pytest.raises(HydraulicsUnavailable):
        circulation_friction(fluid(), [pipe(), object()], 0.0001)


def test_circuit_rejects_unsupported_turbulent_leg():
    with pytest.raises(HydraulicsUnavailable, match="transition/turbulent"):
        circulation_friction(fluid(), [pipe(), annulus()], 1.0)


def test_si_pascal_to_bar_consistency():
    r = segment_pressure_loss(fluid(), pipe(), 0.0001)
    assert r["pressure_loss_bar"]*1e5 == pytest.approx(r["pressure_loss_pa"])


@pytest.mark.parametrize("radial_gap_m,flow_m3_s", [
    (1e-5, 1e-12),
    (1e-8, 1e-20),
])
def test_thin_concentric_annulus_matches_independent_parallel_plate_limit(
        radial_gap_m, flow_m3_s):
    # Independent leading-order no-slip narrow-gap theory:
    # Q = (2*pi*R)*h**3*dp/(12*mu*L) as h/R -> 0.
    # The annulus calculation uses the full cylindrical expression and
    # must approach this law without catastrophic cancellation.
    r_outer = 0.1
    r_inner = r_outer-radial_gap_m
    section = annulus(
        length=10, outer=2*r_outer, inner=2*r_inner)
    result = segment_pressure_loss(fluid(), section, flow_m3_s)
    expected = 6*0.1*10*flow_m3_s / (
        math.pi*r_outer*radial_gap_m**3)
    assert result["reynolds"] < 2000
    assert result["pressure_loss_pa"] == pytest.approx(expected, rel=5e-4)
    assert math.isfinite(result["pressure_loss_pa"])
    assert result["engineering_acceptance"] is False


def test_thin_gap_pressure_scales_as_inverse_gap_cubed():
    # Independently derive the asymptotic geometric scaling, keeping
    # all other laminar conditions fixed.
    results = [
        segment_pressure_loss(
            fluid(), annulus(outer=0.2, inner=0.2-2*gap), 1e-12
        )["pressure_loss_pa"]
        for gap in (1e-5, 2e-5)
    ]
    assert results[0]/results[1] == pytest.approx(8, rel=1e-3)
