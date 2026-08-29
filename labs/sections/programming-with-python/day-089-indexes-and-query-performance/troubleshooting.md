# Troubleshooting — Day 089

Ordered roughly by how often you will meet each one.

## "My numbers are nothing like the captured ones"

**This is expected and is not a fault.** Every timing in
`expected-output/` is from one machine on one day. A different CPU, disk,
Python build, SQLite build, or simply a browser doing something in the
background moves them, sometimes by a large factor.

Check the shape rather than the digits:

- Does the scan column grow roughly in step with the table?
- Does the seek column stay roughly flat as the table grows?
- Is the indexed lookup at least tens of times faster than the scan?

If all three hold, everything is working. `expected-output/FIELDS.md` lists
exactly which values must match and which are expected to differ.

## "The difference is tiny, or the wrong way round"

Almost always one of three things.

**The table is too small.** On 5,000 rows a scan is already instant and
there is nothing for an index to improve. Use at least 100,000 rows; the
captures use 400,000.

**The machine is too busy.** Look at the `spread` figure. If the spread is
bigger than the difference you are trying to see, you have measured noise.
Close whatever else is working, and re-run.

**You timed the wrong thing.** `connection.execute(...)` on its own does
almost no work — the rows are produced as you step through them. Always
`.fetchall()` inside the timed block. `examples/timing.py` does; a hand-
written timer often does not.

## "The plan says my index name, but the query is still slow"

Read the plan again, and read the first word.

```text
SEARCH events USING COVERING INDEX ix_trace (trace_id=?)   <- a seek
SCAN   events USING COVERING INDEX ix_trace                <- still every entry
```

`SCAN ... USING INDEX` means the planner decided your index was a narrower
thing to walk end to end than the table. That can be a genuine
improvement, and it is still linear in the number of rows. Only `SEARCH`
is a descent to the rows you asked for.

This is the single most common misreading of `EXPLAIN QUERY PLAN`.

## "I created the index and the plan did not change"

Work through these in order.

1. **Is a function or expression wrapping the column?** `WHERE
   lower(trace_id) = ?` cannot use an index on `trace_id`. Neither can
   `WHERE substr(...)`, `WHERE date(created_on) = ...`, or `WHERE score * 2
   > ?`. Fix: rewrite the query so the bare column is compared, or build an
   index on the expression itself.
2. **Is the column the leading one in a composite index?** An index on
   `(run_id, status)` cannot seek on `status` alone. Fix: reorder the
   index, or add a second one.
3. **Does the `LIKE` pattern start with a wildcard?** `'%abc'` cannot use
   an index. `'abc%'` can in principle — see the next entry.
4. **Is one branch of an `OR` unindexed?** Then the whole condition falls
   back to a scan. Index every branch, or write it as a `UNION`.
5. **Is the index selective enough to be worth using?** If a value matches
   a third of the table, reading the table is genuinely cheaper than
   seeking a third of it one row at a time, and the planner is right.
   `ANALYZE`, then look at `sqlite_stat1`.
6. **Is it a partial index?** The planner will not use one unless it can
   prove the query falls inside the index's `WHERE` clause.

## "A prefix LIKE will not use my index"

`WHERE trace_id LIKE 'tr-4070%'` scans by default, and this surprises
everybody. SQLite's `LIKE` is case-insensitive by default while an ordinary
index is sorted in binary order, and a case-insensitive match cannot be
answered from a case-sensitive ordering.

Two fixes, both shown in `examples/blocked.py`:

```sql
-- rewrite as the range it really is
WHERE trace_id >= 'tr-4070' AND trace_id < 'tr-4071';

-- or make LIKE case-sensitive, and the planner does the rewrite for you
PRAGMA case_sensitive_like = ON;
```

The second is a per-connection setting and changes the meaning of every
`LIKE` in that connection. Decide deliberately.

## "`no such table: events`"

You ran a script before building the table, or in the wrong directory.
`sqlite3.connect` creates an empty database file rather than complaining,
so a relative path in the wrong place produces exactly this.

```bash
python3 generate.py events.db
ls -l events.db      # about 30 MB
```

## "`no such index`" from `DROP INDEX`

You dropped it already, or an example script tidied up after itself — they
all do. `DROP INDEX IF EXISTS` is safe to repeat.

## "`database is locked`"

Another connection holds a write lock. The usual cause here is an
interactive `sqlite3` shell left open with an uncommitted `BEGIN` in one
window while a script runs in another. Type `.quit` in the shell, or
`COMMIT;` first.

## "`disk I/O error`" or the database stops growing

Out of space. The main table is about 30 MB and the write-cost experiment
builds several more. Free some, or use a smaller table:

```bash
python3 generate.py events.db 100000
```

## "The test suite says the write cost check failed"

The check asserts only that inserting with five indexes is at least 1.5x
slower than without — a very loose bound against about 12x on the authoring
machine. If it fails, something odd is happening. The likely causes: a
filesystem with unusual caching, a machine under heavy load during the
run, or a Python process being throttled. Run `python3 write_cost.py` by
itself and read the three trials; if the spread across trials is enormous,
the machine was busy.

## "`python3 measure.py` says EXERCISE 1 is not done"

That is the starter working. `starter/measure.py` ships unfinished on
purpose and names the next exercise instead of throwing a traceback.
Complete the five exercises in order; the file exits 0 when the last one is
done and the assertions at the end pass.

## "The starter SQL prints scans for everything"

Also correct. `starter/indexes.sql` applies as shipped and shows you the
plans before you have written any indexes. Add one `CREATE INDEX` per
exercise and run it again.

## "Two SQLite version numbers"

Normal. The shell and the Python module are two programs, each linking its
own copy of the library. The suite reports both and requires neither to
match the other. It matters slightly today because the query planner lives
in the library, so two versions may legitimately choose different plans —
if a plan differs from `expected-output/`, check which SQLite you are on.

## "`bash: tests/run_tests.sh: No such file or directory`"

Run it from the lab directory:

```bash
cd labs/sections/programming-with-python/day-089-indexes-and-query-performance
bash tests/run_tests.sh
```

## Windows

`tests/run_tests.sh` is a bash script. Use WSL and follow the Linux path.
The Python and SQL files themselves work unchanged under native Windows;
no captures were taken there, and `expected-output/FIELDS.md` says so
rather than guessing.
