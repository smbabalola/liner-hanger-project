"""Independent interpolation known-answer and fail-closed cases."""
import pytest
from trajectory_interpolation_audit import (
    TrajectoryAuditError, audit_two_station_trajectory as audit,
)


def run(i0=30, i1=60, a0=0, a1=60, L=100, steps=512):
    return audit(
        length_m=L, top_inclination_deg=i0,
        bottom_inclination_deg=i1, top_azimuth_deg=a0,
        bottom_azimuth_deg=a1, steps=steps,
    )


@pytest.mark.parametrize("i,a", [(0,0),(30,0),(60,90),(90,270)])
def test_straight_tangent_exact(i, a):
    r = run(i,i,a,a)
    assert r["endpoint_position_difference_m"] == pytest.approx(0, abs=1e-11)
    assert r["endpoint_tvd_difference_m"] == pytest.approx(0, abs=1e-11)
    assert r["maximum_sampled_tangent_difference_norm"] == pytest.approx(0, abs=1e-11)


@pytest.mark.parametrize("i0,i1", [(0,60),(60,0),(30,60)])
def test_planar_build_drop_same_path(i0, i1):
    r = run(i0,i1,30,30)
    assert r["endpoint_position_difference_m"] == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize("turn", [(0,60),(350,10)])
def test_horizontal_pure_az_turn_same_path(turn):
    r = run(90,90,*turn)
    assert r["endpoint_position_difference_m"] == pytest.approx(0, abs=1e-9)


def test_combined_build_turn_has_distinct_path():
    r = run()
    assert r["endpoint_tvd_difference_m"] == pytest.approx(-2.98576451, abs=1e-5)
    assert r["endpoint_position_difference_m"] == pytest.approx(8.15076067, abs=1e-5)
    assert r["maximum_sampled_tangent_difference_norm"] > 0.1


def test_quadrature_refinement_independent():
    r1, r2, r3 = run(steps=128), run(steps=256), run(steps=512)
    assert abs(r3["endpoint_position_difference_m"]-r2["endpoint_position_difference_m"]) < abs(
        r2["endpoint_position_difference_m"]-r1["endpoint_position_difference_m"])


def test_length_scale():
    x, y = run(L=100), run(L=200)
    assert y["endpoint_position_difference_m"] == pytest.approx(
        2*x["endpoint_position_difference_m"], rel=1e-12)


@pytest.mark.parametrize("bad", [
    {"length_m":0}, {"length_m":float("nan")}, {"length_m":True},
    {"top_inclination_deg":-1}, {"bottom_inclination_deg":91},
    {"top_azimuth_deg":360}, {"bottom_azimuth_deg":-1},
    {"steps":9}, {"steps":True}, {"steps":16388},
])
def test_bad_domains_fail_closed(bad):
    params = dict(length_m=100, top_inclination_deg=30,
                  bottom_inclination_deg=60, top_azimuth_deg=0,
                  bottom_azimuth_deg=60, steps=512)
    params.update(bad)
    with pytest.raises(TrajectoryAuditError):
        audit(**params)


def test_180_dogleg_rejected():
    with pytest.raises(TrajectoryAuditError, match="180-degree"):
        run(90,90,0,180)


def test_azimuth_wrap_shortest():
    r = run(30,30,350,10)
    assert r["signed_azimuth_change_deg"] == 20
    assert r["endpoint_position_difference_m"] > 0


def test_no_approval_claims():
    r = run()
    assert r["status"] == "research_only_not_field_validated"
    assert "No torque/drag" in r["warning"]
