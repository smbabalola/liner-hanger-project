"""BH tally contract regression: deterministic depths, unknowns and Excel parity.

All dimensions are fictional test values, not Baker Hughes dimensions.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bha_tally", ROOT / "scripts" / "bha_tally.py")
bha = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = bha
SPEC.loader.exec_module(bha)


def component(identifier, seq, length, unit="m"):
    return dict(component_id=identifier, sequence=seq, role=identifier, length=length,
                length_unit=unit, source_ref="SYNTHETIC-TEST")


def anchor(component_id="A", end="top", md="1000", unit="m"):
    return dict(component_id=component_id, end=end, measured_depth=md,
                depth_unit=unit, datum="RKB/SYNTHETIC", source_ref="SYNTHETIC-TEST")


def test_manual_depths_are_md_and_anchor_relative():
    tally = bha.manual_tally("as_run",
        [component("A", 1, "2"), component("B", 2, "10"), component("C", 3, "3")],
        anchor())
    assert tally.position_m("A", "top") == bha.Decimal("1000")
    assert tally.position_m("B", "bottom") == bha.Decimal("1012")
    assert tally.position_m("C", "bottom") == bha.Decimal("1015")
    assert tally.position_m("A", "bottom") == bha.Decimal("1002")


def test_reverse_direction_and_unit_conversion():
    tally = bha.manual_tally("planned",
        [component("A", 1, "10", "ft"), component("B", 2, "10", "ft")],
        anchor("B", "bottom", "100", "ft"))
    assert tally.position_m("A", "top") == bha.Decimal("24.3840")
    assert tally.position_m("B", "bottom") == bha.Decimal("30.4800")


def test_unknown_length_blocks_only_crossing_path():
    tally = bha.manual_tally("as_run",
        [component("A", 1, "2"), component("B", 2, None), component("C", 3, "3")],
        anchor("B", "bottom"))
    assert tally.position_m("C", "bottom") == bha.Decimal("1003")
    assert tally.position_m("A", "top") is None


def test_missing_anchor_returns_unavailable():
    tally = bha.manual_tally("as_run", [component("A", 1, "2")])
    assert tally.position_m("A", "bottom") is None


@pytest.mark.parametrize("rows", [
    [component("A", 1, "2"), component("A", 2, "3")],
    [component("A", 2, "2")],
    [component("A", 1, "-2")],
    [component("A", 1, "3", "unspecified")],
])
def test_invalid_manual_tallies_rejected(rows):
    with pytest.raises(bha.TallyError):
        bha.manual_tally("as_run", rows, anchor())


def test_plan_and_as_run_are_separate_and_import_is_review_only():
    planned = bha.manual_tally("planned", [component("A", 1, "2")], anchor())
    as_run = bha.manual_tally("as_run", [component("A", 1, "3")], anchor())
    diff = bha.tally_diff(planned, as_run)
    assert diff["basis_changed"] is True
    assert diff["changed"] == ["A"]
    assert planned.position_m("A", "bottom") == bha.Decimal("1002")


def test_serialization_round_trip():
    tally = bha.manual_tally("as_run", [component("A", 1, "2")], anchor())
    assert bha.Tally.from_dict(tally.to_dict()) == tally


def test_excel_import_matches_manual_depths(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    book = openpyxl.Workbook()
    page = book.active
    page.title = "Actual Tally"
    page.append(["Item", "Order", "Type", "Measured Length", "Units", "Evidence"])
    page.append(["A", 1, "A", 2, "m", "TEST"])
    page.append(["B", 2, "B", 10, "m", "TEST"])
    file = tmp_path / "synthetic_tally.xlsx"
    book.save(file)
    mapping = dict(component_id="Item", sequence="Order", role="Type",
                   length="Measured Length", length_unit="Units", source_ref="Evidence")
    imported = bha.excel_tally(file, basis="as_run", mapping=mapping,
                               sheet_name="Actual Tally", anchor=anchor())
    manual = bha.manual_tally("as_run",
        [component("A", 1, "2"), component("B", 2, "10")], anchor())
    assert imported.position_m("B", "bottom") == manual.position_m("B", "bottom")


def test_excel_formula_rejected(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    book = openpyxl.Workbook()
    page = book.active
    page.title = "Tally"
    page.append(["Item", "Order", "Type", "Length", "Units", "Evidence"])
    page.append(["A", 1, "A", "=1+1", "m", "TEST"])
    file = tmp_path / "formula.xlsx"
    book.save(file)
    mapping = dict(component_id="Item", sequence="Order", role="Type",
                   length="Length", length_unit="Units", source_ref="Evidence")
    with pytest.raises(bha.TallyError, match="formulas"):
        bha.excel_tally(file, basis="as_run", mapping=mapping,
                        sheet_name="Tally", anchor=anchor())
