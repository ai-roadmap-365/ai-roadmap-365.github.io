-- YOUR WORK — the indexes, written by you.
--
--   python3 ../examples/generate.py mine.db 200000
--   sqlite3 mine.db < indexes.sql
--
-- Six numbered exercises. The file APPLIES AS SHIPPED: run it now and it
-- will print the plans for the queries below, all of them scans, because
-- you have not created anything yet. Add one index per exercise and run it
-- again; each plan should change from SCAN to SEARCH.
--
-- Never guess. EXPLAIN QUERY PLAN costs nothing and is right.
.headers on
.mode box
.print ''
.print '=== The queries this file is about, and how they are answered now ==='

-- ---------------------------------------------------------------------------
-- EXERCISE 1 — the plain lookup.
--
-- Query A finds the events of one run. Write an index that turns its plan
-- from "SCAN events" into "SEARCH events USING INDEX ...".
--
-- Name it ix_run. One column.
-- Checked by: "exercise 1: a single-column index turns the run lookup into a seek"
-- >>> WRITE YOUR CREATE INDEX HERE <<<

.print '--- A: the events of one run'
EXPLAIN QUERY PLAN
SELECT event_id, model, score FROM events WHERE run_id = 200;

-- ---------------------------------------------------------------------------
-- EXERCISE 2 — the composite index, and the leftmost-prefix rule.
--
-- Query B filters on run_id AND status. Query C filters on status alone.
-- Write ONE index, named ix_run_status, on (run_id, status).
--
-- Predict both plans BEFORE you run it, and write your prediction down.
-- One of B and C will seek and the other will not, and the reason is that
-- an index on (run_id, status) is sorted by run_id first — so status is
-- only in order inside a single run_id.
-- Checked by: "exercise 2: the composite index serves B and cannot serve C"
-- >>> WRITE YOUR CREATE INDEX HERE <<<

.print '--- B: one run, failures only'
EXPLAIN QUERY PLAN
SELECT count(*) FROM events WHERE run_id = 200 AND status = 'failed';
.print '--- C: failures across every run'
EXPLAIN QUERY PLAN
SELECT count(*) FROM events WHERE status = 'failed';

-- ---------------------------------------------------------------------------
-- EXERCISE 3 — the covering index.
--
-- Query D asks only for score. Write an index named ix_run_score that lets
-- SQLite answer it WITHOUT OPENING THE TABLE AT ALL. You will know you have
-- it when the plan says COVERING INDEX.
--
-- The trick is not a special kind of index. It is putting every column the
-- query mentions into an ordinary one.
-- Checked by: "exercise 3: the covering index answers without touching the table"
-- >>> WRITE YOUR CREATE INDEX HERE <<<

.print '--- D: just the scores for one run'
EXPLAIN QUERY PLAN
SELECT score FROM events WHERE run_id = 200;

-- ---------------------------------------------------------------------------
-- EXERCISE 4 — an index that removes a sort.
--
-- Query E wants the twenty oldest events. Without help the plan contains
-- USE TEMP B-TREE FOR ORDER BY: SQLite sorted every row to hand back twenty.
--
-- Write an index named ix_created that makes that line disappear. An index
-- is already in order; a query that wants that order can just walk it.
-- Checked by: "exercise 4: ORDER BY no longer builds a temporary B-tree"
-- >>> WRITE YOUR CREATE INDEX HERE <<<

.print '--- E: the twenty oldest events'
EXPLAIN QUERY PLAN
SELECT event_id, created_on FROM events ORDER BY created_on LIMIT 20;

-- ---------------------------------------------------------------------------
-- EXERCISE 5 — the partial index.
--
-- Query F asks about failures in a date range. About one row in ten is a
-- failure, so an index over all 200,000 rows is mostly dead weight.
--
-- Write an index named ix_failed_created on events(created_on) with a
-- WHERE clause restricting it to status = 'failed'. Then check the last
-- query in this file: the planner will not use a partial index for a query
-- it cannot prove falls inside that WHERE clause, and that is correct
-- behaviour rather than a disappointment.
-- Checked by: "exercise 5: the partial index serves the failure query only"
-- >>> WRITE YOUR CREATE INDEX HERE <<<

.print '--- F: recent failures'
EXPLAIN QUERY PLAN
SELECT count(*) FROM events
WHERE status = 'failed' AND created_on >= '2025-06-01';

-- ---------------------------------------------------------------------------
-- EXERCISE 6 — the query the index cannot help, and the rewrite that can.
--
-- Query G wraps the indexed column in lower(), so ix_trace below cannot be
-- used: the index holds trace_id, and the query asks about lower(trace_id),
-- which is a different set of values.
--
-- Write a second index, named ix_lower_trace, ON THE EXPRESSION, so that G
-- seeks. The syntax is CREATE INDEX ... ON events(lower(trace_id)).
--
-- Then answer this in a comment, in your own words: when would you rather
-- store lower(trace_id) as its own column instead?
-- Checked by: "exercise 6: an expression index rescues the wrapped column"
CREATE INDEX IF NOT EXISTS ix_trace ON events(trace_id);
-- >>> WRITE YOUR SECOND CREATE INDEX HERE <<<

.print '--- G: a trace id, matched case-insensitively'
EXPLAIN QUERY PLAN
SELECT event_id FROM events WHERE lower(trace_id) = 'tr-407080-72';

-- ---------------------------------------------------------------------------
.print ''
.print '=== What you have built ==='
SELECT name FROM sqlite_schema WHERE type = 'index' AND sql IS NOT NULL ORDER BY name;

.print ''
.print '=== And what it cost: pages in use, and rows per distinct key ==='
ANALYZE;
SELECT idx AS index_name, stat AS rows_and_average_per_key
FROM sqlite_stat1 WHERE idx IS NOT NULL ORDER BY idx;
