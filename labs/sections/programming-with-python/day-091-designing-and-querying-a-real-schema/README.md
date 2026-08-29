# Day 091 lab — From Requirements to Report

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Designing and Querying a Real Schema
- **Day number:** 91 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-091-designing-and-querying-a-real-schema
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-091-designing-and-querying-a-real-schema` when the site is running.
<!-- generated-links:end -->

## Purpose

You are handed a paragraph of prose from somebody who runs a small library and
has never heard the word "schema". By the end of this lab you have turned it
into a working database that answers ten real questions and prints a report a
trustee could read.

That is the whole of the week arriving at once. Day 85 gave you the relational
model, Day 86 `SELECT`, Day 87 keys and joins, Day 88 writing data and
constraints, Day 89 indexes, Day 90 SQLite from Python. None of that is
re-taught here. What is new is the part nobody teaches: **the decisions**.

Nine of them, and every one has a defensible answer on both sides:

1. Surrogate key or natural key — and the ISBN makes the case interesting,
   because it is a genuinely good natural key that is still the wrong primary
   key.
2. Is this thing an entity or an attribute? An author is an entity. A published
   year is not. There is a test.
3. Does the junction table need columns of its own? A book-author link does,
   because the cover credits them in an order.
4. How do you store a date in a database that has no date type?
5. How do you store money in a language whose floats cannot represent 0.10?
6. Enumeration as a `CHECK` constraint or as a lookup table?
7. Which columns may be NULL — deliberately, meaning something?
8. Soft delete or hard delete, and who pays for it afterwards?
9. What do you store, and what do you derive? This one you get wrong first,
   on purpose, and then fix.

Then the querying half, where the design either pays off or does not:
subqueries, `EXISTS` against `IN` against a join, common table expressions,
one genuinely recursive CTE, window functions for the top-N-per-group problem a
`GROUP BY` cannot solve, and views.

## Learning objectives

By the end of this lab you will be able to:

- Read a paragraph of requirements and list the entities, the relationships and
  the cardinality of each, before writing any SQL.
- Choose a surrogate key while keeping the natural key as a `UNIQUE`
  constraint, and say what each choice costs.
- Model a many-to-many relationship as a junction table keyed on the pair, and
  recognise when that table needs an attribute of its own.
- Store timestamps as ISO 8601 text in UTC and explain why that makes string
  comparison chronological, then use that fact in a `CHECK` constraint.
- Store money as integer minor units and keep it in integer arithmetic until
  the moment of display.
- Decide between a `CHECK` constraint and a lookup table for an enumeration,
  with a reason.
- Make nullability a decision rather than an accident, and say what each NULL
  in your schema means.
- Implement soft delete and then pay its price honestly in every present-tense
  query.
- Recognise derived data and refuse to store it, having watched a stored
  version break silently.
- Write scalar and correlated subqueries, and choose between `EXISTS`, `IN` and
  a join by what reads best and what cannot go wrong.
- Use a CTE to make an unreadable query readable, and a recursive CTE to answer
  a hierarchical question no fixed number of joins can.
- Use `ROW_NUMBER`, `RANK` and `SUM ... OVER` and state exactly what a window
  function does that `GROUP BY` cannot.
- Create a view and describe what it does and does not buy you.
- Wrap the whole thing in a repository class and print a report a person would
  actually read.

## Prerequisites

- **Day 85** — the relational model, tables, types, and SQLite from the shell.
- **Day 86** — `SELECT`, `WHERE`, `ORDER BY`, `GROUP BY`, `HAVING`, aggregates,
  and NULL's three-valued logic.
- **Day 87** — primary and foreign keys, one-to-many, many-to-many, `LEFT JOIN`,
  the anti-join idiom, and `PRAGMA foreign_keys` being off by default.
- **Day 88** — `INSERT`, `UPDATE`, transactions, `CHECK` and `UNIQUE`
  constraints, normalization, and migrations.
- **Day 89** — indexes, `EXPLAIN QUERY PLAN`, and measuring rather than
  guessing.
- **Day 90** — SQLite from Python, parameter binding, and the repository
  pattern.
- **Day 70** — floating point, which is why money is an integer here.
- **Day 43** — a working `python3` on your `PATH`.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the versions below |
| Windows | Use WSL and follow the Linux path. The two shell scripts use `mktemp -d`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. The whole database is a few kilobytes and the longest script finishes
in well under a second. No GPU, no network, no disk to speak of.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `sqlite3` shell | 3.25.0 | 3.51.0 | Window functions arrived in 3.25.0 (2018); questions 6, 7 and 8 need them |
| `sqlite3` shell | 3.8.3 | 3.51.0 | `WITH RECURSIVE` arrived in 3.8.3 (2014); question 9 needs it |
| `python3` | 3.11 | 3.14.0 | Standard library only — `sqlite3`, `sys`, `pathlib` |
| `bash` | 3.2 | 3.2.57 | The two harness scripts |

Check all of it in one line:

```bash
sqlite3 :memory: "SELECT sqlite_version(); SELECT row_number() OVER ();"
python3 --version
```

## Free and open-source options

Everything here is free, and two of the three are unusually so.

- **SQLite** is in the **public domain** — not merely open source but released
  without copyright. Nothing to buy, no licence to accept, no server to run.
- **Python** is under the PSF licence, and this lab uses only its standard
  library, so there is nothing to install.
- **PostgreSQL** (PostgreSQL licence) is the free alternative if you want to
  see the same schema with real types — a native `date`, a real `boolean`, a
  native `enum`, and `numeric` for money. The lesson's Alternatives section
  works through what changes. You do not need it for this lab.
- **DB Browser for SQLite** (GPL / MPL, free) will open `library.db` and draw
  the tables if you would rather look at the schema than read it. Optional.

No account, no key, no paid tier, and no part of this lab is degraded without
one.

## Installation

None. Clone or download the repository, change into this directory, and start.

```bash
cd labs/sections/programming-with-python/day-091-designing-and-querying-a-real-schema
python3 --version
sqlite3 --version
```

If either tool lives somewhere unusual, both scripts take an override rather
than guessing:

```bash
PYTHON=/path/to/python3 SQLITE3=/path/to/sqlite3 bash tests/run_tests.sh
```

## File structure

```text
day-091-designing-and-querying-a-real-schema/
├── README.md                     this file
├── metadata.yml                  lab metadata and the recorded run
├── security.md                   what this lab does to your machine, and the
│                                 privacy decisions the schema itself makes
├── troubleshooting.md            grouped by the message you actually see
├── requirements/
│   ├── README.md                 versions, the two SQLite floors, and what is
│   │                             deliberately absent (no ORM, no server)
│   └── requirements.txt          empty of packages, on purpose
├── starter/                      YOUR work happens here
│   ├── 00_brief.md               the requirements document, in prose
│   ├── 01_schema.sql             3 tables written for you, 6 exercises for you
│   ├── 02_questions.sql          the ten questions, exercises 7-16
│   └── 03_check.sh               "N of 16 exercises complete."
├── examples/                     the reference. Read AFTER you have tried
│   ├── 01_schema.sql             the finished schema, with the reasoning
│   ├── 02_seed.sql               invented data with the awkward cases in it
│   ├── 03_questions.sql          the ten answers, narrated
│   ├── 04_rejected_design.sql    a decision made, broken, and revised
│   ├── 05_report.py              repository class + the printed report
│   └── 06_answers.sql            the same ten answers, machine-readable
├── tests/
│   └── run_tests.sh              72 checks of real values
└── expected-output/              captured from a real run on 2026-08-16
    ├── FIELDS.md                 what must match and what may differ
    ├── answers.txt               the ten answers, pipe-separated
    ├── questions.txt             the ten answers, formatted for reading
    ├── rejected-design.txt       the queue position breaking, silently
    ├── report.txt                the finished report
    ├── starter-progress.txt      0 of 16 before, 16 of 16 after
    └── test-run.txt              the full harness run
