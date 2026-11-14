"""LH-CALC-01: source-qualified, deliberately narrow planned-section computations.

No OEM-specific data, default mud, invented datum, MD interpolation or approval.
This models one uniform, fully immersed, flooded section between two EXISTING
survey stations. Multiple sections/pressure states require separate records.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from directional_survey import SurveyStation, integrate_minimum_curvature, SurveyError
from engineering_primitives import (
    _convert, LENGTH_M, DENSITY_KG_M3, LINEAR_MASS_KG_M,
    tubular_capacity, annular_capacity, hydrostatic_pressure_difference,
    flooded_pipe_apparent_weight, PrimitiveError,
)

class PlannedSectionError(ValueError):
    pass


@dataclass(frozen=True)
class SourcedNumber:
    value: str | int | float
    unit: str
    source_id: str
    source_location: str
    source_revision: str
    review_status: str = "unreviewed"

    def si(self, factors: Mapping[str, Decimal], name: str, *, positive=True) -> Decimal:
        for key in ("source_id", "source_location", "source_revision"):
            value = getattr(self, key)
            if not isinstance(value, str) or not value.strip():
                raise PlannedSectionError(f"{name}: {key} required")
        if self.review_status not in ("reviewed", "unreviewed"):
            raise PlannedSectionError(f"{name}: invalid review_status")
        try:
            return _convert(self.value, self.unit, factors, name, positive=positive)
        except PrimitiveError as exc:
            raise PlannedSectionError(str(exc)) from exc


@dataclass(frozen=True)
class PlannedSection:
    case_id: str
    section_id: str
    datum: str
    survey_revision: str
    survey_source_id: str
    survey_stations: tuple[SurveyStation, ...]
    survey_depth_unit: str
    first_station_tvd: SourcedNumber
    top_md: SourcedNumber
    bottom_md: SourcedNumber
    bore_diameter: SourcedNumber
    pipe_outer_diameter: SourcedNumber
    pipe_inner_diameter: SourcedNumber
    dry_linear_mass: SourcedNumber
    fluid_density: SourcedNumber
    flooded_open_pipe: bool

    def validate(self) -> None:
        for name in ("case_id", "section_id", "datum", "survey_revision", "survey_source_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise PlannedSectionError(f"{name} required")
        if type(self.flooded_open_pipe) is not bool or not self.flooded_open_pipe:
            raise PlannedSectionError("flooded/open/pressure-balanced assumption must be explicitly true")
        if self.survey_depth_unit not in LENGTH_M:
            raise PlannedSectionError("survey_depth_unit must be m or ft")
        if not self.survey_stations or len(self.survey_stations) < 2:
            raise PlannedSectionError("two or more sourced survey stations required")
        self.first_station_tvd.si(LENGTH_M, "first_station_tvd", positive=False)
        top = self.top_md.si(LENGTH_M, "top_md", positive=False)
        bottom = self.bottom_md.si(LENGTH_M, "bottom_md", positive=False)
        if top < 0 or bottom <= top:
            raise PlannedSectionError("section MD must be nonnegative and increasing")
        bore = self.bore_diameter.si(LENGTH_M, "bore_diameter")
        outer = self.pipe_outer_diameter.si(LENGTH_M, "pipe_outer_diameter")
        inner = self.pipe_inner_diameter.si(LENGTH_M, "pipe_inner_diameter", positive=False)
        if not 0 <= inner < outer < bore:
            raise PlannedSectionError("required geometry: 0 <= pipe ID < pipe OD < bore ID")
        self.dry_linear_mass.si(LINEAR_MASS_KG_M, "dry_linear_mass")
        self.fluid_density.si(DENSITY_KG_M3, "fluid_density")
        try:
            stations = integrate_minimum_curvature(
                stations=self.survey_stations, depth_unit=self.survey_depth_unit,
                start_tvd=self.first_station_tvd.value,
                start_tvd_unit=self.first_station_tvd.unit, datum=self.datum)
        except SurveyError as exc:
            raise PlannedSectionError(str(exc)) from exc
        md = {s.md_m for s in stations}
        if top not in md or bottom not in md:
            raise PlannedSectionError("section endpoints require exact survey MD stations; no interpolation")
        if any(not s.source_ref.strip() for s in self.survey_stations):
            raise PlannedSectionError("each survey station requires source provenance")

    def calculate(self) -> dict:
        self.validate()
        stations = integrate_minimum_curvature(
            stations=self.survey_stations, depth_unit=self.survey_depth_unit,
            start_tvd=self.first_station_tvd.value,
            start_tvd_unit=self.first_station_tvd.unit, datum=self.datum)
        by_md = {s.md_m: s.tvd_m for s in stations}
        top = self.top_md.si(LENGTH_M, "top_md", positive=False)
        bottom = self.bottom_md.si(LENGTH_M, "bottom_md", positive=False)
        length = bottom - top
        delta_tvd = by_md[bottom] - by_md[top]
        bore = self.bore_diameter.si(LENGTH_M, "bore_diameter")
        outer = self.pipe_outer_diameter.si(LENGTH_M, "pipe_outer_diameter")
        inner = self.pipe_inner_diameter.si(LENGTH_M, "pipe_inner_diameter", positive=False)
        linmass = self.dry_linear_mass.si(LINEAR_MASS_KG_M, "dry_linear_mass")
        rho = self.fluid_density.si(DENSITY_KG_M3, "fluid_density")
        results = {
            "section_length_md_m": length,
            "delta_tvd_m": delta_tvd,
            "tubular_capacity_m3": tubular_capacity(
                inside_diameter=inner, diameter_unit="m", length=length, length_unit="m"),
            "annular_capacity_m3": annular_capacity(
                bore_diameter=bore, pipe_outer_diameter=outer, diameter_unit="m",
                length=length, length_unit="m"),
            "hydrostatic_difference_pa": hydrostatic_pressure_difference(
                fluid_density=rho, density_unit="kg/m3", delta_tvd=delta_tvd, depth_unit="m"),
            "open_flooded_apparent_weight_n": flooded_pipe_apparent_weight(
                outer_diameter=outer, inner_diameter=inner, diameter_unit="m",
                dry_linear_mass=linmass, linear_mass_unit="kg/m",
                fluid_density=rho, density_unit="kg/m3", length=length, length_unit="m"),
        }
        sources = {name: {
            "source_id": getattr(self, name).source_id,
            "source_location": getattr(self, name).source_location,
            "source_revision": getattr(self, name).source_revision,
            "unit": getattr(self, name).unit,
            "review_status": getattr(self, name).review_status
        } for name in ("first_station_tvd", "top_md", "bottom_md",
                        "bore_diameter", "pipe_outer_diameter", "pipe_inner_diameter",
                        "dry_linear_mass", "fluid_density")}
        sources["survey"] = {"source_id": self.survey_source_id,
                             "source_revision": self.survey_revision,
                             "station_sources": [s.source_ref for s in self.survey_stations],
                             "datum": self.datum}
        reviewed = all(x["review_status"] == "reviewed" for k, x in sources.items()
                       if k != "survey")
        return {
            "case_id": self.case_id, "section_id": self.section_id,
            "model": "uniform-section-constant-density-static-v1",
            "status": "numeric_candidate_only" if reviewed else "unreviewed_inputs",
            "results": {k: str(v) for k, v in results.items()},
            "sources": sources,
            "assumptions": ["uniform section and constant fluid density",
                            "fully immersed open and flooded pipe",
                            "pressure-balanced fluid inside and outside",
                            "survey endpoints exactly aligned to section MD"],
            "warning": "No OEM approval, torque/drag, SPP, ECD, safe tripping or setting verdict.",
        }
