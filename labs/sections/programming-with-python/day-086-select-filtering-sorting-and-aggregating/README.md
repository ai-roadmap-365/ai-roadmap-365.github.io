# Day 086 lab — Ask the Database Questions

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** SELECT: Filtering, Sorting, and Aggregating
- **Day number:** 86 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-086-select-filtering-sorting-and-aggregating
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-086-select-filtering-sorting-and-aggregating` when the site is running.
<!-- generated-links:end -->

## Purpose

Yesterday you learned to put rows into a table. Today you learn to ask the table
questions, which is the part you will spend the rest of your career doing.

The lab builds a small library database — 24 books, 12 members, 45 loans — and
then walks you through the eight families of question you can ask one table:
filter it, match patterns in it, sort it, take the top of it, count it, average
it, group it, and filter the groups. Every query is in a file you can run, and
every answer is a number you can check against the seed by hand.

Three things make this lab different from a list of SQL examples.

**The data has holes in it, on purpose.** Four books have no rating. Three have
no genre. Two members gave no city. Fifteen loans have no return date, because
those books are still out. Every one of those holes is a NULL, and NULL is where
SQL stops behaving the way your intuition says it should. `returned_on = NULL`
finds nothing at all. `city <> 'Pune'` quietly discards the members who never
told you their city. `AVG(rating)` gives 4.16, and the "fix" everybody reaches
for gives 3.47 and says nothing about the change.

**You build GROUP BY yourself before you use it.** `examples/groupby_from_scratch.py`
implements grouping and all five aggregates as a dictionary of accumulators over
a list of rows — about twenty lines — and then runs the one SQL statement that
replaces them and asserts the two results are identical. After you have written
the `if rating is not None:` line yourself, "AVG ignores NULLs" stops being a
rule to memorise and becomes the only decision that was ever available.

**Every exercise starts out wrong.** The twelve exercises in
`starter/exercises.sql` are not blanks. They are twelve queries that run, print a
confident, well-formatted answer, and are wrong — the exact queries people
actually write. Your job is to fix each one. `bash starter/check.sh` scores them.

That last point is the lab's argument in miniature. SQL almost never tells you
that you asked the wrong question. It answers the one you actually asked.

## Learning objectives

- Trace a `SELECT` through its **logical evaluation order** — FROM, WHERE,
  GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT/OFFSET — and use that
  order to predict which clause may refer to what.
- Filter rows with comparisons, `AND`/`OR`/`NOT`, `IN` and `BETWEEN`, and say
  what the brackets change when the two operators meet.
- Choose between `LIKE` and `GLOB` knowing that one folds case and the other
  does not, and that they use different wildcards.
- Apply three-valued logic correctly: `IS NULL` as the only test for absence,
  what NULL does inside `AND` and `OR`, and why negative filters on nullable
  columns lose rows without saying so.
- Sort on several keys, control where NULLs land, and take a deterministic top-N
  with `LIMIT` and `OFFSET`.
- Distinguish `COUNT(*)` from `COUNT(column)` and predict the gap between them.
- Group rows into buckets — including by an expression — and filter those
  buckets with `HAVING`, explaining why `WHERE` cannot do it.
- Build grouping and aggregation from scratch in Python and prove it agrees with
  the SQL.
- Recognise the two places SQLite is more permissive than standard SQL, and
  write the portable spelling anyway.

## Prerequisites

- The Day 86 lesson (read it first).
- Day 85: the relational model, SQLite's architecture and type affinity, and
  `CREATE TABLE` / `INSERT` / a first `SELECT`. This lab seeds its own database
  so it runs independently, but it assumes you have met a table before.
- Days 64–66: files, and the habit of a script that returns an exit code.
- Comfort running a bash script and reading a Python `for` loop with a `dict`.
- No knowledge of joins is needed. Every query here is over one table; joins are
  tomorrow.

## Supported operating systems

- **macOS** — fully supported. All captures were taken on macOS 26.5.2 (Apple
  Silicon), sqlite3 3.51.0, Python 3.14.0, bash 3.2.57.
- **Linux** — fully supported on any distribution with bash, `python3` and the
  `sqlite3` shell. On Debian and Ubuntu the shell is packaged separately from
  the library, so you may need `sudo apt install sqlite3`.
- **Windows** — use WSL and follow the Linux path. The `.sql` files run
  unchanged against the native Windows `sqlite3` shell, but the three bash
  scripts do not. That native-Windows path has not been executed on the
  authoring machine and is described rather than promised; see
  [troubleshooting.md](troubleshooting.md).

SQLite **3.30 or newer** is needed for the `NULLS LAST` spelling in
`examples/queries/04-sorting.sql`. The portable equivalent
(`ORDER BY rating IS NULL, rating`) is shown alongside it and works on any
version.

## Hardware requirements

Anything. The database is a single file of a few tens of kilobytes, the whole
test suite finishes in under a second on the authoring machine, and nothing here
holds more than a few dozen rows in memory. No GPU, no network, no disk of
consequence.

## Required software

- `sqlite3` — the command-line shell (3.51.0 here).
- `python3` — 3.9 or newer (3.14.0 here), for the from-scratch comparison. It
  uses only the standard library's `sqlite3` module.
- `bash` — for the three shell scripts (3.2.57 here).

Nothing is installed. See [`requirements/README.md`](requirements/README.md) for
the full table and for what is deliberately absent.

## Free and open-source options

Every tool here is free, and there is nothing to buy at any point.

**SQLite is public domain** — not merely open source but explicitly dedicated to
the public domain by its author, which is why it ships inside browsers, phones,
aircraft and your operating system without anyone negotiating a licence. Python
and bash are free software under their own licences (see
[`requirements/README.md`](requirements/README.md)).

The lesson's Alternatives section covers the wider field honestly: PostgreSQL
and MySQL as free servers when you outgrow a single file, DuckDB as the free
column-store for analytics, pandas as the dataframe answer to the same
questions, and the paid managed services that run all of these for you. Every
query in this lab except two clearly-marked SQLite extensions is standard SQL
and runs unchanged on any of them.

## Installation

There is nothing to install. Check the three tools and build the database:

```bash
cd labs/sections/programming-with-python/day-086-select-filtering-sorting-and-aggregating
sqlite3 --version
python3 --version
bash examples/build_db.sh
```

`build_db.sh` deletes any existing `examples/library.db` and recreates it from
`examples/seed.sql`, so you can run it at any point to get back to a known state.
It prints `seeded: 24 books, 12 members, 45 loans` when it works.

## File structure

```text
day-086-select-filtering-sorting-and-aggregating/
├── README.md                       ← you are here
├── metadata.yml
├── .gitignore                      ← the built database is never committed
├── examples/                       ← the worked queries, all runnable
│   ├── seed.sql                    ← 24 books, 12 members, 45 loans, and the holes
│   ├── build_db.sh                 ← rebuilds examples/library.db from the seed
│   ├── groupby_from_scratch.py     ← GROUP BY in plain Python, asserted equal to SQL
│   ├── exercise-answers.sql        ← the model answers (read AFTER trying)
│   └── queries/
│       ├── 01-filters.sql          ← WHERE, AND/OR, IN, BETWEEN
│       ├── 02-patterns.sql         ← LIKE vs GLOB
│       ├── 03-null-traps.sql       ← three-valued logic, and the traps
│       ├── 04-sorting.sql          ← ORDER BY, DISTINCT, LIMIT, OFFSET
│       ├── 05-aggregates.sql       ← COUNT/SUM/AVG/MIN/MAX and NULL
│       ├── 06-group-by.sql         ← buckets, including grouping by an expression
│       ├── 07-having.sql           ← the filter WHERE cannot express
│       └── 08-case-and-functions.sql ← scalar functions, CASE, computed columns
├── starter/                        ← YOUR work
│   ├── exercises.sql               ← 12 queries that run and are wrong
│   └── check.sh                    ← scores them; exits 0 only at 12 out of 12
├── tests/
│   └── run_tests.sh                ← 124 checks on actual result VALUES
├── expected-output/
│   ├── test-run.txt                ← the full captured harness run
│   ├── queries.txt                 ← every example query file and its output
│   ├── groupby-comparison.txt      ← the Python-versus-SQL proof
│   ├── exercise-check.txt          ← the starter scored, and the answer key
│   └── FIELDS.md                   ← what must match, what may differ
├── requirements/
│   ├── requirements.txt
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