```

## How to run

```bash
# 1. The whole thing. Start here — it should be green before you change
#    anything, and green again when you have finished.
bash tests/run_tests.sh
echo "exit code: $?"

# 2. Read the brief. Twice. Before writing any SQL.
#    starter/00_brief.md

# 3. Find out where you stand. It will say 0 of 16, and say why.
bash starter/03_check.sh

# 4. Now do the work: write your schema in starter/01_schema.sql and your
#    queries in starter/02_questions.sql, re-running step 3 as you go.

# --- everything below is the reference. Look after you have tried. ---

# 5. Build the reference database.
rm -f library.db
sqlite3 library.db < examples/01_schema.sql
sqlite3 library.db < examples/02_seed.sql

# 6. The ten answers, formatted for reading, with a comment above each query
#    explaining which construct the question forced.
sqlite3 library.db < examples/03_questions.sql

# 7. The decision that was made, tried, and thrown away.
rm -f rejected.db
sqlite3 rejected.db < examples/04_rejected_design.sql

# 8. The report a person would actually read.
python3 examples/05_report.py library.db

# 9. The same report as of a different instant, to prove nothing reads a clock.
python3 examples/05_report.py library.db '2026-09-01T09:00:00Z'

# 10. Clean up the two databases step 5 and step 7 created.
rm -f library.db rejected.db
```

## What the commands do

**`bash tests/run_tests.sh`** builds the reference schema, seeds it, and then
checks 72 real values: that the schema encodes the decisions it claims to, that
eleven impossible rows are actually refused, that all ten questions return the
exact expected rows, that the rejected design really does break silently, that
the report prints the right numbers, and that the starter reports honest
progress. Everything happens in a temporary directory that is removed on exit.

**`bash starter/03_check.sh`** builds *your* schema, loads the shared seed into
it, runs *your* queries and the reference queries against the same data, and
compares the ten answer blocks. It never looks at how you wrote a query — only
at whether the rows are right. For the schema it uses introspection
(`pragma_table_info`, `pragma_foreign_key_list`, `sqlite_master`), so it checks
the decisions rather than the text.

**`sqlite3 library.db < examples/01_schema.sql`** creates seven tables, nine
indexes and two views. Read the comments: every one of them records a decision
and its alternative.

**`sqlite3 library.db < examples/02_seed.sql`** inserts data chosen so the
questions have interesting answers — a member who has never borrowed, a member
who left owing money, a book with three authors, a book printed before ISBNs
existed, an author whose birth year is genuinely unknown, a withdrawn book, two
overdue loans, and a reservation queue with a cancellation in the middle of it.

**`sqlite3 library.db < examples/03_questions.sql`** answers the ten questions
in `.mode column`, with a comment above each explaining the choice of construct
and why the obvious alternative is worse.

**`sqlite3 rejected.db < examples/04_rejected_design.sql`** builds a
reservations table that stores the queue position, breaks it in three ordinary
statements with no error raised, and then shows the version that derives the
position instead.

**`python3 examples/05_report.py library.db`** opens the database through
`LibraryRepository` — one method per question, every value bound, never
interpolated — and prints the finished report. The report instant is an
argument with a default, not a clock reading.

## Expected output

The harness ends with a real captured line:

```text
72 checks, 0 failure(s).
```

and exits 0. The starter reports `0 of 16 exercises complete.` with exit 1
before you begin and `16 of 16 exercises complete.` with exit 0 when you are
done.

The ten answers, exactly:

```text
### 1
7|4
### 2
Eli Nakamura|student
### 3
Structure and Interpretation of Computer Programs|3|Harold Abelson, Gerald Jay Sussman, Julie Sussman
The C Programming Language|2|Brian W. Kernighan, Dennis M. Ritchie
The Practice of Programming|2|Brian W. Kernighan, Rob Pike
### 4
Bruno Salgado|The Left Hand of Darkness|10
Chandra Iyer|Neuromancer|5
### 5
Ada Okafor|current|4.10
Farida Haddad|left|3.00
### 6
staff|1|Chandra Iyer|4
standard|1|Ada Okafor|3
standard|2|Dana Whitfield|2
student|1|Bruno Salgado|4
student|2|Eli Nakamura|0
### 7
Neuromancer|1|Bruno Salgado
Neuromancer|2|Ada Okafor
The Left Hand of Darkness|1|Ada Okafor
The Left Hand of Darkness|2|Chandra Iyer
The Left Hand of Darkness|3|Dana Whitfield
### 8
2026-01|1|1
2026-02|1|2
2026-03|1|3
2026-04|1|4
2026-05|2|6
2026-06|3|9
2026-07|3|12
2026-08|2|14
### 9
0|Fiction|0
1|Gothic|1
1|Science Fiction|1
2|Cyberpunk|1
### 10
Donald E. Knuth
```

And the report:

```text
================================================================
FENWICK ROAD COMMUNITY LIBRARY — collection and lending report
as of 2026-08-16T09:00:00Z   (all figures invented for this exercise)
================================================================

