"""LH-CALC-01: minimum-curvature survey integration, not a well-path design tool.

Angles in degrees, depths in a declared unit. No survey interpolation outside
provided stations, and no inferred missing station or datum.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from math import acos, cos, radians, sin, tan, isfinite, pi

LENGTH_M = {"m": Decimal("1"), "ft": Decimal("0.3048")}


class SurveyError(ValueError):
    pass


def _num(v, field):
    if isinstance(v, bool) or v is None:
        raise SurveyError(f"{field}: finite numeric required")
    try:
        d = Decimal(str(v))
    except (ValueError, InvalidOperation):
        raise SurveyError(f"{field}: invalid number") from None
    if not d.is_finite():
        raise SurveyError(f"{field}: non-finite number")
    return d


@dataclass(frozen=True)
class SurveyStation:
    measured_depth: str | int | float
    inclination_deg: str | int | float
    azimuth_deg: str | int | float
    source_ref: str


@dataclass(frozen=True)
class TVDStation:
    md_m: Decimal
    tvd_m: Decimal
    inclination_deg: Decimal
    azimuth_deg: Decimal
    dogleg_rad_from_previous: Decimal | None


def integrate_minimum_curvature(*, stations, depth_unit, start_tvd, start_tvd_unit,
                                datum):
    """Integrate surveyed station TVD by minimum curvature from a known start.

    The supplied start_tvd is the TVD at the FIRST provided survey station,
    not implicitly at MD=0. Returned tuple follows provided measured depths.
    Flat/vertical/horizontal/upward paths are mathematical; no completion or
    mechanical clearance check is implied.
    """
    if depth_unit not in LENGTH_M or start_tvd_unit not in LENGTH_M:
        raise SurveyError("explicit supported depth units required (m, ft)")
    if not isinstance(datum, str) or not datum.strip():
        raise SurveyError("explicit TVD datum required")
    if not isinstance(stations, (list, tuple)) or not stations:
        raise SurveyError("at least one survey station required")
    tvd = _num(start_tvd, "start_tvd") * LENGTH_M[start_tvd_unit]
    if tvd < 0:
        raise SurveyError("start_tvd cannot be negative")
    parsed = []
    for index, st in enumerate(stations):
        if not isinstance(st, SurveyStation):
            raise SurveyError("all stations must be SurveyStation")
        if not isinstance(st.source_ref, str) or not st.source_ref.strip():
            raise SurveyError(f"station {index}: source_ref required")
        md = _num(st.measured_depth, "measured_depth") * LENGTH_M[depth_unit]
        inc = _num(st.inclination_deg, "inclination_deg")
        azi = _num(st.azimuth_deg, "azimuth_deg")
        if md < 0 or inc < 0 or inc > 180 or azi < 0 or azi >= 360:
            raise SurveyError("MD, inclination or azimuth out of supported range")
        if parsed and md <= parsed[-1][0]:
            raise SurveyError("survey MD must be strictly increasing")
        parsed.append((md, inc, azi))
    out = []
    for i, (md, inc, azi) in enumerate(parsed):
        dogleg = None
        if i:
            prev_md, prev_inc, prev_azi = parsed[i-1]
            i1, i2 = radians(float(prev_inc)), radians(float(inc))
            a1, a2 = radians(float(prev_azi)), radians(float(azi))
            dot = cos(i1)*cos(i2) + sin(i1)*sin(i2)*cos(a2-a1)
            dogleg_f = acos(max(-1.0, min(1.0, dot)))
            if not isfinite(dogleg_f):
                raise SurveyError("non-finite dogleg")
            if dogleg_f >= pi - 1e-7:
                raise SurveyError("minimum curvature undefined at 180-degree dogleg")
            rf = 1.0 if dogleg_f < 1e-8 else 2.0 / dogleg_f * tan(dogleg_f / 2)
            if not isfinite(rf):
                raise SurveyError("minimum curvature undefined at 180-degree dogleg")
            delta = float(md - prev_md) * (cos(i1) + cos(i2)) / 2 * rf
            if not isfinite(delta):
                raise SurveyError("non-finite trajectory increment")
            tvd += Decimal(str(delta))
            dogleg = Decimal(str(dogleg_f))
        out.append(TVDStation(md, tvd, inc, azi, dogleg))
    return tuple(out)