All commands are run from this directory.

```bash
# 1. The whole thing. Start here.
bash tests/run_tests.sh
echo "exit code: $?"

# 2. Build your own copy of the database to play with.
bash examples/build_db.sh

# 3. Work through the eight query files in order. Read each file BEFORE you run
#    it — every query has a comment saying what it is meant to show.
sqlite3 -header -column examples/library.db < examples/queries/01-filters.sql
sqlite3 -header -column examples/library.db < examples/queries/02-patterns.sql
sqlite3 -header -column examples/library.db < examples/queries/03-null-traps.sql
sqlite3 -header -column examples/library.db < examples/queries/04-sorting.sql
sqlite3 -header -column examples/library.db < examples/queries/05-aggregates.sql
sqlite3 -header -column examples/library.db < examples/queries/06-group-by.sql
sqlite3 -header -column examples/library.db < examples/queries/07-having.sql
sqlite3 -header -column examples/library.db < examples/queries/08-case-and-functions.sql

# 4. Build GROUP BY by hand, then watch one SQL statement replace it.
python3 examples/groupby_from_scratch.py

# 5. Now the work. Twelve queries that run and lie. Score them first, so you
#    can see all twelve are wrong before you touch anything.
bash starter/check.sh

# 6. Fix them, one at a time, re-scoring as you go. Open the file:
#    starter/exercises.sql — each exercise states the required answer and a hint.
bash starter/check.sh

# 7. Only when you are done, compare with the model answers and read WHY.
sqlite3 examples/library.db < examples/exercise-answers.sql
```

