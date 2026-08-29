# Day 087 lab — Connecting the Tables

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Joins and Relationships
- **Day number:** 87 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-087-joins-and-relationships
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-087-joins-and-relationships` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 85 gave you the relational model and SQLite. Day 86 gave you `SELECT` —
filtering, sorting, grouping, aggregates, and the three-valued logic that makes
`NULL` behave the way it does. Both of those worked inside **one table at a
time**.

Today you find out why the data was in more than one table to begin with, and
what it costs to put it back together.

The lab runs that argument end to end, as a sequence you can execute:

1. **Break it first.** Build one wide table where each book row also carries its
   author's details, then watch three specific things go wrong — rename an
   author and miss a row, so the database now contradicts itself; try to record
   an author whose books you have not catalogued, and find there is no row shape
   that holds one; withdraw a book and lose the only record that its author
   existed.
2. **Split it.** Five tables, each about one kind of thing: `books`, `authors`,
   the `book_authors` junction, `members`, `loans`.
3. **Discover the enforcement is off.** Insert a loan pointing at member 999,
   who does not exist. Watch it succeed. Then turn on `PRAGMA foreign_keys` and
   watch the identical statement be rejected.
4. **Put the pieces back together.** Inner, left outer, cross, self, and
   four-table joins, with the tests checking results **by value** — which rows
   survive, which columns come back NULL, and what the counts actually are.
5. **Build the join yourself.** A nested-loop join and a hash join in plain
   Python over lists of dictionaries, both compared against SQLite for equality.
   30 comparisons against 11 operations, for the same six rows.

The traps are the point. Three of them are built into the seeded data on
purpose, because each one is a mistake you will otherwise make in production
instead of here:

- One member has never borrowed anything, so `count(*)` reports **1** for her
  where `count(l.loan_id)` correctly reports **0**.
- Moving one predicate from `ON` to `WHERE` on the same `LEFT JOIN` is wrong in
  **both directions at once** — it drops a member who genuinely has nothing out,
  and it keeps a member who has never borrowed at all.
- One book has never been borrowed and one author has no catalogued book, so
  the `LEFT JOIN` plus `IS NULL` idiom has something real to find.

All 75 checks run offline, install nothing, and need no privileges.

## Learning objectives

- Reproduce the update, insertion and deletion anomalies mechanically, and
  explain why splitting the table removes all three.
- Model one-to-many by putting the foreign key on the many side, and
  many-to-many with a junction table keyed on the pair.
- State what a foreign key promises, and prove that SQLite promises nothing
  until `PRAGMA foreign_keys = ON` is issued on that connection.
- Write `INNER JOIN` with an explicit `ON`, and say why it is better than the
  older comma-join-with-`WHERE` form that returns identical output.
- Say exactly which rows a `LEFT OUTER JOIN` keeps and which columns come back
  NULL, and use `LEFT JOIN` plus `IS NULL` to find the rows with no match.
- Recognise an accidental cartesian product from its row count and from its
  query plan.
- Write a self-join and a four-table join, and explain the row duplication a
  many-to-many introduces into the result.
- Produce a per-group count that shows a genuine zero, and name the two separate
  mistakes that stop it working.
- Explain why a predicate belongs in `ON` rather than `WHERE` for an outer join.
- Implement a nested-loop join and a hash join from scratch, compare their cost,
  and check both against the database's answer.

## Prerequisites

- The Day 87 lesson (read it first).
- **Day 85** — the relational model, tables, rows, types, and `sqlite3`.
- **Day 86** — `SELECT` with `WHERE`, `ORDER BY`, `GROUP BY`, aggregates, and
  `NULL`'s three-valued logic. Today leans on the `NULL` material constantly.
- **Day 53** — dictionaries. The hash join is a dictionary, and knowing that a
  lookup is roughly constant-time is what makes the cost comparison land.
- **Day 43** — a working `python3` on your `PATH`.
- A terminal and a text editor. Nothing else.

## Supported operating systems

- **macOS** — fully supported. Captures taken on macOS 26.5.2 (Apple Silicon,
  arm64), Python 3.14.0, bash 3.2.57, `sqlite3` shell 3.51.0.
- **Linux** — fully supported. Any distribution with Python 3.11+, bash, and the
  `sqlite3` shell.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` is a
  bash script and uses `mktemp -d`. Native Windows was not tested here, so
  `expected-output/FIELDS.md` records that honestly rather than guessing at a
  capture.

