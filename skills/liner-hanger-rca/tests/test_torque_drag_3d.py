"""Experimental 3D torque drag independent limits and fail-closed cases."""
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_torque_drag_3d import run_payload
from run_torque_drag_weighted_curve import run_payload as planar_payload
from torque_drag_straight import TorqueDragError

EXAMPLE = ROOT / "examples" / "synthetic_torque_drag_3d.json"


def example(*, inc=90, a0=0, a1=60, mass=15, mu=0.2, steps=256):
    raw = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    st = raw["planned_section"]["survey_stations"]
    st[0]["inclination_deg"] = inc
    st[1]["inclination_deg"] = inc
    st[0]["azimuth_deg"] = a0
    st[1]["azimuth_deg"] = a1
    raw["planned_section"]["dry_linear_mass"]["value"] = mass
    raw["axial_friction"]["value"] = mu
    raw["integration_steps"] = steps
    return raw


def results(raw):
    return run_payload(raw)["results"]


@pytest.mark.parametrize("azi", [0, 30, 60, 90])
def test_zero_azimuth_turn_reuses_exact_planar_solver(azi):
    raw = example(inc=60, a0=azi, a1=azi)
    spatial = run_payload(raw)
    planar = planar_payload(raw)
    assert "planar-limit" in spatial["model"]
    assert spatial["results"] == planar["results"]


@pytest.mark.parametrize("turn", [15, 45, 60, 90])
def test_weightless_horizontal_turn_matches_analytic_capstan(turn):
    raw = example(a1=turn, steps=512)
    raw["planned_section"]["dry_linear_mass"]["value"] = (
        1000 * math.pi * (0.1**2 - 0.08**2) / 4)
    r = results(raw)
    theta = math.radians(turn)
    assert float(r["pickup"]["top_tension_n"]) == pytest.approx(
        20000 * math.exp(.2*theta), rel=1e-10)
    assert float(r["slackoff"]["top_tension_n"]) == pytest.approx(
        20000 * math.exp(-.2*theta), rel=1e-10)
    assert float(r["rotation"]["top_tension_n"]) == pytest.approx(20000, rel=1e-10)
    assert float(r["rotation"]["contact_torque_nm"]) == pytest.approx(
        .3 * 20000 * theta * .05, rel=1e-10)


def test_inclined_turn_analytical_weightless_capstan_uses_sin_inc():
    raw = example(inc=30)
    raw["planned_section"]["dry_linear_mass"]["value"] = (
        1000 * math.pi * (0.1**2 - 0.08**2)/4)
    r = results(raw)
    expected = 20000 * math.exp(.2 * math.sin(math.pi/6) * math.pi/3)
    assert float(r["pickup"]["top_tension_n"]) == pytest.approx(expected, rel=1e-10)


def test_negative_turn_magnitude_symmetry():
    p = results(example(a0=0,a1=60))
    n = results(example(a0=60,a1=0))
    for mode in ("pickup","slackoff","rotation"):
        assert float(p[mode]["top_tension_n"]) == pytest.approx(
            float(n[mode]["top_tension_n"]), rel=1e-12)
    assert float(p["rotation"]["contact_torque_nm"]) == pytest.approx(
        float(n["rotation"]["contact_torque_nm"]), rel=1e-12)


def test_azimuth_wrap_around_shortest_path():
    wrapped = results(example(a0=350,a1=10))
    unwrapped = results(example(a0=10,a1=30))
    for mode in ("pickup","slackoff","rotation"):
        assert float(wrapped[mode]["top_tension_n"]) == pytest.approx(
            float(unwrapped[mode]["top_tension_n"]), rel=1e-12)


def test_rk4_refinement_converges_for_weighted_azimuth_turn():
    low = results(example(steps=32))
    med = results(example(steps=64))
    high = results(example(steps=128))
    for mode in ("pickup","slackoff","rotation"):
        x,y,z = (float(r[mode]["top_tension_n"]) for r in (low,med,high))
        assert abs(z-y) < abs(y-x) + 1e-8


def test_source_status_and_limit_warning():
    r = run_payload(example())
    assert r["status"] == "unreviewed_inputs"
    assert r["sources"]["spatial_curve_inputs"]["axial_friction"]["source_id"]
    assert "NOT validated" in r["warning"]


@pytest.mark.parametrize("bad", [
    {"integration_steps": 2},
    {"integration_steps": True},
    {"integration_steps": 20001},
    {"bottom_tension": None},
    {"extra": "unknown"},
])
def test_rejects_schema_or_steps(bad):
    raw = example()
    raw.update(bad)
    with pytest.raises(TorqueDragError):
        run_payload(raw)


@pytest.mark.parametrize("a0,a1", [(0,180), (0,100), (0,269)])
def test_oversized_or_ambiguous_azimuth_turn_rejected(a0,a1):
    with pytest.raises(TorqueDragError, match="azimuth"):
        run_payload(example(a0=a0,a1=a1))


def test_compressive_slackoff_fails():
    raw = example()
    raw["bottom_tension"]["value"]=1
    raw["axial_friction"]["value"]=5
    with pytest.raises(TorqueDragError):
        run_payload(raw)


def test_source_missing_fails():
    raw=example()
    raw["axial_friction"]={"value":"0.2","unit":"1"}
    with pytest.raises(TorqueDragError):
        run_payload(raw)


def test_negative_buoyed_weight_fails():
    with pytest.raises(TorqueDragError, match="floating"):
        run_payload(example(mass=1))
