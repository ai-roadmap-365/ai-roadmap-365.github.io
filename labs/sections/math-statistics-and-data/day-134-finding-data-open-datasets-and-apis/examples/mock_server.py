"""A local mock API for Day 134 -- "Judge the Source Before the Data".

Nothing in this lab talks to the internet. Instead it serves a paginated
dataset, a rate-limited endpoint and an ETag-aware resource over real HTTP
from 127.0.0.1 on an ephemeral port, so the client code you exercise is a
real HTTP client -- it just cannot reach anyone else's machine.

Three endpoints:

* ``GET /dataset?page=N`` -- a paginated JSON collection of ``TOTAL_ROWS``
  rows, ``PAGE_SIZE`` at a time, each page carrying ``has_more`` so a client
  can tell when it has everything without knowing the total in advance.
* ``GET /dataset.csv`` -- the same rows as one CSV document, for the
  ``pandas.read_csv(url)`` demonstration.
* ``GET /ratelimited`` -- returns ``429`` with a ``Retry-After`` header for
  the first ``rate_limit_trigger_count`` requests this server instance has
  seen, then ``200``. Every server carries its own counter, so tests that
  want a source which never relents just ask for a trigger count higher
  than the client's attempt budget.
* ``GET /etag-resource`` -- returns ``200`` with an ``ETag`` header on the
  first request, and ``304`` with an empty body when the caller sends a
  matching ``If-None-Match``.

Standard library only: ``http.server``, ``threading``, ``json``.
"""

from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterator
from urllib.parse import parse_qs, urlparse

PAGE_SIZE = 10
TOTAL_ROWS = 25

ETAG_VALUE = '"d134-etag-v1"'
_ETAG_PAYLOAD = {
    "resource": "codebook",
    "version": 1,
    "fields": {"unemployment_rate": {"unit": "percent"}},
}
ETAG_BODY = json.dumps(_ETAG_PAYLOAD).encode("utf-8")


def _rows(start: int, stop: int) -> list[dict]:
    return [{"id": i, "value": i * 2} for i in range(start, stop)]


@dataclass
class MockAPI:
    """A running mock server plus the log of everything it was asked for."""

    host: str
    port: int
    rate_limit_hits: list[int] = field(default_factory=list)
    request_log: list[str] = field(default_factory=list)

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


def _make_handler(state: dict):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # noqa: A003 - silence stderr access log
            pass

        def do_GET(self) -> None:  # noqa: N802 - name fixed by http.server
            parsed = urlparse(self.path)
            state["log"].append(parsed.path)
            if parsed.path == "/dataset":
                self._dataset(parse_qs(parsed.query))
            elif parsed.path == "/dataset.csv":
                self._dataset_csv()
            elif parsed.path == "/ratelimited":
                self._ratelimited()
            elif parsed.path == "/etag-resource":
                self._etag_resource()
            else:
                self._write(404, b"not found")

        def _write(self, status: int, body: bytes, headers: dict[str, str] | None = None) -> None:
            self.send_response(status)
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def _dataset(self, query: dict[str, list[str]]) -> None:
            page = int(query.get("page", ["1"])[0])
            start = (page - 1) * PAGE_SIZE
            items = _rows(start, min(start + PAGE_SIZE, TOTAL_ROWS))
            has_more = start + PAGE_SIZE < TOTAL_ROWS
            body = json.dumps(
                {"items": items, "page": page, "has_more": has_more, "total": TOTAL_ROWS}
            ).encode("utf-8")
            self._write(200, body, {"Content-Type": "application/json"})

        def _dataset_csv(self) -> None:
            lines = ["id,value"] + [f"{r['id']},{r['value']}" for r in _rows(0, TOTAL_ROWS)]
            body = ("\n".join(lines) + "\n").encode("utf-8")
            self._write(200, body, {"Content-Type": "text/csv"})

        def _ratelimited(self) -> None:
            state["attempts"] += 1
            attempt = state["attempts"]
            if attempt <= state["trigger_count"]:
                state["rate_limit_hits"].append(attempt)
                self._write(429, b"", {"Retry-After": "0"})
                return
            body = json.dumps({"ok": True, "attempt": attempt}).encode("utf-8")
            self._write(200, body, {"Content-Type": "application/json"})

        def _etag_resource(self) -> None:
            if self.headers.get("If-None-Match") == ETAG_VALUE:
                self._write(304, b"", {"ETag": ETAG_VALUE})
                return
            self._write(200, ETAG_BODY, {"Content-Type": "application/json", "ETag": ETAG_VALUE})

    return Handler


@contextmanager
def serve_mock_api(rate_limit_trigger_count: int = 2) -> Iterator[MockAPI]:
    """Serve the mock API on 127.0.0.1 and an ephemeral port for the block.

    ``rate_limit_trigger_count`` is how many requests to ``/ratelimited``
    this instance answers with 429 before it starts answering 200 -- a
    higher count than a test's attempt budget models a source that never
    relents.
    """
    state = {
        "attempts": 0,
        "trigger_count": rate_limit_trigger_count,
        "rate_limit_hits": [],
        "log": [],
    }
    handler = _make_handler(state)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    host, port = httpd.server_address[0], httpd.server_address[1]

    thread = threading.Thread(
        target=httpd.serve_forever, kwargs={"poll_interval": 0.02}, name="d134-mock-api"
    )
    thread.daemon = True
    thread.start()
    try:
        yield MockAPI(
            host=host,
            port=port,
            rate_limit_hits=state["rate_limit_hits"],
            request_log=state["log"],
        )
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":  # A quick manual check of the server itself.
    import urllib.request

    with serve_mock_api() as api:
        with urllib.request.urlopen(f"{api.base_url}/dataset?page=1") as response:
            print("page 1:", response.read().decode()[:80])
        print("requests so far:", api.request_log)
