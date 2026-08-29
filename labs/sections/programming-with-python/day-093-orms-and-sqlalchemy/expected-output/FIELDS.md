# What must match, and what may differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
bash 3.2.57, SQLAlchemy 2.0.51, and the SQLite library 3.53.3 that Python's
`sqlite3` module is linked against.

The captures are compared byte for byte by section 8 of `tests/run_tests.sh`.
That is a deliberately strict check: this lab's whole claim is that the SQL an
ORM emits is observable and stable, and a capture that is allowed to drift
proves nothing.

## Must match exactly, on any machine

These are structural properties of how an ORM works, not artifacts of this
version. If one of them differs, something is genuinely different.

| Value | Where | Must be |
| --- | --- | --- |
| Seeded rows | all | 6 members, 8 books, 4 tags, 11 book-tag pairs, 24 loans, 13 of them unreturned |
| `add()` emits no SQL | `toy.txt`, `sqlalchemy.txt` | 0 statements — `add()` makes an object pending, nothing more |
| Identity map hit | `toy.txt`, `sqlalchemy.txt` | 0 statements, and `first is second` is `True` |
| Toy session total | `toy.txt` | exactly 8 statements |
| Key assigned at flush | both | `None` before, a number after — the database decided it |
| State sequence | `unit-of-work.txt` | transient, pending, persistent, detached, in that order |
| Flush is not commit | `unit-of-work.txt` | an outside connection sees **7** after the flush and **8** after the commit |
| Autoflush ordering | `unit-of-work.txt` | the INSERT is emitted **before** the SELECT that triggered it |
| Detached column read | `unit-of-work.txt` | raises `DetachedInstanceError`, message says "attribute refresh operation cannot proceed" |
| Detached relationship read | `unit-of-work.txt` | raises `DetachedInstanceError`, message says "lazy load operation of attribute 'loans'" |
| Both fixes work | `unit-of-work.txt` | `'Ada Okonkwo'` readable, and `len(ada.loans)` is `4` |
| N+1, lazy | `n-plus-one.txt` | **7** statements for 6 members — that is 1 + N |
| N+1, selectinload | `n-plus-one.txt` | **2** statements, and still 2 when N grows |
| N+1, joinedload | `n-plus-one.txt` | **1** statement |
| joinedload row multiplication | `n-plus-one.txt` | the JOIN returns **24** rows that collapse to **6** Member objects |
| Missing `.unique()` | `n-plus-one.txt` | raises, message names `unique()` |
| Many-to-one N+1 | `n-plus-one.txt` | **9**, not 25 — the identity map caps it at 1 + the 8 distinct books |
| Flush inside a loop | `bulk.txt` | **500** cursor executions for 500 rows |
| One batched flush | `bulk.txt` | **1** cursor execution carrying **500** parameter sets |
| ORM bulk update | `bulk.txt` | **2** executions, and one Python object per matching row |
| Core bulk update | `bulk.txt` | **1** execution, **0** objects |
| Harness total | — | `87 checks, 0 failure(s).`, exit 0 |
| Starter baseline | — | `1 passed, 9 skipped`, exit 0 |

## Where the measurement contradicted the received wisdom

One number in `bulk.txt` is worth reading slowly, because the usual advice
does not survive it.

"Drop to Core for bulk inserts, it is far fewer queries" is repeated
everywhere. **On SQLAlchemy 2.0.51 it is not what the counter shows.** A
batched ORM insert (`add_all()` followed by one `flush()`) and a Core
`insert()` with a list of dictionaries both cost **exactly one cursor
execution** carrying 500 parameter sets. The dramatic gap in this lab is not
ORM against Core at all — it is 500 against 1, and it is entirely about
whether the `flush()` is inside the loop or outside it.

Core's real advantage in the insert case is Python-side work the statement
counter cannot see: no `Loan` instances are constructed, nothing is registered
in the identity map, and the unit of work has no dependency graph to sort.
That is a memory and CPU argument, and this lab does not measure it, so it is
stated as a mechanism rather than as a number.

The `UPDATE` case is different and the counter does capture it: the ORM has to
`SELECT` the rows before it can change them, because it changes objects and it
has no objects until it loads them. Core changes rows and never reads them. At
13 matching rows that is 2 executions against 1; at 1013 matching rows it is
still 2 against 1, but **1013 Python objects against 0**. That is the honest
form of the bulk-operation argument.

## Expected to differ on your machine

- **The version banner in section 1 of the test run.** It prints whatever
  `python3`, SQLAlchemy and SQLite you actually have.
- **The memory address in `unit-of-work.txt`.** `<Member at 0x...>` is
  different in every process. `demo_unit_of_work.py` rewrites it to `0xADDR`
  before printing precisely so the capture is comparable; if you print the
  exception yourself you will see a real address.
- **The `sqlite_version` in `sqlalchemy.txt`.** The `sqlite3` shell and the
  SQLite library Python is linked against are two separate copies and are
  often two different versions.
- **The bulk parameter-set batching.** How many rows SQLAlchemy packs into one
  `executemany` is an implementation decision that has changed across 2.x
  releases and differs by dialect. On another version you may see the 500-row
  insert split across several executions. The *property* — one batched flush
  costs orders of magnitude fewer round trips than a flush per row — holds
  regardless; the exact number 1 does not.

## Deliberately stable, and why

Every database in this lab is built from `examples/library.py`, which has a
fixed seed: the same six members, eight books, four tags and twenty-four
loans, with explicit primary keys and hard-coded dates. Nothing reads a clock
and nothing uses a random value. That is what lets `expected-output/` be
compared byte for byte instead of approximately, and it is the same discipline
Day 91 used for its report: a result you cannot compare against last week's
copy is not a measurement.

The seed is loaded through Core `insert()` rather than through the ORM, on
purpose — it keeps the setup out of every statement count the demos take
afterwards.

## Platform notes

- **Linux** — identical output expected, given Python 3.11 or newer and the
  pinned SQLAlchemy. Not run here, so no capture is claimed for it.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` is a
  bash script and `mktemp -d` is a Unix utility; neither was run on native
  Windows here, so no capture is claimed for it either. The Python files
  themselves use `pathlib` and `tempfile` and have no Unix dependency.

## All personal-looking data is invented

Every member name and email address in the seed is fictional, and every
address uses the `library.test` domain — `.test` is reserved by the IETF for
exactly this purpose and can never resolve. The books and their authors are
real published works; the loans, dates and borrowing records are not, and no
real borrowing record was used anywhere in this lab.