## Hardware requirements

Any computer that runs Python 3.11 or newer. The largest database this lab
builds has 2,500 rows and lives in memory. The whole suite finishes in a couple
of seconds. No GPU, no meaningful memory or disk.

## Required software

- `python3`, version 3.11 or newer — **standard library only**.
- The `sqlite3` command-line shell, version 3.16.0 or newer.
- `bash`, for the test harness.

All three are already on macOS and on a typical Linux install. See
[`requirements/README.md`](requirements/README.md) for versions and for why
there are no third-party packages.

## Free and open-source options

Everything here is free, and there is no paid tier of anything to be nudged
toward. **SQLite is in the public domain** — not merely open source, but
released without copyright by its author, which is why it is embedded in
essentially every phone and browser you own. Python is under the PSF licence.

The lesson's Alternatives section covers PostgreSQL (PostgreSQL licence),
MySQL (GPL-2.0 with a commercial option) and DuckDB (MIT) with the syntax
differences that actually matter — including that both PostgreSQL and MySQL
enforce foreign keys by default, unlike SQLite. All are free to install and run
yourself; the paid products in that space are hosted convenience, not the
database.

## Installation

There is nothing to install.

```bash
cd labs/sections/programming-with-python/day-087-joins-and-relationships
python3 --version
sqlite3 --version
```

If both print a version, you are ready. If `sqlite3` is missing, see
[troubleshooting.md](troubleshooting.md).

## File structure

```text
day-087-joins-and-relationships/
├── README.md                        ← you are here
├── metadata.yml
├── examples/                        ← the worked answers, in running order
│   ├── 01_wide_table.sql            ← the "before": one table, three anomalies
│   ├── 02_schema.sql                ← the five-table split, with the keys
│   ├── 03_seed.sql                  ← real books, invented members and loans
│   ├── 04_foreign_keys.sql          ← the pragma proof, in the shell
│   ├── 05_joins.sql                 ← every join type in the lesson
│   ├── 06_join_from_scratch.py      ← nested-loop and hash joins, checked vs SQL
│   ├── 07_foreign_keys_python.py    ← the pragma proof, plus the transaction trap
│   ├── 08_n_plus_one.py             ← 501 queries against 1, measured
│   └── 09_query_plans.sql           ← EXPLAIN QUERY PLAN: SCAN vs SEARCH
├── starter/                         ← YOUR work: 9 numbered exercises
│   ├── 01_build.sh                  ← complete; builds starter/library.db
│   ├── 02_exercises.sql             ← exercises 1-6, each runnable and wrong
│   └── 03_join_from_scratch.py      ← exercises 7-9, with its own pass/fail report
├── tests/
│   └── run_tests.sh                 ← 75 checks; builds everything in mktemp -d
├── expected-output/
│   ├── test-run.txt                 ← the full harness run
│   ├── anomalies.txt                ← the three anomalies happening
│   ├── foreign-keys.txt             ← the pragma proof, shell and Python
│   ├── joins.txt                    ← all twelve queries and their real results
│   ├── join-from-scratch.txt        ← the two algorithms agreeing with SQL
│   ├── n-plus-one.txt               ← the measured comparison
│   ├── query-plans.txt              ← what the planner chose
│   ├── starter-progress.txt         ← the starter before and after
│   └── FIELDS.md                    ← what must match, what may differ
├── requirements/
│   ├── requirements.txt             ← deliberately empty
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

From this directory.

```bash
# 1. The whole thing. Start here.
bash tests/run_tests.sh
echo "exit code: $?"
```

Then walk the argument yourself, in order. Each step builds on the last.

```bash
# 2. The "before" picture: one wide table, and three things going wrong in it.
sqlite3 anomalies.db < examples/01_wide_table.sql
rm -f anomalies.db

