# What must match, and what may differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
bash 3.2.57, the `sqlite3` shell 3.51.0, and the SQLite library 3.53.3 that
Python's `sqlite3` module is linked against.

Two of those versions matter for this lab specifically. Window functions —
`ROW_NUMBER`, `RANK`, `SUM ... OVER` — need SQLite 3.25.0 (2018) or newer, and
the test suite checks for them by running one before it does anything else.
Recursive common table expressions need 3.8.3 (2014). Both shells above are far
past those.

## Must match exactly, on any machine

These are values, not formatting, and a difference means something is wrong.

| Value | Where | Must be |
| --- | --- | --- |
| Seeded row counts | all | 8 categories, 11 authors, 8 books, 12 credits, 6 members, 14 loans, 7 reservations |
| Q1 — the collection | `answers.txt` §1 | `7\|4` — 7 books on the shelves, 4 out on loan |
| Books table row count | `test-run.txt` | 8, because the withdrawn book is still a row |
| Q2 — never borrowed | `answers.txt` §2 | exactly `Eli Nakamura\|student` |
| Q3 — multi-author books | `answers.txt` §3 | 3 books; SICP has 3 authors in the order Abelson, Sussman, Sussman |
| Q4 — overdue | `answers.txt` §4 | Bruno Salgado 10 days, Chandra Iyer 5 days |
| Q5 — fines | `answers.txt` §5 | Ada Okafor 4.10 (current), Farida Haddad 3.00 (left) |
| Q6 — top two per tier | `answers.txt` §6 | 5 rows; **Eli Nakamura appears with 0** |
| Q7 — reservation queues | `answers.txt` §7 | Neuromancer 2 deep, The Left Hand of Darkness 3 deep |
| Q8 — monthly running total | `answers.txt` §8 | 8 months, ending at 14 |
| Q9 — the Fiction subtree | `answers.txt` §9 | Fiction (0), Gothic (1), Science Fiction (1), Cyberpunk (1) at depth 2 |
| Q10 — never-borrowed authors | `answers.txt` §10 | exactly `Donald E. Knuth` |
| Total fines | `report.txt` | `GBP 7.10  TOTAL` |
| The stored-position design | `rejected-design.txt` | ends with **two members at position 3**, and no error raised |
| The derived version | `rejected-design.txt` | renumbers to 1, 2 after a cancellation |
| Harness total | `test-run.txt` | `72 checks, 0 failure(s).`, exit 0 |
| Starter before | `starter-progress.txt` | `0 of 16 exercises complete.`, exit 1 |
| Starter after | `starter-progress.txt` | `16 of 16 exercises complete.`, exit 0 |

## Expected to differ on your machine

- **The version banner in `test-run.txt`.** It prints whatever `python3` and
  `sqlite3` you actually have. The `sqlite3` shell and the SQLite library
  Python is linked against are two separate copies and are often two different
  versions; on this machine they were 3.51.0 and 3.53.3.
- **Column padding in `questions.txt`.** `.mode column` sizes each column to
  the widest value it has seen, so alignment shifts if a value changes length.
  `answers.txt` exists precisely because it does not have this problem: it is
  pipe-separated with no padding, which is why the tests compare against that
  file and not this one.
- **The wording of `sqlite3` parse errors** quoted in
  `starter-progress.txt`. Older shells word the prefix differently. The part
  that matters is that the seed cannot load into an unfinished schema.

## Deliberately stable, and why

Every "as of now" answer in this lab is computed against the fixed instant
`2026-08-16T09:00:00Z`, passed as a parameter. Nothing here reads a clock. That
is not a testing convenience bolted on afterwards — it is the design decision
that makes a report reproducible, comparable with last month's copy, and
testable at all. `05_report.py` takes the instant as its second argument, and
the test suite runs it a second time with `2026-09-01T09:00:00Z` to prove the
answers move when the parameter moves: the two overdue loans grow from 10 and 5
days to 26 and 21, and two more loans join them.

## Platform notes

- **Linux** — identical output, given Python 3.11+ and a `sqlite3` shell of
  3.25.0 or newer.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` and
  `starter/03_check.sh` are bash scripts and `mktemp -d` is a Unix utility;
  neither was run on native Windows here, so no capture is claimed for it.