To poke at the database interactively, open the shell and stay in it:

```bash
sqlite3 examples/library.db
sqlite> .mode column
sqlite> .headers on
sqlite> .tables
sqlite> .schema books
sqlite> SELECT COUNT(*) FROM loans WHERE returned_on IS NULL;
sqlite> .quit
```

## What the commands do

- `bash tests/run_tests.sh` — the harness. It builds its own database under a
  `mktemp -d` directory (so it never reads your `examples/library.db` and cannot
  be affected by anything you did to it), then runs 124 checks in fourteen
  sections, then deletes that directory in a `trap`. Every check compares an
  **actual result value** to a number or string worked out from the seed by
  hand. It prints `124 checks, 0 failure(s).` and exits 0, or lists each failing
  check with the expected and actual values side by side and exits 1.
- `bash examples/build_db.sh` — drops the three tables and recreates them from
  `examples/seed.sql`. Destructive and idempotent on purpose: run it whenever
  you want a clean database. It accepts an optional path argument, which is how
  the harness points it at a throwaway copy.
- `sqlite3 -header -column examples/library.db < examples/queries/NN-*.sql` —
  runs one themed file of worked queries. `-header` prints column names and
  `-column` aligns the output into readable columns; without them the shell
  prints pipe-separated values, which is better for scripts and worse for
  reading.
- `python3 examples/groupby_from_scratch.py` — runs the four stages (FROM,
  WHERE, GROUP BY, HAVING) as four Python functions, prints how many rows
  survive each one, prints the result table, then runs the equivalent single SQL
  statement and prints that table too. It exits 0 only if the two are identical
  row for row.
- `sqlite3 examples/library.db < starter/exercises.sql` — runs your twelve
  answers and prints them as `exNN|value` lines.
- `bash starter/check.sh` — runs the same file and compares each value with the
  required answer, printing a three-column table and `N correct, M still wrong.`
  It exits 0 only at twelve out of twelve.
- `sqlite3 examples/library.db < examples/exercise-answers.sql` — the model
  answers, each with a comment explaining what the broken version was actually
  asking.

## Expected output

The harness ends like this — a real captured run, in full in
[`expected-output/test-run.txt`](expected-output/test-run.txt):

```text
14. The lab stays offline, stays out of your way, and cleans up
  ok: no URL anywhere in examples/, starter/ or tests/
  ok: nothing under examples/ or starter/ calls sudo
  ok: no stray database in the lab root
  ok: the built database is git-ignored, so it is never committed

124 checks, 0 failure(s).
```

The NULL section is the one to read closely
([`expected-output/test-run.txt`](expected-output/test-run.txt)):

