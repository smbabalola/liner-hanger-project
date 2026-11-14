"""Analytic minimum curvature known-answer and invalid path regression."""
from pathlib import Path
import importlib.util
import sys
from decimal import Decimal
import pytest

path = Path(__file__).resolve().parents[1] / "scripts" / "directional_survey.py"
spec = importlib.util.spec_from_file_location("directional_survey", path)
p = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = p
spec.loader.exec_module(p)


def run(stations):
    return p.integrate_minimum_curvature(stations=stations, depth_unit="m",
        start_tvd=0, start_tvd_unit="m", datum="RKB")


def s(md, inc, azi=0):
    return p.SurveyStation(md, inc, azi, "synthetic known-answer")


def test_vertical_two_stations_100m():
    assert run([s(0, 0), s(100, 0)])[-1].tvd_m == Decimal("100")


def test_horizontal_two_stations_no_tvd_gain():
    assert abs(run([s(0, 90), s(100, 90)])[-1].tvd_m) < Decimal("1e-10")


def test_sixty_degree_constant_inclination_gain():
    assert abs(run([s(0, 60), s(100, 60)])[-1].tvd_m - 50) < Decimal("1e-9")


def test_90_degree_build_known_quarter_circle():
    assert abs(run([s(0, 0), s(100, 90)])[-1].tvd_m -
               Decimal("63.66197723675813")) < Decimal("1e-9")


def test_explicit_nonzero_initial_tvd_and_feet():
    result = p.integrate_minimum_curvature(stations=[s(100, 0), s(200, 0)],
        depth_unit="ft", start_tvd=100, start_tvd_unit="ft", datum="RT")
    assert result[-1].tvd_m == Decimal("60.96")


def test_survey_requires_first_station_tvd_not_zero_assumption():
    result = p.integrate_minimum_curvature(stations=[s(500, 0)],
        depth_unit="m", start_tvd=120, start_tvd_unit="m", datum="RKB")
    assert result[0].tvd_m == 120


@pytest.mark.parametrize("stations,change", [
    ([s(10, 0), s(10, 0)], {}),
    ([s(10, 0), s(0, 0)], {}),
    ([s(0, 181)], {}),
    ([s(0, 0), s(100, 180)], {}),
    ([s(0, 0, 360)], {}),
    ([p.SurveyStation(0, 0, 0, "")], {}),
    ([], {}),
    ([s(0, "NaN")], {}),
    ([s(0, 0)], {"datum": ""}),
])
def test_invalid_survey(stations, change):
    opts = dict(stations=stations, depth_unit="m", start_tvd=0,
                start_tvd_unit="m", datum="RKB")
    opts.update(change)
    with pytest.raises(p.SurveyError):
        p.integrate_minimum_curvature(**opts)
