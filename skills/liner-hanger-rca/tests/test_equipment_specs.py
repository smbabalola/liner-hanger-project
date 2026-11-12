"""Synthetic-only equipment specification and internal MD reference regression."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


specs = load("equipment_specs", "equipment_specs.py")
tally_mod = load("bha_tally_for_specs", "bha_tally.py")


def value(name="rating", kind="pressure_rating", origin="manufacturer",
          value="300", unit="psi", status="unreviewed"):
    return specs.SpecificationValue(
        name=name, kind=kind, value=value, unit=unit, origin=origin,
        source_id="SYNTHETIC-TEST", source_location="fictional:1",
        status=status, entered_by="test engineer",
        reviewed_by="checker" if status == "reviewed" else None,
        reviewed_at="2026-01-01T10:00:00Z" if status == "reviewed" else None)


def record(values):
    return specs.EquipmentRecord(
        specs.EquipmentIdentity("baker_hughes", "synthetic hanger", model="EXAMPLE",
                                revision="fictional-rev"), tuple(values), "TEST-001")


def test_manual_manufacturer_and_job_values_stay_separate():
    original = record([value()])
    candidate = specs.candidate_edit(original, value(
        "job limit", "pressure_rating", "job", "250"))
    assert original.values_by_origin("job") == ()
    assert len(candidate.values_by_origin("manufacturer")) == 1
    assert len(candidate.values_by_origin("job")) == 1


def test_review_is_required_for_comparison():
    r = record([value(), value("job limit", "pressure_rating", "job", "250")])
    assert specs.compare_job_to_manufacturer(r, "job limit", "rating")["status"] == "unavailable"


def test_comparison_is_not_compliance_claim():
    r = record([value(status="reviewed"),
                value("job limit", "pressure_rating", "job", "250", status="reviewed")])
    result = specs.compare_job_to_manufacturer(r, "job limit", "rating")
    assert result["status"] == "numeric_comparison_only"
    assert result["difference"] == "-50"
    assert "Not a limit" in result["warning"]


def test_incompatible_pressure_kind_is_not_compared():
    r = record([value(status="reviewed"),
                value("job set", "setting_pressure", "job", "250", status="reviewed")])
    assert specs.compare_job_to_manufacturer(r, "job set", "rating")["status"] == "not_comparable"


def test_incompatible_units_are_not_compared():
    r = record([value(status="reviewed"),
                value("job limit", "pressure_rating", "job", "250", "bar",
                      status="reviewed")])
    assert specs.compare_job_to_manufacturer(r, "job limit", "rating")["status"] == "not_comparable"


def test_invalid_dimension_and_unreviewed_claim_rejected():
    with pytest.raises(specs.SpecificationError):
        value("length", "length", "manufacturer", "-3", "m").validate()
    with pytest.raises(specs.SpecificationError):
        specs.SpecificationValue(
            name="rating", kind="pressure_rating", value=300, unit="psi",
            origin="manufacturer", source_id="SYNTHETIC", source_location="p1",
            status="reviewed", entered_by="tester").validate()


def test_identical_origin_and_name_conflict_rejected():
    with pytest.raises(specs.SpecificationError, match="duplicate"):
        record([value(), value(value="350")]).validate()


def test_record_roundtrip():
    item = record([value()])
    assert specs.EquipmentRecord.from_dict(item.to_dict()) == item


def synthetic_tally(length="4", length_unit="m"):
    return tally_mod.manual_tally(
        "as_run", [
            dict(component_id="H", sequence=1, role="synthetic hanger",
                 length=length, length_unit=length_unit, source_ref="TEST")],
        dict(component_id="H", end="top", measured_depth=1000,
             depth_unit="m", datum="RKB", source_ref="TEST"))


def reference(offset="1.25", status="reviewed", unit="m"):
    return specs.InternalReference(
        component_id="H", label="hanger_slips", offset=offset, unit=unit,
        source_id="SYNTHETIC", source_location="fictional drawing:2",
        status=status,
        reviewed_by="checker" if status == "reviewed" else None,
        reviewed_at="2026-01-01T10:00:00Z" if status == "reviewed" else None)


def test_reviewed_internal_reference_position():
    assert specs.internal_reference_md(synthetic_tally(), reference()) == specs.Decimal("1001.25")
    assert specs.internal_reference_md(synthetic_tally("4", "m"),
                                       reference("1000", unit="mm")) == specs.Decimal("1001.000")


def test_unknown_offsets_and_lengths_do_not_generate_md():
    assert specs.internal_reference_md(synthetic_tally(), reference(status="unreviewed")) is None
    assert specs.internal_reference_md(synthetic_tally(None), reference()) is None


def test_internal_offset_outside_component_rejected():
    with pytest.raises(specs.SpecificationError, match="beyond"):
        specs.internal_reference_md(synthetic_tally(), reference("8"))


def test_missing_anchor_prevents_internal_position():
    tally = tally_mod.manual_tally("as_run", [
        dict(component_id="H", sequence=1, role="hanger", length="4",
             length_unit="m", source_ref="TEST")])
    assert specs.internal_reference_md(tally, reference()) is None


def test_mismatched_equipment_component_rejected():
    ref = specs.InternalReference(
        component_id="OTHER", label="ball_seat", offset=1, unit="m",
        source_id="SYNTHETIC", source_location="test", status="reviewed",
        reviewed_by="checker", reviewed_at="2026-01-01T00:00:00Z")
    with pytest.raises(specs.SpecificationError, match="absent"):
        specs.internal_reference_md(synthetic_tally(), ref)
