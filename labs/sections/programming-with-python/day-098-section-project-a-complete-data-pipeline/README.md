# Day 098 lab — The Whole Pipeline

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Section Project: A Complete Data Pipeline
- **Day number:** 98 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-098-section-project-a-complete-data-pipeline
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-098-section-project-a-complete-data-pipeline` when the site is running.
<!-- generated-links:end -->

## Purpose

You run a real data pipeline, break it on purpose, and prove each of its five
promises with a number.

The pipeline fetches weather-station readings over HTTP, validates them at the
boundary, stores them in a schema with constraints, reports on a window ending
at an instant you choose, and writes one structured log line per stage. It is
the whole of Course 02 assembled into one working program: Day 78's HTTP and
retries, Day 80's command line, Day 81's scheduling and exit codes, Day 84's
partial-success design, Days 85-91's SQL and schema thinking, Day 93's
SQLAlchemy, Day 94's pydantic gate, Day 95's time zones, Day 96's read on where
concurrency belongs, and Day 97's logging and configuration.

The organising idea is one sentence, and everything in this lab is built to
make it concrete: **a pipeline is not a script that moves data; it is a set of
promises about what happens when something goes wrong.**

So the sources are hostile on purpose. One station fails twice and then
recovers. One fails permanently and quotes your API token back at you inside its
error body. One name is simply wrong and answers 404. Inside the good payloads
sit a record whose temperature arrived as the word `"warm"`, a record that
repeats an earlier record's id exactly, a humidity of 155 per cent, and — the
interesting one — a reading of 41.3 Celsius five minutes after 15.0 Celsius, in
which every single field is legal.

Then you run the pipeline **twice** against one database and watch the second
run store nothing.

Everything is offline. `examples/fixture_server.py` binds 127.0.0.1 on a port
the kernel chooses and stands in for the public API, exactly as Days 82, 84 and
96 do. The only moment this lab needs the network is `pip install`.

## Learning objectives

By the end of this lab you will be able to:

1. Name the promise each of the five pipeline stages makes, and point at the
   code that keeps it.
2. Fetch with a deadline and bounded retries, and decide from a status code
   whether a failure describes a moment or a mistake.
3. Build a pydantic gate that **collects** every bad record with a field path
   and a reason, rather than dying on the first one.
4. Design an idempotence key, enforce it in two layers, and explain why one
   layer keeps the data right while the other keeps the reported count right.
5. Demonstrate that running the pipeline twice stores the data once, and that
   the report and the exit code are identical both times.
6. Build a report at a **parameterised instant** and state the three things
   that buys: a testable number, a backfill, and an incident timeline.
7. Emit one structured log line per stage with a run id threaded through, and
   redact a secret inside the logger rather than by remembering.
8. Choose an exit code that distinguishes success from partial success from
   failure, and say what each collapse costs.
9. Recognise a record that is valid but wrong, and argue for flagging it rather
   than dropping it.

## Prerequisites

- **Day 78** — HTTP, status codes, timeouts and retry with backoff. Stage 1 is
  that lesson with a budget.
- **Day 80** — `argparse`. `examples/pipeline.py` is an ordinary CLI.
- **Day 81** — scheduling, exit codes and the idea that a scheduled job must be
  safe to run twice.
- **Day 84** — the automation toolkit: partial success, config precedence, and
  a fixture server standing in for a real API.
- **Days 85-91** — the relational model, `SELECT`, constraints, indexes, and
  schema design. `examples/store.py` is Day 88 and Day 91 applied without
  ceremony.
- **Day 93** — SQLAlchemy 2.0 declarative models and the Session.
- **Day 94** — pydantic models, `Field` constraints and `ValidationError`.
- **Day 95** — timezone-aware datetimes and ISO 8601 in UTC.
- **Day 96** — the difference between waiting work and computing work.
- **Day 97** — structured logging, configuration precedence, and redaction.
- **Day 43** — `python3 -m venv`; the install below is the same pattern.

## Supported operating systems

- **macOS** — exercised here; every capture in `expected-output/` comes from
  macOS 26.5.2 on Apple Silicon.
- **Linux** — expected to behave identically with Python 3.11 or newer. Not run
  here, so no capture is claimed for it.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` is a
  bash script and uses `mktemp -d`; it was not run on native Windows and no
  behaviour is claimed for it there. The Python files use `pathlib` and
  `tempfile` and have no Unix dependency.

## Hardware requirements

