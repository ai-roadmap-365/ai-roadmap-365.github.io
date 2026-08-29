-- Day 087 · Step 9 — watch the planner choose an algorithm.
--
-- EXPLAIN QUERY PLAN prints how SQLite intends to answer a query. Two words
-- carry most of the meaning:
--
--   SCAN    read every row of this table
--   SEARCH  jump straight to the matching rows using an index
--
-- A SCAN of the outer table with a SEARCH of the inner one is an indexed
-- nested-loop join: the algorithm from 06_join_from_scratch.py, with the inner
-- scan replaced by an index lookup. Two SCANs with no join condition is the
-- cartesian product.
--
-- Run with:  sqlite3 library.db < examples/09_query_plans.sql

.print ''
.print '--- inner join on an indexed foreign key ---'
EXPLAIN QUERY PLAN
SELECT m.name, l.loan_id
  FROM loans   AS l
  JOIN members AS m ON m.member_id = l.member_id;

.print ''
.print '--- the same shape, outer, with the grouping on top ---'
EXPLAIN QUERY PLAN
SELECT m.name, count(l.loan_id)
  FROM members AS m
  LEFT JOIN loans AS l ON l.member_id = m.member_id
 GROUP BY m.member_id;

.print ''
.print '--- a cartesian product: two SCANs and nothing tying them together ---'
EXPLAIN QUERY PLAN
SELECT * FROM books CROSS JOIN authors;
