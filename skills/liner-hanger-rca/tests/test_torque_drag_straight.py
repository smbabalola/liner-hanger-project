"""Independent straight-incline plane force balance; fictional sourced fixture."""
import json
import math
import sys
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_planned_section import from_payload
from planned_job_section import SourcedNumber, PlannedSectionError
from torque_drag_straight import (
    StraightTorqueDragInputs, TorqueDragError,
    friction_sensitivity, predict_straight_section,
)
from directional_survey import SurveyStation


def q(value, unit, name, reviewed=False):
    return SourcedNumber(value, unit, "SYNTHETIC-NOT-OEM",
                         "fictional:" + name, "fictional-r1",
                         "reviewed" if reviewed else "unreviewed")


def case(incl=60, *, mu_ax="0.2", mu_rot="0.3", bottom=20000):
    raw = json.loads((ROOT / "examples" / "synthetic_planned_section.json").read_text())
    raw["survey_stations"][0]["inclination_deg"] = incl
    raw["survey_stations"][1]["inclination_deg"] = incl
    return StraightTorqueDragInputs(
        section=from_payload(raw), axial_friction=q(mu_ax, "1", "axial-mu"),
        rotational_friction=q(mu_rot, "1", "rotary-mu"),
        contact_radius=q("0.05", "m", "contact-radius"),
        bottom_tension=q(bottom, "N", "bottom-boundary"),
    )


def numbers(c):
    return {k: float(v) for k, v in predict_straight_section(c)["results"].items()}


def test_60_degree_incline_independent_plane_balance():
    # Separately derived from cylindrical wall displacement and elementary statics.
    values = numbers(case())
    metal_volume = math.pi * (0.1**2 - 0.08**2) / 4 * 100
    W = (15 * 100 - 1000 * metal_volume) * 9.80665
    normal = W * math.sin(math.pi / 3)
    gravity_axial = W * math.cos(math.pi / 3)
    assert values["low_side_normal_force_n"] == pytest.approx(normal, rel=1e-12)
    assert values["top_pickup_tension_n"] == pytest.approx(
        20000 + gravity_axial + 0.2 * normal, rel=1e-12)
    assert values["top_slackoff_tension_n"] == pytest.approx(
        20000 + gravity_axial - 0.2 * normal, rel=1e-12)
    assert values["top_pure_rotation_tension_n"] == pytest.approx(
        20000 + gravity_axial, rel=1e-12)
    assert values["off_bottom_contact_torque_nm"] == pytest.approx(
        0.3 * normal * 0.05, rel=1e-12)


def test_vertical_has_zero_low_side_friction_torque():
    v = numbers(case(0))
    assert v["low_side_normal_force_n"] == 0
    assert v["axial_drag_force_n"] == 0
    assert v["off_bottom_contact_torque_nm"] == 0
    assert v["top_pickup_tension_n"] == pytest.approx(
        v["top_slackoff_tension_n"])


def test_horizontal_has_no_axial_weight_component():
    v = numbers(case(90))
    assert v["top_pure_rotation_tension_n"] == 20000
    assert v["top_pickup_tension_n"] > 20000 > v["top_slackoff_tension_n"]


def test_zero_axial_friction_collapses_pickup_slackoff():
    v = numbers(case(mu_ax=0))
    assert v["axial_drag_force_n"] == 0
    assert v["top_pickup_tension_n"] == pytest.approx(v["top_slackoff_tension_n"])


def test_zero_rotational_friction_gives_zero_contact_torque():
    v = numbers(case(mu_rot=0))
    assert v["off_bottom_contact_torque_nm"] == 0
    assert v["axial_drag_force_n"] > 0


def test_drag_span_equals_twice_sliding_friction():
    v = numbers(case())
    assert (v["top_pickup_tension_n"] - v["top_slackoff_tension_n"]) == pytest.approx(
        2 * v["axial_drag_force_n"])


def test_mu_monotonicity_and_gravity_independence():
    low, high = numbers(case(mu_ax=0.1)), numbers(case(mu_ax=0.4))
    assert high["top_pickup_tension_n"] > low["top_pickup_tension_n"]
    assert high["top_slackoff_tension_n"] < low["top_slackoff_tension_n"]
    assert high["top_pure_rotation_tension_n"] == low["top_pure_rotation_tension_n"]


def test_pure_rotation_torque_scales_with_radius_and_coefficient():
    low = numbers(case(mu_rot=0.2))
    hi_case = replace(case(mu_rot=0.4), contact_radius=q("0.10", "m", "radius"))
    high = numbers(hi_case)
    assert high["off_bottom_contact_torque_nm"] == pytest.approx(
        low["off_bottom_contact_torque_nm"] * 4)


