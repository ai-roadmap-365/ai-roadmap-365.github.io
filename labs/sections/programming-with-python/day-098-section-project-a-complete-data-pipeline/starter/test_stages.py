"""Nine promises, nine tests. One baseline test that passes before you start.

Each skipped test names the exercise in ``stages.py`` that unblocks it. Do the
exercise, delete that test's ``@exercise(...)`` decorator, and run:

    .venv/bin/pytest starter -q
"""

from __future__ import annotations

import io
import json
import os

import pytest

import fixture_server
import stages

#: When the harness runs this suite against the completed reference, the skip
#: marks must not apply — the whole point is to see all ten pass.
SOLVED = bool(os.environ.get("DAY098_SOLUTION"))


def exercise(number: int, what: str):
    """Skip until the learner has done the exercise; never skip for the key."""
    return pytest.mark.skipif(not SOLVED, reason=f"Exercise {number} — {what}")


SOURCES = ["alpha", "bravo", "charlie"]
REPORT_AT = "2026-08-16T12:00:00Z"


def _run(base_url: str, token: str, **kwargs):
    log = io.StringIO()
    out = io.StringIO()
    code = stages.run(
        base_url,
        sources=SOURCES,
        token=token,
        log_stream=log,
        out=out,
        **kwargs,
    )
    return code, log.getvalue(), out.getvalue()


# ---------------------------------------------------------------------------
# Baseline — passes on the untouched skeleton.
# ---------------------------------------------------------------------------
def test_the_skeleton_runs_and_reports_its_own_failure(base_url, token):
    """The starter is not broken. It is finished-looking and wrong.

    It aborts at the first malformed record, which is exercise 3 — and it says
    so rather than crashing, so you can see the shape of the thing before you
    start improving it.
    """
    fixture_server.reset_flaky_counter()
    code, log_text, out_text = _run(base_url, token)
    assert code in (stages.EXIT_FAILURE, stages.EXIT_SUCCESS, stages.EXIT_PARTIAL)
    assert log_text.strip(), "the skeleton must emit at least one log line"
    for line in log_text.splitlines():
        json.loads(line)  # every line is a complete JSON object


# ---------------------------------------------------------------------------
# Stage 1 — Ingest
# ---------------------------------------------------------------------------
@exercise(1, "give fetch_source a timeout and retries")
def test_a_flaky_source_recovers_after_retries(base_url, token):
    fixture_server.reset_flaky_counter()
    result = stages.fetch_source(
        base_url, "bravo", token=token, attempts=3, backoff=0.0, sleep=lambda _s: None
    )
    assert result.ok, "bravo answers on the third attempt; one attempt is not enough"
    assert result.attempts == 3
    assert len(result.records) == 4


@exercise(2, "retry only retryable statuses")
def test_a_wrong_url_is_not_retried(base_url, token):
    result = stages.fetch_source(
        base_url, "delta", token=token, attempts=3, backoff=0.0, sleep=lambda _s: None
    )
    assert not result.ok
    assert result.status == 404
    assert result.attempts == 1, "a 404 will be a 404 next time too"


# ---------------------------------------------------------------------------
# Stage 2 — Validate
# ---------------------------------------------------------------------------
@exercise(3, "collect every bad record instead of raising")
def test_validation_collects_rather_than_aborts(base_url, token):
    fixture_server.reset_flaky_counter()
    fetched = {
        source: stages.fetch_source(
            base_url, source, token=token, attempts=3, backoff=0.0, sleep=lambda _s: None
        ).records
        for source in ("alpha", "bravo")
    }
    accepted, rejected = stages.validate_all(fetched)
    assert len(accepted) + len(rejected) == 9
    assert len(rejected) >= 1
    assert {r.reading_id for r in rejected} >= {"a-3"}
    assert all(r.problems for r in rejected), "a rejection with no reason cannot be fixed"


