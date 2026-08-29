"""YOUR FILE — exercises 1 to 6.

Six functions. Each one has a docstring saying exactly what it must do, a
signature that is already right, and a `raise NotImplementedError` you
delete. `examples/client.py` contains a complete reference implementation:
use it when you are stuck, but write yours first — reading a solution feels
like learning and is not.

Run your work at any time:

    .venv/bin/pytest starter -q

Unfinished exercises are skipped, so the suite exits 0 from the first
minute. Check everything at the end with:

    bash tests/run_tests.sh

Two rules that apply to every function below, and to every HTTP call you
ever write after today:

  * pass `timeout=` to every request. `requests` has no default;
  * take `session` as a parameter, never reach for `requests.get` inside
    the function. That parameter is what makes exercise 7 possible.
"""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests

# (connect timeout, read timeout). Use this as your default.
DEFAULT_TIMEOUT: tuple[float, float] = (3.05, 10.0)

# The only statuses worth trying again. Everything else is a final answer.
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


class ReadingsError(Exception):
    """Base class for this client's own exceptions."""


class ReadingsUnavailable(ReadingsError):
    """Could not be reached, or kept failing."""


class StationNotFound(ReadingsError):
    """The server said clearly: there is no such station."""


@dataclass(frozen=True)
class Reading:
    station: str
    hour: int
    celsius: float


# ---------------------------------------------------------------------------
# Exercise 1 — fetch and parse JSON
# ---------------------------------------------------------------------------
def fetch_readings(
    base_url: str,
    station: str,
    *,
    session: Any,
    timeout: tuple[float, float] | float = DEFAULT_TIMEOUT,
) -> list[Reading]:
    """GET {base_url}/api/readings with the station as a QUERY PARAMETER.

    Steps:
      1. `response = session.get(f"{base_url}/api/readings",
                                 params={"station": station}, timeout=timeout)`
         — use `params=`, not an f-string. Exercise 1b below shows why.
      2. If `response.status_code == 404`, raise `StationNotFound` with a
         message naming the station. This is exercise 2's requirement, and
         it belongs here.
      3. Call `response.raise_for_status()` for everything else that failed.
      4. `payload = response.json()`, then build one `Reading` per item in
         `payload["readings"]`. Each item has keys `station`, `hour`,
         `celsius`.

    Verify by hand once you have it:
        .venv/bin/pytest starter -q -k fetch_readings
    """
    raise NotImplementedError("exercise 1: fetch and parse the JSON body")


# ---------------------------------------------------------------------------
# Exercise 2 — a failure a human can act on, instead of a traceback
# ---------------------------------------------------------------------------
def describe_failure(response: Any) -> str:
    """Turn a failed response into ONE sentence, with no traceback in it.

    Required format, exactly:
        "HTTP 404 (your request was rejected) — no such station"
        "HTTP 500 (the server failed) — the server fell over"

    Steps:
      1. `response.status_code // 100` gives the family: 3, 4 or 5. Map
         3 -> "redirection", 4 -> "your request was rejected",
         5 -> "the server failed", anything else -> "unexpected status".
      2. If `response.headers.get("Content-Type", "")` starts with
         "application/json", try `response.json()` and append
         f" — {body['detail']}" if the body has a "detail" key, or
         f" — {body['error']}" if it only has "error". Wrap the `.json()`
         call in try/except ValueError: a Content-Type header is a claim,
         not a guarantee.
      3. Return the assembled string. Note the em dash: "—", not "-".
    """
    raise NotImplementedError("exercise 2: describe the failure in one sentence")


# ---------------------------------------------------------------------------
# Exercise 3 — the backoff schedule (used by exercise 4)
# ---------------------------------------------------------------------------
def backoff_delays(
    attempts: int,
    *,
    base: float = 0.5,
    cap: float = 8.0,
    jitter: Callable[[], float] = random.random,
) -> list[float]:
    """Return the waits BETWEEN `attempts` tries — so `attempts - 1` of them.

    Requirements:
      * raise `ValueError` if `attempts < 1`;
      * the raw delay for wait number i (counting from 0) is
        `min(cap, base * 2 ** i)` — 0.5, 1.0, 2.0, 4.0, 8.0, 8.0, ...;
      * multiply each raw delay by `(0.5 + 0.5 * jitter())`, so a wait lands
        somewhere in the top half of its slot, and round to 4 places;
      * `jitter` is a PARAMETER so a test can pass `lambda: 1.0` and get the
        exact schedule, or `lambda: 0.0` and get half of it.

    With `jitter=lambda: 1.0`:
        backoff_delays(1) == []
        backoff_delays(4) == [0.5, 1.0, 2.0]
        backoff_delays(6) == [0.5, 1.0, 2.0, 4.0, 8.0]
    """
    raise NotImplementedError("exercise 3: build the exponential backoff schedule")


