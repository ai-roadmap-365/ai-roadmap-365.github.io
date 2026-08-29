"""The client and judgement functions Day 134's exercises test.

Everything here runs on the standard library's ``urllib.request`` -- no
third-party HTTP client is a dependency of this lab. Day 135 owns turning
the JSON these functions return into a tidy DataFrame; this module stops at
"assembled rows" and "a verdict about whether the source deserves your
time in the first place".
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RateLimitExceeded(RuntimeError):
    """Raised when a source keeps answering 429 past the retry budget.

    A client that retries forever is not polite, it is a denial-of-service
    tool pointed at someone else's server. Giving up loudly, with a count
    of how many times it tried, is the correct behaviour.
    """


def fetch_raw(url: str, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    """One GET via ``urllib.request``. Returns ``(status, headers, body)``.

    ``urllib.request`` raises ``HTTPError`` for any status >= 400, including
    304 in some circumstances and always 429 -- this unwraps that so callers
    can inspect the status code like any other response instead of writing
    a try/except around every call site.
    """
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), exc.read()


def fetch_all_pages(base_url: str, path: str = "/dataset") -> list[dict]:
    """Follow ``has_more`` until the source itself says stop.

    Never loops a fixed number of times and never trusts a total handed to
    it in advance -- the stopping condition is the server's own word for
    "nothing left", which is the only thing that can't drift out of sync
    with what actually got paginated.
    """
    rows: list[dict] = []
    page = 1
    while True:
        status, _, body = fetch_raw(f"{base_url}{path}?page={page}")
        if status != 200:
            raise RuntimeError(f"unexpected status {status} fetching page {page}")
        payload = json.loads(body)
        rows.extend(payload["items"])
        if not payload.get("has_more"):
            break
        page += 1
    return rows


def fetch_with_backoff(
    base_url: str,
    path: str,
    max_attempts: int = 5,
    base_delay: float = 0.01,
) -> tuple[bytes, int]:
    """GET with bounded exponential backoff on 429. Returns ``(body, attempts)``.

    Attempts are capped at ``max_attempts``; a source that never relents
    raises ``RateLimitExceeded`` rather than looping forever.
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        status, headers, body = fetch_raw(f"{base_url}{path}")
        if status == 200:
            return body, attempts
        if status == 429:
            server_hint = headers.get("Retry-After")
            delay = float(server_hint) if server_hint not in (None, "0") else base_delay * (2 ** (attempts - 1))
            time.sleep(delay)
            continue
        raise RuntimeError(f"unexpected status {status}")
    raise RateLimitExceeded(f"gave up after {attempts} attempts, source still rate-limiting")


@dataclass
class CacheEntry:
    """One cached response, keyed by the ETag the source sent with it."""

    etag: str
    body: bytes


def fetch_with_etag(
    base_url: str, path: str, cache: dict[str, CacheEntry]
) -> tuple[bytes, bool, int]:
    """Conditional GET. Returns ``(body, served_from_cache, bytes_over_wire)``.

    The second call for the same path sends ``If-None-Match`` with the
    stored ETag. A ``304`` means the cached copy is still current: the
    caller gets it back with zero bytes counted against the wire, which is
    the entire point of a conditional request -- a re-run costs nothing.
    """
    headers = {}
    cached = cache.get(path)
    if cached is not None:
        headers["If-None-Match"] = cached.etag

    status, response_headers, body = fetch_raw(f"{base_url}{path}", headers=headers)

    if status == 304:
        if cached is None:
            raise RuntimeError("received 304 with nothing cached to serve")
        return cached.body, True, len(body)

    if status == 200:
        etag = response_headers.get("ETag", "")
        cache[path] = CacheEntry(etag=etag, body=body)
        return body, False, len(body)

    raise RuntimeError(f"unexpected status {status}")


