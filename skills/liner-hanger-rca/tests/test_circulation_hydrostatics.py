"""Independent hydrostatic column law and fail-closed datum tests."""
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from circulation_hydrostatics import HydrostaticLayer,static_hydrostatic_imbalance
from circulating_hydraulics import HydraulicsUnavailable

G=9.80665
def layer(name,leg,top,bottom,rho=1000,source="SYNTHETIC-DENSITY",datum="TVD-REFERENCE"):
    return HydrostaticLayer(name,leg,top,bottom,rho,source,datum)


def test_matching_fictional_columns_cancel_exactly():
    a=layer("down","downstream",0,1000)
    b=layer("up","return",0,1000)
    r=static_hydrostatic_imbalance([a,b])
    assert r["downstream_static_column_head_pa"]==pytest.approx(1000*G*1000)
    assert r["return_static_column_head_pa"]==pytest.approx(1000*G*1000)
    assert r["downstream_surface_minus_return_surface_hydrostatic_pa"]==0
    assert r["standpipe_pressure_pa"] is None
    assert r["engineering_acceptance"] is False


def test_different_density_columns_match_independent_physical_head():
    result=static_hydrostatic_imbalance([
        layer("down","downstream",0,1000,1100),
        layer("ret","return",0,1000,1200)
    ])
    # Direct static force over area: column density difference times g*height.
    assert result["downstream_surface_minus_return_surface_hydrostatic_pa"]==pytest.approx(
        (1200-1100)*G*1000,rel=1e-12)


def test_two_layer_gradient_uses_each_actual_tvd_increment():
    result=static_hydrostatic_imbalance([
        layer("d1","downstream",0,400,1000),
        layer("d2","downstream",400,1000,1150),
        layer("r1","return",0,200,1200),
        layer("r2","return",200,1000,1050),
    ])
    expected=G*(200*1200+800*1050-400*1000-600*1150)
    assert result["downstream_surface_minus_return_surface_hydrostatic_pa"]==pytest.approx(expected)
    assert len(result["layers"])==4


def test_hydrostatic_head_is_tvd_not_measured_depth():
    r=static_hydrostatic_imbalance([
        layer("d","downstream",200,400,1100),
        layer("r","return",200,400,1000)
    ])
    assert r["downstream_surface_minus_return_surface_hydrostatic_pa"]==pytest.approx(
        -100*G*200)
    assert r["surface_and_bottom_tvd_endpoints_m"]==[200,400]


def test_reject_vertical_gap_in_same_leg():
    with pytest.raises(HydraulicsUnavailable,match="gap or overlap"):
        static_hydrostatic_imbalance([
            layer("d1","downstream",0,400),
            layer("d2","downstream",401,1000),
            layer("r","return",0,1000)
        ])


def test_reject_different_foot_depth_or_pressure_sensor_level():
    with pytest.raises(HydraulicsUnavailable,match="same TVD endpoints"):
        static_hydrostatic_imbalance([
            layer("d","downstream",0,1000),
            layer("r","return",0,950)
        ])


def test_reject_unverified_mixed_datums():
    with pytest.raises(HydraulicsUnavailable,match="datums"):
        static_hydrostatic_imbalance([
            layer("d","downstream",0,1000,datum="RKB"),
            layer("r","return",0,1000,datum="MSL")
        ])


def test_reject_single_leg_and_duplicate_identity():
    with pytest.raises(HydraulicsUnavailable,match="both vertical"):
        static_hydrostatic_imbalance([layer("one","downstream",0,1000)])
    with pytest.raises(HydraulicsUnavailable,match="duplicate"):
        static_hydrostatic_imbalance([
            layer("same","downstream",0,1000),
            layer("same","return",0,1000)
        ])


@pytest.mark.parametrize("rho",[-1,0,True,float("nan"),float("inf")])
def test_bad_density_rejected(rho):
    with pytest.raises(HydraulicsUnavailable):
        layer("bad","downstream",0,1000,rho)


@pytest.mark.parametrize("top,bottom",[(10,10),(100,0),(-1,100),(0,float("inf"))])
def test_invalid_tvd_span_rejected(top,bottom):
    with pytest.raises(HydraulicsUnavailable):
        layer("bad","downstream",top,bottom)


def test_no_custom_gravity_adjustment_without_validation():
    with pytest.raises(HydraulicsUnavailable,match="standard gravity"):
        static_hydrostatic_imbalance([
            layer("d","downstream",0,1000),layer("r","return",0,1000)
        ],gravity_m_s2=9.7)


def test_missing_density_source_and_datum_rejected():
    with pytest.raises(HydraulicsUnavailable,match="source identity"):
        layer("d","downstream",0,1000,source="")
    with pytest.raises(HydraulicsUnavailable,match="datum"):
        layer("d","downstream",0,1000,datum="")