1. The collection
-----------------
  7 books on the shelves, 4 of them out on loan.
  1 withdrawn book kept in the record so old loans still resolve.
```

The full capture is in `expected-output/report.txt`, and
`expected-output/FIELDS.md` says which values must match on any machine and
which are allowed to differ on yours.

The rejected design ends with two members holding the same queue position, and
no error raised anywhere:

```text
--- the damage, stated as a number: duplicate positions in one queue ---
queue_position  members_at_this_position
--------------  ------------------------
3               2                       
```

## Validation steps

1. `bash tests/run_tests.sh` ends with `72 checks, 0 failure(s).` and exits 0.
2. The schema creates **seven tables and two views**, and **nine explicit
   indexes** — a foreign key creates none of its own.
3. `book_authors` is keyed on the **pair** `(book_id, author_id)` and carries
   `author_position`; `books` has no author column at all.
4. `isbn13` is `UNIQUE` and **nullable**, and exactly one book — *Frankenstein*,
   1818 — legitimately has none.
5. Eleven impossible rows are refused: a loan due before it was borrowed, a
   negative fine, a mis-shaped timestamp, an unknown membership tier, an unknown
   reservation status, a reservation against a book that does not exist, the
   same author credited twice on one book, two authors credited second, a second
   waiting reservation by the same member, a malformed ISBN, and a hard delete
   of a book that has loan history.
6. Question 1 answers **7 and 4** — and `SELECT count(*) FROM books` answers
   **8**, which is the cost of soft delete made visible.
7. Question 6 includes **Eli Nakamura with 0**, which requires both a `LEFT
   JOIN` and `count(l.loan_id)` rather than `count(*)`.
8. Question 7 puts Ada Okafor **second** on the Neuromancer queue, not third:
   the cancelled reservation occupies no slot.
9. Question 9 finds Cyberpunk at **depth 2**, which no fixed number of joins
   could reach.
10. `examples/04_rejected_design.sql` exits **0** — nothing errored — and ends
    with **two members at position 3**.
11. `python3 examples/05_report.py library.db` totals the fines at
    `GBP 7.10` and never imports `datetime`; running it with
    `'2026-09-01T09:00:00Z'` changes the overdue figures from 10 and 5 days to
    26 and 21 and adds two more loans.
12. After the harness finishes, `ls library.db` finds nothing — everything was
    built and removed in a temporary directory.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

72 checks, exit 0 when they all pass and non-zero otherwise. They are value
checks, not file-existence checks: the suite asserts the exact rows each of the
ten questions returns, introspects the schema to confirm the design decisions,
and attempts eleven inserts that must fail.

One check is worth pointing out because it is the one that catches the mistake
this day exists to prevent. If the many-to-many relationship is modelled
wrongly — an author column on `books`, a junction table with its own surrogate
id instead of the pair as its key, or no credit order — then
`book_authors is keyed on the PAIR (book_id, author_id)` fails, and so does
question 3.

The suite also proves it is not vacuous: it deliberately breaks one reference
query by removing a soft-delete filter and confirms the checker catches it.

Overrides, if your tools are somewhere unusual:

```bash
PYTHON=/path/to/python3 SQLITE3=/path/to/sqlite3 bash tests/run_tests.sh
```

## Cleanup

```bash
rm -f library.db rejected.db
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

