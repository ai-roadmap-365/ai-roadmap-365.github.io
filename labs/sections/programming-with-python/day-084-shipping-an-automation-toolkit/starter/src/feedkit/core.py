"""The pure core of the toolkit.

Nothing in this module touches the network, the clock, the filesystem or a
subprocess. Every function here takes plain data and returns plain data, which
is exactly what makes the interesting parts of an automation testable without
starting a server or waiting a second. Day 74 argued for pushing boundaries to
the edges; this module is what the middle looks like when you do.

If you ever find yourself wanting to `import requests` or call `time.time()` in
here, that is the signal that the value belongs in a parameter instead.
"""

from __future__ import annotations

import calendar
import time
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

# `calendar` and `time` appear here only to PARSE a timestamp that was handed
# in as a string. Nothing in this module ever asks what time it is now — that
# question belongs to the clock adapter, so that every test can answer it.

STATE_VERSION = 1

#: Exit codes. These are the machine-readable half of every run, and the
#: scheduler is the thing that reads them.
EXIT_OK = 0
EXIT_FATAL = 1
EXIT_PARTIAL = 3
EXIT_LOCKED = 75


@dataclass(frozen=True)
class Entry:
    """One item collected from one source."""

    id: str
    title: str
    published: str
    source: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "title": self.title,
            "published": self.published,
            "source": self.source,
        }


@dataclass(frozen=True)
class SourceResult:
    """What happened to one source during one run."""

    source: str
    status: str  # "ok" | "failed"
    new_entries: tuple[Entry, ...] = ()
    error: str = ""
    attempts: int = 1


class InvalidPayload(ValueError):
    """The server answered, but not with something this toolkit understands."""


def parse_entries(payload: Any, source: str) -> tuple[Entry, ...]:
    """Validate a decoded JSON payload and turn it into Entry objects.

    A 200 response is not the same thing as a correct response. Validating at
    the edge means every function downstream can assume the shape it was given,
    which is the whole reason this is a separate step rather than a dict lookup
    buried three calls deep.
    """
    if not isinstance(payload, Mapping):
        raise InvalidPayload(f"top level is {type(payload).__name__}, expected an object")
    items = payload.get("entries")
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        raise InvalidPayload("'entries' is missing or is not a list")

    parsed: list[Entry] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise InvalidPayload(f"entry {index} is not an object")
        missing = [field for field in ("id", "title", "published") if field not in item]
        if missing:
            raise InvalidPayload(f"entry {index} is missing {', '.join(missing)}")
        parsed.append(
            Entry(
                id=str(item["id"]),
                title=str(item["title"]),
                published=str(item["published"]),
                source=source,
            )
        )
    return tuple(parsed)


def select_new(
    entries: Iterable[Entry], seen_ids: Iterable[str], max_items: int
) -> tuple[Entry, ...]:
    """Return the entries not already recorded, newest first, capped at max_items.

    This is the idempotence rule, and it is four lines of pure logic precisely
    because the record of what has been seen arrives as an argument rather than
    being read from a file in here.
    """
    # Exercise 1 — the idempotence rule, and the reason a second run is cheap.
    #
    # Return only the entries whose `id` is NOT in `seen_ids`, sorted newest
    # first by (published, id), and no more than `max_items` of them. Treat a
    # negative `max_items` as "no cap".
    #
    # Do it in four lines and resist the urge to open a file in here: the
    # record of what has been seen arrives as an argument precisely so this
    # function stays pure and its test needs nothing but two lists.
    #
    # Check it with:  pytest tests/test_toolkit.py -k select_new
    raise NotImplementedError("Exercise 1: implement select_new in core.py")


def empty_state() -> dict[str, Any]:
    """The state of a toolkit that has never run."""
    return {
        "version": STATE_VERSION,
        "last_run": None,
        "last_success": None,
        "sources": {},
        "entries": [],
    }


def merge_state(
    state: Mapping[str, Any],
    results: Sequence[SourceResult],
    run_id: str,
    started_at: str,
    finished_at: str,
    keep_entries: int = 200,
) -> dict[str, Any]:
    """Fold one run's results into the previous state and return the new state.

    Pure: give it the same inputs and it returns the same dictionary, every
    time, on any machine. The caller decides whether to write it.
    """
    summary = summarise(results)
    sources = {name: dict(value) for name, value in dict(state.get("sources") or {}).items()}
    collected: list[dict[str, str]] = list(state.get("entries") or [])

    for result in results:
        record = sources.setdefault(
            result.source, {"seen_ids": [], "last_success": None, "last_error": ""}
        )
        if result.status == "ok":
            seen = list(record.get("seen_ids") or [])
            seen.extend(entry.id for entry in result.new_entries if entry.id not in seen)
            record["seen_ids"] = seen
            record["last_success"] = finished_at
            record["last_error"] = ""
            collected = [entry.as_dict() for entry in result.new_entries] + collected
        else:
            record["last_error"] = result.error

    collected.sort(key=lambda item: (item["published"], item["id"]), reverse=True)

    new_state: dict[str, Any] = {
        "version": STATE_VERSION,
        "last_run": {
            "run_id": run_id,
            "started_at": started_at,
            "finished_at": finished_at,
            "status": summary["status"],
            "sources_ok": summary["sources_ok"],
            "sources_failed": summary["sources_failed"],
            "new_entries": summary["new_entries"],
        },
        "last_success": (
            finished_at if summary["status"] == "ok" else state.get("last_success")
        ),
        "sources": sources,
        "entries": collected[:keep_entries],
    }
    return new_state


