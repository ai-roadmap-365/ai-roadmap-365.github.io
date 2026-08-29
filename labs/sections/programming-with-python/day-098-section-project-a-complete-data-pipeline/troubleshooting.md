# Troubleshooting, organised by cause

## The environment

**`FAIL: SQLAlchemy is not importable from ...`** or the same for pydantic.
The harness refuses to run rather than skipping silently, because a suite that
quietly skips the only thing it was written to test is worse than one that
fails. Fix it:

```bash
cd labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the harness somewhere else:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

**`the installed SQLAlchemy is the version requirements.txt pins` fails.**
Something upgraded the package out from under the pin. Reinstall from
`requirements/requirements.txt`. If you meant to upgrade, re-run the whole
harness and re-capture `expected-output/` — do not edit the captures by hand.

**`ModuleNotFoundError: No module named 'store'`** when you run a file in
`examples/` directly. The modules import each other by bare name, so
`examples/` has to be on the path:

```bash
export PYTHONPATH=examples
.venv/bin/python examples/demo_run.py
```

`demo_run.py` inserts its own directory into `sys.path` and so needs no
`PYTHONPATH`; the others do.

**`tomllib` not found.** `tomllib` arrived in Python 3.11. On 3.10 or older,
either upgrade or swap `tomllib` for the `tomli` package, which is the same API
under a different name.

## Stage 1 — ingest

**A fetch hangs and never returns.** You removed the `timeout=` from
`urlopen`, or you are running the starter before exercise 1. `urlopen` with no
timeout waits forever, and "forever" is a real duration in a scheduled job.

**`urllib.error.HTTPError: HTTP Error 401: Unauthorized`.** The fixture server
was started with `--token` and you did not set `PIPELINE_API_TOKEN`, or you set
it to something else. Both have to agree.

**A 404 source takes three attempts.** `RETRYABLE_STATUS` does not contain
404 — check that you are actually *using* the set, not just filling it in.
Retrying a 404 costs three round trips to learn what one told you.

**`ResourceWarning: unclosed <socket ...>` or an unraisable exception in
pytest.** `urllib.error.HTTPError` is a *file object*. If you read its body
without closing it, you leak a socket, and `starter/pytest.ini` turns warnings
into errors so you find out immediately rather than in month three of a job
that runs hourly. Use `with exc:` around the read.

## Stage 2 — validate

**The whole run dies with a `ValidationError`.** That is exercise 3 and it is
the skeleton's designed failure. Catch the error per record, build a
`Rejection`, and keep going.

**A rejection has no reason attached.** `ValidationError.errors()` gives a list
of dicts with `loc` (a tuple naming the field path) and `msg`. Without both, a
rejection tells whoever owns the source nothing they can act on.

**`humidity_pct: Input should be less than or equal to 100` for a record you
think is fine.** Check whether you are validating the record you think you are.
The `index` on the `Rejection` is the position inside that source's payload, and
`alpha` sends its bad records at index 2 and index 4.

**A record with 41.3 Celsius sails through.** Correct. Every field is inside
every declared range. A field validator sees one record and cannot know that the
previous reading five minutes earlier was 15.0. That check lives in
`examples/report.py` and it *flags* rather than deletes.

**`Extra inputs are not permitted`.** A source sent a field the model does not
declare, and `extra="forbid"` turned that into a visible event. This is working
as designed: silently ignoring new fields is how a schema drift goes unnoticed
for a quarter. Decide whether to add the field or reject the source.

## Stage 3 — store

**The second run doubles the table.** No idempotence key. Add the
`UniqueConstraint` and, separately, skip the keys already held. You need both:
the constraint keeps the *data* right, the skip keeps the *reported count*
right.

**`IntegrityError: UNIQUE constraint failed: readings.station_id,
readings.reading_id`.** Layer 2 caught what layer 1 missed. Working as designed
if you were attacking it on purpose; otherwise your pre-check is not looking at
the same key the constraint uses.

**`inserted` is 6 on the second run but `total_rows` is still 6.** You dropped
the "already held" pre-check and are relying on `ON CONFLICT DO NOTHING` alone.
The data is fine and the *report is lying*, which is the harder bug to notice.
Section 4 of the harness catches exactly this.

**`sqlite3.OperationalError: database is locked`.** Two writers. SQLite allows
one at a time, by design. In a pipeline this usually means two copies of your
scheduled job overlapped, which is a scheduling problem (Day 81's lock file),
not a database problem.

## Stage 4 — report

**The report's numbers change every time you run it.** It is reading the clock.
Pass `--report-at 2026-08-16T12:00:00Z`. A report that reads the clock cannot be
asserted on, cannot be backfilled and cannot answer "what did the 3 a.m. run
see?".

**`report_at must carry a UTC offset`.** You passed `2026-08-16T12:00:00`
without the `Z`. A timestamp with no offset is not an instant; it is an instant
plus somebody's assumption about which one (Day 95).

**A station is missing from the report entirely.** It is present with a count of
zero, because absence is a fact worth reporting — check you passed the full
`--sources` list. A station silently vanishing from a report is how a source
goes dark for a month unnoticed.

## Stage 5 — observe

**Log lines are missing.** `--log-level warning` suppresses the `info` lines,
including four of the five stage summaries. Set it back to `info`.

**The log goes to the terminal and pollutes the report.** It does not: the
report is on stdout and the log is on stderr. That separation is deliberate and
section 7 of the harness asserts it. Redirect them apart:

```bash
.venv/bin/python examples/pipeline.py ... > report.txt 2> run.jsonl
```

**The token appears in the log.** charlie echoes it back inside its error body.
Redact inside the logger, over every string value at any depth — not by
remembering not to log it.

**The scheduler reports success while a source has been dark for a week.** The
exit code is collapsing 3 into 0. Three outcomes need three codes.

## The tests

**`1 passed, 9 skipped` and you have done the work.** Delete that exercise's
`@exercise(...)` decorator in `test_stages.py`. The skips are the ladder, not
the wall.

**`expected-output/*.txt differs from this run`.** You changed behaviour in
`examples/`. Decide which is right. If the change is intended, re-run and
re-capture the files; never hand-edit a capture to match.

**The harness fails on `no such station` or a connection error.** The fixture
server did not start, or it was already killed. Section 7 waits up to two
seconds for it to announce its port; if your machine is heavily loaded, run the
harness again.

**`Address already in use`.** It should be impossible — the server binds port
0 and the kernel picks a free one. If you see it, something has hard-coded a
port; section 10 of the harness checks for exactly that.