```text
4. NULL and three-valued logic
  ok: NULL = NULL is NULL, not 1 = 
  ok: NULL <> NULL is NULL too = 
  ok: NULL IS NULL is 1 = 1
  ok: NULL AND false is FALSE = 0
  ok: NULL AND true is UNKNOWN = 
  ok: NULL OR true is TRUE = 1
  ok: NULL OR false is UNKNOWN = 
  ok: NOT NULL is UNKNOWN = 
  ok: the trap: returned_on = NULL finds nothing = 0
  ok: the other trap: returned_on <> empty string finds the RETURNED ones = 30
  ok: IS NULL is the only correct test = 15
  ok: naive not-from-Pune loses the members with no city = 8
  ok: the honest version keeps them = 10
  ok: and 8 + 2 Pune members would be 10, not 12 — so the naive query lost 2 = 2
```

Read the last three lines together. There are 12 members and 2 of them live in
Pune, so "not from Pune" must be 10. The obvious query returns 8. Nothing warns
you, and 8 is a perfectly plausible number.

The from-scratch comparison
([`expected-output/groupby-comparison.txt`](expected-output/groupby-comparison.txt)):

```text
The 20 lines of Python:
  FROM      -> 24 rows
  WHERE     -> 20 rows survive
  GROUP BY  -> 6 buckets
  HAVING    -> 3 buckets survive

genre_label  books  rated  avg_rating  min_rating  max_rating  avg_pages 
-----------  -----  -----  ----------  ----------  ----------  ----------
science      7      5      4.3         3.7         4.8         326.285714
mystery      4      4      4.45        4.3         4.6         292.5     
fiction      3      3      4.1         3.5         4.7         443.666667
```

and then the identical table from one SQL statement, followed by
`IDENTICAL: 3 rows match exactly.`

Note `science: 7 books, 5 rated`. That two-row gap is the entire NULL lesson in
one line of output: the average 4.3 is an average of five numbers, not seven,
and only the `rated` column tells you so.

The untouched starter, scored
([`expected-output/exercise-check.txt`](expected-output/exercise-check.txt)):

```text
Exercise   your answer                required
---------  -------------------------  -------------------------
ex01       0                          15                         WRONG
ex02       8                          10                         WRONG
ex03       0                          2                          WRONG
ex04       2                          4                          WRONG
ex05       3.47                       4.16                       WRONG
ex06       20                         4                          WRONG
```

Every one of those twelve wrong answers came from a query that ran without a
warning. Not one of them raised an error.

[`expected-output/queries.txt`](expected-output/queries.txt) holds the output of
all eight query files, and
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states which values must
be identical on your machine and which are expected to differ.

## Validation steps

1. `bash tests/run_tests.sh` ends with `124 checks, 0 failure(s).` and exits 0.
2. `bash examples/build_db.sh` prints `seeded: 24 books, 12 members, 45 loans`,
   and running it a second time prints the same thing — not doubled counts.
3. `SELECT COUNT(*) FROM loans WHERE returned_on = NULL` returns **0** and
   `... WHERE returned_on IS NULL` returns **15**. Both run without error.
4. `SELECT COUNT(*) FROM members WHERE city <> 'Pune'` returns **8**, while
   there are 12 members and 2 of them are in Pune.
5. `SELECT ROUND(AVG(rating),2) FROM books` returns **4.16**, and the same query
   wrapped in `COALESCE(rating,0.0)` returns **3.47**.
6. `SELECT COUNT(*), COUNT(rating) FROM books` returns **24** and **20**.
7. `SELECT author FROM books WHERE COUNT(*) > 3 GROUP BY author` is rejected with
   `Error: in prepare, misuse of aggregate: COUNT()`, and the same question
   written with `HAVING` returns 3 authors.
8. `GROUP BY genre` produces **6** buckets while `COUNT(DISTINCT genre)` returns
   **5** — the missing one is the bucket of unclassified books.
9. `python3 examples/groupby_from_scratch.py` prints
   `IDENTICAL: 3 rows match exactly.` and exits 0.
10. `bash starter/check.sh` on the untouched starter prints
    `0 correct, 12 still wrong.` and exits 1. After you have fixed all twelve it
    prints `12 correct, 0 still wrong.` and exits 0.
11. Deliberately break one: change your fixed exercise 1 back to `= NULL` and
    confirm `check.sh` goes red again and exits non-zero. A scorer you have not
    seen fail is a scorer you have no reason to trust.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

Expected final line: `124 checks, 0 failure(s).` Exit code 0 on success, 1 on
any failure.

Two things about this harness are worth knowing before you read it.