# 3. Split it into five tables and fill them.
rm -f library.db
sqlite3 library.db < examples/02_schema.sql
sqlite3 library.db < examples/03_seed.sql
sqlite3 library.db ".tables"

# 4. The fact worth remembering from today. Note this must be ONE session:
#    the pragma is per connection, so two sqlite3 invocations prove nothing.
sqlite3 library.db < examples/04_foreign_keys.sql; echo "exit: $?"

# 5. Every join type, against real data.
sqlite3 library.db < examples/05_joins.sql

# 6. Build the join yourself, and check it against the database.
python3 examples/06_join_from_scratch.py library.db

# 7. The same pragma fact from Python, including the trap that makes people
#    think the pragma is broken.
python3 examples/07_foreign_keys_python.py

# 8. N+1 queries against one join, measured rather than asserted.
python3 examples/08_n_plus_one.py

# 9. Watch the planner choose an algorithm.
sqlite3 library.db < examples/09_query_plans.sql

# 10. Now your turn. Build your own copy to break.
bash starter/01_build.sh

# 11. Exercises 1-6: six queries that run, and are each wrong in one named way.
sqlite3 starter/library.db < starter/02_exercises.sql

# 12. Exercises 7-9: the two join algorithms. It reports its own pass/fail.
python3 starter/03_join_from_scratch.py

# 13. When all nine are done, the full harness should still be green.
bash tests/run_tests.sh
```

To poke at the data interactively:

```bash
sqlite3 library.db
sqlite> PRAGMA foreign_keys = ON;
sqlite> .mode column
sqlite> .headers on
sqlite> SELECT * FROM members;
sqlite> .quit
```

## What the commands do

- `bash tests/run_tests.sh` — the whole harness, in fourteen sections. It
  resolves `python3` and `sqlite3` (honouring `PYTHON=` and `SQLITE3=`
  overrides), builds every database inside `mktemp -d`, runs all nine example
  files, compares 75 real values, and removes the temporary directory in a
  `trap`. One exit code: 0 if everything matched, non-zero otherwise.
- `examples/01_wide_table.sql` — builds the denormalized table and then commits
  all three anomalies against it. The update anomaly is the one to watch: it
  finishes with **no error at all**, leaving one human being recorded under two
  different names, which is precisely why it is dangerous.
- `examples/02_schema.sql` — the five tables. Read the comments on
  `book_authors` (its primary key is the *pair*, which is what stops a duplicate
  attachment), on `loans` (the foreign keys live on the many side), on `members`
  (`referred_by` points back at the same table, which is what a self-join is
  for), and on the three indexes — **a foreign key does not create an index**,
  and without one every join on that column is a full table scan.
- `examples/03_seed.sql` — real books and their real authors; invented members
  and loans. Three gaps are deliberate: an author with no catalogued book, a
  book never borrowed, and a member who has never borrowed. They are what the
  outer joins later have to find.
- `examples/04_foreign_keys.sql` — the proof. It reads the pragma (`0`), inserts
  a loan for a member who does not exist (**it succeeds**), shows the orphan row,
  finds it with `PRAGMA foreign_key_check`, deletes it, turns enforcement on,
  and reruns the identical insert — which now fails. **The script exits
  non-zero, on purpose.** That final error is the result, not a problem.
- `examples/05_joins.sql` — twelve queries: inner join across the junction, the
  same thing in comma form, a cartesian product, left outer, the two
  `IS NULL` anti-joins, the per-member count done right and then done wrong two
  ways, `ON` versus `WHERE`, a self-join, a four-table join, and the query the
  Python implementation is checked against.
- `examples/06_join_from_scratch.py` — `nested_loop_join` and `hash_join` over
  lists of dictionaries, each returning its own cost counter, then compared with
  SQLite's answer for exact equality. Also a left-outer hash join, where an
  unmatched row is paired with `None` — which is what `NULL` is.
- `examples/07_foreign_keys_python.py` — the same pragma fact from Python, and
  the trap: issued after your first `INSERT`, the pragma is **silently ignored**,
  because Python has opened a transaction and SQLite documents the pragma as a
  no-op inside one. It reads back `0`. The habit that avoids it is to issue it
  as the first statement after connecting.
- `examples/08_n_plus_one.py` — 500 members, 2,000 loans, one question answered
  both ways: 501 queries against 1. It prints real timings **and** says plainly
  that timings vary and the query counts do not.
- `examples/09_query_plans.sql` — `EXPLAIN QUERY PLAN`. `SCAN` means read every
  row; `SEARCH` means jump to the matching ones through an index. A `SCAN` plus
  a `SEARCH` is an indexed nested-loop join — the algorithm from step 6 with the
  inner scan replaced by an index lookup. Two bare `SCAN`s is a cartesian
  product.
- `bash starter/01_build.sh` — complete and working. Builds `starter/library.db`
  for you to break, and can be rerun any time to start over.

## Expected output

The harness ends with a real captured line (all 75 in
[`expected-output/test-run.txt`](expected-output/test-run.txt)):

```text
14. Hygiene: offline, no privilege, no mess left behind
  ok: the only URL anywhere in the lab's scripts is the cited SQLite page
  ok: no line in this lab would actually invoke sudo
  ok: nothing in this lab imports a networking module
  ok: no captured output leaks an absolute home path
  ok: this suite created no database inside the lab directory

