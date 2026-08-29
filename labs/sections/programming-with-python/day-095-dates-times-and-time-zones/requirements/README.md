# Dependencies

**None.** `requirements.txt` lists no packages, and nothing is added to your
Python environment. The day's whole argument is that the standard library
already does this correctly, and that the hard part is knowing which question
you are asking.

| Tool | Version used here | Where it comes from | Licence |
| --- | --- | --- | --- |
| `python3` | 3.14.0 | Whatever Python you installed on Day 43. Standard library only: `datetime`, `zoneinfo`, `time`, `calendar`, `dataclasses`, `pathlib` | PSF licence |
| `bash` | 3.2.57 | Preinstalled on macOS; every Linux has it | GPL |
| IANA time zone database | 2026c | `/usr/share/zoneinfo`, shipped with the operating system | public domain |

Check all three:

```bash
python3 --version
bash --version | head -1
python3 -c "import zoneinfo; print(len(zoneinfo.available_timezones()))"
```

The third line printed `598` on the authoring machine. Yours may print a
different number, and that is not a problem — it is the day's subject.

## The dependency that is not a package

`zoneinfo` contains no time zone data. It is a reader for a database your
operating system installs, and `zoneinfo.TZPATH` lists where it looks:

```bash
python3 -c "import zoneinfo; print(zoneinfo.TZPATH)"
cat /usr/share/zoneinfo/+VERSION   # on macOS and most Linux distributions
```

That database is updated several times a year, because governments change
their minds about daylight saving with about six weeks' notice and sometimes
less. Your operating system's update mechanism is what keeps it current: on
Debian and Ubuntu the package is `tzdata`, on Fedora and RHEL it is also
`tzdata`, and on macOS it arrives with system updates.

**This is the single most important operational fact in the lesson.** A
container image built two years ago and never rebuilt has a two-year-old
opinion about when the clocks change, and it will be confidently wrong on the
first Sunday a government has since moved.

## Minimum versions, and why

**Python 3.9 or newer** for `zoneinfo` itself, which arrived in 3.9 through
PEP 615. Before that the answer was the third-party `pytz` or `dateutil`.

**Python 3.11 or newer** for two things this lab uses:

- `datetime.fromisoformat` accepting the trailing `Z` and most of ISO 8601.
  Before 3.11 it parsed only what `isoformat()` produced, and `"...Z"` raised
  `ValueError` — a genuine and much-complained-about sharp edge.
- The `str | Path` and `timedelta | None` type-hint syntax in the example
  files.

**`fold`, which the whole lab turns on, arrived in Python 3.6** through
PEP 495. Every supported Python has it.

Confirm the two that matter in one line:

```bash
python3 -c "from datetime import datetime; from zoneinfo import ZoneInfo; \
print(datetime.fromisoformat('2026-10-25T01:30:00Z'), \
datetime(2026,10,25,1,30,fold=1,tzinfo=ZoneInfo('Europe/London')).utcoffset())"
```

## Windows

Windows ships no IANA database. `zoneinfo` finds nothing on `TZPATH` and falls
back to a first-party PyPI package called `tzdata`, which contains the same
data as a Python package:

```bash
pip install tzdata
```

That package was created precisely so `zoneinfo` could work identically
everywhere. It is maintained by the Python core developers and updated when
IANA publishes a release. This lab was **not** run on native Windows and no
output is claimed for it; use WSL and follow the Linux path.

## If python3 is somewhere unusual

Both shell scripts take an override rather than guessing:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
PYTHON=/path/to/python3 bash starter/02_check.sh
```

They fail with that instruction rather than silently skipping checks.

## What is deliberately absent

**No `pytz`.** It was the right answer for a decade and it is now the wrong
one for new code. Its unusual `localize()` API exists because it predates
`fold` and had to solve the ambiguous hour without any help from the language.
The lesson covers what it did and why it worked that way; you do not need it
installed to understand the argument.

**No `dateutil`, `arrow` or `pendulum`.** All three are good libraries, all
three are covered in the lesson's Alternatives section from their
documentation, and none of them is installed here — so no output is reproduced
for any of them. What each one buys is stated; what none of them can do is
change the fact that 01:30 happened twice.

**No database and no scheduler.** The failures in the brief are a scheduler's
failures, and reproducing them with a real scheduler would take an afternoon
and teach you less than walking the minutes yourself, which is what
`examples/03_fold.py` does in eight lines.
