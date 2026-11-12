"""Source-gated engineering baseline contracts: synthetic values, no physics model."""
import importlib.util
import sys
from dataclasses import replace
from pathlib import Path

import pytest

path = Path(__file__).resolve().parents[1] / "scripts" / "engineering_baseline.py"
spec = importlib.util.spec_from_file_location("engineering_baseline", path)
baseline = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = baseline
spec.loader.exec_module(baseline)

def make(basis, **kwargs):
    defaults = dict(
        case_id="SYNTH-PLAN-1", stage="running_in_hole",
        parameter="predicted_pickup_hookload", component_id="synthetic-string",
        domain="rig_hookload", location="surface_hook",
        quantity_family="load", value=100, unit="kN", basis=basis,
        source_id="SYNTHETIC-SOURCE", source_location="fictional-row-1",
        source_revision="synthetic-r1", review_status="reviewed",
        model_version="synthetic-arithmetic-1" if basis == "independently_calculated" else None,
        time_basis="synthetic UTC source" if basis == "observed_surface" else None,
        measured_depth_m=1000,
    )
    defaults.update(kwargs)
    return baseline.EngineeringQuantity(**defaults)

def test_independent_prediction_comparison_unit_conversion():
    modeled = make("independently_calculated", value=100, unit="kN")
    original = make("original_design_result", value=100000, unit="N")
    result = baseline.compare_design_prediction(modeled, original)
    assert result["status"] == "numeric_difference_only"
    assert result["difference_in_si"] == "0"
    assert result["si_unit"] == "N"
    assert "No compliance" in result["warning"]

def test_observed_vs_predicted_is_just_difference_not_failure_verdict():
    recorded = make("observed_surface", value=105, unit="kN")
    modeled = make("independently_calculated", value=100, unit="kN")
    result = baseline.compare_observed_to_prediction(recorded, modeled)
    assert result["status"] == "numeric_difference_only"
    assert result["difference_in_si"] == "5000"

@pytest.mark.parametrize("change, reason", [
    ({"case_id": "ANOTHER-WELL"}, "different cases"),
    ({"stage": "setting_hanger"}, "mismatched stage"),
    ({"domain": "tool_hydraulic_force"}, "mismatched domain"),
    ({"location": "tool_mandrel"}, "mismatched location"),
    ({"parameter": "slackoff_load"}, "mismatched parameter"),
    ({"measured_depth_m": 1001}, "different MD; no silent interpolation"),
    ({"measured_depth_m": None}, "depth basis missing on one side"),
])
def test_incompatible_design_results_fail_closed(change, reason):
    modeled = make("independently_calculated")
    original = make("original_design_result", **change)
    assert baseline.compare_design_prediction(modeled, original) == {
        "status": "not_comparable", "reason": reason}

def test_unreviewed_design_result_cannot_be_treated_as_validated():
    modeled = make("independently_calculated", review_status="unreviewed")
    result = baseline.compare_design_prediction(
        modeled, make("original_design_result"))
    assert result["status"] == "incomplete"

def test_no_silent_pressure_basis_conversion():
    modeled = make("independently_calculated", quantity_family="pressure",
                   parameter="seat_differential", unit="psi",
                   pressure_basis="differential", domain="ball_seat")
    original = make("original_design_result", quantity_family="pressure",
                    parameter="seat_differential", unit="psi",
                    pressure_basis="gauge", domain="ball_seat")
    assert baseline.compare_design_prediction(modeled, original)["status"] == "not_comparable"

def test_standpipe_pressure_cannot_be_substituted_for_ball_seat_differential():
    observed = make("observed_surface", quantity_family="pressure",
                    parameter="ball_seat_pressure", unit="psi", pressure_basis="gauge",
                    domain="rig_standpipe")
    calculated = make("independently_calculated", quantity_family="pressure",
                      parameter="ball_seat_pressure", unit="psi",
                      pressure_basis="differential", domain="ball_seat")
    assert baseline.compare_observed_to_prediction(observed, calculated)["status"] == "not_comparable"

def test_no_rig_pump_to_cement_pump_fallback():
    rig = make("observed_surface", quantity_family="flow", unit="L/min",
               parameter="pumping_rate", domain="rig_pump", value=200)
    cement = make("independently_calculated", quantity_family="flow", unit="L/min",
                  parameter="pumping_rate", domain="cementing_unit", value=200)
    assert baseline.compare_observed_to_prediction(rig, cement)["status"] == "not_comparable"

def test_incomplete_source_rejected():
    with pytest.raises(baseline.BaselineError, match="source_location"):
        make("original_design_result", source_location="").validate()

def test_missing_model_version_rejected():
    with pytest.raises(baseline.BaselineError, match="model_version"):
        make("independently_calculated", model_version=None).validate()

def test_missing_observation_time_basis_rejected():
    with pytest.raises(baseline.BaselineError, match="time_basis"):
        make("observed_surface", time_basis=None).validate()

def test_nan_and_unknown_units_are_rejected():
    with pytest.raises(baseline.BaselineError):
        make("original_design_result", value="NaN").validate()
    with pytest.raises(baseline.BaselineError):
        make("original_design_result", unit="unknown").validate()

def test_design_comparison_requires_correct_evidence_basis():
    assert baseline.compare_design_prediction(
        make("planned_input"), make("original_design_result")
    )["status"] == "not_comparable"
