# Day 088 lab — Change the Data Safely

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Inserting, Updating, and Schema Design
- **Day number:** 88 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-088-inserting-updating-and-schema-design
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-088-inserting-updating-and-schema-design` when the site is running.
<!-- generated-links:end -->

## Purpose

For three days you have been reading. Day 85 gave you the relational model and
SQLite, Day 86 gave you `SELECT` with filtering, sorting and grouping, and Day
87 gave you keys, relationships and joins. Every one of those is safe: the worst
a bad `SELECT` can do is give you a wrong answer, and you can run it again.

Today you start changing data, and that symmetry breaks. A bad `UPDATE` does not
give you a wrong answer — it *makes* one, and leaves it there, looking exactly
like a right one.

So this lab is arranged as a series of proofs rather than a series of features.
You will run the most expensive mistake in SQL against a throwaway copy and
measure precisely how many rows it destroys. Then you will prove, one at a time,
that each safety mechanism does what it claims:

- Does the SELECT-first discipline really produce the intended row set?
- Is the database file **byte-for-byte identical** after a rolled-back
  transaction?
- Does each constraint reject the exact bad row it exists for, and what is the
  real error message?
- Does `ON DELETE CASCADE` remove children, and does `RESTRICT` refuse?
- Does the documented table rebuild add a constraint `ALTER TABLE` cannot, without
  losing a row or a foreign key?
- Is a migration runner atomic when a migration fails, and does running it twice
  really apply nothing the second time?

The last of those you build yourself. A migration runner in about 150 lines,
tracking the schema version in `PRAGMA user_version` — the artefact that shows
you what Alembic and Django migrations are actually doing before you decide
whether you need either.

101 checks, all offline, all against databases in a temporary directory that is
deleted when the harness exits.

## Learning objectives

- Measure the damage of a `WHERE`-less `UPDATE`, and use the SELECT-first
  routine that prevents it.
- Write every useful shape of `INSERT`: single row, multi-row `VALUES`,
  `INSERT INTO ... SELECT`, `RETURNING`, and `UPSERT` via `ON CONFLICT`.
- Prove that a rolled-back transaction leaves the database unchanged, and
  discover the one thing about transaction failure that almost everybody has
  backwards.
- Make each of `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `PRIMARY KEY`, foreign
  keys and `STRICT` typing reject a bad row, and read the real error each gives.
- Show that foreign keys are unenforced until you ask, and choose between
  `ON DELETE CASCADE` and `ON DELETE RESTRICT` on what the child row means.
- Perform the documented create-copy-drop-rename rebuild to add a constraint
  `ALTER TABLE` cannot add, preserving rows and foreign keys.
- Build a versioned migration runner that is atomic on failure and idempotent on
  re-run, and explain why the version bump must share the transaction.
- Explain why a training-data table without constraints is a model problem
  waiting to be misdiagnosed.

## Prerequisites

- The Day 88 lesson (read it first).
- Day 85: the relational model, SQLite, and the `sqlite3` shell.
- Day 86: `SELECT`, `WHERE`, `ORDER BY`, `GROUP BY` and aggregates — you will
  write the `SELECT` before every `UPDATE`.
- Day 87: primary and foreign keys, joins, and the fact that
  `PRAGMA foreign_keys` is off by default. This lab proves that one again,
  because it is the single most consequential default in SQLite.
- Day 64–66: files and exceptions, for the migration runner.
- Comfort running a shell command and reading a Python traceback.

## Supported operating systems

- **macOS** — fully supported. All captures were taken on macOS 26.5.2 (Apple
  Silicon, arm64) with the preinstalled `sqlite3` 3.51.0 and Python 3.14.0.
- **Linux** — fully supported. Install `sqlite3` if it is absent; use
  `sha256sum` if you have no `shasum`.
- **Windows** — use WSL and follow the Linux path. On native Windows
  `tests/run_tests.sh` is a bash script and `shasum` is absent. No captures were
  taken on native Windows, so this lab does not claim what it would print there.

## Hardware requirements

Any computer built this century. The largest database this lab creates is about
24 KB, the whole harness finishes in a few seconds, and nothing is downloaded.
No GPU, no special memory, no disk of consequence.

## Required software

| Tool | Why | Version used |
| --- | --- | --- |
| `sqlite3` shell | Every SQL demonstration | 3.51.0 (`/usr/bin/sqlite3`) |
| `python3` (3.9+) | The migration runner, standard library only | 3.14.0 (bundled SQLite 3.53.3) |
| `bash` | The test harness | 3.2.57 |
| `shasum` | The byte-for-byte rollback proof | macOS builtin |

