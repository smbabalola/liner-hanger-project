"""Independent analytical limits for the experimental MC-consistent 3D model."""
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_planned_section import from_payload
from planned_job_section import SourcedNumber
from torque_drag_3d import SpatialCurveInputs
from torque_drag_3d_minimum_curvature import predict_minimum_curvature_curve
from torque_drag_straight import TorqueDragError
from run_torque_drag_3d import run_payload as legacy_run

EXAMPLE = ROOT / "examples" / "synthetic_torque_drag_3d.json"


def fixture(i0=30, i1=60, a0=0, a1=60, *, mu="0.2", steps=256,
            zero_weight=False):
    d = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    s = d["planned_section"]["survey_stations"]
    s[0]["inclination_deg"],s[1]["inclination_deg"] = i0,i1
    s[0]["azimuth_deg"],s[1]["azimuth_deg"] = a0,a1
    d["axial_friction"]["value"] = mu
    d["integration_steps"] = steps
    if zero_weight:
        d["planned_section"]["dry_linear_mass"]["value"] = (
            1000*math.pi*(0.1**2-0.08**2)/4)
    return d


def calculate(d):
    return predict_minimum_curvature_curve(SpatialCurveInputs(
        section=from_payload(d["planned_section"]),
        axial_friction=SourcedNumber(**d["axial_friction"]),
        rotational_friction=SourcedNumber(**d["rotational_friction"]),
        contact_radius=SourcedNumber(**d["contact_radius"]),
        bottom_tension=SourcedNumber(**d["bottom_tension"]),
        integration_steps=d["integration_steps"],
    ))


def _beta(i0,i1,a0,a1):
    i0,i1,a0,a1 = map(math.radians,(i0,i1,a0,a1))
    return math.acos(max(-1,min(1,math.cos(i0)*math.cos(i1)+
                         math.sin(i0)*math.sin(i1)*math.cos(a1-a0))))


@pytest.mark.parametrize("geometry", [
    (0,0,0,0), (30,30,0,0), (30,60,0,0),
    (30,60,0,60), (60,60,350,10),
])
def test_zero_weight_closed_form_great_circle_capstan(geometry):
    i0,i1,a0,a1 = geometry
    result = calculate(fixture(*geometry, zero_weight=True, steps=512))
    b = _beta(*geometry)
    values = result["results"]
    assert float(values["pickup"]["top_tension_n"]) == pytest.approx(
        20000*math.exp(.2*b), rel=1e-10)
    assert float(values["slackoff"]["top_tension_n"]) == pytest.approx(
        20000*math.exp(-.2*b), rel=1e-10)
    assert float(values["rotation"]["top_tension_n"]) == pytest.approx(
        20000, rel=1e-12)
    assert float(values["rotation"]["contact_torque_nm"]) == pytest.approx(
        .3*20000*b*.05, abs=1e-7)


@pytest.mark.parametrize("geometry", [
    (0,0,0,0), (30,30,0,0), (30,60,0,0),
    (30,60,0,60), (60,60,350,10),
])
def test_zero_axial_friction_gravity_is_mc_tvd_integral(geometry):
    i0,i1,a0,a1 = geometry
    d = fixture(*geometry, mu="0", steps=512)
    result = calculate(d)
    wL = float(result["section_buoyed_weight_n"])
    b = _beta(*geometry)
    ratio = 1 if b < 1e-8 else 2*math.tan(b/2)/b
    delta_tvd_over_length = (math.cos(math.radians(i0))+
                             math.cos(math.radians(i1)))*ratio/2
    expected = 20000+wL*delta_tvd_over_length
    for mode in ("pickup","slackoff","rotation"):
        assert float(result["results"][mode]["top_tension_n"]) == pytest.approx(
            expected, rel=1e-10)


def test_combined_build_turn_has_distinct_force_result_from_legacy():
    d = fixture()
    m = calculate(d)
    legacy = legacy_run(d)
    # Two different trajectory conventions are intentionally not identical.
    assert abs(float(m["results"]["rotation"]["top_tension_n"])-
               float(legacy["results"]["rotation"]["top_tension_n"])) > 1
    assert m["model"] == "experimental-3d-minimum-curvature-soft-string-v0.1"


def test_planar_build_remains_weighted_planar_equivalent():
    d = fixture(30,60,0,0)
    mc = calculate(d)
    original = legacy_run(d)
    for mode in ("pickup","slackoff","rotation"):
        assert float(mc["results"][mode]["top_tension_n"]) == pytest.approx(
            float(original["results"][mode]["top_tension_n"]), rel=2e-9)


def test_horizontal_azimuth_turn_remains_legacy_equivalent():
    d = fixture(90,90,0,60)
    mc = calculate(d)
    original = legacy_run(d)
    for mode in ("pickup","slackoff","rotation"):
        assert float(mc["results"][mode]["top_tension_n"]) == pytest.approx(
            float(original["results"][mode]["top_tension_n"]), rel=2e-9)


def test_rk4_convergence_for_weighted_combined_turn():
    values = [calculate(fixture(steps=n))["results"] for n in (32,64,128)]
    for mode in ("pickup","slackoff","rotation"):
        a,b,c = (float(v[mode]["top_tension_n"]) for v in values)
        assert abs(c-b) < abs(b-a)+1e-9


def test_rejects_unreviewed_geometry_but_never_returns_field_approval():
    result = calculate(fixture())
    assert result["status"] == "unreviewed_inputs"
    assert result["sources"]["minimum_curvature_inputs"]["axial_friction"]["source_id"]
    assert "not field-validated" in result["warning"]


@pytest.mark.parametrize("bad", [
    ("integration_steps", 7),
    ("integration_steps", True),
    ("axial_friction", -1),
    ("contact_radius", .01),
])
def test_invalid_inputs_fail_closed(bad):
    key,val = bad
    d = fixture()
    if key=="integration_steps":
        d[key] = val
    else:
        d[key]["value"]=val
    with pytest.raises(TorqueDragError):
        calculate(d)


def test_upstream_180_degree_survey_dogleg_fails_closed():
    with pytest.raises((TorqueDragError,ValueError)):
        calculate(fixture(90,90,0,180))

def test_signed_planar_wall_transfer_is_not_silently_integrated():
    d=fixture(30,60,0,0)
    d["bottom_tension"]["value"]=5000
    with pytest.raises(TorqueDragError,match="contact side transition|near-zero contact"):
        calculate(d)


def test_true_3d_weighted_model_not_approved_as_rig_hookload():
    r=calculate(fixture())
    assert r["status"]=="unreviewed_inputs"
    assert "no liner hanger load" in r["warning"]
    assert "minimum_curvature_delta_tvd_m" in r

def test_independent_high_precision_weighted_3d_known_answer():
    # Independent numerical integration: SciPy DOP853, rtol=1e-12,
    # atol=1e-11, of the vector soft-string ODE for the same fictional
    # 100m (30->60 deg inclination, 0->60 deg azimuth) wet tube.
    # This is an independently computed math answer, not a field benchmark.
    r=calculate(fixture(30,60,0,60,steps=256))["results"]
    assert float(r["pickup"]["top_tension_n"]) == pytest.approx(
        32312.017813922695,rel=2e-9)
    assert float(r["slackoff"]["top_tension_n"]) == pytest.approx(
        25564.335371987625,rel=2e-9)
    assert float(r["rotation"]["top_tension_n"]) == pytest.approx(
        28701.20754776104,rel=2e-9)
    assert float(r["rotation"]["contact_torque_nm"]) == pytest.approx(
        252.07886152249975,rel=2e-9)
