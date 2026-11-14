"""Numerical differences are reported, not self-certified engineering accuracy."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_planned_section import from_payload
from planned_job_section import SourcedNumber
from torque_drag_straight import TorqueDragError
from torque_drag_weighted_curve import WeightedCurveInputs
from weighted_curve_audit import compare_refinement


def fixture():
    raw = json.loads((ROOT / "examples" / "synthetic_torque_drag_weighted_curve.json").read_text())
    return WeightedCurveInputs(
        section=from_payload(raw["planned_section"]),
        axial_friction=SourcedNumber(**raw["axial_friction"]),
        rotational_friction=SourcedNumber(**raw["rotational_friction"]),
        contact_radius=SourcedNumber(**raw["contact_radius"]),
        bottom_tension=SourcedNumber(**raw["bottom_tension"]),
        integration_steps=256,
    )


def test_refinement_reports_all_modes_and_contact_torque_without_approval():
    result = compare_refinement(fixture())
    assert result["status"] == "numeric_differences_only_not_accepted"
    assert result["step_counts"] == [64, 128, 256]
    assert len(result["comparisons"]) == 2
    for comparison in result["comparisons"]:
        assert set(comparison["absolute_tension_difference_n"]) == {
            "pickup", "slackoff", "rotation"}
        assert set(comparison["absolute_contact_force_difference_n"]) == {
            "pickup", "slackoff", "rotation"}
        assert float(comparison["absolute_rotation_contact_torque_difference_nm"]) >= 0


def test_rk4_refinement_reduces_tension_difference_on_smooth_case():
    result = compare_refinement(fixture(), step_counts=(32, 64, 128))
    coarse, fine = result["comparisons"]
    for mode in ("pickup", "slackoff", "rotation"):
        assert float(fine["absolute_tension_difference_n"][mode]) < (
            float(coarse["absolute_tension_difference_n"][mode]))


@pytest.mark.parametrize("steps", [
    (), (256,), (64, 64), (128, 64), (8, 20001),
    (8, 32.0), (True, 32), None,
])
def test_invalid_refinement_step_counts_rejected(steps):
    with pytest.raises(TorqueDragError, match="step_counts"):
        compare_refinement(fixture(), step_counts=steps)


def test_audit_rejects_invalid_inputs():
    with pytest.raises(TorqueDragError, match="WeightedCurveInputs"):
        compare_refinement(None)


def test_refinement_does_not_modify_supplied_case():
    inputs = fixture()
    compare_refinement(inputs, step_counts=(32, 64))
    assert inputs.integration_steps == 256
