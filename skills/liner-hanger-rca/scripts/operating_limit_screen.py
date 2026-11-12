"""Retrospective operating-limit screening with explicit provenance gates.

This module contains NO Baker Hughes ratings or actuation setpoints. A result is
a review candidate, not a proof of downhole state, equipment failure or compliance.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation
from typing import Mapping

# Deliberately narrow and exact. No silent conversion or unit inference.
SUPPORTED_UNITS = {
    "pressure": {"psi", "bar", "kPa"},
    "force": {"lbf", "klbf", "kN"},
    "torque": {"ft-lbf", "N.m"},
    "flow": {"gal/min", "L/min"},
    "rotation": {"rpm"},
}
VALID_COMPARATORS = {"maximum", "minimum", "range"}
VALID_BASIS = {"gauge", "absolute", "differential", "not_applicable"}
VALID_DOMAINS = {"rig_standpipe", "cement_unit_discharge", "tool_internal",
                 "hookload", "top_drive", "rig_pump", "cement_pump"}
VALID_STAGES = {"running", "circulation", "ball_drop", "hanger_setting",
                "running_tool_release", "cementing", "packer_setting"}
VALID_ORIGIN = {"manufacturer", "job"}
ACTIVE_OEM = "baker_hughes"


class LimitError(ValueError):
    pass


def _str(value, label):
    if not isinstance(value, str) or not value.strip():
        raise LimitError(f"{label}: non-empty string required")
    return value.strip()


def _num(value, label):
    if value is None or isinstance(value, bool):
        raise LimitError(f"{label}: numeric value required")
    try:
        number = Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise LimitError(f"{label}: invalid number") from None
    if not number.is_finite():
        raise LimitError(f"{label}: non-finite number")
    return number


@dataclass(frozen=True)
class ToolIdentity:
    manufacturer_id: str
    family: str
    model: str
    size: str
    revision: str
    configuration_id: str

    def validate(self):
        for key, value in asdict(self).items():
            _str(value, f"tool.{key}")
        return self


@dataclass(frozen=True)
class ApprovedLimit:
    """A supplied rule with document, revision and actual approval provenance."""
    rule_id: str
    tool: ToolIdentity
    stage: str
    parameter: str           # e.g. setting_pressure; must match measurement
    quantity: str            # pressure/force/torque/flow/rotation
    unit: str
    pressure_basis: str
    measurement_domain: str
    comparator: str          # maximum, minimum, range
    lower: str | int | float | None
    upper: str | int | float | None
    origin: str
    source_id: str
    source_revision: str
    source_location: str
    approval_reference: str
    reviewed_by: str
    reviewed_at: str
    authorized_for_case: bool = False

    def validate(self):
        _str(self.rule_id, "rule_id")
        self.tool.validate()
        _str(self.parameter, "parameter")
        for name in ("source_id", "source_revision", "source_location",
                     "approval_reference", "reviewed_by", "reviewed_at"):
            _str(getattr(self, name), name)
        if self.stage not in VALID_STAGES or self.origin not in VALID_ORIGIN:
            raise LimitError("invalid stage or limit origin")
        if self.quantity not in SUPPORTED_UNITS or self.unit not in SUPPORTED_UNITS[self.quantity]:
            raise LimitError("unsupported quantity/unit pairing")
        if self.measurement_domain not in VALID_DOMAINS:
            raise LimitError("unknown measurement domain")
        if self.quantity == "pressure":
            if self.pressure_basis not in VALID_BASIS - {"not_applicable"}:
                raise LimitError("pressure basis must be gauge/absolute/differential")
        elif self.pressure_basis != "not_applicable":
            raise LimitError("non-pressure quantity must use not_applicable basis")
        if self.comparator not in VALID_COMPARATORS:
            raise LimitError("invalid comparator")
        if self.comparator == "maximum" and (self.upper is None or self.lower is not None):
            raise LimitError("maximum requires only upper")
        if self.comparator == "minimum" and (self.lower is None or self.upper is not None):
            raise LimitError("minimum requires only lower")
        if self.comparator == "range" and (self.lower is None or self.upper is None):
            raise LimitError("range needs both bounds")
        if self.lower is not None:
            lo = _num(self.lower, "lower")
        if self.upper is not None:
            hi = _num(self.upper, "upper")
        if self.comparator == "range" and lo > hi:
            raise LimitError("range lower exceeds upper")
        return self


@dataclass(frozen=True)
class Observation:
    """A sourced, retrospective surface signal or document-derived measurement."""
    tool: ToolIdentity
    stage: str
    parameter: str
    quantity: str
    value: str | int | float
    unit: str
    pressure_basis: str
    measurement_domain: str
    source_id: str
    channel_id: str
    timestamp: str
    units_verified: bool = False
    channel_mapping_verified: bool = False
    clock_alignment_verified: bool = False
    # This is an explicit equivalence assertion approved by the case reviewer.
    # Do not equate rig SPP and tool-internal pressure solely because both are psi.
    measurement_equivalence_verified: bool = False

    def validate(self):
        self.tool.validate()
        _str(self.parameter, "parameter")
        for key in ("source_id", "channel_id", "timestamp"):
            _str(getattr(self, key), key)
        _num(self.value, "observed value")
        if self.stage not in VALID_STAGES:
            raise LimitError("invalid observation stage")
        if self.quantity not in SUPPORTED_UNITS or self.unit not in SUPPORTED_UNITS[self.quantity]:
            raise LimitError("unsupported observed unit")
        if self.quantity == "pressure":
            if self.pressure_basis not in VALID_BASIS - {"not_applicable"}:
                raise LimitError("invalid pressure basis")
        elif self.pressure_basis != "not_applicable":
            raise LimitError("invalid non-pressure basis")
        if self.measurement_domain not in VALID_DOMAINS:
            raise LimitError("unknown observed measurement domain")
        return self


def screen(limit: ApprovedLimit, observed: Observation) -> dict:
    """Return a traceable *screening finding* only when identity/context match.

    No automatic transfer of a job pressure rule to a tool internal rating,
    cement unit, other sensor, unknown model/revision or other manufacturer.
    """
    limit.validate()
    observed.validate()
    base = {
        "rule_id": limit.rule_id,
        "source": {"document": limit.source_id, "revision": limit.source_revision,
                   "location": limit.source_location, "approval": limit.approval_reference},
        "observation": {"source": observed.source_id, "channel": observed.channel_id,
                        "timestamp": observed.timestamp},
        "status": "unverifiable",
        "reasons": [],
        "conclusion": "No equipment-state, root-cause or final compliance verdict",
    }
    reason = base["reasons"]
    if limit.tool.manufacturer_id != ACTIVE_OEM or observed.tool.manufacturer_id != ACTIVE_OEM:
        reason.append("manufacturer unsupported in release 1")
    if limit.tool != observed.tool:
        reason.append("tool identity/model/size/revision/configuration mismatch")
    if not limit.authorized_for_case:
        reason.append("source approval has not been authorized for this case")
    if limit.stage != observed.stage or limit.parameter != observed.parameter:
        reason.append("operation stage or parameter mismatch")
    if limit.quantity != observed.quantity or limit.unit != observed.unit:
        reason.append("quantity or engineering unit mismatch (no silent conversion)")
    if limit.pressure_basis != observed.pressure_basis:
        reason.append("pressure basis mismatch")
    if limit.measurement_domain != observed.measurement_domain:
        reason.append("sensor/measurement domain mismatch")
    if not observed.units_verified:
        reason.append("source units not verified")
    if not observed.channel_mapping_verified:
        reason.append("sensor mapping not verified")
    if not observed.clock_alignment_verified:
        reason.append("event and telemetry time alignment not verified")
    if not observed.measurement_equivalence_verified:
        reason.append("observed measurement not verified as comparable to rule reference")
    if reason:
        return base
    val = _num(observed.value, "observation")
    low = _num(limit.lower, "lower") if limit.lower is not None else None
    high = _num(limit.upper, "upper") if limit.upper is not None else None
    within = (val <= high if limit.comparator == "maximum" else
              val >= low if limit.comparator == "minimum" else low <= val <= high)
    base["status"] = "within_screening_bounds" if within else "outside_screening_bounds"
    base["comparison"] = {
        "observed": str(val), "lower": str(low) if low is not None else None,
        "upper": str(high) if high is not None else None,
        "unit": limit.unit, "operator": limit.comparator,
    }
    return base


def screen_from_dict(limit: Mapping, observation: Mapping) -> dict:
    """Portable JSON input; invalid schema is rejected, not silently defaulted."""
    try:
        l = dict(limit)
        o = dict(observation)
        l["tool"] = ToolIdentity(**l["tool"])
        o["tool"] = ToolIdentity(**o["tool"])
        return screen(ApprovedLimit(**l), Observation(**o))
    except (KeyError, TypeError) as error:
        raise LimitError(f"invalid screening contract: {error}") from error
