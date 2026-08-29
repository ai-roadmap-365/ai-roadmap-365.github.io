"""The properties an automation has to have, asserted one at a time.

Notice what is NOT tested here: that a happy-path fetch returns three entries.
That is the easy half and it is checked once, in passing. Everything else in
this file is about the parts that are not the happy path — running twice,
failing partway, being interrupted mid-write, being told four different things
by four configuration layers, and being trusted with a secret.

Two of these tests need no server at all, because the core is pure and the
fetcher arrives as an argument. The rest talk to the local fixture server on
127.0.0.1 that `run_tests.sh` started; the address is handed over in
FEEDKIT_TEST_BASE_URL. Nothing here reaches the internet.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import requests

from feedkit import adapters, config as config_module, core, logging_setup, runner
from feedkit import state as state_module

TOKEN = os.environ.get("FEEDKIT_TEST_TOKEN", "")
BASE_URL = os.environ.get("FEEDKIT_TEST_BASE_URL", "")


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@pytest.fixture
def logger(capsys):
    """A logger writing structured JSON to captured stdout."""
    return logging_setup.configure("debug", run_id="test0000", secrets=[TOKEN] if TOKEN else [])


@pytest.fixture
def live_fetcher():
    """A real HttpFetcher pointed at the local fixture server, with a no-op
    sleeper so three retries cost microseconds instead of 1.5 seconds."""
    if not BASE_URL:
        pytest.fail("FEEDKIT_TEST_BASE_URL is not set; run this suite through tests/run_tests.sh")
    session = requests.Session()
    fetcher = adapters.HttpFetcher(
        session=session,
        base_url=BASE_URL,
        token=TOKEN,
        timeout=5.0,
        retries=3,
        backoff_seconds=0.0,
        sleeper=lambda _seconds: None,
    )
    yield fetcher
    session.close()


def settings(**overrides):
    """Build a Config without touching os.environ or any file."""
    values = {
        "base_url": BASE_URL or "http://127.0.0.1:1",
        "sources": ["notes", "links"],
        "max_items": 50,
        "retries": 3,
    }
    values.update(overrides)
    return config_module.resolve(
        file_values={},
        environment={key: value for key, value in values.items()},
        flags={},
        token=TOKEN,
    )


def do_run(tmp_path: Path, fetcher, logger, sources, dry_run=False, clock_value="2026-07-19T10:00:00Z"):
    state_path = tmp_path / "state.json"
    return runner.run_fetch(
        settings(sources=list(sources)),
        fetcher,
        adapters.FixedClock(clock_value),
        state_path,
        tmp_path / "state.json.lock",
        logger,
        dry_run=dry_run,
    ), state_path


# --------------------------------------------------------------------------
# 1. The core is pure, so these need nothing at all
# --------------------------------------------------------------------------


def test_select_new_skips_ids_already_seen():
    entries = [
        core.Entry("a", "first", "2026-07-01T00:00:00Z", "notes"),
        core.Entry("b", "second", "2026-07-02T00:00:00Z", "notes"),
    ]
    assert [e.id for e in core.select_new(entries, ["a"], 10)] == ["b"]
    assert core.select_new(entries, ["a", "b"], 10) == ()


def test_select_new_caps_at_max_items_newest_first():
    entries = [
        core.Entry(str(n), f"t{n}", f"2026-07-0{n}T00:00:00Z", "notes") for n in range(1, 6)
    ]
    picked = core.select_new(entries, [], 2)
    assert [e.id for e in picked] == ["5", "4"]


@pytest.mark.parametrize(
    "statuses, expected",
    [
        (["ok", "ok"], "ok"),
        (["ok", "failed"], "partial"),
        (["failed", "failed"], "failed"),
        ([], "ok"),
    ],
)
def test_summary_status(statuses, expected):
    results = [core.SourceResult(source=f"s{n}", status=s) for n, s in enumerate(statuses)]
    assert core.summarise(results)["status"] == expected


def test_exit_codes_distinguish_partial_from_total_success():
    assert core.exit_code_for({"status": "ok"}) == 0
    assert core.exit_code_for({"status": "partial"}) == 3
    assert core.exit_code_for({"status": "failed"}) == 1


def test_parse_entries_rejects_the_wrong_shape():
    with pytest.raises(core.InvalidPayload):
        core.parse_entries({"entries": [{"id": "x"}]}, "notes")
    with pytest.raises(core.InvalidPayload):
        core.parse_entries({"items": []}, "notes")
    with pytest.raises(core.InvalidPayload):
        core.parse_entries([1, 2, 3], "notes")


def test_watchdog_reports_silence_not_only_errors():
    assert core.is_stale(None, "2026-07-19T10:00:00Z", 3600) is True
    assert core.is_stale("2026-07-19T09:30:00Z", "2026-07-19T10:00:00Z", 3600) is False
    assert core.is_stale("2026-07-19T08:00:00Z", "2026-07-19T10:00:00Z", 3600) is True


# --------------------------------------------------------------------------
# 2. Configuration precedence — all four layers
# --------------------------------------------------------------------------


def test_configuration_precedence_default_file_environment_flag():
    base = {"base_url": "http://127.0.0.1:9"}

    only_default = config_module.resolve({}, base, {})
    assert only_default.max_items == 5
    assert only_default.provenance["max_items"] == "default"

    with_file = config_module.resolve({"max_items": 10}, base, {})
    assert with_file.max_items == 10
    assert with_file.provenance["max_items"] == "file"

    with_env = config_module.resolve({"max_items": 10}, {**base, "max_items": "20"}, {})
    assert with_env.max_items == 20
    assert with_env.provenance["max_items"] == "environment"

    with_flag = config_module.resolve(
        {"max_items": 10}, {**base, "max_items": "20"}, {"max_items": 40}
    )
    assert with_flag.max_items == 40
    assert with_flag.provenance["max_items"] == "flag"


def test_an_unsupplied_flag_does_not_override_anything():
    """argparse leaves absent options as None. None must mean 'no opinion',
    not 'set it to nothing' — the bug that makes every flag override the file."""
    resolved = config_module.resolve(
        {"max_items": 10},
        {"base_url": "http://127.0.0.1:9"},
        {"max_items": None, "retries": None},
    )
    assert resolved.max_items == 10
    assert resolved.provenance["max_items"] == "file"


def test_a_typo_in_the_configuration_file_is_an_error_not_a_shrug():
    with pytest.raises(config_module.ConfigError):
        config_module.resolve({"max_itmes": 10}, {"base_url": "http://127.0.0.1:9"}, {})


def test_a_missing_base_url_stops_the_run():
    with pytest.raises(config_module.ConfigError):
        config_module.resolve({}, {}, {})


def test_the_token_never_comes_from_the_configuration_file():
    resolved = config_module.resolve(
        {}, {"base_url": "http://127.0.0.1:9"}, {}, token="secret-value-123456"
    )
    assert resolved.token == "secret-value-123456"
    assert "secret-value-123456" not in config_module.explain(resolved, None)


# --------------------------------------------------------------------------
# 3. Idempotence, partial failure, dry run — against the local server
# --------------------------------------------------------------------------


def test_running_fetch_twice_processes_each_entry_once(tmp_path, live_fetcher, logger):
    (first, first_code), state_path = do_run(tmp_path, live_fetcher, logger, ["notes", "links"])
    assert first["status"] == "ok"
    assert first["new_entries"] == 5
    assert first_code == 0

    (second, code), _ = do_run(tmp_path, live_fetcher, logger, ["notes", "links"])
    assert second["new_entries"] == 0, "a second run must find nothing new"
    assert code == 0

    stored = json.loads(state_path.read_text())
    assert len(stored["entries"]) == 5
    ids = [entry["id"] for entry in stored["entries"]]
    assert len(ids) == len(set(ids)), "no entry may be recorded twice"


def test_one_broken_source_is_skipped_and_reported_while_others_succeed(
    tmp_path, live_fetcher, logger
):
    (summary, code), state_path = do_run(
        tmp_path, live_fetcher, logger, ["notes", "broken", "links"]
    )
    assert summary["status"] == "partial"
    assert summary["sources_ok"] == 2
    assert summary["sources_failed"] == 1
    assert "broken" in summary["failures"]
    assert code == core.EXIT_PARTIAL, "partial success must not exit 0"

    # The successful sources still did their work.
    stored = json.loads(state_path.read_text())
    assert stored["sources"]["notes"]["seen_ids"]
    assert stored["sources"]["links"]["seen_ids"]
    assert stored["sources"]["broken"]["last_error"]
    assert stored["last_success"] is None, "a partial run is not a success"

    # And the failure is in the human-readable summary, not only in the state.
    assert "FAILED: broken" in core.format_summary(summary, "r1")


def test_a_malformed_payload_is_not_retried_and_is_reported(tmp_path, live_fetcher, logger):
    (summary, code), _ = do_run(tmp_path, live_fetcher, logger, ["notes", "malformed"])
    assert summary["status"] == "partial"
    assert "missing title, published" in summary["failures"]["malformed"]
    assert code == core.EXIT_PARTIAL


def test_retry_with_backoff_recovers_a_temporarily_failing_source(
    tmp_path, live_fetcher, logger
):
    """The fixture server answers /feed/flaky.json with 503, 503, then 200."""
    (summary, code), _ = do_run(tmp_path, live_fetcher, logger, ["flaky"])
    assert summary["status"] == "ok"
    assert summary["new_entries"] == 1
    assert summary["retried"] == {"flaky": 3}, "it should have taken three attempts"
    assert code == 0


def test_dry_run_leaves_the_state_file_byte_identical(tmp_path, live_fetcher, logger):
    (_, _), state_path = do_run(tmp_path, live_fetcher, logger, ["notes"])
    before = state_path.read_bytes()

    (summary, code), _ = do_run(
        tmp_path, live_fetcher, logger, ["notes", "links"], dry_run=True
    )
    assert summary["new_entries"] == 2, "a dry run must still say what it would do"
    assert state_path.read_bytes() == before, "a dry run must not write"
    assert code == 0
    assert not list(tmp_path.glob("*.tmp")), "and must leave no temporary files"


def test_a_second_run_cannot_start_while_one_is_in_progress(tmp_path, live_fetcher, logger):
    lock_path = tmp_path / "state.json.lock"
    with state_module.Lock(lock_path):
        summary, code = runner.run_fetch(
            settings(sources=["notes"]),
            live_fetcher,
            adapters.FixedClock("2026-07-19T10:00:00Z"),
            tmp_path / "state.json",
            lock_path,
            logger,
        )
    assert summary["status"] == "locked"
    assert code == core.EXIT_LOCKED
    assert not (tmp_path / "state.json").exists()


# --------------------------------------------------------------------------
# 4. The state file survives being interrupted
# --------------------------------------------------------------------------


def test_an_interrupted_write_leaves_the_previous_state_intact(tmp_path):
    path = tmp_path / "state.json"
    state_module.write_atomic(path, {"version": 1, "marker": "original"})
    before = path.read_bytes()

    def power_cut():
        raise KeyboardInterrupt("the machine went away mid-write")

    with pytest.raises(KeyboardInterrupt):
        state_module.write_atomic(path, {"version": 1, "marker": "replacement"}, power_cut)

    assert path.read_bytes() == before, "the old state must survive untouched"
    assert json.loads(path.read_text())["marker"] == "original"
    assert not list(tmp_path.glob("*.tmp")), "and the temporary file must be cleaned up"


def test_a_corrupt_state_file_stops_the_run_rather_than_being_overwritten(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{ this is not json")
    with pytest.raises(state_module.StateError):
        state_module.load(path)
    assert path.read_text() == "{ this is not json"


def test_state_is_written_whole_or_not_at_all_under_a_reader(tmp_path):
    """os.replace is atomic: a reader sees the old file or the new one."""
    path = tmp_path / "state.json"
    state_module.write_atomic(path, {"version": 1, "n": 1})
    for n in range(2, 6):
        state_module.write_atomic(path, {"version": 1, "n": n})
        assert json.loads(path.read_text())["n"] == n


# --------------------------------------------------------------------------
# 5. The leak check — the most important assertion in this file
# --------------------------------------------------------------------------


def test_the_secret_never_reaches_the_log(tmp_path, capsys):
    """The token is supplied, is genuinely used (the fixture server rejects a
    request without it), and must appear nowhere in the structured output."""
    if not TOKEN:
        pytest.fail("FEEDKIT_TEST_TOKEN is not set; run this suite through tests/run_tests.sh")

    log = logging_setup.configure("debug", run_id="leak0001", secrets=[TOKEN])
    session = requests.Session()
    try:
        fetcher = adapters.HttpFetcher(
            session=session,
            base_url=BASE_URL,
            token=TOKEN,
            retries=2,
            backoff_seconds=0.0,
            sleeper=lambda _s: None,
            logger=log,
        )
        summary, _ = runner.run_fetch(
            settings(sources=["notes", "broken"]),
            fetcher,
            adapters.FixedClock("2026-07-19T10:00:00Z"),
            tmp_path / "state.json",
            tmp_path / "state.json.lock",
            log,
        )
    finally:
        session.close()

    captured = capsys.readouterr().out
    assert captured.strip(), "the run must actually have logged something"
    assert TOKEN not in captured
    assert TOKEN not in json.dumps(summary)
    assert TOKEN not in (tmp_path / "state.json").read_text()


def test_the_redacting_filter_catches_a_deliberate_leak(capsys):
    """Even when somebody logs the token by mistake — and one day somebody
    will — the filter replaces it before the line is written."""
    secret = "not-a-real-token-abcdef"
    log = logging_setup.configure("debug", run_id="leak0002", secrets=[secret])
    log.info("careless message containing %s", secret, extra={"url": f"?token={secret}"})
    captured = capsys.readouterr().out
    assert secret not in captured
    assert "***REDACTED***" in captured


def test_every_log_line_is_json_carrying_the_run_id_and_the_item(tmp_path, live_fetcher, capsys):
    log = logging_setup.configure("info", run_id="abc12345", secrets=[TOKEN] if TOKEN else [])
    runner.run_fetch(
        settings(sources=["notes", "broken"]),
        live_fetcher,
        adapters.FixedClock("2026-07-19T10:00:00Z"),
        tmp_path / "state.json",
        tmp_path / "state.json.lock",
        log,
    )
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    records = [json.loads(line) for line in lines]
    assert records, "an unattended run that logs nothing cannot be debugged"
    assert all(record["run_id"] == "abc12345" for record in records)
    assert all({"ts", "level", "event"} <= set(record) for record in records)

    failures = [r for r in records if r["level"] == "error"]
    assert failures, "the failed source must be logged at error level"
    assert failures[0]["source"] == "broken", "the log must name WHICH item failed"


# --------------------------------------------------------------------------
# 6. Rendering
# --------------------------------------------------------------------------


def test_report_renders_what_was_collected(tmp_path, live_fetcher, logger):
    (_, _), state_path = do_run(tmp_path, live_fetcher, logger, ["notes", "links"])
    stored = json.loads(state_path.read_text())
    rendered = core.render_report(stored, limit=3)
    assert "5 entries collected; showing 3" in rendered
    assert "Why stdout beats a log file" in rendered


def test_status_says_never_before_the_first_run():
    text, stale = core.render_status(core.empty_state(), "2026-07-19T10:00:00Z", 3600)
    assert "last success: never" in text
    assert stale is True
