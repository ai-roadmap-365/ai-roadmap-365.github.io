"""A small HTTP server you control, built only from the standard library.

Everything in this lab talks to THIS server, on the loopback address
127.0.0.1, on a port the operating system picks at run time. Nothing here
opens a connection to the internet, and nothing here needs one.

Why a local server instead of a real public API:

  * it is fast — no DNS lookup, no round trip across the world;
  * it is deterministic — the same bytes every run, so a test can assert;
  * it is honest — you can ask it for a 500, a 429 or a two-second delay,
    and no real service has to be harmed to produce them;
  * it works on a plane, and it will still work in five years.

The endpoints exist to produce the interesting cases:

  GET  /api/readings          200 with a JSON body
  GET  /api/readings?station= 200, filtered; also echoes the parsed query
  GET  /api/missing           404 with a JSON error body
  GET  /api/broken            500 with a JSON error body
  GET  /old/readings          301 permanent redirect to /api/readings
  GET  /api/flaky             429 with Retry-After for the first N calls,
                              then 200 (call /control/reset to arm it)
  GET  /api/slow?seconds=2    sleeps, then 200 — lets a timeout really fire
  GET  /api/large?kb=512      a large body, for streaming
  POST /api/echo              echoes method, headers and body back as JSON
  GET  /control/reset?fail=2  arms the flaky endpoint, resets counters
  GET  /control/stats         how many TCP connections and requests so far

Run it on its own if you want to poke at it by hand:

    python3 examples/demo_server.py

It prints the address it bound to and serves until you press Ctrl-C.
"""

from __future__ import annotations

import contextlib
import json
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterator
from urllib.parse import parse_qs, urlparse

READINGS: list[dict[str, object]] = [
    {"station": "ALPHA", "hour": 0, "celsius": 12.0},
    {"station": "ALPHA", "hour": 6, "celsius": 14.0},
    {"station": "ALPHA", "hour": 12, "celsius": 20.0},
    {"station": "ALPHA", "hour": 18, "celsius": 22.0},
    {"station": "BRAVO", "hour": 0, "celsius": 3.0},
    {"station": "BRAVO", "hour": 12, "celsius": 9.0},
]


class CountingServer(ThreadingHTTPServer):
    """A threading server that counts the TCP connections it accepts.

    The connection count is what makes "a Session reuses one connection"
    something a test can PROVE rather than something a lesson asserts.
    `get_request` is called once per accepted connection, not once per
    request, so the two numbers diverge exactly when keep-alive works.
    """

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.connections = 0
        self.requests = 0
        self.flaky_remaining = 0
        self.flaky_calls = 0

    def get_request(self):  # noqa: D102 - inherited contract
        conn, addr = super().get_request()
        with self.lock:
            self.connections += 1
        return conn, addr


