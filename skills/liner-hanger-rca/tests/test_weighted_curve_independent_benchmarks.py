"""Independent closed-form planar weighted soft-string checks.

Equations derived by integrating constant-sign Coulomb normal contact;
expected values do NOT come from the solver under test.
"""
from dataclasses import replace
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_torque_drag_weighted_curve import run_payload
from torque_drag_straight import TorqueDragError


def case(*, top=0, bottom=60, tension=20000, steps=256, mu=0.2):
    raw = json.loads((ROOT / "examples" / "synthetic_torque_drag_weighted_curve.json").read_text())
    raw["planned_section"]["survey_stations"][0]["inclination_deg"] = top
    raw["planned_section"]["survey_stations"][1]["inclination_deg"] = bottom
    raw["bottom_tension"]["value"] = tension
    raw["axial_friction"]["value"] = mu
    raw["integration_steps"] = steps
    return raw


def independently_integrated_top(*, top, bottom, mode, mu=0.2, tension=20000):
    """Analytic integrating-factor solution with invariant signed contact side.

    Write n = sign * (w sin i - kT), b = mode*mu*sign.
    T' + bkT = w(cos i + b sin i); i = ib - ks.
    The closed-form particular solution is A sin i + B cos i with
    A=w(b²-1)/[k(1+b²)] and B=2wb/[k(1+b²)].
    """
    w = (15 - 1000 * math.pi * (0.1**2 - 0.08**2) / 4) * 9.80665
    L = 100
    it, ib = math.radians(top), math.radians(bottom)
    k = (ib-it)/L
    assert k != 0
    signed_contact_side = -1 if k > 0 else 1
    b = mode * mu * signed_contact_side
    a = b*k
    A = w * (b*b-1)/(k*(1+b*b))
    B = 2*w*b/(k*(1+b*b))
    particular = lambda angle: A*math.sin(angle)+B*math.cos(angle)
    return (math.exp(-a*L)*tension
            + particular(it)
            - math.exp(-a*L)*particular(ib))


@pytest.mark.parametrize("top,bottom", [(0, 60), (60, 0)])
@pytest.mark.parametrize("mode,label", [(1, "pickup"), (-1, "slackoff"), (0, "rotation")])
def test_weighted_build_drop_matches_closed_form_constant_side(top, bottom, mode, label):
    output = run_payload(case(top=top, bottom=bottom))
    observed = float(output["results"][label]["top_tension_n"])
    analytic = independently_integrated_top(top=top, bottom=bottom, mode=mode)
    assert observed == pytest.approx(analytic, rel=2e-11)
    assert output["results"][label]["signed_contact_side"] == (
        -1 if bottom > top else 1)


def test_weighted_build_contact_side_change_is_rejected_not_hidden():
    # Small but tensile boundary: gravity normal exceeds kT near bottom,
    # then the local normal changes side as tension increases toward top.
    with pytest.raises(TorqueDragError, match="contact side transition"):
        run_payload(case(tension=1000))


def test_normal_contact_side_sign_for_weighted_build_and_drop():
    build = run_payload(case(top=0, bottom=60))
    drop = run_payload(case(top=60, bottom=0))
    for mode in ("pickup", "slackoff", "rotation"):
        assert build["results"][mode]["signed_contact_side"] == -1
        assert drop["results"][mode]["signed_contact_side"] == 1


def test_closed_form_matches_refined_rk4_without_using_rk4_in_reference():
    coarse = run_payload(case(steps=32))
    fine = run_payload(case(steps=256))
    ref = independently_integrated_top(top=0, bottom=60, mode=1)
    ec = abs(float(coarse["results"]["pickup"]["top_tension_n"]) - ref)
    ef = abs(float(fine["results"]["pickup"]["top_tension_n"]) - ref)
    assert ef < ec
    assert ef < 1e-6


def test_weightless_research_limit_retains_nonzero_curvature_contact():
    # This is tested separately by the existing capstan suite; here assert
    # the weighted model does not mistake gravity=0 for no side contact.
    raw = case()
    raw["planned_section"]["dry_linear_mass"]["value"] = (
        1000*math.pi*(0.1**2-0.08**2)/4)
    result = run_payload(raw)
    assert float(result["results"]["rotation"]["integrated_wall_contact_n"]) > 0
    assert result["results"]["rotation"]["signed_contact_side"] == -1
