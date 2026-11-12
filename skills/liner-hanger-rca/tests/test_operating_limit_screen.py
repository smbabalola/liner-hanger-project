"""Operating-limit screen regression; all values/identities deliberately synthetic."""
import importlib.util
import sys
from pathlib import Path

import pytest

FILE = Path(__file__).resolve().parents[1] / "scripts" / "operating_limit_screen.py"
spec = importlib.util.spec_from_file_location("operating_limit_screen", FILE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def identity(manufacturer="baker_hughes", revision="SYNTHETIC-A"):
    return mod.ToolIdentity(manufacturer, "SYNTHETIC-FAMILY", "SYNTHETIC-MODEL",
                            "synthetic-size", revision, "assembly-test-1")


def rule(**changes):
    data = dict(
        rule_id="SYNTHETIC-LIMIT-01", tool=identity(), stage="hanger_setting",
        parameter="recorded_test_pressure", quantity="pressure", unit="psi",
        pressure_basis="gauge", measurement_domain="rig_standpipe",
        comparator="maximum", lower=None, upper=200,
        origin="job", source_id="SYNTHETIC-JOB-PROGRAM",
        source_revision="TEST-A", source_location="synthetic-page-1",
        approval_reference="SYNTHETIC-CHECK-1", reviewed_by="synthetic-reviewer",
        reviewed_at="2026-01-01T00:00:00Z", authorized_for_case=True)
    data.update(changes)
    return mod.ApprovedLimit(**data)


def measurement(**changes):
    data = dict(
        tool=identity(), stage="hanger_setting",
        parameter="recorded_test_pressure", quantity="pressure", value=180,
        unit="psi", pressure_basis="gauge", measurement_domain="rig_standpipe",
        source_id="SYNTHETIC-RIG-CSV", channel_id="synthetic-spp",
        timestamp="2026-01-01T00:10:00Z",
        units_verified=True, channel_mapping_verified=True,
        clock_alignment_verified=True, measurement_equivalence_verified=True)
    data.update(changes)
    return mod.Observation(**data)


def test_screen_within_is_not_proof_of_setting():
    found = mod.screen(rule(), measurement())
    assert found["status"] == "within_screening_bounds"
    assert "No equipment-state" in found["conclusion"]


def test_outside_is_review_candidate_not_failure():
    found = mod.screen(rule(), measurement(value=205))
    assert found["status"] == "outside_screening_bounds"
    assert found["comparison"]["upper"] == "200"


def test_lower_and_window_boundaries():
    r = rule(comparator="minimum", lower=100, upper=None)
    assert mod.screen(r, measurement(value=99))["status"] == "outside_screening_bounds"
    r = rule(comparator="range", lower=100, upper=200)
    assert mod.screen(r, measurement(value=100))["status"] == "within_screening_bounds"
    assert mod.screen(r, measurement(value=200))["status"] == "within_screening_bounds"


@pytest.mark.parametrize("change", [
    {"tool": identity("halliburton")},
    {"tool": identity(revision="SYNTHETIC-B")},
    {"stage": "cementing"},
    {"parameter": "tool_internal_pressure"},
    {"unit": "bar"},
    {"pressure_basis": "differential"},
    {"measurement_domain": "cement_unit_discharge"},
    {"units_verified": False},
    {"channel_mapping_verified": False},
    {"clock_alignment_verified": False},
    {"measurement_equivalence_verified": False},
])
def test_mismatch_fails_closed(change):
    found = mod.screen(rule(), measurement(**change))
    assert found["status"] == "unverifiable"
    assert found["reasons"]


def test_oem_rule_never_leaks_to_other_manufacturer():
    found = mod.screen(rule(tool=identity("halliburton")),
                       measurement(tool=identity("halliburton")))
    assert found["status"] == "unverifiable"
    assert "manufacturer unsupported" in found["reasons"][0]


def test_unapproved_rule_cannot_compare():
    found = mod.screen(rule(authorized_for_case=False), measurement())
    assert found["status"] == "unverifiable"
    assert any("authorized" in r for r in found["reasons"])


@pytest.mark.parametrize("bad", [
    dict(comparator="range", lower=220, upper=100),
    dict(comparator="maximum", lower=20, upper=200),
    dict(quantity="pressure", unit="ft-lbf"),
    dict(upper="NaN"),
    dict(source_id=""),
])
def test_bad_rules_are_rejected(bad):
    with pytest.raises(mod.LimitError):
        mod.screen(rule(**bad), measurement())


def test_json_contract_roundtrip():
    from dataclasses import asdict
    result = mod.screen_from_dict(asdict(rule()), asdict(measurement()))
    assert result["status"] == "within_screening_bounds"


def test_missing_contract_field_is_rejected():
    from dataclasses import asdict
    l = asdict(rule())
    del l["source_revision"]
    with pytest.raises(mod.LimitError):
        mod.screen_from_dict(l, asdict(measurement()))


def test_rig_vs_cementer_domains_not_equivalent():
    from dataclasses import replace
    r = rule(stage="cementing", measurement_domain="cement_unit_discharge",
             parameter="cementer_pressure")
    o = measurement(stage="cementing", parameter="cementer_pressure",
                    measurement_domain="rig_standpipe")
    assert mod.screen(r, o)["status"] == "unverifiable"
    assert "sensor/measurement domain mismatch" in mod.screen(r, o)["reasons"]
