"""Synthetic profile coupling, independent split invariance and fail-closed survey checks."""
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
from run_torque_drag_weighted_profile import run_payload
from torque_drag_straight import TorqueDragError
from torque_drag_weighted_profile import (
    WeightedPlanarProfile, WeightedProfileInterval, predict_weighted_planar_profile,
)
from torque_drag_weighted_curve import (
    WeightedCurveInputs, predict_weighted_curve,
)


def raw():
    return json.loads((ROOT / "examples" / "synthetic_torque_drag_weighted_profile.json").read_text())


def profile():
    p = raw()
    intervals = []
    for row in p["intervals_top_to_bottom"]:
        intervals.append(WeightedProfileInterval(
            section=from_payload(row["planned_section"]),
            axial_friction=SourcedNumber(**row["axial_friction"]),
            rotational_friction=SourcedNumber(**row["rotational_friction"]),
            contact_radius=SourcedNumber(**row["contact_radius"]),
            integration_steps=row["integration_steps"],
        ))
    return WeightedPlanarProfile(tuple(intervals), SourcedNumber(**p["bottom_tension"]))


def test_fictional_two_interval_profile_splits_uniform_100m_curve():
    p = profile()
    result = predict_weighted_planar_profile(p)
    full_raw = json.loads((ROOT / "examples" / "synthetic_torque_drag_weighted_curve.json").read_text())
    full = predict_weighted_curve(WeightedCurveInputs(
        section=from_payload(full_raw["planned_section"]),
        axial_friction=SourcedNumber(**full_raw["axial_friction"]),
        rotational_friction=SourcedNumber(**full_raw["rotational_friction"]),
        contact_radius=SourcedNumber(**full_raw["contact_radius"]),
        bottom_tension=SourcedNumber(**full_raw["bottom_tension"]),
        integration_steps=512,
    ))
    for mode in ("pickup", "slackoff", "rotation"):
        assert float(result["top_tensions_n"][mode]) == pytest.approx(
            float(full["results"][mode]["top_tension_n"]), rel=2e-9)
    assert float(result["total_rotation_contact_torque_nm"]) == pytest.approx(
        float(full["results"]["rotation"]["contact_torque_nm"]), rel=2e-9)
    assert result["status"] == "unreviewed_inputs"


def test_every_mode_propagates_separately():
    r = predict_weighted_planar_profile(profile())
    upper, lower = r["sections_top_to_bottom"]
    for mode in ("pickup", "slackoff", "rotation"):
        assert Decimal(upper["modes"][mode]["bottom_tension_n"]) == Decimal(
            lower["modes"][mode]["top_tension_n"])
    assert Decimal(upper["modes"]["pickup"]["bottom_tension_n"]) > Decimal(
        upper["modes"]["slackoff"]["bottom_tension_n"])


def test_rotation_contact_torque_is_sum_of_two_sections():
    r = predict_weighted_planar_profile(profile())
    upper, lower = r["sections_top_to_bottom"]
    assert Decimal(r["total_rotation_contact_torque_nm"]) == (
        Decimal(upper["incremental_rotation_contact_torque_nm"])
        + Decimal(lower["incremental_rotation_contact_torque_nm"]))
    assert Decimal(upper["cumulative_rotation_contact_torque_nm"]) == Decimal(
        r["total_rotation_contact_torque_nm"])


def test_unequal_friction_between_sections_affects_axial_not_rotation_tension():
    p = profile()
    first = p.intervals_top_to_bottom[0]
    high_mu = replace(first.axial_friction, value="0.4")
    changed = replace(p, intervals_top_to_bottom=(
        replace(first, axial_friction=high_mu), p.intervals_top_to_bottom[1]))
    baseline = predict_weighted_planar_profile(p)
    altered = predict_weighted_planar_profile(changed)
    assert Decimal(altered["top_tensions_n"]["pickup"]) > Decimal(
        baseline["top_tensions_n"]["pickup"])
    assert Decimal(altered["top_tensions_n"]["slackoff"]) < Decimal(
        baseline["top_tensions_n"]["slackoff"])
    assert altered["top_tensions_n"]["rotation"] == baseline["top_tensions_n"]["rotation"]