Note the two SQLite version numbers. The shell and Python link separate copies
of the library, and on the authoring machine they differ by two releases — far
enough that one accepts `ALTER TABLE ... ALTER COLUMN` and the other calls it a
syntax error. The harness prints both, and section 5 turns that difference into
a test. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source, and there is nothing to install beyond
what your operating system already ships. SQLite is in the **public domain** —
not merely permissively licensed — per its own project documentation. Python is
under the PSF licence. There are no third-party packages at all, which is a
teaching decision explained in [`requirements/README.md`](requirements/README.md):
you should write the migration runner that Alembic replaces before you judge
whether you need Alembic.

## Installation

Nothing to install. Confirm your tools and build the database:

```bash
cd labs/sections/programming-with-python/day-088-inserting-updating-and-schema-design
sqlite3 --version
python3 --version
sqlite3 library.db < examples/seed.sql
sqlite3 library.db "SELECT count(*) FROM loans;"      # 12
```

Then — and this is the habit the whole lab is about — take a copy before you
change anything:

```bash
cp library.db library-backup.db
```

## File structure

```text
day-088-inserting-updating-and-schema-design/
├── README.md                          ← you are here
├── metadata.yml
├── examples/                          ← the finished demonstrations
│   ├── seed.sql                       ← the library schema, fully constrained
│   ├── 01-the-expensive-mistake.sql   ← the WHERE-less UPDATE, measured
│   ├── 02-insert-forms.sql            ← INSERT, RETURNING, UPSERT
│   ├── 03-transactions.sql            ← BEGIN, COMMIT, ROLLBACK, atomicity
│   ├── 04-update-and-delete.sql       ← expressions, subqueries, soft delete
│   ├── 05-constraints.sql             ← training data with and without rules
│   ├── 06-cascade-vs-restrict.sql     ← delete rules, and the pragma trap
│   ├── 07-table-rebuild.sql           ← the create-copy-drop-rename dance
│   ├── migrate.py                     ← the migration runner, ~150 lines
│   └── migrations/
│       ├── 001_initial_schema.sql
│       ├── 002_add_soft_delete.sql
│       ├── 003_limit_loan_length.sql  ← a rebuild, run as a migration
│       └── 004_add_generated_columns.sql
├── starter/                           ← YOUR work
│   ├── migrate.py                     ← 4 numbered exercises
│   └── exercises.sql                  ← 6 numbered SQL exercises
├── tests/
│   └── run_tests.sh                   ← 101 checks
├── expected-output/
│   ├── test-run.txt                   ← the full harness run
│   ├── expensive-mistake.txt          ← 12 rows changed, 1 intended
│   ├── insert-forms.txt
│   ├── transactions.txt
│   ├── update-and-delete.txt
│   ├── constraints.txt                ← 7 real rejection messages
│   ├── cascade-and-restrict.txt
│   ├── table-rebuild.txt
│   ├── migrations.txt                 ← applied, idempotent, rolled back
│   └── FIELDS.md                      ← what must match, what may differ
├── requirements/
│   ├── requirements.txt               ← deliberately empty, and says why
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

From the lab directory, after the install step above.

```bash
# 1. The whole thing. Start here.
bash tests/run_tests.sh
echo "exit code: $?"
```

Then work through the demonstrations by hand. **Every destructive one runs
against a copy** — that is the pattern, not a formality.

```bash
# 2. The most expensive mistake in SQL, measured on a throwaway file.
cp library.db scratch.db
sqlite3 scratch.db < examples/01-the-expensive-mistake.sql
rm scratch.db

# 3. Every useful shape of INSERT, plus RETURNING and UPSERT.
cp library.db scratch.db
sqlite3 scratch.db < examples/02-insert-forms.sql

# 4. Transactions. Watch the numbers change inside, then change back.
cp library.db scratch.db
sqlite3 scratch.db < examples/03-transactions.sql

# 5. The byte-for-byte rollback proof, by hand.
cp library.db scratch.db
shasum -a 256 scratch.db
sqlite3 scratch.db "BEGIN; UPDATE loans SET returned = 1;
                    DELETE FROM loans WHERE id <= 3; ROLLBACK;"
shasum -a 256 scratch.db          # identical, character for character