def sha256_of(path: Path) -> str:
    """The SHA-256 hex digest of a file's bytes, for pinning a download."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class SourceVerdict:
    """The result of the five-minute assessment: what's here, what's missing."""

    granularity: str | None
    coverage: str | None
    licence: str | None
    dictionary_present: bool
    problems: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not self.problems


def assess_source(metadata: dict[str, Any]) -> SourceVerdict:
    """Run the five-minute checklist against a source's stated metadata.

    Checks presence, not truth -- it cannot tell you the stated granularity
    is accurate, only that the source bothered to state one. That is still
    the majority of what separates a source worth trusting from one that
    is not, because most low-quality sources fail at "bothered to state it".
    """
    problems: list[str] = []
    granularity = metadata.get("granularity")
    coverage = metadata.get("coverage")
    licence = metadata.get("licence")
    dictionary_present = bool(metadata.get("dictionary"))

    if not granularity:
        problems.append("no stated granularity")
    if not coverage:
        problems.append("no stated coverage")
    if not licence:
        problems.append("no stated licence")
    if not dictionary_present:
        problems.append("no data dictionary")
    if not metadata.get("update_cadence"):
        problems.append("no update cadence")
    if "known_issues" not in metadata:
        problems.append("known issues undocumented")

    return SourceVerdict(
        granularity=granularity,
        coverage=coverage,
        licence=licence,
        dictionary_present=dictionary_present,
        problems=problems,
    )


REDISTRIBUTABLE_LICENCES = {"CC0", "CC-BY", "CC-BY-4.0", "ODbL"}
NON_REDISTRIBUTABLE_LICENCES = {"All rights reserved", "Proprietary"}


def check_licence(licence: str, purpose: str = "redistribution") -> dict[str, Any]:
    """Whether ``licence`` permits ``purpose``, with the reason spelled out.

    Returns a reason rather than a bare boolean on purpose: "allowed" and
    "allowed, with attribution required" are both True and both very
    different obligations for whoever ships the result.
    """
    if licence in REDISTRIBUTABLE_LICENCES:
        reason = f"{licence} permits {purpose}"
        if licence.startswith("CC-BY"):
            reason += ", with attribution to the source"
        if licence == "ODbL":
            reason += ", with share-alike terms for the derived database"
        return {"allowed": True, "reason": reason}

    if licence in NON_REDISTRIBUTABLE_LICENCES:
        return {
            "allowed": False,
            "reason": f"{licence} forbids {purpose}; analysis of the data is not the same permission as republishing it",
        }

    return {
        "allowed": False,
        "reason": f"unrecognised licence '{licence}' -- treat as not redistributable until confirmed",
    }


def check_coverage(dictionary: dict[str, Any], data_keys: set[str]) -> dict[str, Any]:
    """Compare a dataset's actual keys against the dictionary's expected list.

    Detects a gap by comparing sets, not by eyeballing a chart -- a region
    with zero rows looks identical to a region that was never collected
    unless something checks for its *absence* from the key list.
    """
    expected = set(dictionary.get("expected_regions", []))
    missing = sorted(expected - data_keys)
    return {"complete": not missing, "missing": missing, "expected": sorted(expected)}


def definitions_match(dictionary_a: dict[str, Any], dictionary_b: dict[str, Any], column: str) -> bool:
    """Whether two dictionaries define ``column`` the same way."""
    definition_a = dictionary_a["fields"][column]["definition"]
    definition_b = dictionary_b["fields"][column]["definition"]
    return definition_a == definition_b


def naive_join_check(series_a, series_b) -> dict[str, Any]:
    """What most people check before joining two columns: dtype and range.

    Deliberately weak. This is the check that passes on the two
    ``unemployment_rate`` columns the day's opening story describes, which
    is exactly why it is not sufficient on its own.
    """
    dtype_match = series_a.dtype == series_b.dtype
    range_a = (series_a.min(), series_a.max())
    range_b = (series_b.min(), series_b.max())
    ranges_overlap = not (range_a[1] < range_b[0] or range_b[1] < range_a[0])
    return {
        "dtype_match": dtype_match,
        "ranges_overlap": ranges_overlap,
        "would_pass_naive_check": dtype_match and ranges_overlap,
    }


def dictionary_aware_join_check(
    dictionary_a: dict[str, Any], dictionary_b: dict[str, Any], column: str
) -> dict[str, Any]:
    """The check the naive one is missing: do the two sources mean the same thing?"""
    same_definition = definitions_match(dictionary_a, dictionary_b, column)
    if same_definition:
        reason = "definitions match"
    else:
        definition_a = dictionary_a["fields"][column]["definition"]
        definition_b = dictionary_b["fields"][column]["definition"]
        reason = f"definitions differ: {definition_a!r} vs {definition_b!r}"
    return {"same_definition": same_definition, "safe_to_join": same_definition, "reason": reason}


def record_provenance(url: str, checksum: str, retrieved_at: datetime | None = None) -> dict[str, str]:
    """Build the record that makes a download reproducible: url, when, checksum.

    ``retrieved_at`` defaults to now, which is exactly the part that would
    make two calls compare unequal in a test -- callers that need a stable
    comparison (this lab's tests included) pass a fixed timestamp in rather
    than letting the clock make the suite flaky.
    """
    stamp = retrieved_at or datetime.now(timezone.utc)
    return {
        "url": url,
        "retrieved_at": stamp.replace(microsecond=0).isoformat(),
        "sha256": checksum,
    }