Nothing notable. The largest thing here is a nine-record payload and a SQLite
file of a few kilobytes. No GPU, no minimum RAM worth stating.

## Required software

- `python3` 3.11 or newer (3.14.0 here). 3.11 is the floor because
  `examples/config.py` reads TOML with `tomllib`.
- `SQLAlchemy` 2.0.51, `pydantic` 2.13.4 and `pytest` 9.1.1, all pinned in
  `requirements/requirements.txt` and installed into a lab-local `.venv`.
- `bash` for the test harness (3.2.57 here — the version macOS ships).

SQLite arrives with Python; there is nothing to install for it. The HTTP client
and the fixture server are both standard library.

**Not used here:** Airflow, Dagster, Prefect and dbt. The lesson describes all
four from their documentation and says plainly that no output is reproduced for
any of them. Section 1 of the test suite asserts that none is importable, so the
claim cannot go quietly stale.

## Free and open-source options

| Tool | Licence | Cost | Note |
| --- | --- | --- | --- |
| Python | PSF licence | Free | 3.11 or newer |
| SQLAlchemy | MIT | Free | Core and ORM ship together; no commercial edition |
| pydantic | MIT | Free | pydantic-core is Rust and ships as a wheel |
| pytest | MIT | Free | The runner from Week 11 |
| SQLite | Public domain | Free | Arrives with Python; no server to run |
| Apache Airflow | Apache-2.0 | Free to self-host | Described in the lesson; not installed here |
| Dagster | Apache-2.0 | Free to self-host | Described in the lesson; not installed here |
| Prefect | Apache-2.0 | Free to self-host | Described in the lesson; not installed here |
| dbt Core | Apache-2.0 | Free | Described in the lesson; not installed here |

Every one of the four orchestrators also has a commercial hosted product from
its own vendor. No prices, tier limits or free-tier allowances are quoted
anywhere in this lab, because they change and an out-of-date price is worse than
no price.

## Installation

```bash
cd labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python -c "import sqlalchemy, pydantic; print(sqlalchemy.__version__, pydantic.VERSION)"
```

Expect `2.0.51 2.13.4`. That install is the only moment this lab needs the
network. **Nothing after it does** — see "Security notes".

## File structure

```
day-098-section-project-a-complete-data-pipeline/
├── README.md                   this file
├── metadata.yml                lab metadata and the recorded run
├── security.md                 the secret, the gate as a boundary, retry as amplification
├── troubleshooting.md          every error you are likely to hit, by stage
├── requirements/
│   ├── README.md               why each pin exists, and what is deliberately absent
│   └── requirements.txt        SQLAlchemy==2.0.51, pydantic==2.13.4, pytest==9.1.1
├── examples/
│   ├── fixture_server.py       the hostile local API — read this FIRST
│   ├── config.py               four layers of configuration, with provenance
│   ├── logs.py                 one JSON line per stage, run id, redaction
│   ├── ingest.py               stage 1 — timeout, bounded retry, partial success
│   ├── validate.py             stage 2 — the pydantic gate that collects
│   ├── store.py                stage 3 — the schema and the idempotence key
│   ├── report.py               stage 4 — a parameterised instant, and the suspect check
│   ├── pipeline.py             the CLI that wires all five and picks the exit code
│   ├── pipeline.toml           layer 2 of configuration, as a worked example
│   ├── demo_run.py             the whole pipeline, twice, narrated
│   └── stages_solved.py        the starter's answer key, all nine exercises done
├── starter/
│   ├── 00_brief.md             the brief: nine promises to add
│   ├── stages.py               your work: a finished-looking pipeline that is wrong
│   ├── test_stages.py          1 passing, 9 waiting — each names its exercise
│   ├── conftest.py             import paths and the session fixture server
│   └── pytest.ini              warnings are errors here
├── tests/
│   └── run_tests.sh            84 checks in ten sections
└── expected-output/
    ├── FIELDS.md               what must match and what may differ
    ├── demo.txt                captured from a real run
    ├── cli-run.txt             captured from a real run
    ├── config-provenance.txt   captured from a real run
    └── starter-progress.txt    captured from a real run
```

## How to run

```bash
cd labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline
export PYTHONPATH=examples

# 1. The whole thing, twice, narrated. Start here.
.venv/bin/python examples/demo_run.py

# 2. Where every configuration value came from
PIPELINE_LOG_LEVEL=warning PIPELINE_API_TOKEN=demo-token-value \
  .venv/bin/python examples/pipeline.py \
  --config-file examples/pipeline.toml --window-hours 24 --explain-config

# 3. Your turn
.venv/bin/pytest starter -q

# 4. The whole suite
bash tests/run_tests.sh
```