# 6. UPDATE with expressions and subqueries; DELETE and soft delete.
cp library.db scratch.db
sqlite3 scratch.db < examples/04-update-and-delete.sql

# 7. Constraints, on a training-data table. Note what the LOOSE table accepts.
sqlite3 training.db < examples/05-constraints.sql
# ... then make one fire yourself, and read the message:
sqlite3 training.db "INSERT INTO examples_strict (text,label,split,token_count)
                     VALUES ('a new one','neutralish','train',3);"

# 8. Foreign keys: off by default, then CASCADE versus RESTRICT.
cp library.db scratch.db
sqlite3 scratch.db < examples/06-cascade-vs-restrict.sql
sqlite3 scratch.db "PRAGMA foreign_keys = ON; DELETE FROM books WHERE id = 8;"

# 9. The documented rebuild: add a constraint ALTER TABLE cannot add.
cp library.db scratch.db
sqlite3 scratch.db < examples/07-table-rebuild.sql

# 10. The migration runner. Run it TWICE — the second run is the point.
python3 examples/migrate.py --db app.db --dir examples/migrations
python3 examples/migrate.py --db app.db --dir examples/migrations
sqlite3 app.db "PRAGMA user_version;"          # 4

# 11. Prove it is atomic. Break a migration on purpose.
printf 'CREATE TABLE gone (x INTEGER);\nCREATE TABLE nope (bad SYNTAX HERE!!;\n' \
  > examples/migrations/005_broken.sql
python3 examples/migrate.py --db app.db --dir examples/migrations; echo "exit: $?"
sqlite3 app.db "PRAGMA user_version;"          # still 4
sqlite3 app.db "SELECT count(*) FROM sqlite_schema WHERE name='gone';"   # 0
rm examples/migrations/005_broken.sql

# 12. Your task: the four gaps in starter/migrate.py and the six in
#     starter/exercises.sql.
python3 starter/migrate.py --db /tmp/yours.db --dir examples/migrations
```

## What the commands do

- `bash tests/run_tests.sh` — the whole harness, 101 checks in ten sections. It
  builds every database under a `mktemp -d` that a `trap` removes on exit, so it
  never writes to the lab directory and never leaves anything behind. Each check
  compares a **real value** against an expected one and prints both when they
  differ; the constraint checks compare against the **real error message**
  SQLite produced.
- `examples/01-the-expensive-mistake.sql` — runs `UPDATE loans SET returned = 1;`
  with the `WHERE` clause missing and reports `changes()`. One row was intended.
  Twelve are changed. The eight that were destroyed were overwritten with a
  *plausible* value, which is what makes this the expensive one.
- `examples/02-insert-forms.sql` — single-row and multi-row `INSERT`,
  `INSERT INTO ... SELECT`, `RETURNING` to get back the id and the
  `DEFAULT`-filled column, and `UPSERT` updating two rows and inserting a third
  in one statement. Also `DO NOTHING`, and why `excluded.copies` is not `copies`.
- `examples/03-transactions.sql` — three destructive statements confirmed real
  inside a transaction and then abandoned; a two-statement change that must not
  half-happen; and the SELECT-first routine performed properly.
- `examples/04-update-and-delete.sql` — `copies = copies + 2` instead of a
  literal (no read-then-write gap), a correlated-subquery `UPDATE` that fills a
  denormalized counter, a real `DELETE`, and the soft delete that keeps the row
  and stays reversible.
- `examples/05-constraints.sql` — the same training-data table twice. The loose
  one accepts a duplicated example, a null label, a split value that escapes
  your filter, an invented label, and the word `banana` in a column declared
  `INTEGER`. The strict one accepts none of them.
- `examples/06-cascade-vs-restrict.sql` — first proves foreign keys do nothing
  with the pragma off (a parent deletes, the children are orphaned, and
  `PRAGMA foreign_key_check` finds them afterwards), then shows `CASCADE`
  removing three child rows while `changes()` reports only one.
- `examples/07-table-rebuild.sql` — the documented procedure, all four steps in
  one transaction with foreign keys off around it, adding a `CHECK` that
  `ALTER TABLE` cannot add. Then `PRAGMA foreign_key_check` before turning
  enforcement back on.
- `examples/migrate.py` — the runner. It reads `PRAGMA user_version`, applies
  each higher-numbered file inside `BEGIN ... COMMIT` **with the version bump in
  the same transaction**, and refuses malformed migration sets before writing
  anything. `--dry-run` names what it would do; `--status` reports and stops.

## Expected output

The harness ends like this (a real captured run — see
[`expected-output/test-run.txt`](expected-output/test-run.txt) for all 126 lines):

```text
9. Nothing here reaches the network or the wider machine
  ok: no example or starter file opens a network connection (0)
  ok: nothing a learner runs asks for sudo (0)
  ok: every database this suite made lives under one temporary directory
  ok: the lab directory itself was never written to

