# The brief: make a finished-looking pipeline actually keep its promises

You have inherited `stages.py`. It runs. It fetches from three weather stations,
validates what comes back, stores it, prints a summary and exits. On a good day,
against healthy sources, you would never know anything was wrong with it.

Your job is the bad day.

Nine exercises, marked `EXERCISE n` in `stages.py`. Each one turns a stage that
*works* into a stage that keeps a **promise** — a statement about what happens
when something goes wrong at three in the morning with nobody watching.

| # | Stage | The promise you are adding |
| --- | --- | --- |
| 1 | Ingest | Every fetch has a deadline, and a source that blinks gets another chance |
| 2 | Ingest | Only failures worth retrying are retried |
| 3 | Validate | One bad record does not end the run; every bad record is collected |
| 4 | Validate | The gate refuses what the store would have to argue with |
| 5 | Store | Running twice stores once |
| 6 | Report | The report instant is a parameter, so the answer is reproducible |
| 7 | Observe | Every log line carries the run id |
| 8 | Observe | Partial success has its own exit code |
| 9 | Observe | A secret cannot reach the log, even when an upstream echoes it back |

## How to work

```bash
cd labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline
.venv/bin/pytest starter -q          # 1 passed, 9 skipped — the starting line
```

The one passing test proves the skeleton runs end to end. Read what it asserts:
the skeleton **reports its own failure**, because it aborts at the first
malformed record. That is exercise 3, and you can see it before you have written
a line.

Then, for each exercise in order:

1. Read the `EXERCISE n` block in `stages.py`. It names the exact change.
2. Make the change.
3. Delete that exercise's `@exercise(...)` decorator in `test_stages.py`.
4. `.venv/bin/pytest starter -q` — the test tells you whether the promise holds.

Each exercise's docstring also names a `-k` filter, so you can run one at a time:

```bash
.venv/bin/pytest starter -q -k idempotent
```

## What the fixture server does to you

Nothing in this lab reaches the internet. `examples/fixture_server.py` binds
127.0.0.1 on a port the kernel picks, and it is hostile on purpose:

- **alpha** answers immediately with five records: two good, one with a
  temperature of `"warm"`, one that repeats an earlier record's id exactly, and
  one with a humidity of 155 per cent.
- **bravo** returns 500 twice and then 200. Its counter is per server process,
  so the *second* pipeline run finds it healthy — which is what a transient
  failure actually looks like.
- **charlie** returns 500 every time, and its error body politely quotes your
  API token back at you.
- **delta** returns 404. Retrying it is a waste of three round trips.

One of bravo's records is the interesting one: `b-4` reports 41.3 Celsius five
minutes after 15.0 Celsius. Every field is legal. Exercise 4 will not catch it
and is not supposed to. Think about where that check belongs before you look at
`examples/report.py`.

## When you are done

```bash
.venv/bin/pytest starter -q          # 10 passed
bash tests/run_tests.sh              # 84 checks, 0 failure(s)
```

The reference implementation of all nine is in `examples/stages_solved.py`, and
the production version — the same promises, written out at full size across five
modules — is the rest of `examples/`. Read the reference *after* you have tried,
not instead.