To drive the CLI against a live fixture server yourself, start the server in one
terminal and note the port it prints on its first line:

```bash
.venv/bin/python examples/fixture_server.py --token demo-token-value
```

Then, in another terminal (substituting the port it printed):

```bash
cd $(mktemp -d)
PIPELINE_API_TOKEN=demo-token-value PYTHONPATH=<lab>/examples \
  <lab>/.venv/bin/python <lab>/examples/pipeline.py \
  --base-url http://127.0.0.1:PORT --sources alpha,bravo,charlie \
  --report-at 2026-08-16T12:00:00Z --window-hours 12 \
  --run-id run-cli000001 --fixed-clock
echo "exit=$?"
```

Then work through `starter/00_brief.md` and `starter/stages.py`.

## What the commands do

| Command | What it does | What to look at |
| --- | --- | --- |
| `demo_run.py` | Runs the whole pipeline twice against one database, then demonstrates retry policy, the secret leak, and the run id separately | Section 4: `rows inserted  run 1: 6  run 2: 0`, with the store still holding 6 |
| `--explain-config` | Resolves all four configuration layers and prints where each value came from | `api_token ***redacted*** environment` — the source is reported, the value never is |
| `pipeline.py` (live) | One real run: report on stdout, structured log on stderr, exit code to the shell | `exit=3` — partial success, because charlie is dark and two records were rejected |
| `pytest starter -q` | Your exercise suite | `1 passed, 9 skipped` before you start |
| `run_tests.sh` | Everything, including a byte-for-byte comparison against all four captures | The final line |

## Expected output

Every file in `expected-output/` was captured from a real run on 2026-08-16 and
is compared byte for byte by section 9 of the harness.

**The whole day, in one block from `demo.txt`:**

```
  rows inserted        run 1:  6    run 2:  0
  duplicates skipped   run 1:  1    run 2:  7
  rows in the store    run 1:  6    run 2:  6
  reports identical    True
  exit codes identical True
```

**Retry policy, from `demo.txt`:**

```
  bravo    attempts=3  ok=True  status=200  (500 twice, then 200)
  delta    attempts=1  ok=False  status=404  (404, and it will stay 404)
```

**The leak, and the redactor that caught it, from `demo.txt`:**

```
  raw error body from charlie : upstream credentials rejected for token demo-token-value
  after the log redactor      : upstream credentials rejected for token ***redacted***
```

**The report, from `cli-run.txt`:**

```
Station readings report
  as of        2026-08-16T12:00:00Z
  window       12h, from 2026-08-16T00:00:00Z
  in window    5 of 6 stored readings

  station      readings     min C     max C    mean C
  ------------ -------- --------- --------- ---------
  alpha               2      18.4      19.0      18.7
  bravo               3      13.6      41.3      23.3
  charlie             0         -         -         -

  suspect readings (1) — stored and flagged, not dropped:
  bravo: +26.3 C in 5 minutes (2026-08-16T11:45:00Z -> 2026-08-16T11:50:00Z)
```

Three things in that report are decisions rather than accidents. **charlie is
listed with zero readings** rather than omitted, because a station vanishing
from a report is how a source goes dark for a month unnoticed. **Five of six**
readings are in the window because b-1 was recorded at 23:30 the previous day
and the window is twelve hours — the window is a parameter, and a 24-hour one
holds all six. And **the 41.3 Celsius reading is present**, flagged, not
deleted: every one of its fields is legal, so the validation gate could not have
caught it without a rule about the sequence, and dropping it silently would
replace a visible anomaly with an invisible gap.

**Configuration provenance, from `config-provenance.txt`:**

```
setting                value                  source
---------------------  ---------------------  ------------
api_token              ***redacted***         environment
base_url               http://127.0.0.1:8080  default
database_url           sqlite:///pipeline.db  default
log_level              warning                environment
report_at              <unset>                default
retry_attempts         3                      file
retry_backoff_seconds  0.05                   default
sources                alpha,bravo,charlie    file
timeout_seconds        3.0                    file
window_hours           24                     command line
```

