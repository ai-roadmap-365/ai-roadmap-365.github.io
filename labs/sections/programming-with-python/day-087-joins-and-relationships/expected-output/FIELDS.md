# What must match, and what may differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
bash 3.2.57, the `sqlite3` shell 3.51.0, and the SQLite library 3.53.3 that
Python's `sqlite3` module is linked against.

## Must match exactly, on any machine

These are values, not formatting, and a difference means something is wrong.

| Value | Where | Must be |
| --- | --- | --- |
| Row counts after seeding | all | 7 authors, 4 books, 7 pairs, 5 members, 6 loans |
| Inner join across the junction | `joins.txt` §1 | 7 rows |
| Cartesian product | `joins.txt` §3 | 28 rows (4 × 7) |
| Left join authors → books | `joins.txt` §4 | 8 rows; Donald E. Knuth's title and year blank |
| Authors with no catalogued book | `joins.txt` §5 | exactly `7 · Donald E. Knuth` |
| Books never borrowed | `joins.txt` §6 | exactly `104 · The Practice of Programming` |
| Loans per member | `joins.txt` §7 | Ada 2, Bruno 2, Chandra 1, Dana 1, **Eli 0** |
| `count(*)` version | `joins.txt` §7b | identical except **Eli 1** — the wrong answer |
| Inner-join version | `joins.txt` §7c | 4 rows; Eli gone entirely |
| Predicate in `ON` | `joins.txt` §8 | 5 rows, one per member |
| Predicate in `WHERE` | `joins.txt` §8b | 4 rows: Dana dropped, **Eli wrongly kept** |
| Self-join, LEFT | `joins.txt` §9 | 5 rows; Ada and Eli have a blank `referred_by` |
| Four-table join | `joins.txt` §10 | 4 rows; Chandra Iyer appears twice |
| Times borrowed per book | `joins.txt` §11 | 3, 2, 1, **0** |
| `PRAGMA foreign_keys` on a new connection | `foreign-keys.txt` | `0` |
| The orphan insert with the pragma off | `foreign-keys.txt` | succeeds, 1 row |
| The same insert with the pragma on | `foreign-keys.txt` | `FOREIGN KEY constraint failed` |
| `sqlite3` exit code after that rejection | `foreign-keys.txt` | non-zero (`1` here) |
| Pragma set inside an open transaction | `foreign-keys.txt` | reads back `0` — a no-op |
| Nested-loop cost | `join-from-scratch.txt` | 6 rows, 30 comparisons |
| Hash-join cost | `join-from-scratch.txt` | 6 rows, 11 operations |
| Agreement lines | `join-from-scratch.txt` | all three `True` |
| Query counts | `n-plus-one.txt` | `501` against `1` |
| Same answer both ways | `n-plus-one.txt` | `True` |
| Harness total | `test-run.txt` | `75 checks, 0 failure(s).`, exit 0 |
| Starter before | `starter-progress.txt` | `0 of 3 exercises complete.`, exit 1 |
| Starter after | `starter-progress.txt` | `3 of 3 exercises complete.`, exit 0 |

## Expected to differ on your machine

- **The two timings in `n-plus-one.txt`.** They were `0.79 ms` and `0.44 ms`
  here. Yours will differ between machines and between consecutive runs on the
  same machine; on this one the loop measured anywhere from 0.52 ms to 0.79 ms
  across three runs. The **query counts** are the stable part of that
  comparison, which is exactly why the test asserts the counts and not the
  times. Do not treat the millisecond figures as a benchmark of anything.
- **The version banner in `test-run.txt`.** It prints whatever `python3` and
  `sqlite3` you actually have.
- **The `sqlite3` error wording.** Here it reads
  `Runtime error near line 43: FOREIGN KEY constraint failed (19)`. Older shells
  word the prefix differently and may omit the `(19)`. The part that matters —
  `FOREIGN KEY constraint failed` — is what the test greps for.
- **Column padding in the `.mode column` output.** The shell sizes columns to
  the widest value it has seen, so alignment can shift. Values do not.

## Platform notes

- **Linux** — identical output, given Python 3.11+ and a `sqlite3` shell.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` is a
  bash script and `mktemp -d` is a Unix utility; neither was run on native
  Windows here, so no capture is claimed for it.
- **A much older `sqlite3` shell** — `.print`, `pragma_table_info` and
  `pragma_foreign_key_list` used as table-valued functions all need SQLite
  3.16.0 (2017) or newer. Everything here is well within that.
