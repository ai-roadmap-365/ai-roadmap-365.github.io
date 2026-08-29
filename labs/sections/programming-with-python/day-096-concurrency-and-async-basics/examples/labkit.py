"""Shared kit for the Day 096 lab: something that waits, something that
computes, and an honest way to time both.

Standard library only. Nothing here reaches the internet. The "waiting"
work is a small HTTP server bound to the loopback address 127.0.0.1 on an
ephemeral port the operating system chooses, which sleeps a fixed time
before answering. That makes waiting *real* — a socket, a kernel, a
genuine blocked thread — and *reproducible*, because the delay is a
number you set rather than whatever the internet felt like today.

The CPU-bound work is a prime count by trial division. It was chosen for
three properties: it is pure Python, so it holds the interpreter lock; it
is deterministic, so a wrong answer is detectable; and it takes long
enough that process start-up cost does not swamp the measurement.

Every function here is used by at least two of the example scripts, the
starter checker and the test suite.
"""

from __future__ import annotations

import asyncio
import statistics
import threading
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# One tenth of a second per request. Long enough that the waiting dominates
# the measurement, short enough that twenty sequential requests still finish
# in about two seconds.
DEFAULT_DELAY = 0.10

# Trial division below this limit. Calibrated on the authoring machine so a
# single call takes a few hundred milliseconds — long enough that starting a
# process pool is not the thing being measured, short enough that the whole
# test suite still finishes in under a minute. See requirements/README.md.
DEFAULT_PRIME_LIMIT = 500_000

# How many of each kind of unit of work the example scripts use.
WAITING_REQUESTS = 20
COMPUTING_TASKS = 4


# ---------------------------------------------------------------------------
# The waiting half: a fixture server that sleeps, then answers.
# ---------------------------------------------------------------------------


class _WaitHandler(BaseHTTPRequestHandler):
    """Answers any GET after sleeping. The sleep is the whole point."""

    # HTTP/1.0 means the server closes the connection when it has finished
    # writing, so a client can simply read to end-of-stream. That keeps the
    # raw-socket asyncio client in 01_waiting.py down to a dozen lines.
    protocol_version = "HTTP/1.0"

    def do_GET(self) -> None:  # noqa: N802 - name fixed by the base class
        delay = self.server.delay  # type: ignore[attr-defined]
        time.sleep(delay)
        body = f"waited {delay:.3f}s for {self.path}\n".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        """Silence the per-request log line; the measurements are the output."""


class _WaitServer(ThreadingHTTPServer):
    """A threading server, so it can actually answer requests in parallel.

    This matters more than it looks. If the fixture server handled one
    request at a time, every client would measure the SERVER's serialisation
    rather than its own concurrency, and the whole lab would prove nothing.
    """

    daemon_threads = True
    delay = DEFAULT_DELAY


@contextmanager
def fixture_server(delay: float = DEFAULT_DELAY):
    """Run the fixture server for the duration of the block.

    Yields the base URL. Binding to port 0 asks the operating system for a
    free ephemeral port, so two copies of this lab can run at once and
    neither needs a privileged port or a firewall rule.
    """
    server = _WaitServer(("127.0.0.1", 0), _WaitHandler)
    server.delay = delay
    thread = threading.Thread(target=server.serve_forever, name="fixture-server", daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5.0)


def fetch(url: str, timeout: float = 30.0) -> str:
    """Fetch one URL and block until it answers. This is a BLOCKING call."""
    with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310
        return response.read().decode("utf-8")


async def fetch_async(url: str) -> str:
    """Fetch one URL without blocking the event loop.

    Written against raw sockets on purpose. There is no HTTP client in the
    standard library that speaks asyncio, and writing the twelve lines makes
    the point that `await` is where this coroutine gives the loop its turn:
    at the connect, at the drain, and at the read.
    """
    parts = urllib.parse.urlsplit(url)
    host = parts.hostname or "127.0.0.1"
    port = parts.port or 80
    path = parts.path or "/"
    reader, writer = await asyncio.open_connection(host, port)
    request = f"GET {path} HTTP/1.0\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n"
    writer.write(request.encode("ascii"))
    await writer.drain()
    raw = await reader.read()
    writer.close()
    await writer.wait_closed()
    _headers, _sep, body = raw.partition(b"\r\n\r\n")
    return body.decode("utf-8")


def paths(count: int) -> list[str]:
    """The request paths used everywhere in this lab, so counts line up."""
    return [f"/item/{n}" for n in range(1, count + 1)]


def urls(base: str, count: int) -> list[str]:
    return [base + p for p in paths(count)]


# ---------------------------------------------------------------------------
# The computing half: a function that burns CPU and holds the lock.
# ---------------------------------------------------------------------------


def count_primes(limit: int = DEFAULT_PRIME_LIMIT) -> int:
    """Count the primes below `limit` by trial division.

    Deliberately not a sieve. A sieve would be fast and mostly memory-bound;
    this is a tight arithmetic loop in pure Python, which is exactly the
    shape of work that cannot overlap while one interpreter lock exists.
    """
    if limit <= 2:
        return 0
    count = 1  # 2 is prime and is the only even one
    for number in range(3, limit, 2):
        factor = 3
        while factor * factor <= number:
            if number % factor == 0:
                break
            factor += 2
        else:
            count += 1
    return count


# ---------------------------------------------------------------------------
# Measuring, honestly.
# ---------------------------------------------------------------------------


def timed(function, *args, **kwargs) -> tuple[float, object]:
    """Return (elapsed seconds, result). perf_counter is monotonic."""
    start = time.perf_counter()
    result = function(*args, **kwargs)
    return time.perf_counter() - start, result


def repeat(function, times: int = 3) -> tuple[list[float], object]:
    """Run the same thing `times` over and keep every sample.

    One measurement is an anecdote. Three is still a small sample, but it
    shows you the spread, and the spread is the part most benchmarks hide.
    """
    samples: list[float] = []
    result: object = None
    for _ in range(times):
        elapsed, result = timed(function)
        samples.append(elapsed)
    return samples, result


def report(label: str, samples: list[float]) -> float:
    """Print every sample and the median, and return the median.

    The median is the headline because it is the sample least disturbed by
    one unlucky run, and because a mean over three samples with one outlier
    is a lie with a decimal point on it.
    """
    median = statistics.median(samples)
    spread = max(samples) - min(samples)
    runs = ", ".join(f"{s:6.3f}" for s in samples)
    print(f"  {label:<34} runs: {runs}   median {median:6.3f}s   spread {spread:5.3f}s")
    return median


def result_line(name: str, value: float) -> None:
    """One machine-readable line the test suite can parse."""
    print(f"RESULT {name} {value:.4f}")


def shape_line(name: str, holds: bool, detail: str) -> None:
    """The claim that has to survive on another machine: a SHAPE, not a time."""
    print(f"SHAPE {name} {'yes' if holds else 'no'}   ({detail})")