All four layers are visible in that one table: a default nobody touched, three
values from the TOML file, two from the environment, and one from an explicit
flag. Knowing that `timeout_seconds` is 3.0 is half an answer at 3 a.m.; knowing
it is 3.0 *because the deployment's config file says so* is the whole answer.

The harness ends with:

```
84 checks, 0 failure(s).
```

## Validation steps

1. **The install is the version the lab claims.**
   `.venv/bin/python -c "import sqlalchemy, pydantic; print(sqlalchemy.__version__, pydantic.VERSION)"`
   prints `2.0.51 2.13.4`, matching `requirements/requirements.txt`.
2. **The demo exits 0 and its narrative matches.** `demo_run.py` ends with
   `temporary database removed: True`.
3. **The pipeline exits 3, not 0.** Run the live CLI from "How to run" and
   check `echo "exit=$?"`. A partially successful run must not look like a
   clean one.
4. **The second run stores nothing.** Run the same command again with a
   different `--run-id`. `stage.store` reports `inserted: 0` and `total_rows`
   is unchanged at 6.
5. **No secret in the log.** `grep demo-token-value run.jsonl` finds nothing;
   `grep redacted run.jsonl` finds the line where it would have leaked.
6. **The starter baseline is green.** `.venv/bin/pytest starter -q` reports
   `1 passed, 9 skipped` before you have written anything.
7. **The captures still match.** `bash tests/run_tests.sh` compares all four
   byte for byte.
8. **The lab left nothing behind.** After the run,
   `find . -name '*.db' -not -path './.venv/*'` and
   `find . -type d -name __pycache__ -not -path './.venv/*'` are both empty.
   The harness checks this too.

## Tests

```bash
bash tests/run_tests.sh
```

84 checks in ten sections: the environment and the pinned versions; the demo
run; the report's exact values; idempotence attacked directly; validation
collected, counted and explained; configuration provenance; the command-line
pipeline against a live server with its exit codes; the starter; the captured
output; and hygiene.

The harness **resolves its tools** — `$PYTHON` and `$PYTEST` override first,
then `./.venv/bin/<tool>`, then whatever is on `PATH` — and **fails loudly with
install instructions rather than skipping silently** if SQLAlchemy or pydantic
is not importable.

Four checks are worth knowing about because they are unusual:

- **Section 1 asserts that Airflow, Dagster, Prefect and dbt are *not*
  installed.** The lesson says plainly that no output from any of them is
  reproduced. If somebody installs one here, that statement stops being the
  whole truth, and the suite fails rather than letting the text go stale.
- **Section 4 attacks the idempotence key from outside the application.** It
  goes around `store_readings` entirely and asks the database to accept a
  duplicate. `UNIQUE constraint failed: readings.station_id, readings.reading_id`
  is the proof that the guarantee belongs to the schema and not to anybody's
  good intentions.
- **Section 7 runs the pipeline twice and diffs the reports byte for byte.**
  Idempotence that is asserted rather than observed is a wish.
- **Section 8 runs the starter suite a second time against
  `examples/stages_solved.py`.** That proves the nine exercises are *reachable*
  rather than merely stated, and it means a change that makes one impossible
  fails the build.

This harness has been proved to fail, twice, in two different ways.

Deleting the `UniqueConstraint` from `examples/store.py` and re-running reports
**40 failures**, because `ON CONFLICT DO NOTHING` needs the unique index it
names and the whole store stage stops working.

The subtler break is more instructive. Removing only the "already held"
pre-check in `store_readings` — leaving the constraint in place — reports:

```
  FAIL: run 2 stored NOTHING — the idempotence key held
  FAIL: the second store inserts nothing and says so
  FAIL: a duplicate INSIDE one batch is caught too
  FAIL: and it inserted nothing, because everything was already held
  FAIL: the second run's row records none
  FAIL: expected-output/demo.txt differs from this run
84 checks, 6 failure(s).
```

with a non-zero exit status. Look at what the diff says:

```
< "event": "stage.store", "considered": 7, "inserted": 0, "duplicates_skipped": 7, "total_rows": 6
> "event": "stage.store", "considered": 7, "inserted": 6, "duplicates_skipped": 1, "total_rows": 6
```

`total_rows` is **still 6**. The database was never wrong. The *report* was. That
is the whole argument for two layers: the constraint keeps the data right, and
the pre-check keeps the count honest — and a pipeline that lies about how much
it did is a pipeline nobody can reason about.

## Cleanup