Both `tests/run_tests.sh` and `starter/03_check.sh` build everything inside
`mktemp -d` and remove it in a `trap`, so if you only ran those there is
nothing to clean up — and the suite asserts as much. The two databases above
exist only if you ran the optional walkthrough commands by hand.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you actually
see. The ones you are most likely to meet:

- **`near "OVER": syntax error`** — your `sqlite3` predates 3.25.0 and has no
  window functions.
- **`no such table`** — SQLite silently *created* an empty database from a
  mistyped filename rather than complaining. Run `.tables` before assuming your
  schema failed.
- **A `CHECK` that never fires** — a column-level check can only see its own
  column, so a rule comparing two columns must be written at table level; and
  `CHECK (x <> 'bad')` is unknown, not false, when `x` is NULL.
- **`CHECK constraint failed` on a timestamp** — the shape is exactly
  `YYYY-MM-DDTHH:MM:SSZ`. A space instead of the `T`, or a single-digit month,
  is refused on purpose.
- **`misuse of window function`** — window functions cannot appear in `WHERE`.
  Compute in a CTE, filter outside it.
- **`SUM ... OVER` giving the same number on every row** — the `ORDER BY`
  inside `OVER (...)` is missing.
- **A recursive CTE returning one row** — the join in the recursive part is the
  wrong way round.
