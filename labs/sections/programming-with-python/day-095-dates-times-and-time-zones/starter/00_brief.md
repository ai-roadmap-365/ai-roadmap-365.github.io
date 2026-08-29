# The brief — "The Hour That Happened Twice"

Read this before you write any code. It is short, and it is the whole job.

## What happened

A small subscription business runs one job every night. It reconciles the
day's payments, writes a partition of rows into the warehouse, and emails a
summary. It has run at 01:30 every night for two years, and the schedule entry
says exactly that: **01:30, Europe/London**.

Three things went wrong on three different nights, and nobody connected them
for a month.

**On the night of 25 October, every customer was charged twice.** The job ran
at 01:30, finished, and ran again at 01:30. Both runs were legitimate: the
local clock genuinely read 01:30 twice that night, an hour apart, because the
clocks went back at 02:00.

**On the night of 29 March, the job did not run at all.** The clocks went
forward at 01:00, so the local clock went straight from 00:59 to 02:00 and
never showed 01:30. Nothing errored. Nothing alerted. The daily partition for
that date is simply missing, and the gap was found in June.

**And the monitoring dashboard, which measures how long the job takes by
subtracting two clock readings, reported a run of minus forty minutes** on the
October night and a run of eighty-five minutes on the March one. Both figures
went into the average.

Underneath all three is one sentence, and it is the sentence this lab exists
to make true for you:

> A timestamp without a time zone is not a time. It is a rumour.

## What you are going to do

Ten exercises in `starter/01_timezones.py`, marked by `bash starter/02_check.sh`.
They build, in order, everything the three failures needed:

| # | Function | What it proves |
| --- | --- | --- |
| 1 | `zone_count` | the rules live in a database on your disk, not in Python |
| 2 | `to_utc_text` | the storage format, and why a naive datetime cannot use it |
| 3 | `day_length_hours` | the 23-hour day and the 25-hour day, measured |
| 4 | `ambiguous_offsets` | one wall reading, two offsets |
| 5 | `is_nonexistent` | the hour of 29 March that nobody ever saw |
| 6 | `is_ambiguous` | the hour of 25 October that everybody saw twice |
| 7 | `sorted_utc_texts` | why UTC ISO text sorts chronologically as plain text |
| 8 | `measure_elapsed` | which clock a duration is measured with |
| 9 | `offset_at_instant` | the resolver, the easy direction |
| 10 | `resolve_wall` | the resolver, the direction with 0, 1 or 2 answers |

Exercises 9 and 10 are the from-scratch build. You are given a three-line rule
table — a base offset and two transitions — and you write the lookup that
`zoneinfo` performs against the real database. When you have finished, the
checker runs your resolver against `zoneinfo` on thirteen wall-clock readings
and both values of `fold`, twenty-six comparisons, and every one must agree.

That is the point of the day. `zoneinfo` stops being magic the moment you have
written the thirty lines it is doing.

## The rules of engagement

**Nothing reads the clock.** Every instant in your code arrives as an
argument. A test that calls `datetime.now()` passes on 363 days a year and
fails on the two this material is about, which is worse than no test.

**Every date here is real.** Europe/London moved its clocks forward at 01:00
UTC on 29 March 2026 and back at 01:00 UTC on 25 October 2026. Those two
instants come from the IANA database on your machine, and the exercises are
built around them. If your database is unusually old the dates still hold —
they were published years in advance — but run `python3
examples/01_zone_database.py` first and see what you actually have.

**The standard library only.** `datetime`, `zoneinfo`, `time`, `calendar`.
Nothing to install.

## Working order

```bash
bash tests/run_tests.sh          # green before you start
bash starter/02_check.sh         # says 0 of 10, and why

# work down starter/01_timezones.py, re-running the checker as you go

bash starter/02_check.sh examples/07_solution.py   # the answers, afterwards
```

Try each exercise before reading the matching example. Reading a correct
answer to a question you have not yet asked yourself teaches almost nothing,
and this is a subject where almost everyone has to be wrong once before the
distinction lands.
