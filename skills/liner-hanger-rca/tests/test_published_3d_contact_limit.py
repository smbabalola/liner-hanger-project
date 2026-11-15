"""Published 3D soft-string contact law: independently derived weighted limit.

External formulation: Zhang et al. (2026), Scientific Reports,
DOI 10.1038/s41598-026-78097-x, Eq. (16):
N_phi = (F_i+F_{i-1}) sin(i_bar) sin(delta_azimuth/2)
N_G = (F_i+F_{i+1}) cos(delta_azimuth/2) sin(delta_inclination/2)
      + w*delta_L*sin(i_bar).
For constant horizontal inclination, constant rotation-mode axial tension,
and equal adjacent tension, this reduces to orthogonal azimuth-curvature
and vertical gravity normal loads. In the vanishing station-step limit:
N_total = hypot(T * delta_azimuth_rad, W_buoyed).
This is a benchmark for an idealized continuous-contact, pure-rotation,
weighted 3D contact *limit*, NOT paper's field-well force/torque results.

Source: https://www.nature.com/articles/s41598-026-78097-x_reference.pdf
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


@pytest.mark.parametrize("azimuth_change_deg", (15, 45, 80))
def test_weighted_horizontal_3d_rotation_contact_matches_published_normal_law_limit(
    azimuth_change_deg,
):
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    stations = data["planned_section"]["survey_stations"]
    for station in stations:
        station["inclination_deg"] = 90
    stations[0]["azimuth_deg"] = 0
    stations[1]["azimuth_deg"] = azimuth_change_deg
    data["integration_steps"] = 256

    result = predict_minimum_curvature_curve(SpatialCurveInputs(
        section=from_payload(data["planned_section"]),
        axial_friction=SourcedNumber(**data["axial_friction"]),
        rotational_friction=SourcedNumber(**data["rotational_friction"]),
        contact_radius=SourcedNumber(**data["contact_radius"]),
        bottom_tension=SourcedNumber(**data["bottom_tension"]),
        integration_steps=data["integration_steps"],
    ))

    # Independent closed-form reduction of published N_phi, N_G for
    # horizontal constant-T azimuth turn. The vertical gravity normal
    # and horizontal curvature normal are orthogonal.
    bottom_tension_n = float(data["bottom_tension"]["value"])
    total_weight_n = float(result["section_buoyed_weight_n"])
    turn_rad = math.radians(azimuth_change_deg)
    reference_contact_n = math.hypot(
        total_weight_n, bottom_tension_n * turn_rad,
    )
    reference_torque_nm = (
        float(data["rotational_friction"]["value"])
        * float(data["contact_radius"]["value"])
        * reference_contact_n
    )
    rotation = result["results"]["rotation"]

    assert total_weight_n > 0  # genuinely weighted, not capstan
    assert turn_rad > 0  # genuinely changing azimuth, not planar build
    assert float(rotation["top_tension_n"]) == pytest.approx(
        bottom_tension_n, abs=1e-7)
    assert float(rotation["integrated_wall_contact_n"]) == pytest.approx(
        reference_contact_n, rel=1e-9)
    assert float(rotation["contact_torque_nm"]) == pytest.approx(
        reference_torque_nm, rel=1e-9)
    assert result["status"] == "unreviewed_inputs"


def test_published_discrete_3d_contact_terms_converge_to_continuous_weighted_limit():
    # Independent Eq.(16) midpoint finite-element calculation for a
    # 100m horizontal 60-degree azimuth turn, equal tension at every
    # neighbouring station, uniform buoyed weight. No production solver
    # is imported for these expected values.
    length_m, tension_n, total_weight_n = 100., 20000., 12000.
    total_turn_rad = math.pi/3
    reference = math.hypot(tension_n*total_turn_rad, total_weight_n)
    errors = []
    for count in (4, 8, 16, 32, 64):
        delta = total_turn_rad/count
        lateral_per_element = 2*tension_n*math.sin(delta/2)
        gravity_per_element = total_weight_n/count
        accumulated = count*math.hypot(lateral_per_element, gravity_per_element)
        errors.append(abs(accumulated-reference))
    assert errors[-1] < errors[0]
    assert all(b < a for a,b in zip(errors,errors[1:]))
    assert errors[-1]/reference < 3e-5
