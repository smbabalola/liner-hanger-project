"""LH-CALC-01: explicitly unit-typed, SI-valued elementary engineering equations.

General cylindrical geometry and constant-density statics ONLY. These are
not a torque/drag, hydraulics, surge/swab or approved equipment limit model.
No unknown value, geometry or physical assumption is filled by default.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

PI = Decimal("3.1415926535897932384626433832795028841971693993751")
G_STANDARD = Decimal("9.80665")  # standard gravitational acceleration in m/s²
LENGTH_M = {"m": Decimal("1"), "mm": Decimal("0.001"),
            "in": Decimal("0.0254"), "ft": Decimal("0.3048")}
DENSITY_KG_M3 = {"kg/m3": Decimal("1"), "g/cm3": Decimal("1000"),
                 "ppg": Decimal("119.826427316")}
LINEAR_MASS_KG_M = {"kg/m": Decimal("1"), "lbm/ft": Decimal("0.45359237") / Decimal("0.3048")}


class PrimitiveError(ValueError):
    """Missing, nonphysical or ambiguous engineering inputs."""


def _number(value, name):
    if value is None or isinstance(value, bool):
        raise PrimitiveError(f"{name}: finite numerical value required")
    try:
        val = Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise PrimitiveError(f"{name}: invalid number") from None
    if not val.is_finite():
        raise PrimitiveError(f"{name}: non-finite number")
    return val


def _convert(value, unit, family, name, *, positive=True):
    if unit not in family:
        raise PrimitiveError(f"{name}: explicit supported unit required")
    val = _number(value, name) * family[unit]
    if positive and val <= 0:
        raise PrimitiveError(f"{name}: must be positive")
    return val


def _cross_section(outer_m, inner_m):
    if inner_m < 0 or outer_m <= inner_m:
        raise PrimitiveError("diameters: outer must exceed nonnegative inner")
    return PI * (outer_m * outer_m - inner_m * inner_m) / Decimal("4")


def tubular_capacity(*, inside_diameter, diameter_unit, length, length_unit):
    """Return internal cylindrical capacity, m³; excludes joints/restrictions."""
    diameter = _convert(inside_diameter, diameter_unit, LENGTH_M, "inside_diameter")
    length_m = _convert(length, length_unit, LENGTH_M, "length")
    return PI * diameter * diameter * length_m / Decimal("4")


def annular_capacity(*, bore_diameter, pipe_outer_diameter, diameter_unit,
                     length, length_unit):
    """Return concentric open-annulus capacity, m³; ignores eccentricity/couplings."""
    bore = _convert(bore_diameter, diameter_unit, LENGTH_M, "bore_diameter")
    pipe = _convert(pipe_outer_diameter, diameter_unit, LENGTH_M, "pipe_outer_diameter")
    length_m = _convert(length, length_unit, LENGTH_M, "length")
    return _cross_section(bore, pipe) * length_m


def hydrostatic_pressure_difference(*, fluid_density, density_unit, delta_tvd,
                                    depth_unit):
    """Return hydrostatic pressure DIFFERENCE (Pa), positive downwards.

    delta_tvd is positive when the second point is deeper (true vertical depth);
    negative for an upward interval. Assumes one constant-density static fluid.
    This is not absolute pressure, SPP, ECD or pressure across a ball seat.
    """
    rho = _convert(fluid_density, density_unit, DENSITY_KG_M3, "fluid_density")
    depth_m = _convert(delta_tvd, depth_unit, LENGTH_M, "delta_tvd", positive=False)
    return rho * G_STANDARD * depth_m


def flooded_pipe_apparent_weight(*, outer_diameter, inner_diameter, diameter_unit,
                                 dry_linear_mass, linear_mass_unit,
                                 fluid_density, density_unit, length, length_unit):
    """Return apparent weight in N (positive downward) of a flooded pipe segment.

    Assumptions: uniform wall, fully immersed, OPEN and fully fluid-filled pipe;
    identical density fluid inside and outside; no trapped gas, enclosed end
    forces, axial pressure-end loads or tool internals. Fluid buoyancy acts on
    METAL wall volume, not entire outer cylinder. Not surface hookload.
    """
    outer = _convert(outer_diameter, diameter_unit, LENGTH_M, "outer_diameter")
    inner = _convert(inner_diameter, diameter_unit, LENGTH_M, "inner_diameter",
                     positive=False)
    metal_area = _cross_section(outer, inner)
    mass_per_m = _convert(dry_linear_mass, linear_mass_unit, LINEAR_MASS_KG_M,
                          "dry_linear_mass")
    rho = _convert(fluid_density, density_unit, DENSITY_KG_M3, "fluid_density")
    length_m = _convert(length, length_unit, LENGTH_M, "length")
    return (mass_per_m - rho * metal_area) * G_STANDARD * length_m