101 checks, 0 failure(s).
```

The mistake, measured
([`expected-output/expensive-mistake.txt`](expected-output/expensive-mistake.txt)):

```text
--- before: how many loans are outstanding? ---
outstanding=8
returned=4

--- the SELECT you should write first ---
the SELECT matches 1 row(s)

--- the statement with the WHERE clause forgotten ---
UPDATE changed 12 row(s)

--- after ---
outstanding=0
returned=12
```

Seven constraints, seven real error messages
([`expected-output/constraints.txt`](expected-output/constraints.txt)):

```text
Error: stepping, UNIQUE constraint failed: examples_strict.text (19)
Error: stepping, NOT NULL constraint failed: examples_strict.label (19)
Error: stepping, CHECK constraint failed: split IN ('train', 'validation', 'test') (19)
Error: stepping, CHECK constraint failed: label IN ('positive', 'negative', 'neutral') (19)
Error: stepping, CHECK constraint failed: length(trim(text)) > 0 (19)
Error: stepping, cannot store TEXT value in INTEGER column examples_strict.token_count (19)
Error: stepping, CHECK constraint failed: token_count > 0 (19)
```

Read those as documentation. Each one names the rule that fired, which is why a
constraint is better documentation than a comment: it tells you the rule *at the
moment you break it*.

The migration runner, applied then idempotent then rolled back
([`expected-output/migrations.txt`](expected-output/migrations.txt)):

```text
current version: 0
  applying 001: 001_initial_schema.sql ... ok
  applying 002: 002_add_soft_delete.sql ... ok
  applying 003: 003_limit_loan_length.sql ... ok
  applying 004: 004_add_generated_columns.sql ... ok
now at version 4 -- 4 migration(s) applied

current version: 4
up to date -- 0 migration(s) applied

  applying 005: 005_broken.sql ... FAILED