def test_azimuth_turn_inside_interval_rejected():
    p = profile()
    last = p.intervals_top_to_bottom[1]
    st = last.section.survey_stations
    changed = replace(last.section, survey_stations=(
        st[0], replace(st[1], azimuth_deg=20)))
    with pytest.raises(TorqueDragError, match="azimuth"):
        predict_weighted_planar_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0],
                                        replace(last, section=changed))))


def test_azimuth_change_at_boundary_rejected():
    p = profile()
    last = p.intervals_top_to_bottom[1]
    st = tuple(replace(s, azimuth_deg=10) for s in last.section.survey_stations)
    changed = replace(last.section, survey_stations=st)
    with pytest.raises(TorqueDragError, match="azimuth|mismatch"):
        predict_weighted_planar_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0],
                                        replace(last, section=changed))))


def test_boundary_kink_rejected():
    p = profile()
    last = p.intervals_top_to_bottom[1]
    st = last.section.survey_stations
    changed = replace(last.section, survey_stations=(
        replace(st[0], inclination_deg=31), st[1]))
    with pytest.raises(TorqueDragError, match="boundary inclination"):
        predict_weighted_planar_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0],
                                        replace(last, section=changed))))


@pytest.mark.parametrize("start", [49, 51])
def test_md_gap_or_overlap_rejected(start):
    p = profile()
    last = p.intervals_top_to_bottom[1]
    st = last.section.survey_stations
    changed = replace(last.section,
        top_md=replace(last.section.top_md, value=start),
        survey_stations=(replace(st[0], measured_depth=start), st[1]))
    with pytest.raises(TorqueDragError, match="MD gap or overlap"):
        predict_weighted_planar_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0],
                                        replace(last, section=changed))))


def test_tvd_jump_rejected():
    p = profile()
    last = p.intervals_top_to_bottom[1]
    changed = replace(last.section, first_station_tvd=replace(
        last.section.first_station_tvd, value=80))
    with pytest.raises(TorqueDragError, match="TVD discontinuity"):
        predict_weighted_planar_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0],
                                        replace(last, section=changed))))


def test_survey_revision_mismatch_rejected():
    p = profile()
    last = p.intervals_top_to_bottom[1]
    changed = replace(last.section, survey_revision="conflicting-revision")
    with pytest.raises(TorqueDragError, match="revision"):
        predict_weighted_planar_profile(replace(
            p, intervals_top_to_bottom=(p.intervals_top_to_bottom[0],
                                        replace(last, section=changed))))


def test_duplicate_section_id_rejected():
    p = profile()
    first, last = p.intervals_top_to_bottom
    changed = replace(last.section, section_id=first.section.section_id)
    with pytest.raises(TorqueDragError, match="duplicate"):
        predict_weighted_planar_profile(replace(p, intervals_top_to_bottom=(
            first, replace(last, section=changed))))


def test_invalid_bottom_tension_rejected():
    p = profile()
    with pytest.raises(TorqueDragError):
        predict_weighted_planar_profile(replace(
            p, bottom_tension=replace(p.bottom_tension, value=-10)))


def test_empty_profile_rejected():
    with pytest.raises(TorqueDragError, match="at least one"):
        predict_weighted_planar_profile(WeightedPlanarProfile(tuple(), profile().bottom_tension))


def test_contact_side_transition_in_one_section_rejects_entire_profile():
    p = profile()
    with pytest.raises(TorqueDragError, match="contact side transition"):
        predict_weighted_planar_profile(replace(
            p, bottom_tension=replace(p.bottom_tension, value=1000)))


def test_source_metadata_and_warning_preserved():
    r = predict_weighted_planar_profile(profile())
    assert "NOT rig hookload" in r["warning"]
    assert r["sections_top_to_bottom"][0]["sources"]["planned_section"]["survey"]["source_id"]


def test_single_interval_matches_weighted_curve():
    p = profile()
    last = p.intervals_top_to_bottom[-1]
    one = WeightedPlanarProfile((last,), p.bottom_tension)
    combined = predict_weighted_planar_profile(one)
    bare = predict_weighted_curve(WeightedCurveInputs(
        last.section, last.axial_friction, last.rotational_friction,
        last.contact_radius, p.bottom_tension, last.integration_steps))
    for mode in ("pickup", "slackoff", "rotation"):
        assert float(combined["top_tensions_n"][mode]) == pytest.approx(
            float(bare["results"][mode]["top_tension_n"]), rel=1e-12)
