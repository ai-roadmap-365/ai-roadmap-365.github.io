# Expected output — Day 074 lab

These are real captured runs from the authoring machine (macOS 26.5.1, Apple
Silicon, Python 3.14.0, pytest 9.1.1, bash 3.2.57, 2026-07-19). Absolute paths
appear as `<repo>`, `<tmp>` and `<python3.14>`; on your machine they are your
real paths.

## Files

- `sample-run.txt` — `examples/demo.py`, `examples/doubles_demo.py` and
  `examples/autospec_demo.py`, each run end to end.
- `pytest-runs.txt` — the six example suites run individually, including the
  two that are **supposed to fail**, with their full failure output.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  exercises still unfinished (49 checks, 0 failures, exit 0).

## What is deterministic and what is not

Almost everything here is byte-identical on every machine. Three things are
not, and each one is a lesson rather than a defect:

| Varies | Where | Why |
| --- | --- | --- |
| The readings and the timings | `demo.py` section 1, and the failure diff in `test_patch_wrong_target.py` | That section calls the real stand-in service on purpose. It is slow and random — which is the entire argument for stubbing it. |
| Mock object ids, e.g. `id='4465297120'` | `autospec_demo.py`, `pytest-runs.txt` | CPython object addresses. Ignore them. |
| Temporary directory names | pytest's `tmp_path` | A fresh directory per test, cleaned up by pytest. |

Everything in `demo.py` sections 2 to 6, all of `doubles_demo.py`, and every
number in the passing suites is identical on every run, because none of that
code can reach a clock, a network, a disk or a random number generator.

## Required behaviour — the passing suites

| Command | Result |
| --- | --- |
| `pytest examples/test_patch_right_target.py -q` | `2 passed`, exit 0 |
| `pytest examples/test_report_v2_fakes.py -q` | `10 passed`, exit 0 |
| `pytest examples/test_model_boundary.py -q` | `14 passed`, exit 0 |
| `pytest examples/test_autospec_naive.py -q` | `1 passed`, exit 0 — **and that is the problem** |

## Required behaviour — the suites that must FAIL

| Command | Result | What it proves |
| --- | --- | --- |
| `pytest examples/test_autospec_specced.py -q` | `2 failed`, exit 1, `AttributeError: Mock object has no attribute 'fetch_radings'` | `create_autospec` catches the typo that a bare `Mock()` waves through |
| `pytest examples/test_patch_wrong_target.py -q` | `1 failed`, exit 1, an `AssertionError` on the report text, in about 0.4 s | patching `sensor_service.fetch_readings` reaches nobody, because `report_v1` bound its own name at import time |

The test suite asserts both of these failures. A suite that could not tell the
naive test from the specced one would be proving nothing at all.

## Required behaviour — the doubles

| Double | Kind | Contract |
| --- | --- | --- |
| `DummyClient` | dummy | `fetch_readings(...)` raises `AssertionError`; it exists to fill a slot |
| `frozen_clock(day)` | stub | returns a zero-argument callable answering `day` |
| `StubSensorClient(readings)` | stub | `fetch_readings(...)` returns a **copy** of `readings`, ignoring both arguments |
| `SpyClock(day)` | spy | `__call__()` returns `day` and increments `.calls` |
| `RecordingSleep()` | spy | `__call__(seconds)` appends to `.waits` and never sleeps |
| `FakeSensorClient(script)` | fake | records `(station, day)` in `.calls`; raises a scripted `Exception` instance or returns a copy of a scripted list; raises `ReadingsUnavailable` when the script runs out |
| `ScriptedModel(script)` | fake | records prompts in `.prompts`; raises or returns the next scripted reply |

## Required behaviour — the report core (`report_v2.py`)

With no files present anywhere:

| Call | Result |
| --- | --- |
| `summarise("ALPHA", DAY, READINGS)` | `DailyReport("ALPHA", DAY, 24, 12.0, 22.0, 17.0)` |
| `summarise("ALPHA", DAY, [])` | raises `ReportError` containing `empty day` |
| `DailyReport(...).render()` first line | `station ALPHA — 2026-04-12` |
| `DailyReport(...).render()` last line | `  mean     17.0` |
| `DailyReport(...).filename()` | `ALPHA-2026-04-12.txt` |
| `build_report(..., clock=SpyClock(DAY), ...)` | the clock is read exactly **once** |
| `build_report(..., client=FakeSensorClient([READINGS]))` | `client.calls == [("ALPHA", "2026-04-12")]` |
| two `ReadingsUnavailable` then readings, `attempts=3` | succeeds; `RecordingSleep().waits == [0.5, 1.0]` |
| three `ReadingsUnavailable`, `attempts=3` | raises `ReportUnavailable` containing `after 3 attempts` |
| `attempts=0` with a `DummyClient` | raises `ReportError` containing `attempts must be at least 1`, **without** calling the client |
| `import report_v2` | imports `datetime` and `dataclasses` only — no `pathlib`, `time`, `random`, `open` or `print` |

`READINGS` is `[12.0, 14.0, 20.0, 22.0] * 6` — 24 values whose mean is exactly
17.0. Check it by hand: `(12 + 14 + 20 + 22) / 4 = 17`.

## Required behaviour — the model boundary (`model_boundary.py`)

| Call | Result |
| --- | --- |
| `build_prompt(report)` | contains `station: ALPHA`, `date: 2026-04-12`, `mean: 17.0`, and `cold, mild, warm, hot` |
| `parse_verdict("label: mild\nconfidence: 0.82\nnote: calm")` | `Verdict("mild", 0.82, "calm")` |
| a reply with a chatty preamble | still parses |
| `Label:  MILD ` | parses to `mild` — case and spacing are tolerated |
| a missing `label` line | `MalformedResponse: missing field(s): label` |
| `label: balmy` | `MalformedResponse: 'balmy' is not one of cold, mild, warm, hot` |
| `confidence: quite` | `MalformedResponse: confidence 'quite' is not a number` |
| `confidence: 1.4` | `MalformedResponse: confidence 1.4 is outside 0.0-1.0` |
| one malformed reply then a good one, `attempts=2` | succeeds; the **same** prompt was resent; `RecordingSleep().waits == [1.0]` |
| two unusable replies, `attempts=2` | raises `ModelError` naming `MalformedResponse` as the last failure |

## The test suite

`bash tests/run_tests.sh` prints one line per check and ends with a count.

| Starter state | Final line | Exit |
| --- | --- | --- |
| exercises unfinished | `49 checks, 0 failure(s).` | 0 |
| all exercises complete | `39 checks, 0 failure(s).` | 0 |

The count goes **down** when you finish, because ten structural checks ("does
`fakes.py` define `SpyClock`?") are replaced by four behavioural ones that hold
your files to the same standard as the reference. Any check failing exits
non-zero, so the suite is usable in continuous integration.

## Platform notes

- **macOS and Linux** — identical. `bash`, `python3` and `mktemp -d` behave the
  same; the suite passes `-p no:cacheprovider` so pytest writes no cache
  directory into your tree.
- **Windows** — use WSL and follow the Linux path. The report header and
  several headings contain an em dash, so a UTF-8 terminal is needed for them
  to render; the numbers and the exit codes are unaffected.
- **Python version** — verified on 3.14.0 only. The parenthesised multi-line
  `with (...)` form used in the patch tests needs Python 3.10 or newer; on an
  older interpreter, use nested `with` statements instead. `create_autospec`
  and `spec=` have behaved as shown here for many releases, but the exact
  wording of the `AttributeError` message differs between versions — assert on
  the exception type, never on the message text.
