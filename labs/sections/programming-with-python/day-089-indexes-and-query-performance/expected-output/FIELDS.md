# What must match, and what may differ

Every file in this directory is a real capture from a real run on the
authoring machine (macOS 26.5.2, Apple Silicon, arm64, Python 3.14.0, bash
3.2.57, `sqlite3` shell 3.51.0, SQLite 3.53.3 as linked into Python,
2026-08-16). Nothing here was typed by hand or adjusted afterwards.

## Read this first: the timings are machine-specific

**Every millisecond and microsecond figure in this directory is a
measurement of one computer on one day, and yours will differ.** A faster
disk, a busier machine, a different SQLite build, a laptop on battery, a
container with a CPU quota — any of them moves these numbers, sometimes by
a factor of several. That is not a fault in the lab and it is not
something to correct.

What travels between machines is the **shape**:

| Shape | Where you see it | Why it holds anywhere |
| --- | --- | --- |
| A scan's cost grows roughly in proportion to the table | `lookup.txt`: 0.31 → 1.96 → 4.13 → 8.41 ms as rows go 25k → 100k → 200k → 400k | A scan reads every page. Twice the pages is twice the reading |
| A seek's cost barely moves as the table grows | `lookup.txt`: 0.028 → 0.027 → 0.028 → 0.027 ms across the same four sizes | A B-tree descent costs a number of levels, and levels grow with the logarithm of the row count |
| A binary search's step count is about log2(n) | `scan-vs-bisect.txt`: 10.0, 13.4, 16.7, 19.9 steps against log2(n) of 10.0, 13.3, 16.6, 19.9 | Arithmetic, not hardware |
| Writes get slower with more indexes | `write-cost.txt`: about 12x here with five indexes | Every index is another structure the insert must update |
| An index costs disk | `write-cost.txt`: 2.4x the file for the same rows | An index is a second copy of the columns it covers |

`tests/run_tests.sh` asserts those shapes and never a figure. Its two
ratio thresholds — at least 20x faster to read, at least 1.5x slower to
write — sit far below what this machine measured (about 300x and about
12x) precisely so that a slower or busier machine still passes.

## Must match exactly

These are facts about SQLite and about the seeded data, not about your
hardware.

| Value | Where | Why it cannot differ |
| --- | --- | --- |
| `rows: 400,000` and `distinct run_id: 4,000` | `generate.txt` | What `generate.py` builds |
| `named indexes: none — that is on purpose` | `generate.txt` | The table ships bare |
| `tr-407080-72\|atlas-7b\|ok\|0.646802` for `event_id = 123456` | `test-run.txt` | The generator is seeded with 20260816; two builds of the same size are byte-identical, and one check asserts exactly that |
| `SCAN events` before the index | `lookup.txt`, `plans.txt` | No index exists to search |
| `SEARCH events USING INDEX ix_events_run (run_id=?)` after it | `lookup.txt` | The planner's own wording for a seek |
| `matched` = 100 at every table size | `lookup.txt` | 100 events per run, at every size |
| `USE TEMP B-TREE FOR ORDER BY`, then its absence | `composite.txt`, `plans.txt` | An index on `created_on` supplies the order |
| `SEARCH ... USING COVERING INDEX ix_run_score (run_id=?)` | `composite.txt` | Every column the query names is in the index |
| The trailing column alone gets `SCAN events USING COVERING INDEX ix_run_status` | `composite.txt` | The leftmost-prefix rule; this is the point of the section |
| `rows the partial covers : 39,598 (9.9%)` | `composite.txt` | Seeded data: one `status` value in ten is `failed` |
| Partial index 186 pages against a full index's 1,857 | `composite.txt` | Same schema, same seed, same 4,096-byte page |
| `ix_run 400,000 rows, about 100 rows per distinct value` | `composite.txt` | 400,000 rows over 4,000 runs |
| `SCAN` for `lower(trace_id) = ?`, `SEARCH` once an expression index exists | `blocked.txt`, `plans.txt` | An index holds the column's values, not a function of them |
| `SCAN` for `LIKE '%...'`, `SEARCH` for the range rewrite | `blocked.txt` | A B-tree finds values by their beginning |
| `MULTI-INDEX OR` when both branches are indexed, `SCAN events` when one is not | `blocked.txt` | An OR is only as indexed as its worst branch |
| Both `scan` and `bisect` return the same answers | `scan-vs-bisect.txt` | Asserted in the code; the script raises if they ever differ |
| `scan steps` of 494, 5,027, 49,460, 605,052 and `bisect steps` of 10.0, 13.4, 16.7, 19.9 | `scan-vs-bisect.txt` | Counted, not timed, from a seeded target list |
| `40 checks, 0 failure(s).` and exit 0 | `test-run.txt` | The suite either passes or it does not |

## Expected to differ

| Value | Why |
| --- | --- |
| Every `ms` and `us` figure | Your machine, your disk, your load. See the section at the top |
| Every `faster` and `x` ratio | Derived from those timings. On this machine the largest was 309x; anything from tens to thousands is a normal result |
| `spread` on any measurement | How busy your computer was during those seven runs. A large spread beside a small difference means you have measured noise |
| `insert took: 657 ms` in `generate.txt` | Your disk and CPU |
| `sqlite3 --version` and `sqlite3.sqlite_version` | Two programs, each linking its own copy of SQLite. On this machine they read 3.51.0 and 3.53.3; on yours they may match. **Neither case is a fault**, and the suite deliberately does not assert equality |
| `EXPLAIN QUERY PLAN` wording | The planner's output is a human-readable description, not an interface. A different SQLite version may word it differently, and may legitimately choose a different plan |
| Whether a plan says `INDEX` or `COVERING INDEX` in a given line | Whether the planner judged the table read avoidable. Both are seeks; the tests check for `SEARCH` |
| `page size: 4,096` and the page and byte counts that follow from it | 4,096 is what this build of SQLite chose. Another build may choose differently, and every page figure moves with it while the ratios stay |
| Line-drawing characters in `plans.txt` | The shell draws `.mode box` output with box-drawing characters. A terminal or pipe without UTF-8 renders them differently; the numbers inside are what matter |

## Deliberately not asserted

- **No test asserts a duration.** Not a floor, not a ceiling, not a range.
  The suite asserts direction and an order of magnitude, and nothing else.
  A test that pins a millisecond figure measures the computer rather than
  the code, and it will fail on somebody else's laptop for reasons that
  have nothing to do with whether the lab is correct.
- **The two SQLite version numbers are not required to be equal.** They
  are reported and each is required to be readable.
- **`ANALYZE` is not asserted to change a plan.** On this data it does
  not: SQLite's built-in heuristic already picked the more selective of
  the two indexes, and `composite.py` says so in its own output rather
  than implying otherwise. Statistics matter on skewed data and on tables
  whose shape changed after the index was built.
