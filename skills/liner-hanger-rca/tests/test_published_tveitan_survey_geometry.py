"""Public real-well 3D *survey geometry* checks; NEVER torque/drag validation.

K. Tveitan, University of Stavanger MSc (2011), printed Table A-1, p.57,
Well A, five consecutive station rows at MD 1202.50-1318.10 m:
https://uis.brage.unit.no/uis-xmlui/bitstream/handle/11250/183305/Tveitan%2C%20Knut.pdf?isAllowed=y&sequence=1
All source columns printed to 0.01m / 0.01degree; tolerance 0.02m
allows rounding at both endpoints. The five-row excerpt is neither a
field-measured force curve nor a source of friction, tool, or wall-contact data.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from directional_survey import SurveyStation, integrate_minimum_curvature
from trajectory_interpolation_audit import audit_two_station_trajectory

# (MD m, inclination deg, azimuth deg, TVD m, north m, east m)
# Decimal commas in the original paper are transcribed as decimal points.
STATIONS = (
    (1202.50, 24.99, 237.59, 1147.96, -239.95, -48.02),
    (1231.10, 26.02, 242.84, 1173.78, -246.06, -58.70),
    (1260.50, 27.99, 247.17, 1199.97, -251.68, -70.80),
    (1289.50, 29.22, 253.16, 1225.44, -256.37, -83.85),
    (1318.10, 30.82, 259.25, 1250.21, -259.76, -97.73),
)
COORDS = ("north", "east", "down")


@pytest.mark.parametrize("interval", range(4))
@pytest.mark.parametrize("coordinate", COORDS)
def test_independently_published_three_dimensional_station_increments(interval, coordinate):
    """Independent Simpson integration of our great-circle interpolation matches real 3D survey."""
    upper, lower = STATIONS[interval:interval+2]
    audit = audit_two_station_trajectory(
        length_m=lower[0]-upper[0],
        top_inclination_deg=upper[1], bottom_inclination_deg=lower[1],
        top_azimuth_deg=upper[2], bottom_azimuth_deg=lower[2],
        steps=256,
    )
    index = COORDS.index(coordinate)
    observed = lower[(4, 5, 3)[index]] - upper[(4, 5, 3)[index]]
    predicted = audit["samples"][-1]["minimum_curvature_north_east_down_m"][index]
    assert abs(predicted-observed) < 0.02, (
        f"published Well A Table A-1 interval {interval}, {coordinate}: "
        f"computed {predicted}, reported increment {observed}"
    )


def test_actual_skill_minimum_curvature_reproduces_published_tvd_stations():
    """Exercise the production directional survey module, not just audit equations."""
    input_stations = [
        SurveyStation(row[0],row[1],row[2],"Tveitan 2011 Table A-1 printed p.57")
        for row in STATIONS
    ]
    calculated = integrate_minimum_curvature(
        stations=input_stations,depth_unit="m",
        start_tvd=STATIONS[0][3],start_tvd_unit="m",
        datum="Tveitan Well A source TVD datum (relative at MD 1202.50 m)",
    )
    assert len(calculated)==len(STATIONS)
    for actual, source in zip(calculated, STATIONS):
        assert abs(float(actual.tvd_m)-source[3]) < 0.02


def test_published_geometry_is_genuinely_three_dimensional():
    assert STATIONS[-1][1] != STATIONS[0][1]
    assert STATIONS[-1][2] != STATIONS[0][2]
    assert STATIONS[-1][4] != STATIONS[0][4]
    assert STATIONS[-1][5] != STATIONS[0][5]
