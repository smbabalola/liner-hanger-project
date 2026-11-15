"""Synthetic end-to-end *partial* non-Newtonian component budget checks."""
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from circulating_hydraulics import FlowSegment,HydraulicsUnavailable
from circulation_budget import CircuitComponent
from circulation_restrictions import NozzleOrifice
from power_law_laminar_pipe import PowerLawFluid,power_law_laminar_pipe_pressure_loss
from power_law_laminar_annulus import power_law_laminar_annulus_pressure_loss
from power_law_circulation_budget import partial_power_law_circulation_budget


def parts():
    return [
        CircuitComponent(pipe_or_annulus=FlowSegment(
            "synthetic_pipe","pipe",10,.1,flow_leg="downstream")),
        CircuitComponent(nozzle_orifice=NozzleOrifice(
            "synthetic_nozzle",.0002,.8,"SYNTHETIC-COEFFICIENT")),
        CircuitComponent(pipe_or_annulus=FlowSegment(
            "synthetic_annulus","concentric_annulus",10,.2,.1,"return"))
    ]


def evidence():
    return {"synthetic_pipe":"SYNTHETIC-PIPE-REGIME",
            "synthetic_annulus":"SYNTHETIC-ANNULUS-REGIME"}


def run(q=1e-4,components=None,sources=None,n=.7):
    return partial_power_law_circulation_budget(
        PowerLawFluid(1050,.15,n),components if components is not None else parts(),
        q,laminar_evidence_by_section=sources if sources is not None else evidence())


def test_component_budget_equals_separately_computed_rheological_losses():
    components=parts()
    fluid=PowerLawFluid(1050,.15,.7)
    result=run()
    individual_pipe=power_law_laminar_pipe_pressure_loss(
        fluid,components[0].pipe_or_annulus,1e-4,
        laminar_regime_independently_confirmed=True,
        regime_evidence_id="SYNTHETIC-PIPE-REGIME")["pressure_loss_pa"]
    individual_annulus=power_law_laminar_annulus_pressure_loss(
        fluid,components[2].pipe_or_annulus,1e-4,
        laminar_regime_independently_confirmed=True,
        regime_evidence_id="SYNTHETIC-ANNULUS-REGIME")["pressure_loss_pa"]
    bernoulli=1050/2*(1e-4/(.8*.0002))**2
    assert result["modeled_component_pressure_losses_pa"]==pytest.approx(
        individual_pipe+individual_annulus+bernoulli,rel=1e-10)
    assert result["standpipe_pressure_pa"] is None
    assert result["engineering_acceptance"] is False
    assert result["boundary_coverage"]["complete_actual_tool_restrictions"] is False


def test_n_one_without_nozzle_reduces_to_exact_laminar_newtonian_formula():
    components=[parts()[0],parts()[2]]
    result=run(components=components,n=1)
    ri,ro=.05,.1
    q,L,K=1e-4,10,.15
    pipe=128*K*L*q/(math.pi*.1**4)
    ann=8*K*L*q/(math.pi*(ro**4-ri**4-(ro**2-ri**2)**2/math.log(ro/ri)))
    assert result["modeled_component_pressure_losses_pa"]==pytest.approx(
        pipe+ann,rel=1e-4)


def test_laminar_source_identity_required_for_each_section():
    for invalid in ({}, {"synthetic_pipe":"known"}, {
        "synthetic_pipe":"known","synthetic_annulus":""}, {
        "synthetic_pipe":"known","synthetic_annulus":"known","unknown":"X"}):
        with pytest.raises(HydraulicsUnavailable):
            run(sources=invalid)


def test_missing_return_path_fails_closed():
    with pytest.raises(HydraulicsUnavailable,match="downstream and return"):
        run(components=parts()[:2])


def test_turbulence_unavailable_not_partial_success():
    with pytest.raises(HydraulicsUnavailable):
        run(q=1e200)


def test_reversed_flow_legs_rejected():
    p=parts()
    with pytest.raises(HydraulicsUnavailable,match="downstream before return"):
        run(components=[p[-1],p[0],p[1]])


def test_zero_flow_still_never_claims_spp():
    result=run(q=0)
    assert result["modeled_component_pressure_losses_pa"]==0
    assert result["components_in_flow_order"][-1]["zero_shear_radius_m"] is None
    assert result["standpipe_pressure_pa"] is None
