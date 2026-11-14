"""Independent limiting physics checks for research planar weighted-curvature RK4."""
import json
import math
import sys
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from planned_job_section import SourcedNumber
from run_planned_section import from_payload
from torque_drag_straight import (
    StraightTorqueDragInputs, TorqueDragError, predict_straight_section,
)
from torque_drag_weighted_curve import WeightedCurveInputs, predict_weighted_curve
from torque_drag_bend import IdealBendInputs, predict_ideal_bend


def source(v, unit, field):
    return SourcedNumber(str(v), unit, "FICTIONAL-NOT-OEM", "case:" + field,
                         "fictional-r1", "unreviewed")


def example(*, top_i=0, bottom_i=60, mass=15, mu=.2, mu_rot=.3, tension=20000,
            steps=256, az_top=0, az_bot=0):
    raw = json.loads((ROOT / "examples" / "synthetic_torque_drag_straight.json").read_text())["planned_section"]
    raw["survey_stations"][0]["inclination_deg"] = top_i
    raw["survey_stations"][1]["inclination_deg"] = bottom_i
    raw["survey_stations"][0]["azimuth_deg"] = az_top
    raw["survey_stations"][1]["azimuth_deg"] = az_bot
    raw["dry_linear_mass"]["value"] = str(mass)
    return WeightedCurveInputs(
        section=from_payload(raw),
        axial_friction=source(mu, "1", "axial"),
        rotational_friction=source(mu_rot, "1", "rotary"),
        contact_radius=source(.05, "m", "radius"),
        bottom_tension=source(tension, "N", "tension"),
        integration_steps=steps,
    )


def quantities(case):
    out = predict_weighted_curve(case)
    return {k: {label: float(value) for label, value in row.items()}
            for k, row in out["results"].items()}


@pytest.mark.parametrize("incl", [0, 30, 60, 90])
def test_constant_inclination_reduces_to_independent_straight_solver(incl):
    c = example(top_i=incl, bottom_i=incl)
    r = quantities(c)
    ref = predict_straight_section(StraightTorqueDragInputs(
        c.section, c.axial_friction, c.rotational_friction,
        c.contact_radius, c.bottom_tension))["results"]
    assert r["pickup"]["top_tension_n"] == pytest.approx(
        float(ref["top_pickup_tension_n"]), rel=1e-11)
    assert r["slackoff"]["top_tension_n"] == pytest.approx(
        float(ref["top_slackoff_tension_n"]), rel=1e-11)
    assert r["rotation"]["top_tension_n"] == pytest.approx(
        float(ref["top_pure_rotation_tension_n"]), rel=1e-11)
    assert r["rotation"]["contact_torque_nm"] == pytest.approx(
        float(ref["off_bottom_contact_torque_nm"]), rel=1e-11)


def test_no_friction_weighted_build_has_exact_gravity_integral():
    c = example(top_i=0, bottom_i=60, mu=0, mu_rot=0)
    x = quantities(c)
    dry = 15.
    buoyed = dry - 1000 * math.pi * (.1**2 - .08**2) / 4
    w = buoyed * 9.80665
    L = 100
    k = math.pi / 3 / L
    expected = 20000 + w * (math.sin(math.pi/3) - math.sin(0)) / k
    for mode in ("pickup", "slackoff", "rotation"):
        assert x[mode]["top_tension_n"] == pytest.approx(expected, rel=1e-10)


def test_weightless_curvature_converges_to_separate_exact_capstan():
    # Dry mass balances fluid displacement (only a synthetic limiting state).
    mass = 1000 * math.pi * (.1**2 - .08**2)/4
    c = example(top_i=0, bottom_i=60, mass=mass, tension=10000, steps=512)
    x = quantities(c)
    bend = IdealBendInputs(
        bend_id="synthetic-weightless-crosscheck", bottom_tension=c.bottom_tension,
        bend_angle=source(60, "deg", "angle"), axial_friction=c.axial_friction,
        rotational_friction=c.rotational_friction,
        contact_radius=c.contact_radius, zero_distributed_weight=True)
    ref = predict_ideal_bend(bend)["results"]
    assert x["pickup"]["top_tension_n"] == pytest.approx(float(ref["top_pickup_tension_n"]), rel=1e-8)
    assert x["slackoff"]["top_tension_n"] == pytest.approx(float(ref["top_slackoff_tension_n"]), rel=1e-8)
    assert x["rotation"]["top_tension_n"] == pytest.approx(float(ref["top_pure_rotation_tension_n"]), rel=1e-8)
    assert x["rotation"]["contact_torque_nm"] == pytest.approx(
        float(ref["pure_rotation_contact_torque_nm"]), rel=1e-8)


