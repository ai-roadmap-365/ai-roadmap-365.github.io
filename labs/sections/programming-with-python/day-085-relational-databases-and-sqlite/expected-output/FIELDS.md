# What must match, and what may differ

Every file in this directory is a real capture from a real run on the authoring
machine (macOS 26.5.1, Apple Silicon, Python 3.14.0, bash 3.2.57, sqlite3 shell
3.51.0, SQLite 3.53.3 inside Python, 2026-08-16). Nothing here was typed by
hand. Use this page to tell a genuine difference from an expected one.

## Must match exactly

These are facts about SQLite and about the data, not about your machine.

| Value | Where | Why it cannot differ |
| --- | --- | --- |
| `b'SQLite format 3\x00'` | `first-database.txt` | The first 16 bytes of every SQLite database file, fixed by the file format |
| `53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00` | `first-database.txt` | The same 16 bytes in hexadecimal |
| `matches the documented magic string: True` | `first-database.txt` | As above |
| `pages * page size` equals the file size | `first-database.txt` | A database file is a whole number of pages, always |
| `tables: books, loans, members` | `first-database.txt` | What `schema.sql` creates |
| The seven `Runtime error` lines and their constraint names | `constraints.txt` | Each one is a rule written in `schema.sql` |
| `6 / 4 / 7 / 2` after the refused writes | `constraints.txt` | A refused write changes nothing |
| `year_class` = `text` for `not-a-number` | `typing-and-strict.txt` | SQLite type affinity, documented behaviour |
| `rows_matching_year_lt_2000 = 4` out of `rows_total = 5` | `typing-and-strict.txt` | Every INTEGER sorts before every TEXT |
| `cannot store TEXT value in INTEGER column tight.year` | `typing-and-strict.txt` | What STRICT is for |
| `IDENTICAL: 4 rows, same values, same order.` | `scan-vs-sql.txt` | The whole point of the lab |
| `4 row(s); 6 predicate calls to find them` | `scan-vs-sql.txt` | Six books, four published before 1980 |
| The three overdue borrowers and `days_late` of 55, 21 and 6 | `walkthrough.txt` | Computed from fixed dates in `seed.sql` against a fixed 2026-08-16 |
| `loans before: 7, after: 7` | `scan-vs-sql.txt` | Atomicity: the good write is undone with the bad one |
| `44 checks, 0 failure(s).` and exit 0 | `test-run.txt` | The suite either passes or it does not |

## Expected to differ

| Value | Why |
| --- | --- |
| `sqlite3 --version` | Your shell links whatever SQLite your operating system or package manager shipped |
| `sqlite3.sqlite_version` in Python | Your Python links its own copy, and it need not be the same one |
| Whether the two versions agree at all | On the authoring machine they differ (3.51.0 against 3.53.3). On yours they may match. **Neither case is a fault**, and the suite deliberately does not assert equality — it reports both and checks only that each is readable |
| The owner, group, timestamp and `@` flag in `ls -l` | Your account, your filesystem. The capture shows `you staff` because the real username was removed |
| `size: 28,672 bytes` and `page count: 7` | Stable for this exact schema and seed on a 4,096-byte page. A build of SQLite with a different default `page_size` gives different numbers that still satisfy `pages * page_size == file size` |
| `PRAGMA page_size: 4,096` | 4,096 is what both SQLite builds on this machine chose. The page size is a compile-time and per-database setting, so another build may choose differently — read yours off the header rather than assuming this one |
| `PRAGMA journal_mode: delete` | The default rollback journal. If you or a tool has set WAL on the file, this reads `wal` |
| Byte counts in `json-pain.txt` | The JSON is generated with a loop, so the totals are reproducible on a given Python — but `json.dumps` spacing has changed across Python versions before and may again |
| Line-drawing characters in `.mode box` output | The shell draws these with box-drawing characters. A terminal or pipe without UTF-8 renders them differently. The numbers inside are what matter |
| `EXPLAIN QUERY PLAN` wording | The planner's output is a human-readable description, not an interface. A different SQLite version may word it differently or, legitimately, choose a different plan |

## Deliberately not asserted

`tests/run_tests.sh` reports both SQLite versions and checks that each is
readable, and does **not** require them to be equal. Writing that assertion
would have made the suite fail on the authoring machine, and "make the test
match the machine" is the wrong direction: the honest fact is that a shell and
a language binding are two programs, and the version that matters is the one
belonging to the program you are actually running.
