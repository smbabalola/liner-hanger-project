"""Independent design benchmark and planned/observed comparison contract.

This is a source-and-domain gate, NOT a physics solver or approved operating
limit assessor. Missing variables produce unavailable, never invented results.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation

BASES = {"planned_input", "independently_calculated",
         "original_design_result", "observed_surface"}
STATES = {"unreviewed", "reviewed"}
LENGTH = {"m": Decimal("1"), "ft": Decimal("0.3048")}
PRESSURE = {"Pa": Decimal("1"), "kPa": Decimal("1000"),
            "bar": Decimal("100000"), "psi": Decimal("6894.757293168")}
LOAD = {"N": Decimal("1"), "kN": Decimal("1000"),
        "lbf": Decimal("4.4482216152605"),
        "klbf": Decimal("4448.2216152605")}
FLOW = {"m3/s": Decimal("1"), "L/min": Decimal("0.001")/Decimal("60")}
SPEED = {"m/s": Decimal("1"), "m/min": Decimal("1")/Decimal("60"),
         "ft/min": Decimal("0.3048")/Decimal("60")}
FAMILIES = {"length": LENGTH, "pressure": PRESSURE, "load": LOAD,
            "flow": FLOW, "speed": SPEED}
PRESSURE_BASIS = {"gauge", "absolute", "differential", "not_applicable"}

class BaselineError(ValueError):
    pass

def _required(value, field):
    if not isinstance(value, str) or not value.strip():
        raise BaselineError(f"{field}: non-empty string required")
    return value.strip()

def _dec(value, field):
    if isinstance(value, bool) or value is None:
        raise BaselineError(f"{field}: finite number required")
    try:
        number = Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise BaselineError(f"{field}: invalid number") from None
    if not number.is_finite():
        raise BaselineError(f"{field}: non-finite number")
    return number

@dataclass(frozen=True)
class EngineeringQuantity:
    case_id: str
    stage: str
    parameter: str
    component_id: str
    domain: str
    location: str
    quantity_family: str
    value: str | int | float
    unit: str
    basis: str
    source_id: str
    source_location: str
    source_revision: str
    review_status: str = "unreviewed"
    pressure_basis: str = "not_applicable"
    measured_depth_m: str | int | float | None = None
    model_version: str | None = None
    time_basis: str | None = None
    note: str | None = None

    def validate(self):
        for name in ("case_id", "stage", "parameter", "component_id",
                     "domain", "location", "source_id", "source_location",
                     "source_revision"):
            _required(getattr(self, name), name)
        if self.basis not in BASES or self.review_status not in STATES:
            raise BaselineError("invalid basis or review status")
        if self.quantity_family not in FAMILIES or self.unit not in FAMILIES[self.quantity_family]:
            raise BaselineError("unsupported or inconsistent quantity family / unit")
        if self.pressure_basis not in PRESSURE_BASIS:
            raise BaselineError("invalid pressure basis")
        if (self.quantity_family == "pressure") != (self.pressure_basis != "not_applicable"):
            raise BaselineError("pressure basis must be supplied for pressures only")
        _dec(self.value, "value")
        if self.measured_depth_m is not None and _dec(self.measured_depth_m, "measured_depth_m") < 0:
            raise BaselineError("negative MD not allowed")
        if self.basis == "independently_calculated":
            _required(self.model_version, "model_version")
        if self.basis == "observed_surface":
            _required(self.time_basis, "time_basis")
        return self

    def to_dict(self):
        return asdict(self)

def compare_quantities(left: EngineeringQuantity, right: EngineeringQuantity,
                       *, expected_bases: tuple[str, str], require_review: bool = True):
    """Compare like-with-like values; does not certify a model or approve limits.

    MD-specific values require matching measured depth; no interpolation is
    silently performed. 'gauge' and 'absolute' pressure are not interchangeable.
    """
    left.validate()
    right.validate()
    if (left.basis, right.basis) != expected_bases:
        return {"status": "not_comparable", "reason": "incorrect evidence bases"}
    if left.case_id != right.case_id:
        return {"status": "not_comparable", "reason": "different cases"}
    attributes = ("stage", "parameter", "component_id", "domain",
                  "location", "quantity_family", "pressure_basis")
    for attr in attributes:
        if getattr(left, attr) != getattr(right, attr):
            return {"status": "not_comparable", "reason": "mismatched " + attr}
    if (left.measured_depth_m is None) != (right.measured_depth_m is None):
        return {"status": "not_comparable", "reason": "depth basis missing on one side"}
    if left.measured_depth_m is not None:
        if _dec(left.measured_depth_m, "MD") != _dec(right.measured_depth_m, "MD"):
            return {"status": "not_comparable", "reason": "different MD; no silent interpolation"}
    if require_review and (left.review_status != "reviewed" or right.review_status != "reviewed"):
        return {"status": "incomplete", "reason": "independent source or model review pending"}
    values = FAMILIES[left.quantity_family]
    normalized_left = _dec(left.value, "value") * values[left.unit]
    normalized_right = _dec(right.value, "value") * values[right.unit]
    return {
        "status": "numeric_difference_only",
        "left": str(left.value), "left_unit": left.unit,
        "right": str(right.value), "right_unit": right.unit,
        "difference_in_si": str(normalized_left - normalized_right),
        "si_unit": {"length": "m", "pressure": "Pa", "load": "N",
                    "flow": "m3/s", "speed": "m/s"}[left.quantity_family],
        "left_source": f"{left.source_id}:{left.source_location}",
        "right_source": f"{right.source_id}:{right.source_location}",
        "warning": "No compliance, fault, equivalence or OEM-model validity verdict.",
    }

def compare_design_prediction(model_result, original_design_result):
    return compare_quantities(
        model_result, original_design_result,
        expected_bases=("independently_calculated", "original_design_result"))

def compare_observed_to_prediction(observed, model_result):
    return compare_quantities(
        observed, model_result,
        expected_bases=("observed_surface", "independently_calculated"))
