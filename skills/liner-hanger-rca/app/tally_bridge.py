"""Local-only adapter for the existing source-gated Python BHA tally engine.

This server is an optional calculation bridge for the offline investigation UI.
It never reads local job source files, makes external calls, infers a datum or
turns planned equipment into proof of as-run downhole geometry.
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from bha_tally import TallyError, manual_tally  # noqa: E402

MAX_BODY = 512 * 1024
ALLOWED_ORIGINS = {"null", "http://127.0.0.1:8765", "http://localhost:8765"}
PORT = 8766


def evaluate(payload):
    if not isinstance(payload, dict):
        raise TallyError("Expected a JSON object")
    basis = payload.get("basis")
    if basis != "as_run":
        raise TallyError("Only as_run component lists can be evaluated as actual geometry")
    components = payload.get("components")
    if not isinstance(components, list) or len(components) > 300:
        raise TallyError("Expected 1 to 300 as-run components")
    anchor = payload.get("anchor")
    if not isinstance(anchor, dict):
        raise TallyError("Source-linked component anchor and measured-depth datum required")
    if not anchor.get("reviewer"):
        raise TallyError("Investigator review identity is required")
    if not anchor.get("reviewed"):
        raise TallyError("Explicit investigator source/datum check required")
    tally = manual_tally(
        basis,
        [{
            "component_id": row["component_id"],
            "sequence": row["sequence"],
            "role": row["role"],
            "length": row.get("length"),
            "length_unit": row.get("length_unit"),
            "source_ref": row["source_ref"],
        } for row in components],
        {key: anchor[key] for key in
         ("component_id", "end", "measured_depth", "depth_unit", "datum", "source_ref")},
    )
    boundaries = []
    for row in tally.components:
        top = tally.position_m(row.component_id, "top")
        bottom = tally.position_m(row.component_id, "bottom")
        boundaries.append({
            "component_id": row.component_id,
            "role": row.role,
            "source_ref": row.source_ref,
            "top_md_m": str(top) if top is not None else None,
            "bottom_md_m": str(bottom) if bottom is not None else None,
        })
    return {
        "basis": "as_run",
        "anchor": {key: anchor[key] for key in
                   ("component_id", "end", "measured_depth", "depth_unit", "datum", "source_ref", "reviewer")},
        "boundaries": boundaries,
        "engine": "bha_tally.py/Tally.position_m",
        "review_level": "investigator-declared; independent engineering check outstanding",
        "no_inference": "No string stretch, tool actuation, or running-depth/anchor synchronization",
    }


class Handler(BaseHTTPRequestHandler):
    def _origin_allowed(self):
        origin = self.headers.get("Origin")
        return origin is None or origin in ALLOWED_ORIGINS

    def _respond(self, status, payload):
        raw = json.dumps(payload, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        if self.path != "/v1/tally/positions" or not self._origin_allowed():
            return self._respond(403, {"error": "Origin or path not permitted"})
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin", "null"))
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/v1/tally/positions" or not self._origin_allowed():
            return self._respond(403, {"error": "Origin or path not permitted"})
        try:
            length = int(self.headers.get("Content-Length", "-1"))
            if not 0 <= length <= MAX_BODY:
                return self._respond(413, {"error": "Request body size not supported"})
            payload = json.loads(self.rfile.read(length))
            return self._respond(200, evaluate(payload))
        except (KeyError, ValueError, TypeError, TallyError) as error:
            return self._respond(422, {"error": str(error)})

    def log_message(self, fmt, *args):
        return  # No case data in console logs


def serve(host="127.0.0.1", port=PORT):
    with ThreadingHTTPServer((host, port), Handler) as server:
        print(f"Local tally bridge: http://{host}:{port} (Ctrl+C to stop)", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    serve()
