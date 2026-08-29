#!/usr/bin/env python3
"""A local fixture server, so the whole lab runs with no internet at all.

It binds 127.0.0.1 on port **0**, which asks the operating system for any free
port, then prints the port it was given on the first line of stdout. The test
harness reads that line. Hard-coding a port is how a test suite collides with
whatever the learner already has running, and the handful of ports that
tutorials reach for by default are taken on most developer machines by
lunchtime.

Behaviour, chosen so the harness can prove the toolkit's failure design:

    /feed/notes.json      200, from tests/fixtures/feed/
    /feed/links.json      200
    /feed/papers.json     200
    /feed/malformed.json  200 with a body that is valid JSON but the wrong
                          shape — the case a status code cannot warn you about
    /feed/broken.json     500 every single time — the source that must be
                          skipped and reported while the others still succeed
    /feed/flaky.json      503, 503, then 200 — the source that proves retry
                          with backoff actually recovers
    /health               200 "ok", used only for the readiness loop

Every request requires `Authorization: Bearer <token>` when a token was given
on the command line, and answers 401 otherwise. That is what makes the secret
in this lab real rather than decorative: if redaction were achieved by simply
never sending the token, the leak test would prove nothing.

Run it by hand if you like:

    python3 tests/fixture_server.py --token demo-token-value

Stop it with Ctrl-C. It is single-threaded, serves only 127.0.0.1, and exits
when its parent harness kills it.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "feed"

#: How many times /feed/flaky.json has been asked for, this process.
_flaky_hits = 0
_lock = threading.Lock()


class FixtureHandler(BaseHTTPRequestHandler):
    server_version = "feedkit-fixture/1.0"
    token = ""

    def log_message(self, fmt: str, *args: object) -> None:
        """Silence the default per-request line on stderr; the harness has its
        own output and a wall of request logs helps nobody."""

    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: object) -> None:
        self._send(status, json.dumps(payload).encode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802 - the name is fixed by http.server
        global _flaky_hits

        if self.path == "/health":
            self._send(200, b"ok", "text/plain")
            return

        if self.token:
            supplied = self.headers.get("Authorization", "")
            if supplied != f"Bearer {self.token}":
                self._json(401, {"error": "missing or wrong Authorization header"})
                return

        if self.path == "/feed/broken.json":
            self._json(500, {"error": "this source is broken on purpose"})
            return

        if self.path == "/feed/flaky.json":
            with _lock:
                _flaky_hits += 1
                hits = _flaky_hits
            if hits < 3:
                self._json(503, {"error": f"temporarily unavailable (attempt {hits})"})
                return
            self._json(
                200,
                {
                    "source": "flaky",
                    "entries": [
                        {
                            "id": "f-001",
                            "title": "Recovered on the third attempt",
                            "published": "2026-07-11T07:00:00Z",
                        }
                    ],
                },
            )
            return

        if self.path.startswith("/feed/") and self.path.endswith(".json"):
            name = self.path[len("/feed/") : -len(".json")]
            candidate = FIXTURES / f"{name}.json"
            # Refuse anything that escapes the fixture directory.
            if candidate.resolve().parent != FIXTURES.resolve() or not candidate.is_file():
                self._json(404, {"error": f"no such source: {name}"})
                return
            self._send(200, candidate.read_bytes())
            return

        self._json(404, {"error": "not found"})


def main() -> int:
    parser = argparse.ArgumentParser(description="Local fixture server for the Day 84 lab.")
    parser.add_argument("--token", default="", help="require this bearer token on every request")
    args = parser.parse_args()

    FixtureHandler.token = args.token
    # Port 0 means "any free port"; the kernel picks and we read it back.
    server = HTTPServer(("127.0.0.1", 0), FixtureHandler)
    port = server.server_address[1]

    # First line of stdout is the contract with the harness.
    print(port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