```bash
cd labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline
rm -f pipeline.db
find . -type d -name '__pycache__' -not -path './.venv/*' -prune -exec rm -rf -- {} +
rm -rf starter/.pytest_cache .pytest_cache
rm -rf .venv                # optional: removes the lab virtual environment
git checkout -- starter/    # optional: reset your exercise work
```

`demo_run.py` and the test harness both work inside temporary directories they
create and remove — the demo prints `temporary database removed: True` as proof
rather than as a promise. `pipeline.db` only appears if you ran the CLI by hand
from inside the lab directory.

## Troubleshooting

`troubleshooting.md` covers every error you are likely to hit, organised by
stage. The four you are most likely to meet:

- **The run dies with a `ValidationError`** — that is the skeleton's designed
  failure and it is exercise 3. Collect, do not abort.
- **`ResourceWarning` / unraisable exception in pytest** — `HTTPError` is a file
  object. Not closing it leaks a socket, and in a job that runs hourly forever
  that is a slow resource-exhaustion bug nothing warns you about in production.
  `starter/pytest.ini` turns warnings into errors precisely so you find it now.
- **`inserted` is 6 on the second run but `total_rows` is still 6** — you have
  one layer of idempotence, not two. The data is fine and the report is lying.
- **The report's numbers change every run** — it is reading the clock. Pass
  `--report-at`.

## Security notes

`security.md` has the full treatment. The short version:

- The lab needs the network exactly once, to install three packages. Section 10
  of the harness scans every script and fails if any URL points anywhere except
  127.0.0.1.
- **The secret is real and the leak it catches is real.** charlie's error body
  quotes the API token back at you. Nobody wrote code to log it; an upstream
  service put it in a message and the message went to the log. Redaction lives
  inside the logger, where it cannot be forgotten.
- **The validation gate is a security boundary**, not merely a quality one:
  `extra="forbid"` makes a source changing shape a visible event, and length
  limits bound what one broken source can write into your table.
- **Retry is an amplification risk.** Three attempts against a struggling
  service is three times the load at the worst possible moment. Add jitter and
  honour `Retry-After` in production.
- **Every stored row names the run that wrote it**, which is what makes
  `DELETE FROM readings WHERE ingested_by_run = 'run-abc123'` a complete undo of
  one bad backfill.
- Every station name, reading and token here is invented.

## Extension exercises

1. **Fetch the sources concurrently.** Day 96 said the fetch is waiting work.
   Replace the sequential loop in `fetch_all` with `ThreadPoolExecutor` or
   `asyncio.gather`, and then measure — with three sources against a loopback
   server, see whether it is even detectable. Forming an opinion about when the
   complexity is worth it is the exercise; the code is the easy part.
2. **Add a backfill mode.** `--report-at` already lets you ask about the past.
   Give the pipeline a `--since` and `--until` so it can re-fetch a missed day.
   Because the store is idempotent, you should be able to run it over a range
   that overlaps what you already hold and change nothing.
3. **Undo a run.** Write `pipeline.py --undo-run <run_id>` using the
   `ingested_by_run` column, and then convince yourself with the `runs` table
   that you deleted exactly what that run wrote and nothing else.
4. **Give the gate a sequence rule.** Move the suspect-jump check out of the
   report and into a second validation pass that has access to the previously
   stored reading for that station. Decide whether the result should be
   rejected, flagged, or quarantined in a third table — and write down why.
5. **Add a dead-letter table.** Right now rejections are logged and then gone.
   Store them, with their reason and their raw payload, so somebody can fix the
   source and replay them. Then decide what "replay" means for idempotence.
6. **Break the clock.** Set `report_at` to an instant inside the window and
   watch the numbers change; then remove the parameter and try to write a test
   for the result. The frustration is the lesson.
7. **Add a second store.** Write the same accepted readings to a JSON Lines
   file as well as the database, and make *that* idempotent too. It is harder
   than it looks, and understanding why is understanding what a unique
   constraint was doing for you.

## Navigation

- **This lab:** Day 98 — Section Project: A Complete Data Pipeline
  (`labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline/`).
- **Previous day:** Day 97 — Logging and Configuration
  (`labs/sections/programming-with-python/`).
- **Next day:** Day 99
  (`labs/sections/programming-with-python/`), which begins the next week of
  Programming with Python.
- **Week 14 — Data Formats and Pipelines**, inside Programming with Python →
  Data and Databases. This is the week's final day and the section project: the
  pieces from Days 78 to 97 assembled into one program that keeps its promises.