- **A total of `7.099999999999999`** — money left integer arithmetic somewhere.

## Security notes

`security.md` has the full account. In short: nothing here opens a socket, runs
`sudo`, needs a credential, or installs anything, and the test suite checks each
of those rather than promising them — including that no URL appears anywhere in
the lab's scripts.

The data point worth repeating: the books and authors are real published works,
and **everything else is invented** — the library, the six members, their email
addresses, the loans, the fines, the reservations. Every invented address is on
the reserved `.invalid` domain so it can never be delivered to, and the suite
fails if any address is not.

The design point, which is this day's own: what you choose to store is the
ceiling on what can ever leak, soft delete keeps data you may have been asked to
remove, and the disclosure boundary is the query rather than the table —
question 4 produces a named person's reading record in a single row.

## Extension exercises

1. **Add a copies table and find out what it breaks.** The brief quietly
   assumes one physical copy per title. Real libraries own three copies of the
   popular ones. Introduce `copies(copy_id, book_id, acquired_at, condition)`,
   move the loan's foreign key from `book_id` to `copy_id`, and then rewrite
   every one of the ten questions. Some are unchanged, some need one more join,
   and at least one becomes genuinely ambiguous — "how many books are out?" now
   has two different correct answers. Write down which, and what you would ask
   the library.
2. **Turn the tier enumeration into a lookup table, migration and all.** Give
   tiers a display label, a loan allowance and a sort order. Write the
   migration as Day 88 would: create the table, backfill it, add the foreign
   key, drop the `CHECK`. Then answer honestly whether the schema is better,
   and say what specifically made it so.
3. **Answer question 6 without a window function.** It can be done — a
   correlated subquery counting how many members in the same tier borrowed more
   is the classic route. Write it, check it gives the same five rows, then run
   `EXPLAIN QUERY PLAN` on both and write a paragraph on which you would rather
   maintain and why.
4. **Make the recursive CTE safe against a cycle.** Move `Fiction` under
   `Cyberpunk` so the tree eats itself, and watch what happens. Then add a
   depth guard, and separately work out what constraint would have prevented
   the cycle in the first place. Decide whether that constraint is worth having.
5. **Cost the soft delete.** Count every query in this lab that had to filter
   `withdrawn_at IS NULL` or `left_at IS NULL`, and every one that deliberately
   did not. Then design the hard-delete alternative — an archive table, or a
   deletion job with a retention window — and write down what each version
   costs at query time, at write time, and in the conversation where somebody
   asks you to delete their data.

## Navigation

- **Previous day:** Day 90 — SQLite from Python
  (`labs/sections/programming-with-python/day-090-sqlite-from-python/`).
- **Next day:** Day 92 — Beyond Tables: NoSQL and Key-Value Stores
  (`labs/sections/programming-with-python/day-092-beyond-tables-nosql-and-key-value/`).
- **Week 13 project:** the week's project directory
  (`labs/sections/programming-with-python/projects/week-13/`), which builds
  directly on the schema you designed here.