class DemoHandler(BaseHTTPRequestHandler):
    # HTTP/1.1 is what makes keep-alive possible. With HTTP/1.0 the server
    # closes after every response and connection reuse cannot be shown.
    protocol_version = "HTTP/1.1"
    server_version = "DayLab/1.0"
    sys_version = ""

    # ---- plumbing ---------------------------------------------------------

    def log_message(self, fmt: str, *args) -> None:
        """Silence the default stderr access log; tests want clean output."""

    def version_string(self) -> str:
        """The Server header. Kept short and stable so captures are diffable."""
        return self.server_version

    def _send(
        self,
        status: int,
        body: bytes,
        content_type: str = "application/json",
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(
        self,
        status: int,
        payload: object,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, indent=None, separators=(",", ":")).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8", extra_headers)

    # ---- routing ----------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        with self.server.lock:
            self.server.requests += 1

        if parsed.path == "/api/readings":
            self._readings(query)
        elif parsed.path == "/api/search":
            # Echoes the query string exactly as the server parsed it. This
            # is how you see what your client really sent, which is the
            # whole argument for `params=` over string concatenation.
            self._send_json(200, {"raw_query": parsed.query, "parsed": dict(query)})
        elif parsed.path == "/api/missing":
            self._send_json(
                404,
                {"error": "not_found", "detail": "no such station", "path": parsed.path},
            )
        elif parsed.path == "/api/broken":
            self._send_json(500, {"error": "internal", "detail": "the server fell over"})
        elif parsed.path == "/old/readings":
            self._send(
                301,
                b"",
                "text/plain; charset=utf-8",
                {"Location": "/api/readings"},
            )
        elif parsed.path == "/api/flaky":
            self._flaky()
        elif parsed.path == "/api/slow":
            time.sleep(float(query.get("seconds", ["2"])[0]))
            self._send_json(200, {"slept": float(query.get("seconds", ["2"])[0])})
        elif parsed.path == "/api/large":
            self._large(query)
        elif parsed.path == "/control/reset":
            with self.server.lock:
                self.server.flaky_remaining = int(query.get("fail", ["2"])[0])
                self.server.flaky_calls = 0
            self._send_json(200, {"flaky_remaining": self.server.flaky_remaining})
        elif parsed.path == "/control/stats":
            with self.server.lock:
                stats = {
                    "connections": self.server.connections,
                    "requests": self.server.requests,
                    "flaky_calls": self.server.flaky_calls,
                }
            self._send_json(200, stats)
        else:
            self._send_json(404, {"error": "not_found", "path": parsed.path})

    def do_POST(self) -> None:  # noqa: N802 - name fixed by the base class
        parsed = urlparse(self.path)
        with self.server.lock:
            self.server.requests += 1
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""

        if parsed.path != "/api/echo":
            self._send_json(404, {"error": "not_found", "path": parsed.path})
            return

        try:
            parsed_body: object = json.loads(raw.decode("utf-8")) if raw else None
        except json.JSONDecodeError:
            parsed_body = None

        self._send_json(
            201,
            {
                "method": "POST",
                "path": parsed.path,
                "content_type": self.headers.get("Content-Type"),
                "user_agent": self.headers.get("User-Agent"),
                "authorization_seen": self.headers.get("Authorization") is not None,
                "body_bytes": length,
                "json": parsed_body,
            },
        )

    # ---- individual endpoints --------------------------------------------

    def _readings(self, query: dict[str, list[str]]) -> None:
        station = query.get("station", [None])[0]
        known = {str(r["station"]) for r in READINGS}
        if station is not None and station not in known:
            self._send_json(
                404,
                {
                    "error": "not_found",
                    "detail": f"no station named {station}",
                    "known": sorted(known),
                },
            )
            return
        rows = [r for r in READINGS if station is None or r["station"] == station]
        self._send_json(
            200,
            {
                "station": station,
                "count": len(rows),
                "query_seen": {k: v for k, v in query.items()},
                "readings": rows,
            },
        )

    def _flaky(self) -> None:
        with self.server.lock:
            self.server.flaky_calls += 1
            attempt = self.server.flaky_calls
            if self.server.flaky_remaining > 0:
                self.server.flaky_remaining -= 1
                remaining = self.server.flaky_remaining
                rate_limited = True
            else:
                remaining = 0
                rate_limited = False
        if rate_limited:
            self._send_json(
                429,
                {"error": "rate_limited", "attempt": attempt, "still_failing": remaining},
                {"Retry-After": "1"},
            )
        else:
            self._send_json(200, {"ok": True, "attempt": attempt})

    def _large(self, query: dict[str, list[str]]) -> None:
        kilobytes = int(query.get("kb", ["512"])[0])
        # A repeating 1 KiB line, so the body is large but perfectly
        # predictable: every byte is derivable from `kb`.
        line = (b"x" * 1023) + b"\n"
        body = line * kilobytes
        self._send(200, body, "text/plain; charset=utf-8")


def wait_until_accepting(host: str, port: int, timeout: float = 5.0) -> None:
    """Poll the port until a connection succeeds, or give up loudly.

    This is the readiness loop that replaces `time.sleep(1)`. A fixed sleep
    is both too slow (usually) and too short (sometimes), which is the
    recipe for a test that fails once a fortnight on a loaded machine.
    """
    deadline = time.monotonic() + timeout
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.25):
                return
        except OSError as exc:  # not up yet
            last_error = exc
            time.sleep(0.01)
    raise RuntimeError(f"the local test server never became ready on port {port}: {last_error}")


@contextlib.contextmanager
def running_server() -> Iterator[CountingServer]:
    """Start the server on an ephemeral port and shut it down afterwards.

    Binding port 0 asks the operating system for any free port, which is the
    only way to avoid colliding with whatever the learner already has
    running. The real port is read back from `server_address` afterwards.
    """
    server = CountingServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, name="demo-server", daemon=True)
    thread.start()
    try:
        wait_until_accepting(*server.server_address[:2])
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def base_url(server: CountingServer) -> str:
    host, port = server.server_address[:2]
    return f"http://{host}:{port}"


if __name__ == "__main__":
    with running_server() as srv:
        print(f"serving on {base_url(srv)} — press Ctrl-C to stop")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nstopped.")
