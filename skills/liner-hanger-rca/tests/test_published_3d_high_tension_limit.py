"""Published 3D high-tension analytical *limit*, not independent field validation.

Fazaelizadeh, Hareland & Aadnoy (2010), Modern Applied Science 4(2),
DOI 10.5539/mas.v4n2p2, equations (13)-(14).
https://www.ccsenet.org/journal/index.php/mas/article/view/4418/4229
The paper uses a weightless-in-bend Coulomb capstan for curvature friction,
adds static gravity after the bend, and gives friction torque at the bottom
tension; this is explicitly an asymptotic approximation at high tension,
NOT the same weighted vector wall-contact ODE used by the skill.

Our comparison holds *nonzero physical pipe weight* fixed while increasing
a fictional lower boundary tension. This establishes an independent
published *asymptotic-equation comparison* and convergence, not valid
well equipment loads or a field-sized approval. No model value is fitted.
"""
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from planned_job_section import SourcedNumber
from run_planned_section import from_payload
from torque_drag_3d import SpatialCurveInputs
from torque_drag_3d_minimum_curvature import predict_minimum_curvature_curve

EXAMPLE = ROOT / "examples" / "synthetic_torque_drag_3d.json"
BETA = math.acos(
    math.cos(math.radians(30)) * math.cos(math.radians(60)) +
    math.sin(math.radians(30)) * math.sin(math.radians(60)) *
    math.cos(math.radians(60))
)


def _run(bottom):
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    st = payload["planned_section"]["survey_stations"]
    st[0]["inclination_deg"], st[1]["inclination_deg"] = 30, 60
    st[0]["azimuth_deg"], st[1]["azimuth_deg"] = 0, 60
    payload["bottom_tension"]["value"] = str(bottom)
    payload["integration_steps"] = 256
    inp = SpatialCurveInputs(
        section=from_payload(payload["planned_section"]),
        axial_friction=SourcedNumber(**payload["axial_friction"]),
        rotational_friction=SourcedNumber(**payload["rotational_friction"]),
        contact_radius=SourcedNumber(**payload["contact_radius"]),
        bottom_tension=SourcedNumber(**payload["bottom_tension"]),
        integration_steps=payload["integration_steps"],
    )
    return predict_minimum_curvature_curve(inp)


def _published_asymptotic(bottom, total_buoyed_weight):
    """Separate implementation of 2010 Eqs. (13)-(14) for purely axial and rotary motion."""
    upper = math.radians(30)
    lower = math.radians(60)
    # Eq (13)'s vertical projection: planar mean-cos factor, deliberately
    # NOT the production 3D MC TVD computation. Valid only as a high-T limit
    # where this difference is small compared with the total axial tension.
    gravity = total_buoyed_weight * (
        math.sin(lower) - math.sin(upper)) / (lower-upper)
    return {
        "pickup": bottom * math.exp(+0.2 * BETA) + gravity,
        "slackoff": bottom * math.exp(-0.2 * BETA) + gravity,
        "rotation_tension": bottom + gravity,
        # Eq (14): stationary axial travel (psi=0), independent rotary
        # coefficient, contact radius and bottom tensile force.
        "rotation_torque": 0.3 * 0.05 * bottom * BETA,
    }


@pytest.mark.parametrize("observable", [
    "pickup", "slackoff", "rotation_tension", "rotation_torque",
])
def test_nonzero_weight_3d_converges_to_published_high_tension_force_limit(observable):
    """Compare real nonzero weight with externally *published* analytical high-T equations."""
    bottom = 2_000_000.0  # fictional mathematical limit, NOT operating setpoint
    response = _run(bottom)
    w = float(response["section_buoyed_weight_n"])
    assert w > 1000  # nonzero-weight; not the existing zero-weight capstan fixture
    ref = _published_asymptotic(bottom, w)[observable]
    if observable == "rotation_torque":
        actual = float(response["results"]["rotation"]["contact_torque_nm"])
    elif observable == "rotation_tension":
        actual = float(response["results"]["rotation"]["top_tension_n"])
    else:
        actual = float(response["results"][observable]["top_tension_n"])
    # Explicit limited asymptotic tolerance (weight/bottom tension ~0.006).
    assert abs(actual-ref)/abs(ref) < 0.01


@pytest.mark.parametrize("mode", ["pickup", "slackoff"])
def test_published_limit_relative_difference_decreases_as_tension_increases(mode):
    """Friction/curvature approximation must approach source's high-T regime."""
    errors = []
    for bottom in (200_000.0, 2_000_000.0):
        response = _run(bottom)
        w = float(response["section_buoyed_weight_n"])
        expected = _published_asymptotic(bottom, w)[mode]
        observed = float(response["results"][mode]["top_tension_n"])
        errors.append(abs(observed-expected)/abs(expected))
    assert errors[1] < errors[0]
    assert errors[1] < 0.01


def test_published_3d_asymptote_never_changes_research_only_status():
    result = _run(2_000_000)
    assert result["status"] == "unreviewed_inputs"
    assert "not field-validated" in result["warning"]
