"""A small paginated JSON API, built only from the standard library.

Everything in this lab talks to THIS server, on the loopback address
127.0.0.1, on a port the operating system picks at run time. Nothing here
opens a connection to the internet, and nothing here needs one.

The server mimics the shape of a real order-history API: customers arrive
one page at a time, each customer carries a list of orders (a one-to-many
nesting), and one field is missing from the early pages and only appears
from page 3 onward -- the schema-drift case this lab detects on purpose.

Endpoints:

  GET /api/customers?page=N&page_size=K
      Page N (1-indexed) of the full customer list, K per page. Answers
      {"page", "page_size", "total_pages", "customers": [...]}.

  GET /api/customers/incremental?since=ISO8601
      Every customer whose updated_at is greater than or equal to `since`
      (inclusive lower bound -- see the lesson for why), sorted by
      updated_at ascending. Answers {"customers": [...], "watermark": ISO}
      where watermark is the updated_at of the last record returned, or
      `since` unchanged if nothing matched.

  GET /control/stats
      {"requests": N} -- how many requests this server has answered since
      the last reset. This is what proves a "replay from raw" step made
      zero additional calls.

  GET /control/reset
      Zeroes the request counter without touching the dataset.

Run it on its own if you want to poke at it by hand:

    python3 examples/api_server.py

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

# The seven-customer dataset. Page 1 and 2 (customers C1-C4) carry no
# `loyalty_tier` field at all -- not null, ABSENT -- and it first appears on
# C5, the first customer on page 3. That absence is what a schema-drift
# detector has to notice: pandas will backfill the missing key as NaN once
# the frame is assembled, and the six earlier rows will look fine unless
# something is watching for exactly this.
CUSTOMERS: list[dict[str, object]] = [
    {
        "customer_id": "C1",
        "name": "Ada Lovelace",
        "updated_at": "2026-01-05T10:00:00Z",
        "total_amount_due": "500.00",
        "orders": [
            {"order_id": "O1", "amount": "200.00", "status": "paid"},
            {"order_id": "O2", "amount": "300.00", "status": "paid"},
        ],
    },
    {
        "customer_id": "C2",
        "name": "Grace Hopper",
        "updated_at": "2026-01-06T10:00:00Z",
        "total_amount_due": "750.00",
        "orders": [{"order_id": "O3", "amount": "750.00", "status": "paid"}],
    },
    {
        "customer_id": "C3",
        "name": "Alan Turing",
        "updated_at": "2026-01-07T10:00:00Z",
        "total_amount_due": "300.00",
        "orders": [
            {"order_id": "O4", "amount": "100.00", "status": "paid"},
            {"order_id": "O5", "amount": "100.00", "status": "refunded"},
            {"order_id": "O6", "amount": "100.00", "status": "paid"},
        ],
    },
    {
        "customer_id": "C4",
        "name": "Katherine Johnson",
        "updated_at": "2026-01-08T10:00:00Z",
        "total_amount_due": "0.00",
        "orders": [],
    },
    {
        "customer_id": "C5",
        "name": "Margaret Hamilton",
        "updated_at": "2026-01-09T10:00:00Z",
        "total_amount_due": "420.00",
        "loyalty_tier": "gold",
        "orders": [{"order_id": "O7", "amount": "420.00", "status": "paid"}],
    },
    {
        "customer_id": "C6",
        "name": "Radia Perlman",
        "updated_at": "2026-01-10T10:00:00Z",
        "total_amount_due": "150.00",
        "loyalty_tier": "silver",
        "orders": [{"order_id": "O8", "amount": "150.00", "status": "paid"}],
    },
    {
        "customer_id": "C7",
        "name": "Hedy Lamarr",
        "updated_at": "2026-01-11T10:00:00Z",
        "total_amount_due": "610.00",
        "loyalty_tier": "gold",
        "orders": [{"order_id": "O9", "amount": "610.00", "status": "paid"}],
    },
]

PAGE_SIZE_DEFAULT = 2


class CountingServer(ThreadingHTTPServer):
    """A threading server that counts every request it answers.

    This counter is what turns "the replay touched no network" from a claim
    into something a test can read back and assert on.
    """

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.requests = 0


class CustomerAPIHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "DayLab/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args) -> None:  # noqa: D102 - silence stderr
        pass

    def version_string(self) -> str:
        return self.server_version

    def _send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        with self.server.lock:
            self.server.requests += 1

        if parsed.path == "/api/customers":
            self._page(query)
        elif parsed.path == "/api/customers/incremental":
            self._incremental(query)
        elif parsed.path == "/control/stats":
            with self.server.lock:
                self._send_json(200, {"requests": self.server.requests})
        elif parsed.path == "/control/reset":
            with self.server.lock:
                self.server.requests = 0
            self._send_json(200, {"requests": 0})
        else:
            self._send_json(404, {"error": "not_found", "path": parsed.path})

    def _page(self, query: dict[str, list[str]]) -> None:
        page = int(query.get("page", ["1"])[0])
        page_size = int(query.get("page_size", [str(PAGE_SIZE_DEFAULT)])[0])
        total_pages = -(-len(CUSTOMERS) // page_size)  # ceiling division
        start = (page - 1) * page_size
        rows = CUSTOMERS[start : start + page_size]
        self._send_json(
            200,
            {"page": page, "page_size": page_size, "total_pages": total_pages, "customers": rows},
        )

    def _incremental(self, query: dict[str, list[str]]) -> None:
        since = query.get("since", ["1970-01-01T00:00:00Z"])[0]
        matched = [c for c in CUSTOMERS if str(c["updated_at"]) >= since]
        matched.sort(key=lambda c: str(c["updated_at"]))
        watermark = str(matched[-1]["updated_at"]) if matched else since
        self._send_json(200, {"customers": matched, "watermark": watermark})


def wait_until_accepting(host: str, port: int, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.25):
                return
        except OSError as exc:
            last_error = exc
            time.sleep(0.01)
    raise RuntimeError(f"the local test server never became ready on port {port}: {last_error}")


@contextlib.contextmanager
def running_server() -> Iterator[CountingServer]:
    """Start the server on an ephemeral port and shut it down afterwards."""
    server = CountingServer(("127.0.0.1", 0), CustomerAPIHandler)
    thread = threading.Thread(target=server.serve_forever, name="api-server", daemon=True)
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
        print(f"serving on {base_url(srv)} -- press Ctrl-C to stop")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nstopped.")
