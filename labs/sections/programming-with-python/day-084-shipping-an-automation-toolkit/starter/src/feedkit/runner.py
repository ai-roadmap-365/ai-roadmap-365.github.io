"""One unattended run, start to finish.

This is the only module that knows the ORDER of things: acquire the lock, load
the state, fetch each source with retries, skip and report the ones that fail,
fold the successes into the state, write the state atomically, print the
summary, return an exit code. Everything it does with the outside world arrives
as an argument — the fetcher, the clock, the logger, the paths — which is why
the whole thing can be exercised against a fake fetcher in a millisecond.

The failure policy is the part worth reading twice, because it is the part that
distinguishes an automation from a script:

* a **transport error or a 5xx** on one source is retried with backoff and, if
  it never succeeds, is SKIPPED and REPORTED — one broken source must not stop
  the other four;
* a **payload that does not parse** is not retried, because it will not parse
  next time either; it is skipped and reported the same way;
* a **failure to acquire the lock** stops everything immediately, because the
  correct response to "a run is already happening" is to do nothing;
* an **unusable state file or an invalid configuration** stops everything,
  because continuing would mean guessing about the thing that records what has
  already been done.

Partial success is the normal case for a batch job, and it gets its own exit
code. Reporting 0 because "most of it worked" is how an automation becomes a
thing nobody can trust.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Protocol, Sequence

from . import core, state as state_module
from .adapters import FetchError
from .config import Config


class Fetcher(Protocol):
    def fetch(self, source: str) -> tuple[Any, int]: ...


def new_run_id() -> str:
    """A short, unique label for one run. Every log line carries it, so the
    lines belonging to a single 03:00 run can be pulled out of a month of
    output with one grep."""
    return uuid.uuid4().hex[:8]


def fetch_sources(
    sources: Sequence[str],
    fetcher: Fetcher,
    seen: dict[str, list[str]],
    max_items: int,
    logger: Any,
) -> list[core.SourceResult]:
    """Fetch every source, collecting successes and failures side by side."""
    # Exercise 7 — skip and report, rather than stop.
    #
    # Build a list of core.SourceResult, one per source. For each source:
    #   * log that it started, with extra={"source": source} so the line names
    #     WHICH item this is — an unattended log without that is unreadable;
    #   * call fetcher.fetch(source), then core.parse_entries(payload, source);
    #   * catch FetchError and core.InvalidPayload TOGETHER: log at ERROR with
    #     the source name, append a SourceResult with status="failed" and
    #     str(exc) as the error, and CONTINUE to the next source. One broken
    #     source must not cost you the other four;
    #   * on success, call core.select_new(entries, seen.get(source, []),
    #     max_items), log the count and the attempt number, and append a
    #     SourceResult with status="ok".
    #
    # Do not catch bare Exception here. A KeyboardInterrupt or a programming
    # error is not a source failure, and swallowing it turns a bug into a
    # mysteriously empty run.
    #
    # Check it with:  pytest tests/test_toolkit.py -k skipped_and_reported
    raise NotImplementedError("Exercise 7: implement fetch_sources in runner.py")


def run_fetch(
    config: Config,
    fetcher: Fetcher,
    clock: Any,
    state_path: Path,
    lock_path: Path,
    logger: Any,
    dry_run: bool = False,
    run_id: str | None = None,
) -> tuple[dict[str, Any], int]:
    """Do one fetch run. Returns the summary and the exit code.

    The run id is passed IN rather than generated here, so that the id stamped
    on every log line and the id recorded in the state file are the same
    string. Two ids for one run is a small bug that makes an incident twice as
    slow to investigate, and it is easy to ship without noticing.
    """
    run_id = run_id or new_run_id()
    started_at = clock.now_iso()

    try:
        with state_module.Lock(lock_path):
            logger.info("run started", extra={"status": "started", "path": str(state_path)})
            current = state_module.load(state_path)
            seen = {
                name: list(record.get("seen_ids") or [])
                for name, record in dict(current.get("sources") or {}).items()
            }

            results = fetch_sources(config.sources, fetcher, seen, config.max_items, logger)
            finished_at = clock.now_iso()
            summary = core.summarise(results)
            merged = core.merge_state(current, results, run_id, started_at, finished_at)

            if dry_run:
                logger.info(
                    "dry run — state not written",
                    extra={"status": "dry-run", "count": summary["new_entries"]},
                )
            else:
                state_module.write_atomic(state_path, merged)
                logger.info(
                    "state written",
                    extra={"status": summary["status"], "path": str(state_path)},
                )
    except state_module.LockHeld as exc:
        logger.error("another run is in progress", extra={"status": "locked"})
        return (
            {
                "run_id": run_id,
                "status": "locked",
                "sources_total": 0,
                "sources_ok": 0,
                "sources_failed": 0,
                "new_entries": 0,
                "failures": {"lock": str(exc)},
                "retried": {},
            },
            core.EXIT_LOCKED,
        )

    summary["run_id"] = run_id
    exit_code = core.exit_code_for(summary)
    logger.info(
        "run finished",
        extra={"status": summary["status"], "count": summary["new_entries"]},
    )
    return summary, exit_code