75 checks, 0 failure(s).
```

The foreign-key proof, in full — this is the part worth reading twice
([`expected-output/foreign-keys.txt`](expected-output/foreign-keys.txt)):

```text
--- 1. what the pragma says on a brand-new connection ---
setting              value
-------------------  -----
PRAGMA foreign_keys  0

--- 2. insert a loan for member 999, who does not exist ---
rows_inserted
-------------
1

--- 3. the orphan row is really there ---
loan_id  book_id  member_id
-------  -------  ---------
900      101      999

--- 4. and the database will tell you, if you ask it to check ---
table  rowid  parent   fkid
-----  -----  -------  ----
loans  900    members  0

--- 5. clean up, enable enforcement, and try the identical insert ---
setting              value
-------------------  -----
PRAGMA foreign_keys  1

--- 6. the same statement, now rejected ---
Runtime error near line 43: FOREIGN KEY constraint failed (19)

exit code: 1
```

The same fact from Python, with the transaction trap:

```text
--- 2. the trap: the pragma is a no-op inside an open transaction ---
connection.in_transaction: True
pragma set, but it reads back as: 0
after commit(), setting it again reads back as: 1
the same insert now raises IntegrityError: FOREIGN KEY constraint failed
```

The zero-count trap, all three versions side by side
([`expected-output/joins.txt`](expected-output/joins.txt) §7, §7b, §7c):

```text
=== 7. the LEFT JOIN trap — loans per member, zeroes included ===
member          loans
--------------  -----
Ada Okafor      2
Bruno Salgado   2
Chandra Iyer    1
Dana Whitfield  1
Eli Nakamura    0

=== 7b. count(*) instead of count(l.loan_id) — the wrong answer ===
member          loans_wrong
--------------  -----------
Eli Nakamura    1

=== 7c. INNER JOIN instead — the member with zero loans vanishes ===
(Eli Nakamura is absent entirely)
```

And `ON` against `WHERE`, which is wrong in both directions
([`expected-output/joins.txt`](expected-output/joins.txt) §8 and §8b):

```text
=== 8. ON versus WHERE on an outer join — ON keeps every member ===
member          loan_id  returned_on
--------------  -------  -----------
Ada Okafor      2
Bruno Salgado   6
Chandra Iyer    4
Dana Whitfield
Eli Nakamura

