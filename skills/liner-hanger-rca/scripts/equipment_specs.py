"""Editable, source-tracked equipment specifications for OFFLINE investigation.

Data entered by engineers are not automatically manufacturer-approved. This
module does not invent BH dimensions, technical limits or operating instructions.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation
from typing import Mapping

LENGTH_FACTORS = {"m": Decimal("1"), "ft": Decimal("0.3048"),
                  "mm": Decimal("0.001"), "in": Decimal("0.0254")}
STATUS = {"unreviewed", "reviewed"}
ORIGINS = {"manufacturer", "job"}
KINDS = {"length", "outside_diameter", "inside_diameter", "weight",
         "pressure_rating", "setting_pressure", "release_pressure",
         "differential_pressure_limit", "tensile_limit", "compression_limit",
         "torque_limit", "shear_limit", "flow_rate_limit", "temperature_limit",
         "ball_diameter", "connection", "other"}


class SpecificationError(ValueError):
    pass


def _decimal(value, label):
    if isinstance(value, bool) or value is None:
        raise SpecificationError(f"{label}: numeric value required")
    try:
        number = Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise SpecificationError(f"{label}: invalid numeric value") from None
    if not number.is_finite():
        raise SpecificationError(f"{label}: non-finite numeric value")
    return number


def _required(value, label):
    if not isinstance(value, str) or not value.strip():
        raise SpecificationError(f"{label} is required")
    return value.strip()


@dataclass(frozen=True)
class EquipmentIdentity:
    manufacturer_id: str
    tool_family: str
    model: str | None = None
    size: str | None = None
    revision: str | None = None
    part_number: str | None = None

    def validate(self):
        _required(self.manufacturer_id, "manufacturer_id")
        _required(self.tool_family, "tool_family")
        return self


@dataclass(frozen=True)
class SpecificationValue:
    """A single sourced value, never silently mixed with an alternate source."""
    name: str
    kind: str
    value: str | int | float
    unit: str
    origin: str                # manufacturer OR job, not both
    source_id: str             # document ID or job record
    source_location: str       # page, drawing position or job-log reference
    status: str = "unreviewed"
    entered_by: str = "unknown"
    entered_at: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    notes: str | None = None

    def validate(self):
        _required(self.name, "name")
        if self.kind not in KINDS:
            raise SpecificationError("unsupported specification kind")
        _ = _decimal(self.value, self.name)  # numerical entries only in this MVP
        _required(self.unit, "unit")
        if self.origin not in ORIGINS or self.status not in STATUS:
            raise SpecificationError("invalid origin or review status")
        _required(self.source_id, "source_id")
        _required(self.source_location, "source_location")
        _required(self.entered_by, "entered_by")
        if self.status == "reviewed" and (not self.reviewed_by or not self.reviewed_at):
            raise SpecificationError("reviewed value requires reviewer and review timestamp")
        if self.kind in {"length", "outside_diameter", "inside_diameter", "ball_diameter"}:
            if self.unit not in LENGTH_FACTORS or _decimal(self.value, self.name) <= 0:
                raise SpecificationError("dimension requires positive value and supported length unit")
        return self


@dataclass(frozen=True)
class EquipmentRecord:
    identity: EquipmentIdentity
    values: tuple[SpecificationValue, ...]
    record_id: str

    def validate(self):
        _required(self.record_id, "record_id")
        self.identity.validate()
        seen = set()
        for value in self.values:
            value.validate()
            key = (value.origin, value.name)
            if key in seen:
                raise SpecificationError("duplicate value name within one origin; reconcile revisions explicitly")
            seen.add(key)
        return self

    @classmethod
    def from_dict(cls, raw: Mapping):
        try:
            result = cls(identity=EquipmentIdentity(**raw["identity"]),
                         values=tuple(SpecificationValue(**v) for v in raw["values"]),
                         record_id=raw["record_id"])
            return result.validate()
        except (KeyError, TypeError) as error:
            raise SpecificationError(f"invalid equipment record: {error}") from error

    def to_dict(self):
        return asdict(self)

    def values_by_origin(self, origin):
        return tuple(v for v in self.values if v.origin == origin)


def candidate_edit(record: EquipmentRecord, value: SpecificationValue):
    """Non-mutating edit candidate; does not confer approval or overwrite an OEM value."""
    record.validate()
    value.validate()
    kept = [v for v in record.values
            if not (v.origin == value.origin and v.name == value.name)]
    return EquipmentRecord(record.identity, tuple(kept + [value]), record.record_id).validate()


def compare_job_to_manufacturer(record: EquipmentRecord, job_name: str,
                                manufacturer_name: str):
    """Screen an engineer-reviewed pair with exact same kind/unit.

    Returns NOT_COMPARABLE rather than converting unrelated pressure definitions.
    This is a recorded-value comparison, not an OEM-compliance verdict.
    """
    record.validate()
    jobs = [v for v in record.values if v.origin == "job" and v.name == job_name]
    specs = [v for v in record.values if v.origin == "manufacturer"
             and v.name == manufacturer_name]
    if not jobs or not specs:
        return {"status": "unavailable", "reason": "missing job or manufacturer value"}
    job, spec = jobs[0], specs[0]
    if job.status != "reviewed" or spec.status != "reviewed":
        return {"status": "unavailable", "reason": "values require independent review"}
    if job.kind != spec.kind or job.unit != spec.unit:
        return {"status": "not_comparable", "reason": "different parameter kind or units"}
    return {"status": "numeric_comparison_only",
            "job_value": str(_decimal(job.value, job.name)),
            "manufacturer_value": str(_decimal(spec.value, spec.name)),
            "difference": str(_decimal(job.value, job.name) - _decimal(spec.value, spec.name)),
            "unit": job.unit,
            "warning": "Not a limit/approval verdict; verify rating basis, direction and applicability."}


@dataclass(frozen=True)
class InternalReference:
    """A measured component reference offset from its TOP boundary, not an OEM default."""
    component_id: str
    label: str               # e.g. hanger_slips, packer_element, ball_seat
    offset: str | int | float
    unit: str
    source_id: str
    source_location: str
    status: str = "unreviewed"
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    def validate(self):
        _required(self.component_id, "component_id")
        _required(self.label, "label")
        _required(self.source_id, "source_id")
        _required(self.source_location, "source_location")
        if self.unit not in LENGTH_FACTORS:
            raise SpecificationError("reference offset unit must be m, ft, mm or in")
        if _decimal(self.offset, "offset") < 0:
            raise SpecificationError("reference offset cannot be negative")
        if self.status not in STATUS:
            raise SpecificationError("invalid reference review status")
        if self.status == "reviewed" and (not self.reviewed_by or not self.reviewed_at):
            raise SpecificationError("reviewed reference requires reviewer and timestamp")
        return self


def internal_reference_md(tally, ref: InternalReference):
    """Nominal MD of sourced internal reference, or None if unavailable/unreviewed.

    Underlying tally must anchor to the same explicit MD datum; this function
    does not claim as-run absolute downhole position or TVD.
    """
    ref.validate()
    tally.validate()
    if ref.status != "reviewed":
        return None
    component = next((c for c in tally.components
                      if c.component_id == ref.component_id), None)
    if component is None:
        raise SpecificationError("reference component absent from selected tally")
    if component.length_m is None:
        return None
    offset_m = _decimal(ref.offset, "offset") * LENGTH_FACTORS[ref.unit]
    if offset_m > component.length_m:
        raise SpecificationError("internal reference extends beyond component length")
    top_md = tally.position_m(ref.component_id, "top")
    return None if top_md is None else top_md + offset_m