# ---------------------------------------------------------------------------
# Exercise 4 — retry on 429 and 5xx, and on nothing else
# ---------------------------------------------------------------------------
def get_with_retry(
    url: str,
    *,
    session: Any,
    attempts: int = 4,
    timeout: tuple[float, float] | float = DEFAULT_TIMEOUT,
    sleep: Callable[[float], None] = time.sleep,
    jitter: Callable[[], float] = random.random,
    params: dict[str, Any] | None = None,
) -> Any:
    """GET `url`, retrying only what deserves it. Return the final response.

    Steps:
      1. `delays = backoff_delays(attempts, jitter=jitter)`.
      2. Loop `for attempt in range(1, attempts + 1)`:
         a. call `session.get(url, params=params, timeout=timeout)` inside
            `try: ... except requests.exceptions.RequestException as exc:`.
            A transport failure has NO status code, because there is no
            response — record it and fall through to the sleep;
         b. if the status is NOT in `RETRY_STATUSES`, RETURN the response
            immediately. A 404 is a final answer, and retrying it is a bug;
         c. otherwise remember the failure. If the response carries a
            `Retry-After` header, use `min(float(header), 8.0)` as this
            wait instead of your computed one — the server knows better
            than you do. Guard the float() with try/except ValueError,
            because Retry-After may legally be a date instead of seconds;
         d. if `attempt <= len(delays)`, call `sleep(delays[attempt - 1])`.
      3. After the loop, raise `ReadingsUnavailable` with a message
         containing the exact text f"after {attempts} attempts".

    `sleep` is a parameter for the Day 74 reason: a test passes a recorder
    and proves the schedule in microseconds without anything waiting.
    """
    raise NotImplementedError("exercise 4: retry 429 and 5xx with backoff")


# ---------------------------------------------------------------------------
# Exercise 5 — a Session with shared headers and a token from the environment
# ---------------------------------------------------------------------------
def make_session(user_agent: str = "day078-yours/1.0 (course exercise)") -> requests.Session:
    """Build a `requests.Session` carrying the headers every call should send.

    Steps:
      1. `session = requests.Session()`.
      2. `session.headers.update({...})` with "User-Agent": user_agent and
         "Accept": "application/json".
      3. Read `os.environ.get("READINGS_TOKEN")`. If it is set, add
         `session.headers["Authorization"] = f"Bearer {token}"`. If it is
         not set, add NO Authorization header at all.
      4. Return the session.

    Never write a token into this file. A secret in source control is a
    secret you have to rotate, and you will not enjoy the afternoon.
    """
    raise NotImplementedError("exercise 5: build the session")


# ---------------------------------------------------------------------------
# Exercise 6 — stream a large body instead of loading it
# ---------------------------------------------------------------------------
def stream_to_file(
    url: str,
    destination: str,
    *,
    session: Any,
    chunk_size: int = 8192,
    timeout: tuple[float, float] | float = DEFAULT_TIMEOUT,
) -> tuple[int, int, str]:
    """Download `url` to `destination` without holding the whole body at once.

    Return (bytes written, number of chunks read, sha256 hex digest).

    Steps:
      1. `digest = hashlib.sha256()`, and counters at zero.
      2. `with session.get(url, stream=True, timeout=timeout) as response:`
         — `stream=True` means the headers have arrived and the body has
         not. Call `response.raise_for_status()` inside the block.
      3. `with open(destination, "wb") as handle:` then
         `for chunk in response.iter_content(chunk_size=chunk_size):`
         — skip a falsy chunk, write it, feed it to the digest, and count
         both bytes and chunks.
      4. Return the three values.

    The point: at no moment does more than one chunk exist in memory. Try
    this against a four-gigabyte file without `stream=True` and your
    process will be killed by the operating system.
    """
    raise NotImplementedError("exercise 6: stream the body a chunk at a time")


# ---------------------------------------------------------------------------
# Provided, complete — the pure part, which needs no network at all.
# ---------------------------------------------------------------------------
def summarise(readings: list[Reading]) -> dict[str, float]:
    values = [r.celsius for r in readings]
    if not values:
        raise ReadingsError("cannot summarise an empty set of readings")
    return {
        "count": float(len(values)),
        "min": min(values),
        "max": max(values),
        "mean": round(sum(values) / len(values), 4),
    }


def _digest_unused() -> str:  # pragma: no cover - keeps hashlib imported for you
    return hashlib.sha256(b"").hexdigest()
