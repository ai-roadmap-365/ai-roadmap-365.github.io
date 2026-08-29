# Expected output — Day 070 lab

These are real captured runs from the authoring machine (macOS 26.5.1, Apple
Silicon, Python 3.14.0, bash 3.2.57, 2026-07-19). Nothing in this lab reads
the clock, the network, or a random number, so the same commands produce the
same bytes on any machine with Python 3.

## Files

- `sample-run.txt` — `python3 examples/demo.py club.json` driven end to end:
  the roster, the monthly revenue, the JSON round trip, and every domain rule
  being refused in turn; then the first eighteen lines of the JSON the
  repository wrote; then two direct calls into the pure core showing money
  adding within a currency and refusing across currencies.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  exercises still unfinished (33 checks, 0 failures, exit 0). Absolute paths
  appear as `<repo>`; on your machine they are your real repository path.

## Required behaviour of the domain core

Your finished `starter/gym_core.py` must satisfy exactly this, with no files
present anywhere:

| Call | Result |
| --- | --- |
| `MembershipNumber("GYM-0007") == MembershipNumber("GYM-0007")` | `True` (value equality) |
| `MembershipNumber("GYM-0007").value = "GYM-9999"` | raises `dataclasses.FrozenInstanceError` |
| `MembershipNumber("0007")`, `"GYM-7"`, `"gym-0007"`, `"GYM-00007"`, `7` | each raises `InvalidMembershipNumber` |
| `Money(2900, "EUR") == Money(2900, "EUR")` | `True`; `Money(2900, "USD")` is not equal to it |
| `Money(-1, "EUR")`, `Money(1.5, "EUR")`, `Money(True, "EUR")`, `Money(100, "eur")`, `Money(100, "EURO")` | each raises `InvalidMoney` |
| `Money(2900, "EUR") + Money(4900, "EUR")` | `Money(7800, "EUR")`; `str(...)` is `78.00 EUR` |
| `Money(100, "EUR") + Money(100, "USD")` | raises `CurrencyMismatch` |
| `DateRange(date(2026, 4, 30), date(2026, 4, 1))` | raises `InvalidDateRange` |
| `DateRange(date(2026, 4, 1), date(2026, 4, 30)).contains(date(2026, 4, 30))` | `True`; `date(2026, 5, 1)` is `False` |
| `PlanTier("basic")` | `PlanTier.BASIC`; `PlanTier("pluss")` raises `ValueError` |
| two `Member`s with the same number but different names | compare equal, and land in the same set slot |
| a `Member` after a rename, a plan switch and a check-in | same `hash()` as before (identity is the number) |
| a basic member's 12th check-in in a month | succeeds; the 13th raises `CheckInLimitExceeded` |
| a plus member's 28 check-ins in a month | all succeed |
| `CheckIn(...).day = other_day` | raises `dataclasses.FrozenInstanceError` |
| enrolling `GYM-0001` twice | raises `DuplicateMember` |
| `club.find(MembershipNumber("GYM-9999"))` | raises `UnknownMember` |
| a club of 29.00 + 49.00 + 29.00 EUR plans | `monthly_revenue()` is `Money(10700, "EUR")` |
| every exception class above | is a subclass of `GymError` |

## Required behaviour of the repository

| Action | Result |
| --- | --- |
| `save(club)` then `load()` | a club with the same name, the same roster, the same revenue, and every check-in intact |
| the file on disk | plain JSON: `{"club": ..., "members": [{"number", "name", "joined_on", "plan", "check_ins"}]}` |
| `load()` on a file hand-edited to `"price_cents": -1` | raises `InvalidMoney` — values are rebuilt through the domain constructors |

## Required behaviour of the CLI adapter

| Command | Output | Exit code |
| --- | --- | --- |
| `python3 examples/demo.py club.json` | roster, `monthly revenue: 107.00 EUR`, `round trip intact: True`, and six refused rules | 0 |
| `python3 examples/demo.py /nonexistent-dir-xyz/club.json` | `error: [Errno 2] No such file or directory: ...` on standard error | 2 |

## Platform notes

- The only difference between macOS and Linux is the shell prompt (`$`) shown
  before each command in `sample-run.txt`; the program's own bytes are
  identical.
- The test runner writes only into directories made with `mktemp -d` and
  removes each one when that check finishes, so a failed run leaves nothing
  behind but the temporary directory of the check that crashed.
- `demo.py` writes `club.json` into whatever directory you run it from. The
  `Cleanup` section of the README removes it.
- On Windows, run everything inside WSL. The em dash and the `—` in the
  roster header need a UTF-8 terminal; on a legacy code page the roster text
  may render with replacement characters while the numbers stay correct.
