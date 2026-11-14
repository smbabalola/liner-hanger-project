"""Numerical refinement audit for the experimental weighted planar curve.

Produces differences, NOT an automatic engineering acceptance or operating
safety verdict. Caller must evaluate tolerances against intended application.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from torque_drag_straight import TorqueDragError
from torque_drag_weighted_curve import WeightedCurveInputs, predict_weighted_curve

FIELDS = ("pickup", "slackoff", "rotation")


def compare_refinement(inputs: WeightedCurveInputs, *, step_counts=(64, 128, 256)):
    if not isinstance(inputs, WeightedCurveInputs):
        raise TorqueDragError("WeightedCurveInputs required")
    if (not isinstance(step_counts, (tuple, list)) or len(step_counts) < 2
        or any(type(n) is not int or not 8 <= n <= 20000 for n in step_counts)
        or any(b <= a for a, b in zip(step_counts, step_counts[1:]))):
        raise TorqueDragError("step_counts must be strictly increasing integers in 8..20000")
    snapshots = [
        predict_weighted_curve(replace(inputs, integration_steps=n))
        for n in step_counts
    ]
    comparisons = []
    for earlier, later in zip(snapshots, snapshots[1:]):
        tension_deltas = {
            mode: str(abs(
                Decimal(earlier["results"][mode]["top_tension_n"])
                - Decimal(later["results"][mode]["top_tension_n"])))
            for mode in FIELDS
        }
        torque_delta = abs(
            Decimal(earlier["results"]["rotation"]["contact_torque_nm"])
            - Decimal(later["results"]["rotation"]["contact_torque_nm"])
        )
        contact_deltas = {
            mode: str(abs(
                Decimal(earlier["results"][mode]["integrated_wall_contact_n"])
                - Decimal(later["results"][mode]["integrated_wall_contact_n"])))
            for mode in FIELDS
        }
        comparisons.append({
            "steps_from": earlier["integration_steps"],
            "steps_to": later["integration_steps"],
            "absolute_tension_difference_n": tension_deltas,
            "absolute_rotation_contact_torque_difference_nm": str(torque_delta),
            "absolute_contact_force_difference_n": contact_deltas,
        })
    return {
        "case_id": inputs.section.case_id,
        "model": "weighted-planar-rk4-refinement-audit-v0.1",
        "status": "numeric_differences_only_not_accepted",
        "step_counts": list(step_counts),
        "comparisons": comparisons,
        "warning": "Numerical convergence comparison only; no automated operating approval, accuracy certification, or field-validity conclusion.",
    }
