# Week 14 project — Your Own Data Pipeline

This week was about **data formats and pipelines**: non-relational stores and
what each one trades away, ORMs and SQLAlchemy, validation with pydantic,
dates and time zones, concurrency and async, logging and configuration, and
then Day 98 assembled all of it into one working pipeline.

Day 98 handed you a pipeline. This project is the same shape against **data
you actually care about**, and the difference matters: somebody else's fixture
server never surprises you, and a real source will.

## What you are building

A pipeline that ingests a real source, validates it, stores it, reports on it,
and can be run unattended — for a dataset you have a genuine reason to track.
Weather for somewhere you travel. Your library's due dates. Prices of a thing
you buy. Air quality where you live. Your own commits. Anything with new
records over time.

The domain is yours. The five promises are not:

1. **Ingest** — a timeout on every request, retry only what is worth retrying,
   and partial success reported honestly.
2. **Validate** — a gate that collects every bad record, counts them, and
   reports them well enough to fix the source. One bad record must never end
   the run.
3. **Store** — a schema with constraints and an idempotence key, so running
   twice stores once.
4. **Report** — answers to the questions the pipeline exists for, at an
   instant you pass in rather than one it reads from the clock.
5. **Observe** — one structured log line per stage carrying a run id,
   configuration resolved by precedence with printable provenance, and an exit
   code a scheduler can act on.

## Requirements

- **A real source, and permission to read it** (Day 79): prefer an API, a data
  dump or a feed. If you scrape, honour `robots.txt` in code and rate-limit
  yourself. Record provenance with the data — where it came from, when, and
  under what terms.
- **Validation that has actually rejected something** (Day 94): your models
  must have caught at least one genuinely malformed record from the real
  source. If nothing has ever failed, your schema is too loose — tighten it
  until reality disagrees with it, then keep the report.
- **Time handled properly** (Day 95): store timestamps as ISO 8601 in UTC.
  If your source reports local times, say in `NOTES.md` what you did about
  ambiguous and nonexistent hours.
- **A schema with real constraints** (Days 88, 91, 93): through SQLAlchemy or
  by hand. `PRAGMA foreign_keys = ON` per connection. At least one constraint
  must have refused a row you actually tried to insert.
- **Idempotence you have tested** (Days 81, 98): run it twice, assert the row
  count is unchanged. Derive the key from the unit of work, never from a
  timestamp.
- **Concurrency only where it pays** (Day 96): if you fetch several sources,
  measure sequential against concurrent and keep the numbers. If concurrency
  did not help, say so and leave it out — that is a finding, not a failure.
- **Logging and configuration** (Day 97): four layers with provenance, one
  structured line per stage, and no secret in any log line — with a test that
  greps for the secret's value to prove it.
- **A schedule** (Day 81): a crontab line, launchd plist or systemd timer,
  committed, plus a note on what the scheduled environment does not inherit.

## Steps

1. Write down the questions you want answered before choosing a source. They
   decide the schema more than the data does.
2. Fetch one record by hand and read it properly. Note every field that is
   optional, inconsistently typed, or a date in disguise.
3. Write the pydantic models against that reality, not against the API's
   documentation — the two differ more often than you would like.
4. Build the store with constraints, then try to insert three rows that should
   be impossible.
5. Run the ingest against the real source and watch what breaks. This is the
   step that teaches; the fixture never did this.
6. Make it idempotent, then prove it by running it twice.
7. Add the report and fix the instant so its output can be compared.
8. Add logging and configuration last, then run it from an empty directory
   with only environment variables set.
9. Schedule it and leave it running for a few days. Then read your own logs
   and see whether they tell you what happened.

## Expected output

- `python -m yourpipeline run` → a summary naming records fetched, accepted,
  rejected and stored, exit code 0.
- The same command run twice → the second run stores nothing new and says so.
- A run with the source unreachable → a non-zero exit code, a named failure,
  and no partial write.
- `python -m yourpipeline report --as-of <instant>` → identical output on two
  consecutive runs.
- Your rejects report → at least one real malformed record from the live
  source, with its `loc` and `type`.
- `grep -c '"level"' logs/run.jsonl` → one line per stage per run, parseable
  as JSON.
- `bash tests/run_tests.sh` → all checks pass with no network access, against
  a recorded fixture rather than the live source.

## Validation

- [ ] Every request sets a timeout; a test proves a slow source is given up on.
- [ ] The validation gate has rejected a real record from the live source, and
      the report is committed as evidence.
- [ ] Running twice leaves the row count unchanged, asserted by a test.
- [ ] At least one schema constraint has refused a row you actually tried.
- [ ] Timestamps are ISO 8601 UTC; local-time handling is documented.
- [ ] The report takes its instant as a parameter and is byte-identical across
      two runs.
- [ ] Configuration resolves defaults → file → environment → flags, and the
      tool can print where each value came from.
- [ ] No secret appears in any log line, proved by a test that greps for it.
- [ ] Tests run entirely offline against a recorded fixture.
- [ ] A schedule file is committed with a note on what it does not inherit.
- [ ] `NOTES.md` records what surprised you about the real source. This is the
      most valuable page in the project.

## Troubleshooting

- Everything validates on day one and never again? The source changed shape.
  That is the normal case, and it is why the gate reports rather than crashes.
- Duplicates creeping in? Your idempotence key includes something that varies
  between runs — a fetch time, a position in a list, a sort order.
- The second run is empty when it should not be? The opposite failure: your
  key is too coarse and is collapsing genuinely distinct records.
- Timestamps an hour out twice a year? You stored local time. Store UTC and
  convert at the display edge.
- Concurrency made it slower? Likely the work is not waiting-bound, or the
  source is rate-limiting you. Measure before keeping it.
- Logs unreadable after a week? They are prose, not records. One JSON object
  per line, with a run id, and you can answer questions with `jq`.
- Scheduled runs do nothing while the command works by hand? It inherited
  neither your PATH nor your virtual environment. Use absolute paths and
  reproduce the environment with `env -i` to confirm.
