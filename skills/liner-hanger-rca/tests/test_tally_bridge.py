"""Tests of the real Python tally adapter, not a reimplementation of tally math."""
import importlib.util
import json
import threading
from decimal import Decimal
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

BRIDGE_FILE = Path(__file__).resolve().parents[1] / "app" / "tally_bridge.py"
spec = importlib.util.spec_from_file_location("real_tally_bridge", BRIDGE_FILE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


def case():
    return {
        "basis": "as_run",
        "components": [
            {"component_id": "DP-1", "sequence": 1, "role": "drill_pipe",
             "length": 2, "length_unit": "m", "source_ref": "TALLY-A p.1"},
            {"component_id": "RT-1", "sequence": 2, "role": "running_tool",
             "length": 10, "length_unit": "ft", "source_ref": "TALLY-A p.2"},
            {"component_id": "LINER-1", "sequence": 3, "role": "liner",
             "length": None, "length_unit": None, "source_ref": "TALLY-A p.3"},
        ],
        "anchor": {"component_id": "RT-1", "end": "bottom",
                   "measured_depth": "1000", "depth_unit": "m",
                   "datum": "RKB", "source_ref": "TALLY-A p.2",
                   "reviewer": "Test engineer", "reviewed": True},
    }


def test_engine_adapter_real_decimal_math_and_unresolved_length():
    output = bridge.evaluate(case())
    dp, rt, liner = output["boundaries"]
    assert Decimal(rt["bottom_md_m"]) == 1000
    assert Decimal(rt["top_md_m"]) == Decimal("996.9520")
    assert Decimal(dp["bottom_md_m"]) == Decimal(rt["top_md_m"])
    assert Decimal(dp["top_md_m"]) == Decimal("994.9520")
    assert Decimal(liner["top_md_m"]) == 1000
    assert liner["bottom_md_m"] is None
    assert output["review_level"].startswith("investigator-declared")
    assert output["engine"] == "bha_tally.py/Tally.position_m"


@pytest.mark.parametrize("mutation", [
    lambda p: p.update(basis="planned"),
    lambda p: p["anchor"].update(reviewed=False),
    lambda p: p["anchor"].update(reviewer=""),
    lambda p: p["anchor"].update(datum=""),
    lambda p: p["anchor"].update(component_id="UNLISTED"),
    lambda p: p["components"][1].update(length_unit=None),
    lambda p: p["components"][1].update(length=-10),
])
def test_engine_adapter_rejects_untrusted_geometry(mutation):
    payload = case()
    mutation(payload)
    with pytest.raises((bridge.TallyError, KeyError, TypeError)):
        bridge.evaluate(payload)


def test_loopback_api_and_origin_gate():
    server = ThreadingHTTPServer(("127.0.0.1", 0), bridge.Handler)
    runner = threading.Thread(target=server.serve_forever, daemon=True)
    runner.start()
    endpoint = f"http://127.0.0.1:{server.server_port}/v1/tally/positions"
    body = json.dumps(case()).encode()
    try:
        request = Request(endpoint, body, {"Content-Type": "application/json",
                                          "Origin": "null"})
        with urlopen(request, timeout=5) as response:
            result = json.load(response)
            assert response.headers["Access-Control-Allow-Origin"] == "null"
            assert Decimal(result["boundaries"][1]["bottom_md_m"]) == 1000
        forbidden = Request(endpoint, body, {"Content-Type": "application/json",
                                             "Origin": "https://attacker.example"})
        with pytest.raises(HTTPError) as exc:
            urlopen(forbidden, timeout=5)
        assert exc.value.code == 403
        bad = case()
        bad["anchor"]["reviewed"] = False
        rejected = Request(endpoint, json.dumps(bad).encode(), {"Content-Type": "application/json"})
        with pytest.raises(HTTPError) as exc:
            urlopen(rejected, timeout=5)
        assert exc.value.code == 422
    finally:
        server.shutdown()
        server.server_close()
        runner.join(timeout=5)