def test_weighted_build_converges_on_refinement():
    p = example(top_i=0, bottom_i=60, steps=64)
    r64 = quantities(p)
    r128 = quantities(replace(p, integration_steps=128))
    r256 = quantities(replace(p, integration_steps=256))
    for mode in ("pickup", "slackoff", "rotation"):
        a = r64[mode]["top_tension_n"]
        b = r128[mode]["top_tension_n"]
        c = r256[mode]["top_tension_n"]
        assert abs(c-b) < abs(b-a) + 1e-9
        assert c > 0


def test_weighted_drop_converges_on_refinement():
    p = example(top_i=60, bottom_i=0, steps=64)
    a = quantities(p)
    b = quantities(replace(p, integration_steps=256))
    for mode in ("pickup", "slackoff", "rotation"):
        assert a[mode]["top_tension_n"] == pytest.approx(
            b[mode]["top_tension_n"], rel=5e-6)


def test_build_and_drop_have_different_signed_normal_reactions():
    build = quantities(example(top_i=0, bottom_i=60))
    drop = quantities(example(top_i=60, bottom_i=0))
    # Curvature contribution can add to or subtract from low-side gravity.
    assert build["rotation"]["integrated_wall_contact_n"] != pytest.approx(
        drop["rotation"]["integrated_wall_contact_n"], rel=1e-6)


def test_no_axial_friction_pickup_and_slackoff_match():
    v = quantities(example(mu=0))
    assert v["pickup"]["top_tension_n"] == pytest.approx(v["slackoff"]["top_tension_n"])
    assert v["rotation"]["contact_torque_nm"] > 0


def test_no_rotational_friction_zero_torque():
    v = quantities(example(mu_rot=0))
    assert v["rotation"]["contact_torque_nm"] == 0
    assert v["pickup"]["top_tension_n"] > 0


def test_increased_friction_enlarges_tensile_pickup_slackoff_span():
    lo, hi = quantities(example(mu=.1)), quantities(example(mu=.4))
    assert hi["pickup"]["top_tension_n"] > lo["pickup"]["top_tension_n"]
    assert hi["slackoff"]["top_tension_n"] < lo["slackoff"]["top_tension_n"]


def test_output_is_sourced_unreviewed_research_model():
    r = predict_weighted_curve(example())
    assert r["status"] == "unreviewed_inputs"
    assert "not field-validated" in r["warning"]
    assert r["integration_steps"] == 256
    assert r["sources"]["weighted_curve_inputs"]["axial_friction"]["source_location"] == "case:axial"


@pytest.mark.parametrize("step", [0, 1, 7, -1, 20001, 32.0, True, None])
def test_step_count_must_be_explicit_supported_integer(step):
    with pytest.raises(TorqueDragError, match="integration_steps"):
        predict_weighted_curve(replace(example(), integration_steps=step))


@pytest.mark.parametrize("bad", [
    {"axial_friction": source(-.1, "1", "mu")},
    {"rotational_friction": source(-.1, "1", "mu")},
    {"bottom_tension": source(0, "N", "zero")},
    {"bottom_tension": source(-1, "N", "negative")},
    {"contact_radius": source(.01, "m", "bad-radius")},
    {"contact_radius": source("NaN", "m", "invalid")},
    {"bottom_tension": source(10000, "unknown", "unit")},
])
def test_fail_closed_bad_physics_or_units(bad):
    with pytest.raises(TorqueDragError):
        predict_weighted_curve(replace(example(), **bad))


def test_3d_turn_rejected():
    with pytest.raises(TorqueDragError, match="azimuth"):
        predict_weighted_curve(example(az_bot=20))


def test_unsupported_over_horizontal_inclination_rejected():
    c = example()
    from directional_survey import SurveyStation
    stations = (c.section.survey_stations[0], replace(c.section.survey_stations[1], inclination_deg=120))
    with pytest.raises(TorqueDragError, match="inclination"):
        predict_weighted_curve(replace(c, section=replace(c.section, survey_stations=stations)))


def test_negative_buoyed_weight_is_rejected():
    with pytest.raises(TorqueDragError, match="floating"):
        predict_weighted_curve(example(mass=1))


def test_compressive_slackoff_state_rejected():
    with pytest.raises(TorqueDragError, match="compression"):
        predict_weighted_curve(example(top_i=90, bottom_i=90, tension=1, mu=5))


def test_fixed_bottom_tension_is_not_liner_hanger_actuation_force():
    r = predict_weighted_curve(example())
    assert "liner-hanger" in r["warning"]
