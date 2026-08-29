"""Stage 1 — Ingest.

**The promise:** every fetch has a deadline, only failures worth retrying are
retried, and a source that never answers does not take the run down with it.

Three decisions, all from Day 78 and Day 84.

**A timeout on every call.** A request with no timeout has no upper bound on how
long your 3 a.m. run takes. ``urllib.request.urlopen`` accepts ``timeout``; the
default is whatever the socket module's default is, which is usually None,
which is forever.

**Retry only what is worth retrying.** A 500 or a 503 means the server had a bad
moment and might not next time. A 404 means the URL is wrong, and it will be
just as wrong in two seconds — retrying it costs three round trips to learn the
same thing and delays every other source. 429 is retryable because it is the
server asking you to slow down, which is exactly what backoff does.

**Be honest about partial success.** ``fetch_all`` never raises. It returns one
``FetchResult`` per source, some with records and some with an error, and the
caller decides what that means. A pipeline that dies because one of five sources
is down has thrown away four sources' worth of good data.

Why ``urllib.request`` and not ``requests`` (Day 78): this pipeline makes one
GET with a timeout and a header. The standard library does that. Every
dependency is a version to pin, a CVE to track and a thing that can break your
scheduled job at 3 a.m., so the bar for adding one is "it earns its place".
``requests`` earns it the moment you need sessions, connection pooling, or
retries with the sophistication of ``urllib3``'s ``Retry``.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

#: Status codes worth a second attempt. Everything else is a decision, not luck.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class FetchResult:
    """What one source gave us, and what it cost to find out."""

    source: str
    ok: bool
    records: list[dict] = field(default_factory=list)
    attempts: int = 0
    status: int | None = None
    error: str = ""
    retried: bool = False


def _get_json(url: str, *, token: str, timeout: float) -> tuple[int, object]:
    request = urllib.request.Request(url, method="GET")
    request.add_header("Accept", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.status, json.loads(response.read().decode("utf-8"))


def fetch_source(
    base_url: str,
    source: str,
    *,
    token: str = "",
    timeout: float = 5.0,
    attempts: int = 3,
    backoff: float = 0.05,
    sleep: Callable[[float], None] = time.sleep,
) -> FetchResult:
    """Fetch one source, retrying only what is worth retrying.

    ``sleep`` is injected so tests do not have to wait for real backoff.
    """
    url = f"{base_url.rstrip('/')}/stations/{source}/readings"
    tried = 0
    last_status: int | None = None
    last_error = ""

    while tried < attempts:
        tried += 1
        try:
            status, payload = _get_json(url, token=token, timeout=timeout)
        except urllib.error.HTTPError as exc:
            # HTTPError is a *file object*. Not closing it leaks a socket, which
            # in a process that runs once an hour forever is a slow resource
            # exhaustion bug that nothing warns you about in production.
            with exc:
                last_status = exc.code
                body = exc.read().decode("utf-8", errors="replace")
            try:
                last_error = str(json.loads(body).get("error", body))
            except (json.JSONDecodeError, AttributeError):
                last_error = body
            if exc.code not in RETRYABLE_STATUS:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_status = None
            last_error = f"{type(exc).__name__}: {exc}"
        else:
            records = payload.get("records", []) if isinstance(payload, dict) else []
            return FetchResult(
                source=source,
                ok=True,
                records=list(records),
                attempts=tried,
                status=status,
                retried=tried > 1,
            )
        if tried < attempts:
            sleep(backoff * (2 ** (tried - 1)))

    return FetchResult(
        source=source,
        ok=False,
        attempts=tried,
        status=last_status,
        error=last_error,
        retried=tried > 1,
    )


def fetch_all(
    base_url: str,
    sources: list[str],
    *,
    token: str = "",
    timeout: float = 5.0,
    attempts: int = 3,
    backoff: float = 0.05,
    sleep: Callable[[float], None] = time.sleep,
) -> list[FetchResult]:
    """Fetch every source in order. Never raises; a failure is a result."""
    return [
        fetch_source(
            base_url,
            source,
            token=token,
            timeout=timeout,
            attempts=attempts,
            backoff=backoff,
            sleep=sleep,
        )
        for source in sources
    ]
