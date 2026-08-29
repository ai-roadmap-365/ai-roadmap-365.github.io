-- Day 089 — reading query plans in the sqlite3 shell.
--
--   sqlite3 events.db < plans.sql
--
-- Everything here is EXPLAIN QUERY PLAN. It costs nothing, changes nothing,
-- and is the only honest way to find out what the engine intends to do.
-- Run it before you optimise anything, and again afterwards.
--
-- Dot-commands are instructions to the shell, not SQL: no semicolon, and
-- never a trailing comment on the same line.
.headers on
.mode box

.print ''
.print '=== 0. What indexes exist right now ==='
-- sqlite_schema is an ordinary table. Your indexes are rows in it.
SELECT name, tbl_name, sql FROM sqlite_schema WHERE type = 'index';

.print ''
.print '=== 1. A lookup with no index: SCAN means every row ==='
EXPLAIN QUERY PLAN
SELECT event_id, model, score FROM events WHERE run_id = 200;

.print ''
.print '=== 2. The same lookup, with an index ==='
CREATE INDEX IF NOT EXISTS ix_run ON events(run_id);
EXPLAIN QUERY PLAN
SELECT event_id, model, score FROM events WHERE run_id = 200;

.print ''
.print '=== 3. And the answers are identical, which is the point ==='
SELECT count(*) AS rows_found, round(avg(score), 4) AS mean_score
FROM events WHERE run_id = 200;

.print ''
.print '=== 4. Covering: every column the query wants is in the index ==='
CREATE INDEX IF NOT EXISTS ix_run_score ON events(run_id, score);
EXPLAIN QUERY PLAN
SELECT score FROM events WHERE run_id = 200;

.print ''
.print '=== 5. ORDER BY with no usable index builds a temporary tree ==='
DROP INDEX IF EXISTS ix_created;
EXPLAIN QUERY PLAN
SELECT event_id, created_on FROM events ORDER BY created_on LIMIT 20;

.print ''
.print '=== 6. ORDER BY served straight off the index: no sort at all ==='
CREATE INDEX IF NOT EXISTS ix_created ON events(created_on);
EXPLAIN QUERY PLAN
SELECT event_id, created_on FROM events ORDER BY created_on LIMIT 20;

.print ''
.print '=== 7. The leftmost prefix, in three plans ==='
DROP INDEX IF EXISTS ix_run;
DROP INDEX IF EXISTS ix_run_score;
DROP INDEX IF EXISTS ix_created;
CREATE INDEX ix_run_status ON events(run_id, status);
.print '--- both columns: SEARCH'
EXPLAIN QUERY PLAN
SELECT count(*) FROM events WHERE run_id = 200 AND status = 'failed';
.print '--- leading column only: SEARCH'
EXPLAIN QUERY PLAN
SELECT count(*) FROM events WHERE run_id = 200;
.print '--- trailing column only: SCAN, because the index is sorted by run_id first'
EXPLAIN QUERY PLAN
SELECT count(*) FROM events WHERE status = 'failed';

.print ''
.print '=== 8. A function on the column puts the answer out of reach ==='
DROP INDEX IF EXISTS ix_run_status;
CREATE INDEX ix_trace ON events(trace_id);
.print '--- plain equality: SEARCH'
EXPLAIN QUERY PLAN
SELECT event_id FROM events WHERE trace_id = 'tr-407080-72';
.print '--- wrapped in lower(): SCAN, with the index sitting right there'
EXPLAIN QUERY PLAN
SELECT event_id FROM events WHERE lower(trace_id) = 'tr-407080-72';
.print '--- the fix: an index on the expression itself'
CREATE INDEX ix_lower_trace ON events(lower(trace_id));
EXPLAIN QUERY PLAN
SELECT event_id FROM events WHERE lower(trace_id) = 'tr-407080-72';

.print ''
.print '=== 9. What ANALYZE writes down ==='
ANALYZE;
SELECT tbl, idx, stat FROM sqlite_stat1 WHERE idx IS NOT NULL ORDER BY idx;

.print ''
.print '=== 10. Tidy up, so the next script starts from a bare table ==='
DROP INDEX IF EXISTS ix_trace;
DROP INDEX IF EXISTS ix_lower_trace;
ANALYZE;
SELECT count(*) AS named_indexes_remaining
FROM sqlite_schema WHERE type = 'index' AND sql IS NOT NULL;
