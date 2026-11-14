"""Independent two-segment conservation and fail-closed profile integration checks."""
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
from torque_drag_straight import TorqueDragError
from torque_drag_profile import ProfileInterval, StraightProfile, predict_straight_profile


def q(val, unit, name):
    return SourcedNumber(val, unit, "SYNTHETIC-NOT-OEM",
                         f"synthetic:{name}", "fictional-r1", "unreviewed")


def source_section(top, bottom, *, inc=60, mass=15, rho=1000, od="0.1", md_unit="m"):
    raw = json.loads((ROOT / "examples" / "synthetic_planned_section.json").read_text())
    raw["case_id"] = "SYNTHETIC-PROFILE-NOT-A-WELL"
    raw["section_id"] = f"section-{top}-{bottom}"
    raw["survey_source_id"] = "COMMON-SURVEY"
    raw["survey_revision"] = "fictional-r1"
    raw["survey_depth_unit"] = md_unit
    raw["survey_stations"] = [
        dict(measured_depth=top, inclination_deg=inc, azimuth_deg=0,
             source_ref=f"survey:MD={top}"),
        dict(measured_depth=bottom, inclination_deg=inc, azimuth_deg=0,
             source_ref=f"survey:MD={bottom}"),
    ]
    # First station TVD in metres, since a constant 60-degree inclination:
    raw["first_station_tvd"]["value"] = str(Decimal(str(top)) * Decimal("0.5"))
    raw["first_station_tvd"]["unit"] = "m"
    raw["top_md"]["value"] = top
    raw["bottom_md"]["value"] = bottom
    raw["pipe_outer_diameter"]["value"] = od
    raw["dry_linear_mass"]["value"] = mass
    raw["fluid_density"]["value"] = rho
    return from_payload(raw)


def interval(top, bottom, *, mu_ax="0.2", mu_rot="0.3", mass=15):
    return ProfileInterval(
        source_section(top, bottom, mass=mass),
        q(mu_ax, "1", "mu-axial"), q(mu_rot, "1", "mu-rotary"),
        q("0.05", "m", "contact-radius"),
    )


def profile():
    return StraightProfile((interval(0, 50), interval(50, 100)),
                           q(20000, "N", "deep-tension"))


def numbers(p):
    result = predict_straight_profile(p)
    return {key: float(value) for key, value in result["top_section_tensions_n"].items()}, result


def test_two_equal_sections_match_independent_single_length_plane_balance():
    values, r = numbers(profile())
    displaced_metal = math.pi * (.1**2 - .08**2) / 4 * 100
    weight = (15 * 100 - 1000 * displaced_metal) * 9.80665
    n = weight * math.sin(math.pi / 3)
    axial = weight * math.cos(math.pi / 3)
    assert values["pickup"] == pytest.approx(20000 + axial + .2 * n, rel=1e-12)
    assert values["slackoff"] == pytest.approx(20000 + axial - .2 * n, rel=1e-12)
    assert values["rotation"] == pytest.approx(20000 + axial, rel=1e-12)
    assert float(r["total_friction_contact_torque_nm"]) == pytest.approx(.3 * n * .05, rel=1e-12)


def test_mode_specific_tension_boundaries_propagate_not_cross_contaminate():
    _, r = numbers(profile())
    upper, lower = r["sections_top_to_bottom"]
    for mode in ("pickup", "slackoff", "rotation"):
        key = ("top_pure_rotation_tension_n" if mode == "rotation"
               else f"top_{mode}_tension_n")
        assert Decimal(upper[f"bottom_{mode}_tension_n"]) == Decimal(lower[key])
    assert Decimal(upper["bottom_pickup_tension_n"]) > Decimal(upper["bottom_slackoff_tension_n"])


def test_torque_accumulates_from_deep_to_shallow():
    _, r = numbers(profile())
    upper, lower = r["sections_top_to_bottom"]
    assert Decimal(upper["cumulative_contact_torque_nm"]) == (
        Decimal(lower["incremental_contact_torque_nm"]) +
        Decimal(upper["incremental_contact_torque_nm"]))
    assert r["status"] == "unreviewed_inputs"


