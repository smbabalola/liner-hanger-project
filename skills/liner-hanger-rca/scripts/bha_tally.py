"""Source-gated, offline BHA tally contract for retrospective investigation.

No OEM dimensions, setting limits or assumed string stretch are embedded here.
Measured depths are on one explicitly named datum and are NOT TVD.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Mapping, Sequence

FT_TO_M = Decimal("0.3048")
VALID_UNITS = {"m", "ft"}
VALID_BASIS = {"planned", "as_run"}
VALID_ENDS = {"top", "bottom"}


class TallyError(ValueError):
    """An input is ambiguous or invalid; no estimate should be substituted."""


def _number(value, label):
    if value is None or isinstance(value, bool):
        raise TallyError(f"{label}: numeric value required")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise TallyError(f"{label}: invalid number") from None
    if not result.is_finite():
        raise TallyError(f"{label}: non-finite number")
    return result


def _metres(value, unit, label):
    if unit not in VALID_UNITS:
        raise TallyError(f"{label}: unit must be explicitly 'm' or 'ft'")
    return _number(value, label) * (FT_TO_M if unit == "ft" else Decimal(1))


@dataclass(frozen=True)
class Component:
    component_id: str
    sequence: int                  # Top-to-bottom, consecutive from 1
    role: str                      # Physical component description/role, not approved OEM rule
    length: str | int | float | None
    length_unit: str | None
    source_ref: str
    manufacturer_id: str | None = None
    tool_family: str | None = None
    model: str | None = None
    revision: str | None = None
    reference_point: str | None = None  # e.g. "hanger_slips"; internal offset not inferred

    @property
    def length_m(self):
        if self.length is None:
            return None
        result = _metres(self.length, self.length_unit, f"{self.component_id}.length")
        if result <= 0:
            raise TallyError(f"{self.component_id}.length: must be positive")
        return result


@dataclass(frozen=True)
class Anchor:
    component_id: str
    end: str                        # 'top' or 'bottom' of known component
    measured_depth: str | int | float
    depth_unit: str
    datum: str                      # e.g. rig-floor/RKB, explicit
    source_ref: str

    @property
    def md_m(self):
        result = _metres(self.measured_depth, self.depth_unit, "anchor.measured_depth")
        if result < 0:
            raise TallyError("anchor.measured_depth: must be non-negative")
        return result


@dataclass(frozen=True)
class Tally:
    basis: str                      # planned or as_run; NEVER silently mixed
    components: tuple[Component, ...]
    anchor: Anchor | None = None
    version: str = "1.0"

    def validate(self):
        if self.basis not in VALID_BASIS:
            raise TallyError("basis must be planned or as_run")
        if not self.components:
            raise TallyError("tally must contain at least one component")
        ids = set()
        for index, component in enumerate(self.components, start=1):
            if not component.component_id.strip() or component.component_id in ids:
                raise TallyError("empty or duplicate component_id")
            ids.add(component.component_id)
            if component.sequence != index:
                raise TallyError("components must be in unique top-to-bottom sequence 1..N")
            if not component.role.strip():
                raise TallyError(f"{component.component_id}: role is required")
            if not component.source_ref.strip():
                raise TallyError(f"{component.component_id}: measurement/source provenance required")
            _ = component.length_m  # Reject invalid lengths, never replace unknowns
        if self.anchor is not None:
            if self.anchor.component_id not in ids or self.anchor.end not in VALID_ENDS:
                raise TallyError("anchor must identify a component and its top/bottom boundary")
            if not self.anchor.datum.strip() or not self.anchor.source_ref.strip():
                raise TallyError("anchor datum and source are required")
            _ = self.anchor.md_m
        return self

    def position_m(self, component_id: str, end: str):
        """Return a measured depth in metres or None when the path has missing data."""
        self.validate()
        if end not in VALID_ENDS:
            raise TallyError("end must be top or bottom")
        if self.anchor is None:
            return None
        ids = [c.component_id for c in self.components]
        if component_id not in ids:
            raise TallyError(f"unknown component_id: {component_id}")
        a = ids.index(self.anchor.component_id)
        b = ids.index(component_id)
        # Boundaries: top of component i -> index i; bottom -> index i+1.
        ai = a + (1 if self.anchor.end == "bottom" else 0)
        bi = b + (1 if end == "bottom" else 0)
        if ai == bi:
            return self.anchor.md_m
        lo, hi = sorted((ai, bi))
        steps = [c.length_m for c in self.components[lo:hi]]
        if any(v is None for v in steps):
            return None
        offset = sum(steps, Decimal(0))
        return self.anchor.md_m + (offset if bi > ai else -offset)

    def to_dict(self):
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Mapping):
        try:
            components = tuple(Component(**c) for c in payload["components"])
            anchor = Anchor(**payload["anchor"]) if payload.get("anchor") else None
            result = cls(basis=payload["basis"], components=components,
                         anchor=anchor, version=payload.get("version", "1.0"))
            return result.validate()
        except (KeyError, TypeError) as error:
            raise TallyError(f"invalid tally contract: {error}") from error


def manual_tally(basis: str, rows: Sequence[Mapping], anchor: Mapping | None = None):
    """Build a validated tally from engineer-entered rows."""
    return Tally.from_dict({"basis": basis, "components": list(rows), "anchor": anchor})


def excel_tally(path, *, basis: str, mapping: Mapping[str, str],
                sheet_name: str, anchor: Mapping | None = None):
    """Read a .xlsx tally with explicit column mapping; never modifies a live tally.

    Required mapped fields: component_id, sequence, role, length, length_unit,
    source_ref. Workbook formulas in mapped columns are rejected, as are ambiguous
    blank rows and unknown units. Import returns a *candidate* to be reviewed.
    """
    from pathlib import Path
    path = Path(path)
    if path.suffix.lower() != ".xlsx":
        raise TallyError("only .xlsx is accepted; convert legacy .xls separately")
    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise TallyError("Excel import requires openpyxl (pip install openpyxl)") from error
    required = {"component_id", "sequence", "role", "length", "length_unit", "source_ref"}
    optional = {"manufacturer_id", "tool_family", "model", "revision", "reference_point"}
    if not required.issubset(mapping) or set(mapping) - required - optional:
        raise TallyError("explicit column mapping is missing required fields or has unknown keys")
    if len(set(mapping.values())) != len(mapping):
        raise TallyError("two fields cannot map to the same Excel column")
    book = load_workbook(path, read_only=True, data_only=False, keep_links=False)
    try:
        if sheet_name not in book.sheetnames:
            raise TallyError("sheet name not found")
        sheet = book[sheet_name]
        values = sheet.iter_rows(values_only=True)
        header = next(values, None)
        if not header:
            raise TallyError("empty Excel sheet")
        headers = [str(h).strip() if h is not None else "" for h in header]
        if len(headers) != len(set(h for h in headers if h)):
            raise TallyError("duplicate header names")
        for col in mapping.values():
            if col not in headers:
                raise TallyError(f"missing Excel column: {col}")
        cols = {field: headers.index(name) for field, name in mapping.items()}
        rows = []
        for excel_row, cells in enumerate(values, start=2):
            row = {field: (cells[index] if index < len(cells) else None)
                   for field, index in cols.items()}
            if all(v is None or v == "" for v in row.values()):
                continue
            if any(isinstance(v, str) and v.startswith("=") for v in row.values()):
                raise TallyError(f"{sheet_name}!row {excel_row}: formulas are not accepted")
            if row.get("length") == "":
                row["length"] = None
            if row.get("sequence") is None:
                raise TallyError(f"{sheet_name}!row {excel_row}: missing sequence")
            try:
                row["sequence"] = int(row["sequence"])
            except (TypeError, ValueError):
                raise TallyError(f"{sheet_name}!row {excel_row}: invalid sequence") from None
            if row.get("source_ref") in (None, ""):
                row["source_ref"] = f"{path.name}!{sheet_name}:{excel_row} (unverified)"
            rows.append(row)
        return manual_tally(basis, rows, anchor)
    finally:
        book.close()


def tally_diff(existing: Tally, candidate: Tally):
    """Review output only. Caller must explicitly accept candidate; no mutation."""
    existing.validate()
    candidate.validate()
    before = {c.component_id: c for c in existing.components}
    after = {c.component_id: c for c in candidate.components}
    return {
        "basis_changed": existing.basis != candidate.basis,
        "anchor_changed": existing.anchor != candidate.anchor,
        "added": sorted(after.keys() - before.keys()),
        "removed": sorted(before.keys() - after.keys()),
        "changed": sorted(k for k in before.keys() & after.keys() if before[k] != after[k])
    }
