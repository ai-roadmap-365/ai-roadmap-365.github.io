# Troubleshooting — Day 095

Grouped by the message you actually see, or by the wrong answer you actually
get. The second group is longer, because this subject fails quietly far more
often than it raises anything.

## Errors you can see

### `ZoneInfoNotFoundError: 'No time zone found with key Europe/London'`

Your machine has no IANA time zone database where `zoneinfo` looks. Check:

```bash
python3 -c "import zoneinfo; print(zoneinfo.TZPATH)"
ls /usr/share/zoneinfo | head
```

- **Linux** — install your distribution's `tzdata` package.
- **A slim container image** — this is the usual cause. `python:3.x-slim` and
  Alpine images often ship without `tzdata`. Add it in the Dockerfile, or add
  the `tzdata` PyPI package as a dependency.
- **Windows** — there is no system database, by design. `pip install tzdata`.

### `ModuleNotFoundError: No module named 'zoneinfo'`

You are on Python 3.8 or older. `zoneinfo` arrived in 3.9. Upgrade, or use the
`backports.zoneinfo` package on the older interpreter.

### `ValueError: Invalid isoformat string: '2026-10-25T01:30:00Z'`

You are on Python 3.10 or older, where `fromisoformat` did not accept the
trailing `Z`. Two options: upgrade to 3.11+, or replace the suffix first —
`text.replace("Z", "+00:00")` — which is the workaround that was everywhere
for years.

### `ValueError: time data '...' does not match format '%Y-%m-%d %H:%M:%S %Z'`

`%Z` parses far less than people expect: on this machine it accepted only
`UTC` and `GMT`, and rejected `BST` and `EST`. Even when it succeeds it
produces a **naive** datetime — the zone name is parsed and then discarded.
Use `%z` with a numeric offset (`+0100`), or better, use ISO 8601 text and
`fromisoformat`.

### `ValueError: second must be in 0..59, not 60`

You have been handed a leap second — `23:59:60`. Python's `datetime` cannot
represent one, because it implements POSIX time in which every day has exactly
86400 seconds. If the input is a real UTC timestamp containing `:60`, the
usual handling is to clamp it to `:59` and record that you did.

### `TypeError: can't subtract offset-naive and offset-aware datetimes`

You mixed a naive datetime with an aware one. This is the one time-zone
mistake Python does catch for you, and it is a gift. Make the naive one aware
by attaching the zone it actually came from — not the machine's local zone
just because that is easiest.

### `AttributeError: 'NoneType' object has no attribute '__dict__'` from `dataclasses`

You are loading a module by file path without registering it in `sys.modules`
first. `@dataclass` looks its defining module up there. `starter/check_exercises.py`
has the two-line fix, with a comment.

## Wrong answers with no error at all

This is where the day lives.

### Every day measures 24 hours, including 29 March

You subtracted two *local* datetimes. That gives the wall-clock difference,
which is 24 hours by construction on every day of the year. Convert both to
UTC before subtracting:

```python
(end.astimezone(UTC) - start.astimezone(UTC))
```

### Two datetimes an hour apart compare equal

Expected, documented, and the cause of more than one production bug. Two aware
datetimes with the **same** `tzinfo` object are compared by their wall-clock
fields, and `fold` is ignored in that comparison. Convert both to UTC before
comparing, sorting, or using them as dictionary keys.

### `is_ambiguous` also returns True for the nonexistent hour

`fold=0` and `fold=1` give different instants in *both* cases, so `!=` cannot
tell them apart. The direction can: an ambiguous reading gives the **earlier**
instant at `fold=0`, a nonexistent one gives the **later**. Test `first < second`.

### A scheduled job runs twice, or not at all

The schedule is expressed in local time and the local clock repeated or
skipped the hour. Schedule in UTC. If the requirement genuinely is "09:00
local whatever happens", store the zone name alongside the local time and
recompute the next firing instant after every run — never store a
pre-computed list of future instants, because the database can change
underneath it.

### A duration comes out negative, or an hour too long

You measured with `time.time()` or by subtracting two local datetimes. Use
`time.monotonic()` for any elapsed time. The rule is short: **wall clock for
when, monotonic for how long.**

### A sort by timestamp gives the wrong order

Your column holds local time. Text order equals chronological order **only**
for UTC ISO 8601 at a fixed width. Local text sorts wrongly even when the
offset is included, because the comparison never reaches the offset on the
end. Store UTC; convert at display.

### Timestamps drift by an hour after a deployment

Two likely causes, and it is worth checking both. Either the process's `TZ`
environment variable differs between machines and something is using local
time implicitly, or the container image's `tzdata` is older than the change a
government has since made. `python3 examples/01_zone_database.py` prints the
database version; compare it across your environments.

### The whole test suite passes today and fails in October

It reads the clock somewhere. Every instant in a test about time zones must be
written out in the source. Grep your suite for `now()`, `today()` and
`utcnow()`; every hit is a test that will fail on a date you cannot control.

## Checking the environment quickly

```bash
python3 --version
python3 -c "import zoneinfo; print(zoneinfo.TZPATH, len(zoneinfo.available_timezones()))"
cat /usr/share/zoneinfo/+VERSION 2>/dev/null || echo "no +VERSION file"
python3 examples/01_zone_database.py
```

If `tests/run_tests.sh` fails on a value rather than on an error, read
`expected-output/FIELDS.md` first: it separates the values that must match on
any machine from the ones that are legitimately allowed to differ on yours.