@exercise(4, "constrain the model so out-of-range values are rejected")
def test_out_of_range_values_are_rejected(base_url, token):
    fixture_server.reset_flaky_counter()
    fetched = {
        source: stages.fetch_source(
            base_url, source, token=token, attempts=3, backoff=0.0, sleep=lambda _s: None
        ).records
        for source in ("alpha", "bravo")
    }
    accepted, rejected = stages.validate_all(fetched)
    assert len(accepted) == 7
    assert {r.reading_id for r in rejected} == {"a-3", "a-5"}
    problems = " ".join(p for r in rejected for p in r.problems)
    assert "humidity_pct" in problems and "temperature_c" in problems


# ---------------------------------------------------------------------------
# Stage 3 — Store
# ---------------------------------------------------------------------------
@exercise(5, "idempotence key, then insert only what is new")
def test_running_twice_stores_once(base_url, token, tmp_path):
    fixture_server.reset_flaky_counter()
    url = f"sqlite:///{tmp_path / 'pipeline.db'}"
    first_code, _, _ = _run(base_url, token, database_url=url, run_id="run-one")
    second_code, second_log, _ = _run(base_url, token, database_url=url, run_id="run-two")
    events = [json.loads(line) for line in second_log.splitlines()]
    store = next(e for e in events if e["event"] == "stage.store")
    assert store["inserted"] == 0, "the second run must store nothing new"
    assert store["duplicates_skipped"] == 7
    assert store["total_rows"] == 6, "six distinct readings, however many times you run"


# ---------------------------------------------------------------------------
# Stage 4 — Report
# ---------------------------------------------------------------------------
@exercise(6, "make the report instant a parameter")
def test_the_report_is_built_at_a_fixed_instant(base_url, token, tmp_path):
    fixture_server.reset_flaky_counter()
    url = f"sqlite:///{tmp_path / 'pipeline.db'}"
    _run(base_url, token, database_url=url)
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine(url, future=True)
    with Session(engine) as session:
        summary = stages.build_report(
            session, report_at=REPORT_AT, window_hours=12, stations=SOURCES
        )
    engine.dispose()
    assert summary["report_at"] == REPORT_AT
    assert summary["window_start"] == "2026-08-16T00:00:00Z"
    assert summary["readings_in_window"] == 5
    assert summary["stations"] == {"alpha": 2, "bravo": 3, "charlie": 0}


# ---------------------------------------------------------------------------
# Stage 5 — Observe
# ---------------------------------------------------------------------------
@exercise(7, "carry the run id on every log line")
def test_every_log_line_carries_the_run_id(base_url, token, tmp_path):
    fixture_server.reset_flaky_counter()
    url = f"sqlite:///{tmp_path / 'pipeline.db'}"
    _, log_text, _ = _run(base_url, token, database_url=url, run_id="run-abc123")
    events = [json.loads(line) for line in log_text.splitlines()]
    assert events, "a run with no log is a run you cannot investigate"
    assert {e.get("run_id") for e in events} == {"run-abc123"}
    stage_events = [e["event"] for e in events if e["event"].startswith("stage.")]
    assert stage_events == [
        "stage.ingest",
        "stage.validate",
        "stage.store",
        "stage.report",
        "stage.observe",
    ]


@exercise(8, "return 3 for partial success")
def test_partial_success_gets_its_own_exit_code(base_url, token, tmp_path):
    fixture_server.reset_flaky_counter()
    url = f"sqlite:///{tmp_path / 'pipeline.db'}"
    code, _, _ = _run(base_url, token, database_url=url)
    assert code == stages.EXIT_PARTIAL, (
        "charlie failed permanently and two records were rejected: that is not success"
    )


@exercise(9, "redact secrets inside the logger")
def test_no_secret_reaches_the_log(base_url, token, tmp_path):
    fixture_server.reset_flaky_counter()
    url = f"sqlite:///{tmp_path / 'pipeline.db'}"
    _, log_text, out_text = _run(base_url, token, database_url=url)
    assert token not in log_text, "charlie's error body echoed the token straight into the log"
    assert token not in out_text
    assert "***redacted***" in log_text, "redaction must leave a visible mark, not a silent gap"
