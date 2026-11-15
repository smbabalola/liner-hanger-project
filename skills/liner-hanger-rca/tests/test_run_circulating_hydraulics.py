"""Restricted circulating hydraulics CLI schema and example tests."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from circulating_hydraulics import HydraulicsUnavailable
from run_circulating_hydraulics import main, run_payload


def case():
    return json.loads((ROOT / "examples" / "synthetic_laminar_circuit.json")
                      .read_text(encoding="utf-8"))


def test_restricted_synthetic_example():
    result = run_payload(case())
    assert result["status"] == "partial_circuit_friction_only"
    assert result["standpipe_pressure_pa"] is None
    assert len(result["segments"]) == 2
    assert result["modeled_straight_segment_friction_pa"] > 0


def test_cli_prints_json(capsys):
    assert main([str(ROOT / "examples" / "synthetic_laminar_circuit.json")]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["standpipe_pressure_pa"] is None


def test_cli_file_output(tmp_path):
    out = tmp_path / "result.json"
    assert main([str(ROOT / "examples" / "synthetic_laminar_circuit.json"),
                 "--output", str(out)]) == 0
    assert json.loads(out.read_text())["engineering_acceptance"] is False


@pytest.mark.parametrize("field", ["fluid", "flow_m3_s", "segments"])
def test_missing_required_top_field_rejected(field):
    x = case()
    del x[field]
    with pytest.raises(HydraulicsUnavailable):
        run_payload(x)


def test_extra_field_rejected():
    x = case()
    x["standpipe_pressure_pa"] = 500000
    with pytest.raises(HydraulicsUnavailable):
        run_payload(x)


def test_unknown_fluid_field_rejected():
    x = case()
    x["fluid"]["yield_point"] = 15
    with pytest.raises(HydraulicsUnavailable):
        run_payload(x)


def test_unknown_segment_field_rejected():
    x = case()
    x["segments"][0]["bit_nozzle_loss"] = 10
    with pytest.raises(HydraulicsUnavailable):
        run_payload(x)


def test_empty_segments_rejected():
    x = case()
    x["segments"] = []
    with pytest.raises(HydraulicsUnavailable):
        run_payload(x)


def test_cli_rejects_malformed_json(tmp_path, capsys):
    inp = tmp_path / "bad.json"
    inp.write_text("{")
    assert main([str(inp)]) == 2
    assert "unavailable" in capsys.readouterr().err


def test_cli_rejects_turbulent_input(tmp_path, capsys):
    x = case()
    x["flow_m3_s"] = 1
    inp = tmp_path / "turbulent.json"
    inp.write_text(json.dumps(x))
    assert main([str(inp)]) == 2
    assert "laminar-only" in capsys.readouterr().err
