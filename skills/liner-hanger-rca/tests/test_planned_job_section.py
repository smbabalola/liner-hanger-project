"""Source-gated single-section planned calculation integration, synthetic only."""
import sys
from decimal import Decimal
from pathlib import Path
from dataclasses import replace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from directional_survey import SurveyStation
from planned_job_section import PlannedSection, SourcedNumber, PlannedSectionError


def q(value, unit, name, *, reviewed=True):
    return SourcedNumber(value, unit, "SYNTHETIC-PACK",
                        "example:" + name, "fictional-rev-1",
                        "reviewed" if reviewed else "unreviewed")


def fixture():
    return PlannedSection(
        case_id="SYNTH-NOT-KHRM", section_id="synthetic-section-1",
        datum="RKB", survey_revision="synthetic-survey-r1", survey_source_id="SYNTHETIC-SURVEY",
        survey_stations=(SurveyStation(0, 0, 0, "synthetic survey row 1"),
                         SurveyStation(100, 0, 0, "synthetic survey row 2")),
        survey_depth_unit="m",
        first_station_tvd=q(0, "m", "tvd0"),
        top_md=q(0, "m", "md0"), bottom_md=q(100, "m", "md100"),
        bore_diameter=q("0.2", "m", "bore"),
        pipe_outer_diameter=q("0.1", "m", "od"),
        pipe_inner_diameter=q("0.08", "m", "id"),
        dry_linear_mass=q(15, "kg/m", "pipeweight"),
        fluid_density=q(1000, "kg/m3", "density"),
        flooded_open_pipe=True,
    )


def test_vertical_synthetic_section_closed_form_outputs():
    result = fixture().calculate()
    assert result["status"] == "numeric_candidate_only"
    assert result["results"]["section_length_md_m"] == "100"
    assert result["results"]["delta_tvd_m"] == "100.0"
    assert Decimal(result["results"]["hydrostatic_difference_pa"]) == 980665
    assert abs(Decimal(result["results"]["tubular_capacity_m3"]) - Decimal("0.5026548245743669")) < Decimal("1e-15")
    assert abs(Decimal(result["results"]["annular_capacity_m3"]) - Decimal("2.356194490192345")) < Decimal("1e-15")
    assert result["sources"]["fluid_density"]["source_location"] == "example:density"
    assert result["sources"]["survey"]["datum"] == "RKB"


def test_horizontal_section_uses_tvd_not_measured_depth():
    job = fixture()
    horizontal = replace(job, survey_stations=(
        SurveyStation(0, 90, 0, "synthetic h1"), SurveyStation(100, 90, 0, "synthetic h2")))
    out = horizontal.calculate()["results"]
    assert abs(Decimal(out["hydrostatic_difference_pa"])) < Decimal("1e-7")
    assert Decimal(out["section_length_md_m"]) == 100


def test_unreviewed_input_never_looks_reviewed():
    job = fixture()
    result = replace(job, fluid_density=q(1000, "kg/m3", "density", reviewed=False)).calculate()
    assert result["status"] == "unreviewed_inputs"


def test_si_equivalent_diameter_unit():
    job = fixture()
    metric = job.calculate()["results"]["annular_capacity_m3"]
    imperial = replace(job, bore_diameter=q(200, "mm", "bore"),
                       pipe_outer_diameter=q(100, "mm", "od")).calculate()["results"]["annular_capacity_m3"]
    assert Decimal(metric) == Decimal(imperial)


@pytest.mark.parametrize("change", [
    {"case_id": ""},
    {"survey_revision": ""},
    {"flooded_open_pipe": False},
    {"bore_diameter": q("0.09", "m", "bad-geometry")},
    {"fluid_density": q(None, "kg/m3", "missing-density")},
    {"dry_linear_mass": q(0, "kg/m", "invalid-mass")},
    {"bottom_md": q(99, "m", "unmatched-endpoint")},
    {"top_md": q(100, "m", "reversed")},
    {"fluid_density": SourcedNumber(1000, "kg/m3", "", "location", "rev")},
    {"survey_stations": (SurveyStation(0, 0, 0, "synthetic"),)},
])
def test_incomplete_or_invalid_plans_fail_closed(change):
    with pytest.raises(PlannedSectionError):
        replace(fixture(), **change).calculate()


def test_no_implicit_approval_in_output():
    result = fixture().calculate()
    assert "No OEM approval" in result["warning"]
    assert "torque/drag" in result["warning"]
    assert result["case_id"] == "SYNTH-NOT-KHRM"