=== 8b. the same predicate moved to WHERE — the outer join collapses ===
member         loan_id  returned_on
-------------  -------  -----------
Ada Okafor     2
Bruno Salgado  6
Chandra Iyer   4
Eli Nakamura
```

Dana Whitfield is gone — she is a member and has genuinely returned everything.
Eli Nakamura is still there, showing an empty `loan_id`, as though she had a
book out. She has never borrowed anything in her life; her NULL-extended row
simply satisfies `returned_on IS NULL`. One misplaced predicate, two opposite
errors.

The two hand-written joins
([`expected-output/join-from-scratch.txt`](expected-output/join-from-scratch.txt)):

```text
nested-loop join: 6 rows, 30 key comparisons
hash join:        6 rows, 11 operations
  (6 x 5 = 30 against 6 + 5 = 11; the gap widens as the square)

nested-loop == SQL: True
hash        == SQL: True
nested-loop == hash: True
```

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states which values must
be identical on your machine and which are expected to differ.

## Validation steps

1. `bash tests/run_tests.sh` ends with `75 checks, 0 failure(s).` and exits 0.
2. `examples/01_wide_table.sql` leaves **two different spellings** of one
   author's name in the table, having raised no error, and zero rows mentioning
   Brooks after his only book is withdrawn.
3. `examples/04_foreign_keys.sql` prints `PRAGMA foreign_keys  0` first, then
   inserts the orphan **successfully**, then prints `PRAGMA foreign_keys  1`,
   then fails with `FOREIGN KEY constraint failed`, and **exits non-zero**.
4. The inner join across the junction returns **7** rows; `books CROSS JOIN
   authors` returns **28**; dropping one join condition from the three-table
   join returns **49**.
5. The left join of authors to books returns **8** rows, and the extra one is
   Donald E. Knuth with both right-hand columns NULL.
6. `LEFT JOIN` plus `IS NULL` finds exactly `Donald E. Knuth`, exactly
   `104 · The Practice of Programming`, and exactly `Eli Nakamura`.
7. Loans per member reads Ada 2, Bruno 2, Chandra 1, Dana 1, **Eli 0** with
   `count(l.loan_id)`; switching to `count(*)` reports **1** for Eli; switching
   to an inner join drops her row entirely.
8. Moving the `returned_on IS NULL` predicate from `ON` to `WHERE` takes the
   result from 5 rows to 4 — losing Dana Whitfield and keeping Eli Nakamura.
9. The self-join keeps 5 members with `LEFT JOIN` and only 3 with `JOIN`.
10. The four-table join returns **4** rows for **3** outstanding loans, because
    one book has two authors.
11. `python3 examples/06_join_from_scratch.py library.db` prints `True` on all
    three comparison lines, `30 key comparisons`, `11 operations`, and exits 0.
12. `python3 examples/08_n_plus_one.py` prints `501` and `1` queries and
    `same answer: True`.
13. `python3 starter/03_join_from_scratch.py` prints `0 of 3 exercises
    complete.` and exits 1 before you start; `3 of 3` and exit 0 when finished.
14. After the harness finishes, `ls library.db` finds nothing — it built and
    removed everything in a temporary directory.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `75 checks, 0 failure(s).` Exits 0 on success, non-zero on
any failure.

Two sections are worth reading before you run it.

**Section 3** is the foreign-key proof, and it is built so that it cannot pass
by accident. It does not check that an error message exists somewhere; it checks
that the *identical* insert statement succeeds with the pragma off and is
rejected with the pragma on, and that the shell's exit status changes
accordingly. A check that only ever looked for the error would still pass
against a database that rejected everything.

**Section 13** is the one that proves the starter is real. It runs the shipped
starter and requires it to report `0 of 3` and exit non-zero. Then it takes a
*copy*, patches in the three answers, and requires that copy to report `3 of 3`
and exit 0. A starter whose exercises cannot actually be completed, or a checker
that would go green either way, is worth nothing — so both directions are
asserted rather than assumed.

A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

```bash
rm -f library.db anomalies.db starter/library.db
```

To discard your exercise answers and start the starter over:
`git checkout -- starter/`.

The test harness needs no cleanup: it creates its databases inside `mktemp -d`
and removes them in a `trap`, and the final section asserts that no database was
left in the lab directory. Nothing was installed, so there is nothing to
uninstall.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The ones you are most likely to
meet: `no such table`, which usually means SQLite silently *created* an empty
database from a mistyped filename rather than complaining; a
`FOREIGN KEY constraint failed` that never happens, which is the pragma being
off; a pragma that reads back as `0` in Python, which is it being ignored inside
an open transaction; a join returning far more rows than either table has, which
is a missing join condition; and a `LEFT JOIN` behaving like an inner one, which
is a predicate that has drifted into the `WHERE` clause.

## Security notes

See [security.md](security.md). Short version: no network, no `sudo`, no
credentials, nothing installed, and every one of those claims is asserted by the
suite rather than promised in prose. The members and loans are invented — no
real borrowing history appears anywhere, and the reason matters: `books`,
`members` and `loans` are each fairly harmless on their own, and **the join is
what creates the sensitive record**, tying a named person to what they read and
when. A join can produce a disclosure that none of its inputs contains, so the
unit to reason about when deciding who may see what is the query, not the table.
Foreign keys are an integrity control and not a security control; they stop a
loan pointing at a member who does not exist and stop nothing else.

## Extension exercises

1. **Add a `publishers` table** and give `books` a `publisher_id`. That is
   another one-to-many, and the key goes on the many side — on `books`, not a
   list of books on `publishers`. Then write the five-table join that reports
   who has what out, by whom, published by whom. Notice how the row count
   behaves when you add a table on the *one* side compared with adding one on
   the many side.
2. **Find the co-authors.** For a given author, list everyone they have shared a
   book with. This needs `book_authors` joined to itself, and the join condition
   is subtler than the `members` self-join: match on `book_id` while requiring
   `a1.author_id <> a2.author_id`, or you will report every author as their own
   co-author. Then decide whether you want `<>` or `<` and explain the
   difference to the result.
3. **Break referential integrity on purpose, then find it.** With the pragma
   **off**, insert three orphan loans. Run `PRAGMA foreign_key_check` and read
   what it tells you. Now try to turn enforcement on and re-run the check —
   does enabling the pragma retroactively reject the rows already there? Answer
   that by experiment, not by guessing, and write down what it implies about
   inheriting a database somebody else has been writing to for years.
4. **Make the cartesian product hurt.** Insert 5,000 rows into a scratch table
   and cross join it with itself. Run `EXPLAIN QUERY PLAN` first, then put a
   `LIMIT` on it before you run the query itself. Twenty-five million rows is
   not a rounding error, and feeling that once is worth more than reading about
   it.
5. **Add a sort-merge join** to `06_join_from_scratch.py`. Sort both sides by the
   join key, then walk them with two pointers. Count its operations alongside
   the other two, and work out when a planner would prefer it — the answer
   involves whether the inputs are *already* sorted, which is exactly what an
   index gives you.
6. **Make the N+1 comparison honest across a network.** You cannot do that here,
   so do it in writing instead. Read
   <https://www.sqlite.org/np1queryprob.html>, then take the measured numbers
   from `08_n_plus_one.py` and estimate the same workload with a 1 ms round trip
   per query. State which of the two designs you would choose for an embedded
   database and which for a client-server one, and say what changed between
   them. The point is that the correct answer depends on a fact about
   deployment, not on a rule about joins.
7. **Denormalize on purpose.** Add a `loan_count` column to `members` and keep
   it correct as loans are inserted and deleted. Then write down every way it
   can drift out of step with the truth, and what it would take to guarantee it
   does not. This is the exercise that explains why the wide table you deleted
   at the start of the lab is still, sometimes, the right answer.

## Navigation

- **Previous day:** Day 86 — SELECT: filtering, sorting, and aggregating
  (`labs/sections/programming-with-python/day-086-select-filtering-sorting-and-aggregating/`).
- **Next day:** Day 88 — inserting, updating, and schema design
  (`labs/sections/programming-with-python/day-088-inserting-updating-and-schema-design/`).
- **Week 13 project:** the week's project directory
  (`labs/sections/programming-with-python/projects/week-13/`), which builds on
  the schema you designed here.