def test_tension_boundary_additive_not_hookload():
    v1 = numbers(case(bottom=10000))
    v2 = numbers(case(bottom=20000))
    assert v2["top_pickup_tension_n"] - v1["top_pickup_tension_n"] == pytest.approx(10000)
    assert "NOT rig hookload" in predict_straight_section(case())["warning"]


def test_unit_equivalence_bottom_force():
    metric = numbers(case(bottom=20000))
    imperial = replace(case(), bottom_tension=q(Decimal("20000") /
         Decimal("4.4482216152605"), "lbf", "bottom"))
    # decimal input/float conversion effects limited by ratio representation
    assert numbers(imperial)["top_pickup_tension_n"] == pytest.approx(
        metric["top_pickup_tension_n"], rel=1e-12)


def test_unreviewed_provenance_propagates():
    assert predict_straight_section(case())["status"] == "unreviewed_inputs"


def test_hypothetical_sensitivity_never_approved():
    outputs = friction_sensitivity(case(), axial_candidates=[0.1, 0.3],
                                    rotational_candidates=[0.2, 0.4])
    assert len(outputs) == 4
    assert all(result["status"] == "unreviewed_inputs" for result in outputs)
    assert all(result["sources"]["torque_drag_inputs"]["axial_friction"]["source_id"]
               == "SENSITIVITY-NOT-SOURCED" for result in outputs)


@pytest.mark.parametrize("alter", [
    {"axial_friction": q(-0.1, "1", "negative")},
    {"rotational_friction": q(-0.1, "1", "negative")},
    {"axial_friction": q("NaN", "1", "nan")},
    {"axial_friction": q(0.2, "unknown", "unit")},
    {"contact_radius": q(0.01, "m", "inside-pipe")},
    {"bottom_tension": q(-1, "N", "compression")},
    {"bottom_tension": q(None, "N", "missing")},
])
def test_invalid_friction_and_boundaries_rejected(alter):
    with pytest.raises(TorqueDragError):
        predict_straight_section(replace(case(), **alter))


@pytest.mark.parametrize("inc", [-1, 91, 100])
def test_unsupported_inclinations_fail_closed(inc):
    # Build a valid sourced section first. The source-intake layer correctly
    # rejects inclination -1 before a TorqueDragInputs object can be created.
    # Replacing the stations here exercises the torque/drag API's own
    # fail-closed error contract at its boundary, including upstream errors.
    c = case()
    stations = tuple(replace(station, inclination_deg=inc)
                     for station in c.section.survey_stations)
    unsupported = replace(c, section=replace(c.section, survey_stations=stations))
    with pytest.raises(TorqueDragError, match="inclination|range|supported"):
        predict_straight_section(unsupported)


def test_invalid_survey_is_rejected_by_source_intake_before_engine():
    raw = json.loads((ROOT / "examples" / "synthetic_planned_section.json").read_text())
    raw["survey_stations"][0]["inclination_deg"] = -1
    with pytest.raises(PlannedSectionError, match="inclination"):
        from_payload(raw)


def test_dogleg_change_rejected_even_if_section_integrator_can_handle_it():
    c = case()
    changed = replace(c.section, survey_stations=(
        SurveyStation(0, 0, 0, "fictional-start"),
        SurveyStation(100, 60, 0, "fictional-end")))
    with pytest.raises(TorqueDragError, match="curvature"):
        predict_straight_section(replace(c, section=changed))


def test_azimuth_turn_rejected():
    c = case()
    changed = replace(c.section, survey_stations=(
        SurveyStation(0, 60, 0, "fictional-start"),
        SurveyStation(100, 60, 10, "fictional-end")))
    with pytest.raises(TorqueDragError, match="curvature"):
        predict_straight_section(replace(c, section=changed))


def test_compressive_slackoff_rejected_as_unsupported():
    with pytest.raises(TorqueDragError, match="compressive"):
        predict_straight_section(case(90, bottom=0, mu_ax=0.8))


def test_floating_pipe_rejected():
    c = case()
    updated = replace(c.section, dry_linear_mass=q(1, "kg/m", "floating"))
    with pytest.raises(TorqueDragError, match="negative apparent weight"):
        predict_straight_section(replace(c, section=updated))


def test_no_sensitivity_empty_candidate_list():
    with pytest.raises(TorqueDragError):
        friction_sensitivity(case(), axial_candidates=[], rotational_candidates=[0.2])