**It checks values, not exit codes.** A test that only asserted "the query ran"
would pass on all twelve of the broken starter queries, because all twelve run
perfectly. Every check here names the value it expects.

**Section 5 exists to stop you making the numbers agree by cheating.** The most
tempting way to make NULLs stop being annoying is to fill them in — replace the
missing ratings with 0.0, the missing return dates with an empty string — and
then every simple query "works". Section 5 pins the values that such a fix would
change: `MIN(rating)` must be `3.2` and not `0.0`; `AVG(rating)` must be `4.16`
and must **not** equal the `COALESCE`-to-zero average of `3.47`; `SUM` over zero
rows must be NULL while `TOTAL` over the same rows is `0.0`. If someone
"fixes" the seed data, those checks go red.

The harness also pins the two places SQLite is more permissive than standard SQL
— a `SELECT` alias used in `WHERE`, and a bare column in an aggregate query — so
the lesson's claims about portability stay tied to observed behaviour rather than
to memory.

## Cleanup

```bash
rm -f examples/library.db
```

That is all of it. Nothing was installed, no service was started, no port was
opened, nothing was written outside this directory, and the test harness removes
its own `mktemp -d` directory in a `trap` even if you interrupt it with Ctrl-C.

To reset your exercise work: `git checkout -- starter/exercises.sql`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The ones you are most likely to
meet: `unable to open database file`, which is nearly always the wrong working
directory; `no such table: books`, which means a typo in the database name
created a fresh empty file rather than failing; a query returning 0 rows when
you are certain it should not, which in this lab is almost always a NULL;
`misuse of aggregate: COUNT()`, which is an aggregate in `WHERE` where it should
be in `HAVING`; and an average that looks too low, which is `COALESCE(col, 0)`
inventing data.

## Security notes

See [security.md](security.md). Short version: this lab opens no socket, needs
no credentials, starts no daemon and touches nothing outside its own directory —
SQLite has no users and no passwords, so access to the data is exactly
filesystem access to one file. The risk in this topic is not here but in the
very next thing anyone does with a query, which is to build one by pasting a
value into a string; `security.md` shows why parameter placeholders are the only
correct answer and why escaping quotes yourself is not. It also makes a point
that belongs to today specifically: publishing aggregates is not automatically
anonymising, because a bucket containing one row identifies one person. All
names in the seed are fictional and every email address uses the permanently
reserved `.invalid` domain.

## Extension exercises

1. **Add the query you actually want.** Write one question about this data that
   none of the eight files answers, then answer it. If it needs data from two
   tables, you have just discovered why tomorrow is about joins.
2. **Find the smallest bucket.** Write a query that returns the grouping key with
   the fewest rows in it. Then re-read the privacy paragraph in `security.md` and
   decide whether that result would be safe to publish if these were real people.
3. **Make the NULL handling explicit.** Take `06-group-by.sql` query 6.3 and add
   a column that reports what fraction of each bucket actually has a rating.
   A summary that does not say how much data it is based on is a summary you
   cannot act on.
4. **Break the scorer on purpose.** Edit `starter/check.sh` to require `99` for
   exercise 1, run it, and watch that row go red. One minute, and afterwards you
   know the green ticks mean something.
5. **Time the OFFSET.** Write a loop that pages through the books table with
   `LIMIT 5 OFFSET N` for increasing N, and reason about what the engine has to
   do for each page. With 24 rows you will measure nothing; the point is to
   predict what happens at 24 million and then check your prediction against the
   lesson's explanation.
6. **Port it.** Take `06-group-by.sql` and work out, without running it, which
   queries would need changing for PostgreSQL. There are two, and both are noted
   in the files. Then decide whether you want to keep writing the SQLite-only
   spelling.
7. **Extend the from-scratch script.** Add `COUNT(DISTINCT author)` per bucket to
   `groupby_from_scratch.py` and to the SQL, and keep the assertion passing. You
   will need a `set` in the accumulator, which is exactly what the engine does.

## Navigation

- **Previous day:** Day 85 — the relational model, SQLite, and your first table
  (`labs/sections/programming-with-python/day-085-relational-databases-and-sqlite/`).
- **Next day:** Day 87 — joins and relationships, which is how you ask questions
  that span more than one table
  (`labs/sections/programming-with-python/day-087-joins-and-relationships/`).
- **Week 13:** SQL and Relational Databases
  (`labs/sections/programming-with-python/`).
