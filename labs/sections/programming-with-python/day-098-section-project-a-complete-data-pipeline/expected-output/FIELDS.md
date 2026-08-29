# What must match, and what may legitimately differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 on Apple Silicon (arm64), Python 3.14.0,
SQLAlchemy 2.0.51, pydantic 2.13.4, SQLite 3.53.3 (the library inside Python),
pytest 9.1.1, bash 3.2.57. Section 9 of `tests/run_tests.sh` compares all four
byte for byte against a live run.

## Must match exactly

These are the numbers the lesson argues from. If any of them changes, either
the fixtures changed or the pipeline stopped keeping a promise.

| Value | Where | Why it is fixed |
| --- | --- | --- |
| 9 records fetched | `stage.ingest` | alpha serves 5, bravo serves 4, charlie serves none |
| 7 attempts on run 1 | `stage.ingest` | alpha 1 + bravo 3 + charlie 3 |
| 5 attempts on run 2 | `stage.ingest` | bravo already recovered, so 1 + 1 + 3 |
| 7 accepted, 2 rejected | `stage.validate` | a-3 (temperature is prose) and a-5 (humidity 155) |
| 6 inserted, 1 duplicate on run 1 | `stage.store` | a-4 repeats a-2's idempotence key |
| 0 inserted, 7 duplicates on run 2 | `stage.store` | the whole point of the day |
| 6 total rows, always | `stage.store` | however many times you run it |
| exit code 3 | `run.end` | charlie is dark and two records were rejected |
| alpha 18.4 / 19.0 / 18.7 | the report | 184 and 190 deci-Celsius; the mean is exact |
| bravo 13.6 / 41.3 / 23.3 | the report | 136, 150 and 413; the mean is exact |
| charlie 0 readings | the report | reported rather than omitted, because absence is a fact |
| 5 of 6 in window | the report | b-1 at 23:30 the previous day falls outside 12 hours |
| 1 suspect reading | the report | +26.3 C in 5 minutes, stored and flagged |

## Deliberately made deterministic

Two things in a real pipeline are not reproducible, and both were made so on
purpose rather than left to luck:

- **Log timestamps.** `--fixed-clock` (and `logs.fixed_clock()` in the demo)
  starts at `2026-08-16T12:00:00Z` and advances one second per line. A real run
  uses `logs.utc_clock`, and its `ts` values will be the wall clock. Nothing
  else in the log changes.
- **The report instant.** `--report-at` is a parameter. Omit it and the report
  covers the window ending now, which is correct behaviour and not comparable
  against a stored capture. That is the trade the lesson argues for.

## May legitimately differ on another machine

- **The port.** The fixture server binds 127.0.0.1 on port 0 and the kernel
  picks. `demo_run.py` prints `http://127.0.0.1:<port>` for exactly this
  reason; nothing in the captures depends on the number.
- **The temporary directory.** `demo_run.py` works inside one and removes it,
  and it deliberately runs with that directory as its working directory so
  `database_url` can stay at its short default value. No absolute path from
  the authoring machine appears in any capture, and section 10 of the harness
  checks that.
- **Python, SQLAlchemy, pydantic and SQLite versions.** Section 1 prints them
  and asserts the two pinned ones match `requirements/requirements.txt`. A
  different pydantic minor version could reword a validation message — the
  harness asserts on the field name and the leading words of the message
  (`Input should be a valid number`, `Input should be less than or equal to
  100`), which are the parts that carry meaning.
- **pytest's summary line.** `1 passed, 9 skipped in 0.64s` includes a
  duration. The harness matches `1 passed, 9 skipped` and ignores the rest;
  `starter-progress.txt` stores one particular run of it.

## What is not claimed

- Nothing here was run on Linux or on native Windows. The code uses `pathlib`,
  `tempfile` and the standard library's HTTP server, and no platform-specific
  behaviour is claimed for either.
- No orchestrator (Airflow, Dagster, Prefect, dbt) is installed here, no
  output from one is reproduced anywhere in this lab or the lesson, and
  section 1 of the harness asserts that this remains true.
