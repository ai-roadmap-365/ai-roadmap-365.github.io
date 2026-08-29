"""The reference client — the shape every HTTP call in this course will take.

Three rules are baked into every function here, and they are the three that
separate a script from something you can leave running:

  1. Every request has a TIMEOUT. `requests` has no default one. A call
     without a timeout can wait forever on a socket that will never answer,
     and "forever" is not an exaggeration.
  2. Every function takes its `session` as a PARAMETER. That is Day 74's
     boundary argument applied to the network: a function that calls
     `requests.get` directly can only be tested with a real server or a
     patch, while a function that takes a session can be tested with a
     fifteen-line fake and no server at all.
  3. Retries are only for the failures worth retrying — 429 and 5xx. A 400,
     a 401 or a 404 will give the same answer however many times you ask.

Nothing here knows anything about a particular host. `base_url` is passed
in, which is why the same client works against the local test server and
would work against a real API.
"""

from __future__ import annotations

import hashlib
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Protocol

import requests

# 10 seconds to finish reading the body, 3.05 to get the connection open.
# The odd 3.05 is the documented habit: connect timeouts slightly larger
# than a multiple of 3 line up with the TCP retransmission window.
DEFAULT_TIMEOUT: tuple[float, float] = (3.05, 10.0)

# The families worth trying again. Everything else is a permanent answer.
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


class ReadingsError(Exception):
    """Base class for everything this client raises on purpose."""


class ReadingsUnavailable(ReadingsError):
    """The server could not be reached, or kept failing."""


class StationNotFound(ReadingsError):
    """The server answered clearly: there is no such station."""


class HttpSession(Protocol):
    """The slice of `requests.Session` this client actually uses.

    Writing the boundary down as a Protocol costs three lines and buys two
    things: mypy checks that a fake really implements it, and a reader can
    see exactly how much of `requests` the code depends on.
    """

    def get(self, url: str, **kwargs: Any) -> Any: ...

    def post(self, url: str, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class Reading:
    station: str
    hour: int
    celsius: float


def make_session(user_agent: str = "day078-lab/1.0 (course exercise)") -> requests.Session:
    """A Session with the headers every request from this client should carry.

    A Session is two things at once: a place to put shared configuration,
    and a pool of open TCP connections. The second is the one people forget,
    and it is worth roughly the whole cost of the handshake per request.
    """
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }
    )
    token = os.environ.get("READINGS_TOKEN")
    if token:
        # Read from the environment, never written in the file. A token in
        # source control is a token you have to rotate.
        session.headers["Authorization"] = f"Bearer {token}"
    return session


def fetch_readings(
    base_url: str,
    station: str,
    *,
    session: HttpSession,
    timeout: tuple[float, float] | float = DEFAULT_TIMEOUT,
) -> list[Reading]:
    """Fetch one station's readings. The whole point is the `session=` parameter.

    Note `params=` rather than string concatenation. `requests` percent-encodes
    the values for you, so a station called `ALPHA ONE&BRAVO` produces a legal
    URL instead of a second query parameter you did not mean to send.
    """
    response = session.get(
        f"{base_url}/api/readings",
        params={"station": station},
        timeout=timeout,
    )
    if response.status_code == 404:
        raise StationNotFound(f"no station named {station!r}")
    response.raise_for_status()
    payload = response.json()
    return [
        Reading(station=row["station"], hour=int(row["hour"]), celsius=float(row["celsius"]))
        for row in payload["readings"]
    ]


def describe_failure(response: Any) -> str:
    """Turn a failed response into one sentence a human can act on.

    A traceback is for the programmer. This is for the person running the
    program, and it is the difference between "it crashed" and "the server
    said the station does not exist".
    """
    families = {
        3: "redirection",
        4: "your request was rejected",
        5: "the server failed",
    }
    family = families.get(response.status_code // 100, "unexpected status")
    detail = ""
    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("application/json"):
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict) and "detail" in body:
            detail = f" — {body['detail']}"
        elif isinstance(body, dict) and "error" in body:
            detail = f" — {body['error']}"
    return f"HTTP {response.status_code} ({family}){detail}"


def backoff_delays(
    attempts: int,
    *,
    base: float = 0.5,
    cap: float = 8.0,
    jitter: Callable[[], float] = random.random,
) -> list[float]:
    """The waits between `attempts` tries: exponential, capped, with jitter.

    The jitter is not decoration. Without it, a hundred clients that all saw
    the same outage retry at the same instant, and the server that was
    recovering is knocked over again by a synchronised wave. `jitter` is a
    parameter so a test can pass `lambda: 0.0` and assert exact numbers.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    delays = []
    for i in range(attempts - 1):
        raw = min(cap, base * (2**i))
        delays.append(round(raw * (0.5 + 0.5 * jitter()), 4))
    return delays


def get_with_retry(
    url: str,
    *,
    session: HttpSession,
    attempts: int = 4,
    timeout: tuple[float, float] | float = DEFAULT_TIMEOUT,
    sleep: Callable[[float], None] = time.sleep,
    jitter: Callable[[], float] = random.random,
    params: dict[str, Any] | None = None,
) -> Any:
    """GET with retries on 429 and 5xx — and on nothing else.

    `sleep` and `jitter` arrive as parameters for exactly the reason Day 74
    gave: a test can pass a recording sleep and prove the schedule in
    microseconds, without anything ever waiting.
    """
    delays = backoff_delays(attempts, jitter=jitter)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, params=params, timeout=timeout)
        except requests.exceptions.RequestException as exc:
            # A transport-level failure: DNS, connection refused, timeout.
            # There is no status code here because there is no response.
            last_error = exc
        else:
            if response.status_code not in RETRY_STATUSES:
                return response
            last_error = ReadingsUnavailable(describe_failure(response))
            # A server that says how long to wait knows better than we do.
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None and attempt <= len(delays):
                try:
                    delays[attempt - 1] = min(float(retry_after), 8.0)
                except ValueError:
                    pass
        if attempt <= len(delays):
            sleep(delays[attempt - 1])
    raise ReadingsUnavailable(f"gave up after {attempts} attempts: {last_error}")


def stream_to_file(
    url: str,
    destination: str,
    *,
    session: HttpSession,
    chunk_size: int = 8192,
    timeout: tuple[float, float] | float = DEFAULT_TIMEOUT,
) -> tuple[int, int, str]:
    """Download a body without ever holding all of it in memory.

    Returns (bytes written, chunks read, sha256 hex digest). `stream=True`
    means the response headers have arrived and the body has not; the body
    is pulled a chunk at a time as you iterate.
    """
    digest = hashlib.sha256()
    total = 0
    chunks = 0
    with session.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with open(destination, "wb") as handle:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                handle.write(chunk)
                digest.update(chunk)
                total += len(chunk)
                chunks += 1
    return total, chunks, digest.hexdigest()


def summarise(readings: Iterable[Reading]) -> dict[str, float]:
    """Pure function, no network. The part worth testing without a server."""
    values = [r.celsius for r in readings]
    if not values:
        raise ReadingsError("cannot summarise an empty set of readings")
    return {
        "count": float(len(values)),
        "min": min(values),
        "max": max(values),
        "mean": round(sum(values) / len(values), 4),
    }
