# What must match, and what may differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
bash 3.2.57, the `sqlite3` shell 3.51.0, and the SQLite library 3.53.3 that
Python's `sqlite3` module is linked against.

One version floor matters for this lab. SQLite's JSON functions became part of
the default build in **3.38.0** (2022), and the `->` and `->>` operators
arrived in that same release. `tests/run_tests.sh` checks for all three before
it does anything else, so an older shell fails with one clear line rather than
a page of syntax errors.

## No output is reproduced for Redis, MongoDB, Cassandra or DynamoDB

None of those four is installed on the authoring machine and no server was
available, so **this directory contains no captured output from any of them**.
The lesson describes them from their published documentation and shows the
commands you would run; it never shows a transcript it did not produce. If you
have one of them running, the shapes in this lab will map onto it directly, but
the numbers you see will be yours, not ours.

Everything captured here comes from the two stores that genuinely ship with the
tools this course already installed: SQLite and Python's `dbm`.

## Must match exactly, on any machine

These are values, not formatting, and a difference means something is wrong.

| Value | Where | Must be |
| --- | --- | --- |
| Seeded row counts | `relational.txt` | 6 authors, 4 books, 7 credits, 3 members, 4 loans |
| The refused write | `relational.txt` | `table books has no column named titel`, and the file ends at that line |
| Books after the refusal | tests | still 4 — the bad row never got in |
| Keys in the `dbm` store | `key-value.txt` | `['book:101', 'book:102', 'book:103', 'book:104']` |
| Get by key | `key-value.txt` | `keys examined: 1` |
| Filter by a non-key field | `key-value.txt` | `keys examined: 4 of 4 (every key in the store)` |
| With the hand-built index | `key-value.txt` | `keys examined: 3 (one index key, then one key per hit)` |
| The stale index | `key-value.txt` | `ids in that index with no book left in the store: [102]`, and `no error was raised at any point` |
| `->` versus `->>` | `json-in-sqlite.txt` §2 | `arrow_type` is `text`, `arrow2_type` is `integer` |
| Plan without the index | `json-in-sqlite.txt` §5 | `SCAN documents` |
| Plan with the index | `json-in-sqlite.txt` §6 | `SEARCH documents USING COVERING INDEX idx_documents_shelf` |
| Plan for the `->>` spelling | `json-in-sqlite.txt` §7 | `SCAN documents` — the index matches the expression, not the question |
| The misspelled document | `json-in-sqlite.txt` §8-9 | `rows_inserted` 1; then 5 documents in the table and 4 with a title; the `LIKE '%Compilers%'` query returns zero rows |
| `find('shelf', 'F137')` | `docstore.txt` §3 | 50 documents, identical before and after the index |
| Plans in the built store | `docstore.txt` §3 | `SCAN documents` then `SEARCH documents USING INDEX idx_docs_shelf` |
| The misspelled document's fields | `docstore.txt` §4a | `['authors', 'book_id', 'published_year', 'shelf', 'titel']` |
| The title query for it | `docstore.txt` §4a | `[]` — present in the store, invisible to the query |
| The four-shape summary | `schema-on-read.txt` | relational REFUSED / 4 stored; the other three ACCEPTED / 5 stored; **`query finds it` is `no` in all four** |
| Harness total | `test-run.txt` | `67 checks, 0 failure(s).`, exit 0 |
| Starter before | `starter-progress.txt` | `0 of 5 exercises complete.`, exit 1 |
| Starter after | `starter-progress.txt` | `5 of 5 exercises complete.`, exit 0 |

The single most important row in that table is the last column of the
four-shape summary. The document is stored in three of the four shapes **and no
query for its title can see it in any of them**. Assert both halves or you have
asserted nothing: a store that rejected the write would also return zero rows.

## Expected to differ on your machine

- **The two timings and the ratio in `docstore.txt` §3.** The capture here
  reads `without index: 5.779 ms`, `with index: 0.066 ms`, `ratio: 88x`. A
  repeat run on the same machine gave 5.902 / 0.062 / 95x. Yours will differ —
  disk, CPU, and whatever else is running all move it. The test suite therefore
  asserts a floor of 5x and asserts the plan change, never a millisecond
  figure. What is not allowed to differ is the direction: the indexed lookup is
  much faster and the plan says SEARCH.
- **The `dbm` backend name in `key-value.txt`.** Python picks a backend when it
  creates the file and reports it through `dbm.whichdb()`. On the authoring
  machine that was `dbm.sqlite3`, which became the default in Python 3.13. An
  older Python may report `dbm.gnu` or `dbm.ndbm`; a Linux box with GDBM will
  usually report `dbm.gnu`. **The value size in bytes may differ with it**, and
  so may the on-disk file names — some backends create `library_kv.db`, others
  create `library_kv.dir` plus `library_kv.pag`. None of that changes a single
  lesson in this lab: every backend is bytes in, bytes out, addressed by one
  key. The tests match `dbm.` as a prefix rather than the exact backend.
- **The version banner in `test-run.txt`.** It prints whatever `python3` and
  `sqlite3` you actually have. The `sqlite3` shell and the SQLite library
  Python links against are two separate copies, often two different versions;
  on this machine they were 3.51.0 and 3.53.3.
- **Column padding in `relational.txt` and `json-in-sqlite.txt`.** `.mode
  column` sizes each column to the widest value it has seen, so alignment
  shifts if any value changes length. The tests read values out of the database
  rather than out of these transcripts, precisely so that padding cannot break
  them.
- **The exact wording of the `sqlite3` parse error** in `relational.txt`. Older
  shells word the `Parse error near line N:` prefix differently. The part that
  matters, and the part the tests match, is `no column named titel`.

## Deliberately non-zero, and why

`examples/01_relational.sql` **exits 1**, and that is the point of the file.
Its last statement misspells a column on purpose so that you see the relational
engine refuse the write, at the moment of the mistake, naming the field. Every
other shape in this lab accepts the same mistake in silence. If that script
ever exits 0, something has stopped enforcing the schema and the whole
comparison has quietly lost its control case.

## Platform notes

- **Linux** — the same output, given Python 3.11+ and a `sqlite3` shell of
  3.38.0 or newer, except for the `dbm` backend name discussed above.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` is a
  bash script and `mktemp -d` is a Unix utility; neither was run on native
  Windows here, so no capture is claimed for it.
