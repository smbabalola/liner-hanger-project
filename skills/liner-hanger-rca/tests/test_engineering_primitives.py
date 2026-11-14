"""LH-CALC-01: independent statics/geometry known-answer and fail-closed tests."""
import importlib.util
import sys
from decimal import Decimal
from pathlib import Path
import pytest

path = Path(__file__).resolve().parents[1] / "scripts" / "engineering_primitives.py"
spec = importlib.util.spec_from_file_location("engineering_primitives", path)
p = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = p
spec.loader.exec_module(p)


def approx(actual, expected, tolerance="1e-8"):
    assert abs(actual - Decimal(str(expected))) <= Decimal(tolerance)


def test_one_metre_diameter_one_metre_length_cylinder():
    approx(p.tubular_capacity(inside_diameter=1, diameter_unit="m", length=1, length_unit="m"),
           "0.7853981633974483096")


def test_annulus_0_2_bore_0_1_pipe_ten_metres():
    approx(p.annular_capacity(bore_diameter="0.2", pipe_outer_diameter="0.1",
                             diameter_unit="m", length=10, length_unit="m"),
           "0.2356194490192345")


def test_units_inches_and_feet_match_si():
    metric = p.tubular_capacity(inside_diameter="0.1016", diameter_unit="m", length="3.048", length_unit="m")
    oilfield = p.tubular_capacity(inside_diameter=4, diameter_unit="in", length=10, length_unit="ft")
    assert metric == oilfield


def test_hydrostatic_water_100m_constant_density():
    assert p.hydrostatic_pressure_difference(fluid_density=1000, density_unit="kg/m3",
                 delta_tvd=100, depth_unit="m") == Decimal("980665")


def test_hydrostatic_direction_and_md_vs_tvd():
    kwargs = dict(fluid_density=1000, density_unit="kg/m3", depth_unit="m")
    assert p.hydrostatic_pressure_difference(delta_tvd=-100, **kwargs) == Decimal("-980665")
    assert p.hydrostatic_pressure_difference(delta_tvd=0, **kwargs) == 0


def test_flooded_metal_volume_and_weight_against_hand_balance():
    # Metal volume = π(0.2²-0.1²)/4 × 2 = 0.0471238898038469 m³.
    # Apparent weight = (200kg - water mass displaced) × 9.80665 m/s².
    val = p.flooded_pipe_apparent_weight(outer_diameter="0.2", inner_diameter="0.1",
             diameter_unit="m", dry_linear_mass=100, linear_mass_unit="kg/m",
             fluid_density=1000, density_unit="kg/m3", length=2, length_unit="m")
    expected = (Decimal(200) - Decimal(1000) * Decimal("0.0471238898038469")) * Decimal("9.80665")
    approx(val, expected, "1e-9")


def test_hydrostatic_g_per_cc_equals_kg_per_m3():
    kwargs = dict(delta_tvd=100, depth_unit="m")
    assert p.hydrostatic_pressure_difference(fluid_density=1, density_unit="g/cm3", **kwargs) == p.hydrostatic_pressure_difference(fluid_density=1000, density_unit="kg/m3", **kwargs)


@pytest.mark.parametrize("call,kwargs", [
    (p.tubular_capacity, dict(inside_diameter=None, diameter_unit="m", length=1, length_unit="m")),
    (p.tubular_capacity, dict(inside_diameter=1, diameter_unit="unknown", length=1, length_unit="m")),
    (p.tubular_capacity, dict(inside_diameter=1, diameter_unit="m", length=0, length_unit="m")),
    (p.tubular_capacity, dict(inside_diameter="NaN", diameter_unit="m", length=1, length_unit="m")),
    (p.annular_capacity, dict(bore_diameter=0.1, pipe_outer_diameter=0.2, diameter_unit="m", length=1, length_unit="m")),
    (p.hydrostatic_pressure_difference, dict(fluid_density=0, density_unit="kg/m3", delta_tvd=100, depth_unit="m")),
    (p.flooded_pipe_apparent_weight, dict(outer_diameter=.2, inner_diameter=-.1, diameter_unit="m",
         dry_linear_mass=100, linear_mass_unit="kg/m", fluid_density=1000, density_unit="kg/m3",
         length=1, length_unit="m")),
])
def test_invalid_cases_raise(call, kwargs):
    with pytest.raises(p.PrimitiveError):
        call(**kwargs)
