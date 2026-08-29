# Week 13 project — Personal Library Database

This week was about **SQL and relational databases**: the relational model and
SQLite, `SELECT` with filtering and aggregation, joins and relationships,
writing data with transactions and constraints, indexes and query plans,
SQLite from Python, and designing a real schema. Day 91 walked you through
somebody else's requirements. This project is the same work with the training
wheels off: **your** collection, **your** questions, and a schema nobody
checked before you built it.

## What you are building

A database for a collection you actually own — books, films, board games,
recipes, plants, tools, whatever you have enough of to be annoying to keep
track of — plus a Python reporting script that answers questions you actually
have about it.

The domain matters less than the discipline. What makes this a Week 13 project
rather than a spreadsheet is that the schema refuses to record things that
cannot be true, the questions are answered by the database rather than by
Python loops, and every number in the report can be traced to a query you can
explain.

Pick a domain with at least one real many-to-many relationship and at least one
hierarchy or ordering. A collection where everything is a flat list of
independent items will not exercise the week.

## Requirements

Show this week's skills:

- **A schema derived from written requirements** (Day 91): before any
  `CREATE TABLE`, write a paragraph of prose describing the domain as if to
  somebody who has never seen it. Then annotate it — which phrase is an
  entity, which an attribute, which a relationship, which is derived. Keep
  both; the annotation is the deliverable, not scaffolding.
- **Keys chosen deliberately** (Day 91): a surrogate primary key, with any
  natural key kept as a `UNIQUE` constraint. Write one sentence on what would
  break if you had made the natural key the primary key.
- **Relationships that match reality** (Day 87): at least one one-to-many and
  one many-to-many. If your junction table has an attribute of its own — an
  order, a role, a date — say so, because that is the junction becoming an
  entity.
- **Constraints doing the work** (Day 88): `NOT NULL`, `UNIQUE`, `CHECK` and
  foreign keys, with `PRAGMA foreign_keys = ON` set per connection. For each
  constraint, name the impossible row it exists to prevent. At least three
  must be things you would otherwise have validated in Python.
- **Nothing derived is stored** (Day 91): if a value can be computed from
  other rows, compute it. If you decide to store one anyway, write down why
  and what will keep it honest.
- **Ten questions, ten queries** (Days 86, 87, 91): write the questions in
  English first. At least one must need a `LEFT JOIN` to show zeros, one a
  common table expression, one a window function, and one a subquery or
  `EXISTS`. If a question turns out awkward to answer, that is information
  about your schema — record what you changed.
- **Measured indexing** (Day 89): generate or import enough rows that at least
  one query is genuinely slow, capture `EXPLAIN QUERY PLAN` before and after
  an index, and record both timings. Then find one index you added that did
  not help, and remove it.
- **A repository, not scattered SQL** (Day 90): all SQL in one module, every
  value bound as a parameter, transactions where they belong. No SQL string
  anywhere is built by concatenation or an f-string.
- **A reproducible report**: the script takes the report instant as a
  parameter with a default rather than reading the clock, so its output can be
  compared and tested.

## Steps

1. Write the prose description and annotate it. Do not open an editor for SQL
   until you have.
2. Write the ten questions. These decide the schema more than the entities do.
3. Draw the tables and relationships on paper. It is faster to notice a
   missing junction table there than after seeding.
4. Build the schema with its constraints, then deliberately try to insert four
   impossible rows and confirm each is refused.
5. Seed enough real data to be interesting, including the awkward cases: the
   item with no relationships, the one with several, the withdrawn one.
6. Answer the ten questions one at a time, and after each one ask whether the
   schema made it easy or awkward.
7. Grow the data until something is slow, then index by measurement rather
   than by guess.
8. Wrap it in the repository and write the report.
9. Run the whole thing from an empty directory to prove the setup is complete.

## Expected output

- `python3 report.py` → the full report, identical on two consecutive runs.
- `python3 report.py --as-of 2026-01-01T00:00:00Z` → a different, correct
  report for that instant.
- Each of the four impossible inserts → a real error message naming the
  constraint that refused it, captured in your notes.
- `EXPLAIN QUERY PLAN` for your slow query → `SCAN` before the index and
  `SEARCH ... USING INDEX` after, both captured.
- Your timing note → the before and after figures, with the number of rows
  stated, and a sentence saying these are your machine's numbers.
- `bash tests/run_tests.sh` (or `pytest`) → every question's answer checked
  against a value you computed by hand from the seed data.
- `grep -rn "f\"SELECT\|' + \|\" + " repository.py` → no matches.

## Validation

- [ ] The prose description and its annotation are committed, and every table
      traces back to a phrase in it.
- [ ] A surrogate primary key everywhere, with natural keys as `UNIQUE`, and a
      written sentence on what a natural primary key would have broken.
- [ ] At least one many-to-many, with any junction attribute called out.
- [ ] Four impossible rows are refused by the schema, with the real error
      messages captured — not by application code.
- [ ] `PRAGMA foreign_keys = ON` is set on every connection, and a test proves
      an orphan insert fails.
- [ ] No derived value is stored, or the one exception is justified in writing.
- [ ] Ten English questions, ten queries, including a `LEFT JOIN` showing
      zeros, a CTE, a window function, and an `EXISTS` or subquery.
- [ ] At least one query measured before and after an index, with both plans
      and both timings captured, and one unhelpful index found and removed.
- [ ] All SQL lives in the repository module and every value is bound.
- [ ] The report takes its instant as a parameter and is identical across two
      runs.
- [ ] Tests assert the actual answers, computed by hand from the seed data —
      not merely that the queries execute.
- [ ] The database is built by a script from schema and seed files; the `.db`
      file itself is not committed.

## Troubleshooting

- Every question needs a Python loop after the query? The schema is fighting
  you. Usually a missing junction table or a hierarchy stored as a text path.
- A `CHECK` constraint that never fires? SQLite accepts a `CHECK` referencing
  a column that does not exist in some forms. Try the impossible row and watch
  it succeed — a constraint you have never seen refuse anything is decoration.
- Foreign keys silently ignored? `PRAGMA foreign_keys` is off by default and
  is per connection, and it is a no-op inside a transaction. Set it
  immediately after connecting.
- The index made no difference? Check the plan, not the clock. If it still
  says `SCAN`, something wraps the column in a function, or the `LIKE` has a
  leading wildcard, or the composite index's leftmost column is not in the
  query.
- The second run of the report differs? Something read the clock. Search for
  `now`, `today` and `datetime.now`.
- A query returns nothing and you cannot see why? If it uses `NOT IN`, put one
  NULL in the subquery's column and watch the whole result disappear. Use
  `NOT EXISTS`.
- Numbers ending in odd fractions of a penny? Money is in a float somewhere.
  It should be an integer count of minor units all the way to the display
  edge.
