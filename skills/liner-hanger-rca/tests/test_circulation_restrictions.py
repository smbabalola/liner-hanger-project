"""Independent orifice/nozzle physics in a fictional hydraulic circuit."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from circulation_restrictions import NozzleOrifice, nozzle_orifice_loss
from circulating_hydraulics import HydraulicsUnavailable


def nozzle(area=.0002,cd=.8):
    return NozzleOrifice("fictional_nozzle",area,cd,"SYNTHETIC-CALIBRATION-ONLY")


def test_independent_incompressible_orifice_known_answer():
    # Rearranged public Bernoulli orifice equation:
    # Q = Cd A sqrt(2*dP/rho). With dP=12500 Pa, rho=1000,
    # Cd=0.8, A=0.0002 m2, Q=0.0008 m3/s.
    rho,dp_target,cd,area=1000.,12500.,.8,.0002
    q=cd*area*math.sqrt(2*dp_target/rho)
    result=nozzle_orifice_loss(rho,nozzle(area,cd),q)
    assert result["pressure_loss_pa"]==pytest.approx(dp_target,rel=1e-12)
    assert result["coefficient_source_id"]=="SYNTHETIC-CALIBRATION-ONLY"
    assert result["standpipe_pressure_pa"] is None
    assert result["engineering_acceptance"] is False


def test_orifice_pressure_quadruples_with_double_flow():
    a=nozzle_orifice_loss(1000,nozzle(),.0001)
    b=nozzle_orifice_loss(1000,nozzle(),.0002)
    assert b["pressure_loss_pa"]==pytest.approx(4*a["pressure_loss_pa"])


def test_orifice_density_and_area_sensitivity():
    a=nozzle_orifice_loss(1000,nozzle(),.0001)
    b=nozzle_orifice_loss(1200,nozzle(area=.0004),.0001)
    assert b["pressure_loss_pa"]==pytest.approx(.3*a["pressure_loss_pa"])


def test_zero_flow_is_zero_nozzle_dynamic_loss():
    assert nozzle_orifice_loss(1000,nozzle(),0)["pressure_loss_pa"]==0


@pytest.mark.parametrize("area", [0,-1,float("nan"),float("inf"),True])
def test_unsupported_orifice_area_fails_closed(area):
    with pytest.raises(HydraulicsUnavailable):
        nozzle(area=area)


@pytest.mark.parametrize("cd", [0,-.1,1.01,float("nan"),float("inf"),True])
def test_unsupported_discharge_coefficient_fails_closed(cd):
    with pytest.raises(HydraulicsUnavailable):
        nozzle(cd=cd)


def test_missing_source_or_non_supported_geometry_rejected():
    with pytest.raises(HydraulicsUnavailable,match="sourced"):
        NozzleOrifice("n",.0002,.8,"")
    with pytest.raises(HydraulicsUnavailable,match="geometry"):
        NozzleOrifice("n",.0002,.8,"fictional",geometry="jet-impingement")


@pytest.mark.parametrize("q",[-1,True,".1",float("nan"),float("inf")])
def test_unsupported_flow_fails_closed(q):
    with pytest.raises(HydraulicsUnavailable):
        nozzle_orifice_loss(1000,nozzle(),q)


def test_extreme_finite_orifice_flow_fails_closed_without_python_overflow():
    with pytest.raises(HydraulicsUnavailable,match="overflow|nonfinite"):
        nozzle_orifice_loss(1000,nozzle(),1e200)
