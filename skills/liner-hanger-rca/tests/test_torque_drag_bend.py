"""Independent capstan analytical limit: no buoyed distributed weight."""
import math
import sys
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from planned_job_section import SourcedNumber
from torque_drag_bend import IdealBendInputs, predict_ideal_bend
from torque_drag_straight import TorqueDragError


def src(value, unit, name, status="unreviewed"):
    return SourcedNumber(value, unit, "SYNTHETIC-NOT-OEM",
                         "fixture:" + name, "fictional-r1", status)


def fixture(*, angle=90, mu=0.2, mu_rot=0.3, tension=10000, radius=0.05):
    return IdealBendInputs(
        bend_id="fictional-weightless-dogleg",
        bottom_tension=src(tension, "N", "bottom-tension"),
        bend_angle=src(angle, "deg", "dogleg"),
        axial_friction=src(mu, "1", "axial-friction"),
        rotational_friction=src(mu_rot, "1", "rotary-friction"),
        contact_radius=src(radius, "m", "radius"),
        zero_distributed_weight=True,
    )


def values(p):
    return {k: float(v) for k, v in predict_ideal_bend(p)["results"].items()}


def test_quarter_circle_independent_capstan_analytic_reference():
    # Conventional capstan equation can be derived independently from
    # dN=T d(theta), dT=mu dN integrated around a weightless bend.
    p = fixture()
    out = values(p)
    x = .2 * math.pi / 2
    assert out["top_pickup_tension_n"] == pytest.approx(10000 * math.exp(x), rel=1e-12)
    assert out["top_slackoff_tension_n"] == pytest.approx(10000 * math.exp(-x), rel=1e-12)
    assert out["top_pure_rotation_tension_n"] == 10000
    assert out["pickup_integrated_contact_normal_n"] == pytest.approx(
        10000 * (math.exp(x) - 1) / .2, rel=1e-12)
    assert out["slackoff_integrated_contact_normal_n"] == pytest.approx(
        10000 * (1 - math.exp(-x)) / .2, rel=1e-12)
    assert out["pure_rotation_integrated_contact_normal_n"] == pytest.approx(
        10000 * math.pi / 2, rel=1e-12)
    assert out["pure_rotation_contact_torque_nm"] == pytest.approx(
        .3 * 10000 * math.pi / 2 * .05, rel=1e-12)


def test_zero_angle_identity_even_with_friction():
    out = values(fixture(angle=0))
    assert out["top_pickup_tension_n"] == 10000
    assert out["top_slackoff_tension_n"] == 10000
    assert out["pure_rotation_contact_torque_nm"] == 0
    assert out["pickup_integrated_contact_normal_n"] == 0


def test_frictionless_bend_has_equal_tension_and_finite_normal():
    out = values(fixture(mu=0, mu_rot=0))
    assert out["top_pickup_tension_n"] == 10000
    assert out["top_slackoff_tension_n"] == 10000
    assert out["pickup_integrated_contact_normal_n"] == pytest.approx(10000 * math.pi / 2)
    assert out["slackoff_integrated_contact_normal_n"] == pytest.approx(10000 * math.pi / 2)
    assert out["pure_rotation_contact_torque_nm"] == 0


def test_tension_reciprocity_when_friction_angle_reversed_by_mode():
    out = values(fixture())
    assert (out["top_pickup_tension_n"] * out["top_slackoff_tension_n"]
            == pytest.approx(10000 ** 2, rel=1e-12))


def test_nonzero_bend_rotation_torque_is_independent_of_axial_mu():
    first = values(fixture(mu=0.05))
    second = values(fixture(mu=0.5))
    assert first["pure_rotation_contact_torque_nm"] == pytest.approx(
        second["pure_rotation_contact_torque_nm"], rel=1e-12)


def test_more_axial_friction_increases_pickup_and_reduces_slackoff():
    low, high = values(fixture(mu=0.1)), values(fixture(mu=0.4))
    assert high["top_pickup_tension_n"] > low["top_pickup_tension_n"]
    assert high["top_slackoff_tension_n"] < low["top_slackoff_tension_n"]


def test_double_rotation_radius_doubles_contact_torque():
    low = values(fixture(radius=0.05))
    high = values(fixture(radius=0.1))
    assert high["pure_rotation_contact_torque_nm"] == pytest.approx(
        low["pure_rotation_contact_torque_nm"] * 2, rel=1e-12)


def test_one_hundred_eighty_degree_boundary_accepted():
    out = values(fixture(angle=180))
    assert out["top_pickup_tension_n"] == pytest.approx(
        10000 * math.exp(.2 * math.pi), rel=1e-12)


def test_rad_deg_unit_equivalence():
    deg = values(fixture(angle=90))
    rad = replace(fixture(), bend_angle=src(
        Decimal("1.5707963267948966192313216916397514420985846996876"),
        "rad", "dogleg-radians"))
    assert values(rad)["top_pickup_tension_n"] == pytest.approx(
        deg["top_pickup_tension_n"], rel=1e-12)


def test_sourced_unreviewed_status_not_approval():
    out = predict_ideal_bend(fixture())
    assert out["status"] == "unreviewed_inputs"
    assert "weightless" in out["warning"]


@pytest.mark.parametrize("change", [
    {"bend_id": ""},
    {"bottom_tension": src(0, "N", "zero-tension")},
    {"bottom_tension": src(-3, "N", "compression")},
    {"bend_angle": src(-1, "deg", "negative-angle")},
    {"bend_angle": src(181, "deg", "too-many-degrees")},
    {"bend_angle": src("NaN", "rad", "invalid")},
    {"axial_friction": src(-.1, "1", "negative-mu")},
    {"rotational_friction": src(-.1, "1", "negative-rot-mu")},
    {"contact_radius": src(0, "m", "zero-radius")},
    {"zero_distributed_weight": False},
    {"zero_distributed_weight": None},
    {"axial_friction": src(.3, "unsupported", "friction-units")},
    {"bottom_tension": SourcedNumber(10000, "N", "", "loc", "rev")},
])
def test_rejects_nonphysical_or_unqualified_input(change):
    with pytest.raises(TorqueDragError):
        predict_ideal_bend(replace(fixture(), **change))


def test_excessive_friction_angle_fails_before_exponentiation():
    with pytest.raises(TorqueDragError, match="excessive"):
        predict_ideal_bend(fixture(mu=100))


def test_does_not_modify_existing_straight_profile():
    from torque_drag_profile import predict_straight_profile, StraightProfile
    from torque_drag_straight import StraightTorqueDragInputs
    # The bend's model is intentionally independent; invalid substitution
    # into straight-profile cannot silently acquire curvature capability.
    assert StraightProfile.__dataclass_fields__.keys() == {
        "intervals_top_to_bottom", "bottom_tension"
    }
    assert predict_ideal_bend(fixture())["model"] != "contiguous-colinear-straight-profile-v0.1"
