# What must match, and what may legitimately differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.1 (Apple Silicon, arm64), Python 3.14.0
with the standard-library `sqlite3` module linked against SQLite 3.53.3,
bash 3.2.57. Nothing here was typed by hand or adjusted afterwards.

Use this page before you conclude that something is wrong.

## Must be identical on your machine

These are properties of the code and of SQLite, not of the hardware.

| Where | Value | Why it cannot differ |
| --- | --- | --- |
| `injection.txt` | the concatenated query returns **3** rows and prints all three PINs | The crafted value makes the WHERE clause true for every row |
| `injection.txt` | the built statement reads `... WHERE name = 'Ada' OR '1'='1'` | It is printed before it is run |
| `injection.txt` | `execute` raises `ProgrammingError: You can only execute one statement at a time.` | A documented limit of the module |
| `injection.txt` | `members table exists afterwards: False` after `executescript` | The DROP really ran |
| `injection.txt` | every bound lookup returns **0** rows and the table keeps **3** | Binding cannot change a compiled statement |
| `transactions.txt` | `after CREATE TABLE (DDL): False`, `after INSERT (DML): True` | The module opens a transaction before DML, not DDL |
| `transactions.txt` | `is the connection still usable after the with-block? True` | `with connection:` manages a transaction, never the connection |
| `transactions.txt` | pragma inside a transaction `-> 0`, outside `-> 1` | `PRAGMA foreign_keys` is a no-op inside a transaction |
| `errors.txt` | the class in every row of the table | Fixed by the module and by SQLite |
| `report.txt` | `55`, `21` and `6` days late | The seed dates and `AS_OF` are literals |
| `report.txt` | book ids, titles and copy counts | Fixed by `seed.py` |
| `cursors.txt` | `cursor.rowcount for a SELECT -> -1` | SQLite cannot know the row count in advance |
| `cursors.txt` | `isinstance(row, dict) = False` for `sqlite3.Row` | `Row` is not a dict subclass |
| `unit-tests.txt` | `Ran 29 tests`, `OK` | The suite is fixed |
| `test-run.txt` | `64 checks, 0 failure(s).` and exit 0 | The harness is fixed |

## Expected to differ

| Where | What varies | What is still true |
| --- | --- | --- |
| `test-run.txt` | the two version lines: `python: 3.14.0` and `sqlite3.sqlite_version: 3.53.3` | Any Python 3.12+ with SQLite 3.37+ passes; the harness checks the capability, not the number |
| `bulk-insert.txt` | all six timing figures | The **order** is the fact: a loop with no transaction is far slower than a batched loop, which is a little slower than `executemany` |
| `bulk-insert.txt` | the `relative` column, here 1411x and 2455x | On a machine with different `fsync` behaviour this gap is smaller — a container on a virtual disk may show tens rather than thousands. The sign never changes |
| `cursors.txt` | the two peak-memory figures and their ratio | `fetchall` peaks in the megabytes; iterating peaks in the hundreds of bytes. The harness asserts only that they are more than 100x apart |
| `unit-tests.txt` | `Ran 29 tests in 0.048s` — the seconds | The count and `OK` do not vary |
| every file | temporary directory names such as `day090-injection-azz0ifv4` | They are created by `mktemp` and removed before the script exits |

## What a difference actually means

- **`foreign_keys(raw): 1`** instead of `0` — something on your system sets
  the pragma by default. Nothing in the lab does; check for a `~/.sqliterc`
  or an environment that preloads settings.
- **The bound lookup returns rows** — the value is being interpolated
  somewhere rather than bound. That is the bug the whole lab is about.
- **`with connection:` closed the connection** — this has never been the
  module's behaviour on any released version. Check that you did not call
  `close()` yourself.
- **A timing "relative" column near 1.0x for the first row** — your
  filesystem is not really flushing to disk, which is normal in some
  containers and virtual machines. The lesson still holds; the demonstration
  is just less dramatic.

## Windows

No captures were taken on native Windows, and none are invented here.
`tests/run_tests.sh` is a bash script and needs WSL or Git Bash. Every
Python file runs unchanged on Windows, including the temporary-directory
handling, because it goes through `tempfile` and `pathlib` rather than
hard-coded paths.
