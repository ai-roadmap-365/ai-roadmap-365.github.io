"""A fake session — the Day 74 payoff, in about forty lines.

`fetch_readings` and `get_with_retry` both take a `session` parameter. That
one design decision means the network can be replaced by this file, and the
tests that use it need no server, no socket, no port, and no waiting.

Compare the two shapes:

    def fetch(station):                      # untestable without a network
        return requests.get(URL, params=...) # or without patching

    def fetch(station, *, session):          # testable with FakeSession
        return session.get(URL, params=...)

FakeResponse implements only the slice of `requests.Response` the client
actually touches: `.status_code`, `.headers`, `.json()`, `.text`, and
`raise_for_status()`. That slice being small is itself information — it
tells you how little of `requests` your code depends on.
"""

from __future__ import annotations

import json as _json
from typing import Any

import requests


class FakeResponse:
    """The part of a response this client uses, and nothing else."""

    def __init__(
        self,
        status_code: int,
        payload: Any = None,
        headers: dict[str, str] | None = None,
        text: str | None = None,
    ) -> None:
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {"Content-Type": "application/json; charset=utf-8"}
        self.text = text if text is not None else _json.dumps(payload)

    def json(self) -> Any:
        if self._payload is None:
            raise ValueError("no JSON body")
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"{self.status_code} error")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None


class FakeSession:
    """A scripted stand-in for `requests.Session`.

    It is a fake, a spy and a stub at once, exactly as Day 74 described:
    it answers from a script, it records every call, and a scripted item
    that happens to be an exception instance is raised instead of returned —
    which is how a test produces a ConnectionError or a Timeout on demand.
    """

    def __init__(self, script: list[Any] | None = None) -> None:
        self._script = list(script or [])
        self.calls: list[dict[str, Any]] = []

    def _next(self, method: str, url: str, kwargs: dict[str, Any]) -> Any:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self._script:
            raise AssertionError(
                f"the fake session ran out of scripted responses at call {len(self.calls)}"
            )
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def get(self, url: str, **kwargs: Any) -> Any:
        return self._next("GET", url, kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        return self._next("POST", url, kwargs)

    @property
    def timeouts(self) -> list[Any]:
        """Every timeout value passed in — so a test can prove one was set."""
        return [call.get("timeout") for call in self.calls]