def summarise(results: Sequence[SourceResult]) -> dict[str, Any]:
    """Reduce a run's results to the handful of numbers a human reads."""
    ok = [result for result in results if result.status == "ok"]
    failed = [result for result in results if result.status != "ok"]
    new_entries = sum(len(result.new_entries) for result in ok)

    if not results:
        status = "ok"
    elif not failed:
        status = "ok"
    elif not ok:
        status = "failed"
    else:
        status = "partial"

    return {
        "status": status,
        "sources_total": len(results),
        "sources_ok": len(ok),
        "sources_failed": len(failed),
        "new_entries": new_entries,
        "failures": {result.source: result.error for result in failed},
        "retried": {result.source: result.attempts for result in results if result.attempts > 1},
    }


def exit_code_for(summary: Mapping[str, Any]) -> int:
    """Map a run summary onto the exit code the scheduler will read.

    Partial success gets its own code. Reporting 0 for "most of it worked" is
    the single most common way an automation lies to the person who owns it.
    """
    # Exercise 2 — make partial success visible to the machine.
    #
    # Map summary["status"] onto an exit code: "ok" -> EXIT_OK,
    # "partial" -> EXIT_PARTIAL, anything else -> EXIT_FATAL.
    #
    # Three lines. The temptation to return 0 for "partial" because most of it
    # worked is exactly the habit this exercise exists to break: the scheduler
    # reads the exit code and nothing else, and an automation that reports
    # success while dropping items is one nobody can ever trust again.
    #
    # Check it with:  pytest tests/test_toolkit.py -k exit_codes
    raise NotImplementedError("Exercise 2: implement exit_code_for in core.py")


def format_summary(summary: Mapping[str, Any], run_id: str, dry_run: bool = False) -> str:
    """The human-readable run summary, printed at the end of every run."""
    lines = [
        f"run {run_id}: {summary['status']}"
        + ("  (dry run — nothing was written)" if dry_run else ""),
        f"  sources: {summary['sources_ok']} ok, {summary['sources_failed']} failed,"
        f" {summary['sources_total']} total",
        f"  new entries: {summary['new_entries']}",
    ]
    for source, attempts in sorted(dict(summary.get("retried") or {}).items()):
        lines.append(f"  retried: {source} succeeded on attempt {attempts}")
    for source, error in sorted(dict(summary.get("failures") or {}).items()):
        lines.append(f"  FAILED: {source}: {error}")
    return "\n".join(lines)


def render_report(state: Mapping[str, Any], limit: int) -> str:
    """Render what has been collected. Reads state, touches nothing."""
    entries = list(state.get("entries") or [])
    if not entries:
        return "No entries collected yet. Run `feedkit fetch` first."

    shown = entries[: limit if limit >= 0 else len(entries)]
    width = max(len(entry["source"]) for entry in shown)
    lines = [f"{len(entries)} entries collected; showing {len(shown)}", ""]
    for entry in shown:
        lines.append(f"  {entry['published']}  {entry['source']:<{width}}  {entry['title']}")
    return "\n".join(lines)


def render_status(state: Mapping[str, Any], now: str, max_age_seconds: int) -> tuple[str, bool]:
    """Render the status block and say whether the toolkit has gone quiet.

    The second half of the tuple is the watchdog answer: True when the last
    successful run is older than the allowance. Alerting on silence catches the
    failure mode that alerting on errors cannot — the run that never happened.
    """
    last_success = state.get("last_success")
    last_run = state.get("last_run")
    stale = is_stale(last_success, now, max_age_seconds)

    lines = [f"last success: {last_success or 'never'}"]
    if last_run:
        lines.append(
            f"last run:     {last_run['run_id']} at {last_run['finished_at']}"
            f" ({last_run['status']}, {last_run['new_entries']} new)"
        )
    else:
        lines.append("last run:     never")
    lines.append(f"now:          {now}")
    lines.append(
        f"watchdog:     {'STALE' if stale else 'fresh'}"
        f" (allowance {max_age_seconds}s)"
    )
    for name, record in sorted(dict(state.get("sources") or {}).items()):
        note = record.get("last_error") or "ok"
        lines.append(
            f"  {name}: {len(record.get('seen_ids') or [])} seen,"
            f" last success {record.get('last_success') or 'never'} — {note}"
        )
    return "\n".join(lines), stale


def is_stale(last_success: str | None, now: str, max_age_seconds: int) -> bool:
    """True when the last success is missing or older than the allowance.

    Timestamps are ISO 8601 strings, compared by parsing them into seconds. The
    parsing lives in the caller's clock adapter; here we accept the already
    normalised comparison to keep this module free of the datetime module's
    timezone surprises. Both arguments must be UTC ISO strings.
    """
    if not last_success:
        return True
    return _iso_seconds(now) - _iso_seconds(last_success) > max_age_seconds


def _iso_seconds(value: str) -> int:
    """Seconds since the epoch for a UTC ISO 8601 timestamp such as
    2026-07-19T10:11:12Z. Deliberately small and deliberately strict."""
    cleaned = value.replace("Z", "").split(".")[0]
    parsed = time.strptime(cleaned, "%Y-%m-%dT%H:%M:%S")
    return calendar.timegm(parsed)
