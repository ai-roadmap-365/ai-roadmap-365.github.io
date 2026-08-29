#!/usr/bin/env python3
"""A local fixture server, so the whole pipeline runs with no internet at all.

It binds 127.0.0.1 on port **0**, which asks the operating system for any free
port, then prints the port it was given on the first line of stdout. Hard-coding
a port is how a test suite collides with whatever the learner already has
running, and the handful of ports tutorials reach for are taken on most
developer machines by lunchtime.

Every route exists to make one pipeline promise testable:

    /stations/alpha/readings    200, five records, two of them deliberately bad
                                and one of them a duplicate of another
    /stations/bravo/readings    500, 500, then 200 — the source that proves a
                                retry actually recovers. The counter is per
                                server process, so the SECOND pipeline run gets
                                a 200 on its first attempt, which is what a
                                transient failure looks like in real life.
    /stations/charlie/readings  500 every single time — the source that must be
                                skipped and reported while the others succeed.
                                Its error body echoes the supplied token back,
                                which is a real and common upstream leak and is
                                why the log redactor in logs.py is not
                                decorative.
    /stations/delta/readings    404 — a source name that is simply wrong.
                                Retrying it would waste three round trips to
                                learn the same thing.
    /health                     200 "ok", used only for the readiness loop.

Every request requires ``Authorization: Bearer <token>`` when a token was given
on the command line, and answers 401 otherwise.

Run it by hand if you like:

    .venv/bin/python examples/fixture_server.py --token demo-token-value

Stop it with Ctrl-C. It serves only 127.0.0.1 and exits when its parent dies.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer

#: The two well-behaved payloads. Every value here is invented.
PAYLOADS: dict[str, dict[str, object]] = {
    "alpha": {
        "station_id": "alpha",
        "records": [
            {
                "station_id": "alpha",
                "reading_id": "a-1",
                "observed_at": "2026-08-16T09:00:00Z",
                "temperature_c": 18.4,
                "humidity_pct": 61,
            },
            {
                "station_id": "alpha",
                "reading_id": "a-2",
                "observed_at": "2026-08-16T10:00:00Z",
                "temperature_c": 19.0,
                "humidity_pct": 58,
            },
            {
                # Malformed: the temperature arrived as prose.
                "station_id": "alpha",
                "reading_id": "a-3",
                "observed_at": "2026-08-16T11:00:00Z",
                "temperature_c": "warm",
                "humidity_pct": 57,
            },
            {
                # Byte-for-byte duplicate of a-2. Valid, so the validation gate
                # passes it; the store's idempotence key is what drops it.
                "station_id": "alpha",
                "reading_id": "a-2",
                "observed_at": "2026-08-16T10:00:00Z",
                "temperature_c": 19.0,
                "humidity_pct": 58,
            },
            {
                # Out of range: humidity is a percentage.
                "station_id": "alpha",
                "reading_id": "a-5",
                "observed_at": "2026-08-16T12:00:00Z",
                "temperature_c": 21.3,
                "humidity_pct": 155,
            },
        ],
    },
    "bravo": {
        "station_id": "bravo",
        "records": [
            {
                "station_id": "bravo",
                "reading_id": "b-1",
                "observed_at": "2026-08-15T23:30:00Z",
                "temperature_c": 12.2,
                "humidity_pct": 80,
            },
            {
                "station_id": "bravo",
                "reading_id": "b-2",
                "observed_at": "2026-08-16T08:15:00Z",
                "temperature_c": 13.6,
                "humidity_pct": 77,
            },
            {
                "station_id": "bravo",
                "reading_id": "b-3",
                "observed_at": "2026-08-16T11:45:00Z",
                "temperature_c": 15.0,
                "humidity_pct": 74,
            },
            {
                # Valid but wrong: 41.3 C is inside every range the gate
                # checks, and it is a 26.3 C jump in five minutes. No
                # field-level rule can catch this one.
                "station_id": "bravo",
                "reading_id": "b-4",
                "observed_at": "2026-08-16T11:50:00Z",
                "temperature_c": 41.3,
                "humidity_pct": 74,
            },
        ],
    },
}

_bravo_hits = 0
_lock = threading.Lock()


def reset_flaky_counter() -> None:
    """Put bravo back to 'fails the next two attempts'. Used by the tests."""
    global _bravo_hits
    with _lock:
        _bravo_hits = 0


class FixtureHandler(BaseHTTPRequestHandler):
    server_version = "pipeline-fixture/1.0"
    token = ""

    def log_message(self, fmt: str, *args: object) -> None:
        """Silence the default per-request line; the pipeline has its own log."""

    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: object) -> None:
        self._send(status, json.dumps(payload).encode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802 - the name is fixed by http.server
        global _bravo_hits

        if self.path == "/health":
            self._send(200, b"ok", "text/plain")
            return

        if self.token:
            supplied = self.headers.get("Authorization", "")
            if supplied != f"Bearer {self.token}":
                self._json(401, {"error": "missing or wrong Authorization header"})
                return

        if not self.path.startswith("/stations/") or not self.path.endswith("/readings"):
            self._json(404, {"error": "not found"})
            return

        name = self.path[len("/stations/") : -len("/readings")]

        if name == "bravo":
            with _lock:
                _bravo_hits += 1
                hits = _bravo_hits
            if hits <= 2:
                self._json(500, {"error": f"station bravo is warming up (attempt {hits})"})
                return
            self._json(200, PAYLOADS["bravo"])
            return

        if name == "charlie":
            # A real upstream leak pattern: the error body echoes the secret.
            self._json(
                500,
                {"error": f"upstream credentials rejected for token {self.token or 'none'}"},
            )
            return

        if name in PAYLOADS:
            self._json(200, PAYLOADS[name])
            return

        self._json(404, {"error": f"no such station: {name}"})


def start_background_server(token: str = "") -> tuple[ThreadingHTTPServer, int]:
    """Start the fixture server on a thread and return it with its port.

    Used by demo_run.py and by the test harness so no second process, and no
    fixed port, is ever needed.
    """
    FixtureHandler.token = token
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Local fixture server for the Day 98 lab.")
    parser.add_argument("--token", default="", help="require this bearer token on every request")
    args = parser.parse_args()

    FixtureHandler.token = args.token
    server = HTTPServer(("127.0.0.1", 0), FixtureHandler)
    print(server.server_address[1], flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