def test_sections_can_have_different_sourced_dry_mass():
    p = profile()
    changed = replace(p, intervals_top_to_bottom=(
        interval(0, 50, mass=20), interval(50, 100, mass=15)))
    a = numbers(p)[0]
    b = numbers(changed)[0]
    assert b["pickup"] > a["pickup"] and b["rotation"] > a["rotation"]


def test_sections_can_have_different_friction():
    p = profile()
    changed = replace(p, intervals_top_to_bottom=(
        interval(0, 50, mu_ax="0.4", mu_rot="0.6"), interval(50, 100)))
    a, old = numbers(p)
    b, new = numbers(changed)
    assert b["pickup"] > a["pickup"]
    assert b["slackoff"] < a["slackoff"]
    assert b["rotation"] == pytest.approx(a["rotation"])
    assert Decimal(new["total_friction_contact_torque_nm"]) > Decimal(old["total_friction_contact_torque_nm"])


def test_gap_rejected():
    p = profile()
    with pytest.raises(TorqueDragError, match="gap"):
        predict_straight_profile(replace(p, intervals_top_to_bottom=(
            interval(0, 50), interval(51, 100))))


def test_overlap_rejected():
    p = profile()
    with pytest.raises(TorqueDragError, match="overlap"):
        predict_straight_profile(replace(p, intervals_top_to_bottom=(
            interval(0, 55), interval(50, 100))))


def test_boundary_dogleg_rejected():
    p = profile()
    changed = replace(p, intervals_top_to_bottom=(
        interval(0, 50), replace(interval(50, 100),
                                 section=source_section(50, 100, inc=45))))
    with pytest.raises(TorqueDragError, match="orientation"):
        predict_straight_profile(changed)


def test_survey_revision_mismatch_rejected():
    p = profile()
    lower = p.intervals_top_to_bottom[1]
    changed = replace(p, intervals_top_to_bottom=(
        p.intervals_top_to_bottom[0],
        replace(lower, section=replace(lower.section, survey_revision="different"))))
    with pytest.raises(TorqueDragError, match="survey"):
        predict_straight_profile(changed)


def test_tvd_discontinuity_rejected_without_interpolation():
    p = profile()
    lower = p.intervals_top_to_bottom[1]
    bad = replace(lower.section, first_station_tvd=q(99, "m", "wrong-datum"))
    with pytest.raises(TorqueDragError, match="TVD"):
        predict_straight_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0],
                                        replace(lower, section=bad))))


def test_duplicate_id_rejected():
    p = profile()
    lower = p.intervals_top_to_bottom[1]
    changed = replace(lower, section=replace(lower.section, section_id="section-0-50"))
    with pytest.raises(TorqueDragError, match="duplicate"):
        predict_straight_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0], changed)))


def test_negative_boundary_rejected():
    p = profile()
    with pytest.raises(TorqueDragError, match="compressive"):
        predict_straight_profile(replace(p, bottom_tension=q(-100, "N", "compression")))


def test_missing_boundary_source_rejected():
    p = profile()
    with pytest.raises(TorqueDragError, match="invalid sourced"):
        predict_straight_profile(replace(p, bottom_tension=SourcedNumber(
            20000, "N", "", "missing-id", "fictional", "unreviewed")))


def test_empty_profile_rejected():
    with pytest.raises(TorqueDragError, match="at least one"):
        predict_straight_profile(StraightProfile(tuple(), q(0, "N", "bottom")))


def test_one_interval_matches_single_section_solver():
    from torque_drag_straight import StraightTorqueDragInputs, predict_straight_section
    p = StraightProfile((interval(0, 100),), q(20000, "N", "bottom"))
    r = predict_straight_profile(p)
    x = p.intervals_top_to_bottom[0]
    single = predict_straight_section(StraightTorqueDragInputs(
        x.section, x.axial_friction, x.rotational_friction,
        x.contact_radius, p.bottom_tension))
    for mode, key in (("pickup", "top_pickup_tension_n"),
                      ("slackoff", "top_slackoff_tension_n"),
                      ("rotation", "top_pure_rotation_tension_n")):
        assert Decimal(r["top_section_tensions_n"][mode]) == Decimal(single["results"][key])
    assert Decimal(r["total_friction_contact_torque_nm"]) == Decimal(
        single["results"]["off_bottom_contact_torque_nm"])