error: 005_broken.sql: unrecognized token: "!"
error: rolled back; database is still at version 4
```

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states which of these
values are fixed facts about SQL and which are properties of this machine.

## Validation steps

1. `bash tests/run_tests.sh` ends with `101 checks, 0 failure(s).` and exits 0.
2. The WHERE-less `UPDATE` reports `changed 12 row(s)` while the SELECT-first
   version reports `1`.
3. `shasum -a 256` before and after a rolled-back transaction gives the **same**
   hash, and `sqlite3 db .dump` gives byte-identical output.
4. A script that ends `... COMMIT;` after a constraint error **keeps** the
   earlier successful statement (`copies` is 13); the same script ending
   `ROLLBACK;` does not (`copies` is 3). Both are checked.
5. Each of the seven bad training rows is refused with a message naming the
   constraint, and `examples_strict` still holds exactly 4 rows afterwards.
6. `PRAGMA foreign_keys` reports `0` on a new connection. With it off, deleting
   member 1 leaves 2 orphaned loans and `PRAGMA foreign_key_check` finds them.
7. With it on, deleting member 3 reports `members_deleted=1 loans_left=9` — the
   cascade removed three rows and `changes()` mentioned none of them.
8. `DELETE FROM books WHERE id = 8` fails with `FOREIGN KEY constraint failed`;
   deleting an unreferenced book succeeds.
9. After the rebuild: 13 loans, 2 foreign keys, 0 `foreign_key_check`
   violations, the new 90-day `CHECK` present and the old ones still there.
10. `migrate.py` applies 4 migrations then applies 0; a broken migration exits 1,
    leaves `user_version` at 4, and creates none of its tables.
11. `git status` is clean apart from `library.db`, `app.db` and any `scratch.db`
    you made by hand.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `101 checks, 0 failure(s).` Exits 0 on success, non-zero on
any failure.

Two sections are worth reading before you run them. **Section 2** does not merely
assert that a rollback works — it takes a SHA-256 of the file, runs three
destructive statements, confirms *inside the transaction* that they took effect,
rolls back, and requires the hash to be identical. Then it does the same thing
with a full `.dump` comparison, because a checksum tells you the bytes match and
a dump tells you the rows do.

**Section 5** probes what your `ALTER TABLE` can actually do rather than trusting
the documentation or this README. The four documented operations must work. The
three that are not documented — adding a `CHECK`, a `UNIQUE` or a foreign key —
must fail. And `ALTER COLUMN ... SET NOT NULL`, which arrived in SQLite 3.53.0,
is asserted to match *your build's own version number*, so the check is correct
on an older or a newer machine rather than only on the authoring one.

To watch the suite fail, change an expected value — make `"seed has 6 members"`
expect `"999"` — and re-run. A suite you have never seen fail is a suite you have
no reason to trust.

## Cleanup

```bash
rm -f library.db library-backup.db scratch.db training.db app.db fresh.db
rm -f examples/migrations/005_broken.sql
```

The harness needs no cleanup: it works entirely inside a `mktemp -d` directory
that a `trap` removes on exit, including on Ctrl-C. The last check in the suite
confirms the lab directory was never written to. To reset your own work:
`git checkout -- starter/`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The ones you are most likely to
meet: an `UPDATE` that changed more rows than you expected (today's whole
subject — restore your copy); `0 rows changed` when you expected some, which is
almost always type, case or whitespace in the `WHERE` clause; a foreign key that
did nothing, which is `PRAGMA foreign_keys` being off; `Error: near` on
`ALTER TABLE`, which is the version boundary; and a transaction that failed but
kept its earlier changes anyway, which is correct and is explained there.

## Security notes

See [security.md](security.md). Short version: the lab touches nothing outside a
temporary directory, reaches no network, and needs no `sudo` — but it teaches
genuinely destructive SQL, so every demonstration runs against a copy and you
should never practise on a database you care about. It also states the rule that
becomes urgent the moment a schema sits behind a web form: build statements with
bound parameters, never string formatting, because the injected version of
today's lesson is a stranger running your WHERE-less `UPDATE`. The one place
`migrate.py` formats a value into SQL is `PRAGMA user_version`, which accepts no
bound parameter; the value is an `int()` from a filename and the source says so.

## Extension exercises

1. **Add `ON DELETE SET NULL` to the picture.** Add a `reserved_by` column to
   `books` referencing `members` with `ON DELETE SET NULL`, then delete a member
   and watch the third option behave. Write down, in one sentence each, the
   question that makes each of `CASCADE`, `RESTRICT` and `SET NULL` the right
   answer.
2. **Make the runner record history.** `PRAGMA user_version` holds one number,
   so it cannot say *when* a migration ran or how long it took. Add a
   `schema_migrations` table alongside it and write both. Then answer the harder
   question: if the table and `user_version` ever disagree, which one is right,
   and how would you find out?
3. **Add a down-migration.** Give each migration a matching `NNN_name.down.sql`
   and a `--rollback-to N` flag. Then work out why so many teams that build this
   never use it — and what they do instead when a migration goes wrong in
   production.
4. **Break the rebuild on purpose.** In `007-table-rebuild.sql`, omit one foreign
   key from the retyped definition in step 1. Run it, then run
   `PRAGMA foreign_key_list('loans')`. Nothing errors. This is the failure mode
   the rebuild procedure is most often hit by, and seeing it silently succeed is
   worth more than reading the warning.
5. **Normalize something.** Add an `authors` table and move `books.author` into
   it as a foreign key, using a migration and the rebuild procedure. Count how
   many rows changed and how many queries you had to rewrite. That number is the
   real cost of the normalization the lesson recommends.
6. **Then denormalize it back.** Add a `loan_count` to `members`, keep it correct
   with a trigger, and then write down every way it can still drift. Compare that
   with the generated column in migration 004, which cannot drift at all — and
   work out why you cannot use a generated column for `loan_count`.
7. **Fill a table from a real feed.** Take the JSON from Day 65, design a
   constrained `STRICT` table for it, and load it with an `UPSERT` so the loader
   is safe to run twice. Then run it twice and prove it.

## Navigation

- **Previous day:** Day 87 — keys, relationships and joins
  (`labs/sections/programming-with-python/day-087-keys-relationships-and-joins/`).
- **Next day:** Day 89 — indexes and query performance
  (`labs/sections/programming-with-python/day-089-indexes-and-query-performance/`).
  Every index it adds is a schema change, applied by the runner you built today.
- **Week 13 project:** `labs/sections/programming-with-python/projects/week-13/`.
