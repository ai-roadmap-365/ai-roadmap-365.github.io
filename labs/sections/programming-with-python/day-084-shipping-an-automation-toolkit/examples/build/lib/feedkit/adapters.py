"""The edges: the network, the clock, and sleeping.

Everything in this module talks to something outside the process. That is the
whole reason it is a separate module — the core can be tested with plain data
because none of this leaks into it, and this module can be swapped for a fake
in a test because the runner receives it as an argument rather than importing
it. Day 74's rule, applied to the two boundaries that hurt most.

Note the constructor of `HttpFetcher`: it takes a session, a timeout, a retry
count, a backoff base AND a `sleeper`. Injecting the sleeper is what lets the
test suite exercise three retries in microseconds instead of seconds, without
anybody having to patch `time.sleep` globally and hope.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Callable, Protocol

import requests


class FetchError(RuntimeError):
    """A source could not be fetched, after every retry was spent."""


class Clock(Protocol):
    """The clock, as an interface, so a test can hand over a fixed time."""

    def now_iso(self) -> str: ...


class SystemClock:
    """The real clock. UTC, always — a job that runs at 02:30 local time runs
    twice or not at all on the two days a year the offset changes."""

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FixedClock:
    """A clock that never moves. Shipped rather than hidden in a test file,
    because it belongs to the design, not to the tests."""

    def __init__(self, value: str) -> None:
        self.value = value

    def now_iso(self) -> str:
        return self.value


#: Statuses worth trying again: the server said "not now", not "never".
RETRYABLE_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504})


class HttpFetcher:
    """Fetch one source's JSON, with a timeout and bounded retries.

    Three things here are not optional in an unattended job:

    * a **timeout** on every request — the default in `requests` is no timeout
      at all, and a job with no timeout does not fail, it hangs, which is the
      one outcome no supervisor can see;
    * **bounded** retries with exponential backoff — unbounded retries turn a
      failing dependency into a self-inflicted outage;
    * a retry decision based on WHAT went wrong. A 503 is worth another go; a
      404 or a 401 will be a 404 or a 401 forever, and retrying it is just
      noise you will pay for in someone else's server logs.
    """

    def __init__(
        self,
        session: requests.Session,
        base_url: str,
        token: str = "",
        timeout: float = 5.0,
        retries: int = 3,
        backoff_seconds: float = 0.5,
        sleeper: Callable[[float], None] = time.sleep,
        logger: Any = None,
    ) -> None:
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.retries = max(1, retries)
        self.backoff_seconds = backoff_seconds
        self.sleeper = sleeper
        self.logger = logger

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            # Identify the client honestly — Day 79's rule, and the thing that
            # lets an operator find you when your job misbehaves.
            "User-Agent": "feedkit/1.0 (personal automation toolkit)",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def fetch(self, source: str) -> tuple[Any, int]:
        """Return the decoded payload and the attempt number that succeeded."""
        url = f"{self.base_url}/feed/{source}.json"
        last_error = "no attempt was made"

        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(url, headers=self._headers(), timeout=self.timeout)
            except requests.RequestException as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if self.logger:
                    self.logger.warning(
                        "fetch attempt failed",
                        extra={"source": source, "attempt": attempt, "status": "transport"},
                    )
            else:
                if response.status_code == 200:
                    try:
                        return response.json(), attempt
                    except ValueError as exc:
                        # A body that is not JSON will not become JSON on a
                        # retry. Fail now.
                        raise FetchError(f"response was not JSON: {exc}") from exc
                last_error = f"HTTP {response.status_code}"
                if response.status_code not in RETRYABLE_STATUS:
                    raise FetchError(f"{last_error} (not retryable)")
                if self.logger:
                    self.logger.warning(
                        "fetch attempt failed",
                        extra={
                            "source": source,
                            "attempt": attempt,
                            "status": response.status_code,
                        },
                    )

            if attempt < self.retries:
                self.sleeper(self.backoff_seconds * (2 ** (attempt - 1)))

        raise FetchError(f"{last_error} after {self.retries} attempts")


def build_session() -> requests.Session:
    """One Session for the whole run, so the connection is reused across
    sources instead of being renegotiated for each one."""
    return requests.Session()
