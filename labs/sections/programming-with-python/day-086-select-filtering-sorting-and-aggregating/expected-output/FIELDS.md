# What must be true, on any platform

The captures in this directory came from a real run on the authoring machine
(macOS 26.5.2, Apple Silicon, sqlite3 3.51.0, Python 3.14.0, bash 3.2.57). This
file separates the values that are allowed to differ on your machine from the
ones that are not, so you can tell a real failure from a cosmetic difference.

This lab is unusually strict on that second list, and deliberately so. The whole
database is built from `examples/seed.sql`, there is no clock in any query, and
nothing is random. Almost every number below is required to match exactly. If
one of them does not, something is genuinely wrong.

## Values that will differ on your machine, and should

| Value | Why |
| --- | --- |
| The `throwaway database:` path in `test-run.txt` | `tests/run_tests.sh` builds its database under `mktemp -d`, whose directory name is random by design |
| The two version numbers on the second line | Yours will match whatever `sqlite3` and `python3` you have. Everything in this lab works on SQLite 3.30 or newer |
| Absolute paths printed by `examples/build_db.sh` | They contain your checkout location; the captures show `<repo>` where the authoring machine's home directory was |
| Column padding in `-column` output | The shell sizes each column to its widest value, so a longer path or a wider terminal shifts the spacing |

## Values that must be identical, everywhere

| Value | Required |
| --- | --- |
| The final line of `bash tests/run_tests.sh` | `122 checks, 0 failure(s).` and exit code 0 |
| The seed | `seeded: 24 books, 12 members, 45 loans` |
| The four deliberate holes | 4 unrated books, 3 unclassified books, 2 members with no city, 15 loans still out |
| `SELECT COUNT(*) FROM loans WHERE returned_on = NULL` | `0` — the trap, and it never errors |
| `SELECT COUNT(*) FROM loans WHERE returned_on IS NULL` | `15` — the correct form |
| `SELECT ROUND(AVG(rating),2) FROM books` | `4.16` |
| `SELECT ROUND(AVG(COALESCE(rating,0.0)),2) FROM books` | `3.47` — a different question, and the wrong answer to this one |
| `SELECT COUNT(*) FROM members WHERE city <> 'Pune'` | `8`, against 12 members and 2 from Pune — the naive filter loses 2 people |
| `SELECT SUM(rating) FROM books WHERE genre='no-such-genre'` | empty, which is how the shell renders NULL. `TOTAL(...)` over the same rows gives `0.0` |
| Authors with more than three titles | `3`, and the most prolific is `Ada Fenwick` with 5 |
| `SELECT author FROM books WHERE COUNT(*) > 3 GROUP BY author` | Rejected: `Error: in prepare, misuse of aggregate: COUNT()` |
| Genre buckets | `6` with GROUP BY, `5` with `COUNT(DISTINCT genre)` |
| The from-scratch comparison | `FROM 24 rows`, `WHERE 20 rows survive`, `GROUP BY 6 buckets`, `HAVING 3 buckets survive`, then `IDENTICAL: 3 rows match exactly.` and exit 0 |
| `bash starter/check.sh` on the untouched starter | `0 correct, 12 still wrong.` and exit code 1 |
| `examples/exercise-answers.sql` | The twelve values `15, 10, 2, 4, 4.16, 4, Ledger of Tides, 6, Ada Fenwick, 3, 28.0, 4` |

## The one platform note worth stating plainly

`sqlite3` ships with macOS. On Debian and Ubuntu the shell is a separate package
(`sqlite3`) from the library, so a machine with Python's `sqlite3` module working
perfectly can still have no `sqlite3` command. `tests/run_tests.sh` checks for it
first and stops with that instruction rather than failing halfway through.

Older SQLite builds are the only version-sensitive part of this lab, in exactly
two places: `NULLS FIRST` / `NULLS LAST` in `ORDER BY` arrived in **SQLite 3.30
(2019)**, and everything else here has been available for far longer. If your
shell rejects `NULLS LAST`, `ORDER BY rating IS NULL, rating` does the same job
on any version — both forms are shown in `examples/queries/04-sorting.sql`, and
the test suite checks that they agree.
