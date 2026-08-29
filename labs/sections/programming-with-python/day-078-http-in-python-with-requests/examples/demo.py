"""The whole lab in one run: eight sections, one local server, no internet.

    python3 examples/demo.py

Each section is one of the operational points from the lesson, demonstrated
rather than asserted. Read the timings — they are where the argument lives.
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from client import (  # noqa: E402
    DEFAULT_TIMEOUT,
    StationNotFound,
    backoff_delays,
    describe_failure,
    fetch_readings,
    get_with_retry,
    make_session,
    stream_to_file,
    summarise,
)
from demo_server import base_url, running_server  # noqa: E402


class RecordingSleep:
    """A spy, straight out of Day 74. It records waits and never waits."""

    def __init__(self) -> None:
        self.waits: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.waits.append(round(seconds, 4))


def section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def main() -> int:
    with running_server() as server:
        root = base_url(server)
        session = make_session()

        section("1. A request and a response, in the pieces that matter")
        response = session.get(
            f"{root}/api/readings", params={"station": "ALPHA"}, timeout=DEFAULT_TIMEOUT
        )
        print(f"  request method   : {response.request.method}")
        print(f"  request path     : {response.request.path_url}")
        print(f"  request headers  : {len(response.request.headers)} sent")
        print(f"  status code      : {response.status_code} {response.reason}")
        print(f"  content type     : {response.headers['Content-Type']}")
        print(f"  .content is      : {type(response.content).__name__}, {len(response.content)} bytes")
        print(f"  .text is         : {type(response.text).__name__}, {len(response.text)} characters")
        print(f"  .json() is       : {type(response.json()).__name__} with keys {sorted(response.json())}")
        print(f"  elapsed          : {response.elapsed.total_seconds():.4f}s")

        section("2. params= versus gluing strings together")
        awkward = "ALPHA ONE&station=BRAVO"
        good = session.get(f"{root}/api/search", params={"station": awkward}, timeout=DEFAULT_TIMEOUT)
        bad = session.get(f"{root}/api/search?station={awkward}", timeout=DEFAULT_TIMEOUT)
        print(f"  station value    : {awkward!r}")
        print(f"  params=          : {good.request.path_url}")
        print(f"    server parsed  : {good.json()['parsed']}")
        print(f"  f-string         : {bad.request.path_url}")
        print(f"    server parsed  : {bad.json()['parsed']}")
        print("  the f-string smuggled a second parameter in. params= encoded it.")

        section("3. Status codes: a 404 is a successful response")
        missing = session.get(f"{root}/api/missing", timeout=DEFAULT_TIMEOUT)
        print(f"  the call itself  : returned normally, no exception")
        print(f"  status_code      : {missing.status_code}")
        print(f"  bool(response)   : {bool(missing)}   <- False for 4xx and 5xx")
        print(f"  described        : {describe_failure(missing)}")
        try:
            missing.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            print(f"  raise_for_status : {type(exc).__name__}: {str(exc).split(' for url')[0]}")
        try:
            fetch_readings(root, "NOWHERE", session=session)
        except StationNotFound as exc:
            print(f"  the client raises: StationNotFound: {exc}")

        section("4. A redirect, followed and unfollowed")
        followed = session.get(f"{root}/old/readings", timeout=DEFAULT_TIMEOUT)
        print(f"  final status     : {followed.status_code}")
        print(f"  final url path   : {followed.url.rsplit('/', 1)[-1]}")
        print(f"  history          : {[r.status_code for r in followed.history]}")
        raw = session.get(f"{root}/old/readings", timeout=DEFAULT_TIMEOUT, allow_redirects=False)
        print(f"  unfollowed       : {raw.status_code}, Location: {raw.headers['Location']}")
        print("  301 is permanent — a client may cache it. 302 is temporary.")

        section("5. The timeout that is not there by default")
        started = time.monotonic()
        try:
            session.get(f"{root}/api/slow", params={"seconds": 3}, timeout=(3.05, 0.5))
        except requests.exceptions.Timeout as exc:
            waited = time.monotonic() - started
            print(f"  asked for        : 3 seconds of server work")
            print(f"  read timeout     : 0.5s")
            print(f"  raised after     : {waited:.2f}s — {type(exc).__name__}")
        print("  with no timeout= at all, that call waits for the full 3s, and")
        print("  against a server that never answers it waits forever.")

        section("6. Retry with backoff — and what must never be retried")
        session.get(f"{root}/control/reset", params={"fail": 2}, timeout=DEFAULT_TIMEOUT)
        sleeper = RecordingSleep()
        started = time.monotonic()
        result = get_with_retry(
            f"{root}/api/flaky",
            session=session,
            attempts=4,
            sleep=sleeper,
            jitter=lambda: 1.0,
        )
        print(f"  server sent      : 429, 429, then 200")
        print(f"  final status     : {result.status_code} on attempt {result.json()['attempt']}")
        print(f"  waits requested  : {sleeper.waits}  (Retry-After: 1 overrode the schedule)")
        print(f"  real time taken  : {time.monotonic() - started:.3f}s — the sleep was injected")
        print(f"  schedule alone   : {backoff_delays(5, jitter=lambda: 1.0)}")
        print(f"  with half jitter : {backoff_delays(5, jitter=lambda: 0.0)}")
        not_retried = session.get(f"{root}/api/missing", timeout=DEFAULT_TIMEOUT)
        print(f"  404 retryable?   : {not_retried.status_code in {429, 500, 502, 503, 504}}")
        print("  a 404 will be a 404 on the tenth try. Retrying it is a bug.")

        section("7. Session and connection reuse")
        before = server.connections
        with requests.Session() as pooled:
            for _ in range(5):
                pooled.get(f"{root}/api/readings", timeout=DEFAULT_TIMEOUT).close()
        with_session = server.connections - before
        before = server.connections
        for _ in range(5):
            requests.get(f"{root}/api/readings", timeout=DEFAULT_TIMEOUT).close()
        without_session = server.connections - before
        print(f"  5 calls, one Session      : {with_session} TCP connection(s)")
        print(f"  5 calls, requests.get()   : {without_session} TCP connection(s)")
        print("  each extra connection is a handshake — and, over TLS, several.")

        section("8. Streaming a large body instead of loading it")
        with tempfile.TemporaryDirectory() as tmp:
            destination = str(Path(tmp) / "large.txt")
            total, chunks, digest = stream_to_file(
                f"{root}/api/large?kb=512", destination, session=session, chunk_size=8192
            )
            print(f"  bytes written    : {total}")
            print(f"  chunks read      : {chunks} of at most 8192 bytes")
            print(f"  peak held        : one chunk, not {total} bytes")
            print(f"  sha256           : {digest[:32]}...")
        readings = fetch_readings(root, "ALPHA", session=session)
        print(f"  and the summary  : {summarise(readings)}")
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
