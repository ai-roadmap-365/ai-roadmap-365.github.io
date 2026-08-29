-- Day 091 — the ten questions from the brief, answered.
--
-- Run against a database built by 01_schema.sql and 02_seed.sql:
--   sqlite3 library.db < examples/03_questions.sql
--
-- Every "as of now" question uses the fixed report instant
-- 2026-08-16T09:00:00Z so the answers are reproducible and testable.
--
-- Read the comment above each query before the query. The interesting part is
-- which construct each question forced, and why the obvious alternative is
-- either wrong or unreadable.

PRAGMA foreign_keys = ON;
.mode column
.headers on
.width 0

.print '=== 1. How many books are on the shelves, and how many are out? ==='
-- Two scalar subqueries in the SELECT list. Each returns exactly one row and
-- one column, which is the only thing a scalar subquery is allowed to do.
-- Neither depends on the other, so neither is correlated. Written as a join
-- this would need a cross join of two aggregates to say the same thing less
-- clearly.
--
-- Note what "on the shelves" had to mean: withdrawn_at IS NULL. That filter is
-- the running cost of soft delete, and the query that forgets it reports 8.
SELECT
  (SELECT count(*) FROM books WHERE withdrawn_at IS NULL)          AS in_collection,
  (SELECT count(*) FROM loans WHERE returned_at IS NULL)           AS on_loan_now,
  (SELECT count(*) FROM books)                                     AS rows_in_books;

.print ''
.print '=== 2. Which current members have never borrowed anything? ==='
-- NOT EXISTS, and this is the shape to reach for by default. It is a
-- correlated subquery: the inner query mentions m.member_id from the outer
-- one, so it is conceptually re-evaluated per member. It stops at the first
-- matching row rather than building a list, it multiplies no rows, and —
-- unlike NOT IN — it is immune to a NULL in the subquery's column.
SELECT m.member_id, m.full_name, m.tier
  FROM members AS m
 WHERE m.left_at IS NULL
   AND NOT EXISTS (SELECT 1 FROM loans AS l WHERE l.member_id = m.member_id)
 ORDER BY m.member_id;

.print ''
.print '=== 3. Books with more than one author, in credited order ==='
-- The junction table earning its extra column. author_position is not derivable
-- from anything else — not from the author id, not from the name, not from the
-- insertion order, which SQL does not promise to preserve.
--
-- HAVING rather than WHERE, because the condition is on the aggregate.
SELECT b.title,
       count(*)                                              AS author_count,
       group_concat(a.name, ', ')                            AS credited_order
  FROM books        AS b
  JOIN book_authors AS ba ON ba.book_id  = b.book_id
  JOIN authors      AS a  ON a.author_id = ba.author_id
 GROUP BY b.book_id, b.title
HAVING count(*) > 1
 ORDER BY author_count DESC, b.title;

.print ''
.print '=== 4. Loans overdue as of 2026-08-16T09:00:00Z, and by how many days ==='
-- ISO 8601 in UTC makes "overdue" a string comparison, and julianday() reads
-- the same text to give the difference in days. CAST to INTEGER truncates
-- towards zero, which is what "whole days late" means.
--
-- The WITH clause here holds one value. That is not overkill: it puts the
-- report instant in exactly one place, so changing it cannot leave two halves
-- of the query disagreeing about what "now" means.
WITH report(now) AS (VALUES ('2026-08-16T09:00:00Z'))
SELECT l.loan_id,
       m.full_name                                                  AS member,
       b.title,
       l.due_at,
       CAST(julianday((SELECT now FROM report)) - julianday(l.due_at) AS INTEGER)
                                                                    AS days_overdue
  FROM loans   AS l
  JOIN members AS m ON m.member_id = l.member_id
  JOIN books   AS b ON b.book_id   = l.book_id
 WHERE l.returned_at IS NULL
   AND l.due_at < (SELECT now FROM report)
 ORDER BY days_overdue DESC;

.print ''
.print '=== 5. Fines owed per member, in pounds — including members who left ==='
-- Money lives as an integer count of pence and is divided by 100 exactly once,
-- at the very last moment, for display. Every sum, every comparison and every
-- stored value above this line is an integer.
--
-- This question deliberately does NOT filter left_at: a debt does not stop
-- existing because somebody cancelled their membership. Question 6 does filter
-- it. Which soft-delete filter applies is a property of the question, not of
-- the table, and that is the entire cost of soft delete.
SELECT m.full_name,
       CASE WHEN m.left_at IS NULL THEN 'current' ELSE 'left' END   AS standing,
       sum(l.fine_pence)                                            AS fine_pence,
       printf('%.2f', sum(l.fine_pence) / 100.0)                    AS fine_pounds
  FROM members AS m
  JOIN loans   AS l ON l.member_id = m.member_id
 GROUP BY m.member_id, m.full_name
HAVING sum(l.fine_pence) > 0
 ORDER BY fine_pence DESC;

.print ''
.print '=== 6. Top two borrowers in each tier (current members only) ==='
-- The top-N-per-group problem, and the reason window functions exist.
--
-- A plain GROUP BY can give you the count per member, or the maximum count per
-- tier, but it cannot give you the top two *rows* per tier: aggregation
-- collapses the rows it aggregates, so the member's name is gone by the time
-- you know the count is a winner. ROW_NUMBER computes a value across a
-- partition without collapsing anything, so every column survives to be
-- filtered on in the outer query.
--
-- The LEFT JOIN inside the CTE is what keeps Eli Nakamura, who has borrowed
-- nothing, in her tier's ranking at all. count(l.loan_id) rather than count(*)
-- is what makes her count 0 rather than 1 (Day 87).
WITH per_member AS (
  SELECT m.member_id,
         m.full_name,
         m.tier,
         count(l.loan_id) AS loan_count
    FROM members AS m
    LEFT JOIN loans AS l ON l.member_id = m.member_id
   WHERE m.left_at IS NULL
   GROUP BY m.member_id, m.full_name, m.tier
),
ranked AS (
  SELECT tier,
         full_name,
         loan_count,
         ROW_NUMBER() OVER (PARTITION BY tier ORDER BY loan_count DESC, full_name) AS position,
         RANK()       OVER (PARTITION BY tier ORDER BY loan_count DESC)            AS tier_rank
    FROM per_member
)
SELECT tier, position, tier_rank, full_name, loan_count
  FROM ranked
 WHERE position <= 2
 ORDER BY tier, position;

.print ''
.print '=== 7. The reservation queue for every book with people waiting ==='
-- The queue position is derived, not stored. ROW_NUMBER over a partition of
-- book_id, ordered by the time the reservation was made, renumbers itself for
-- free every time somebody cancels — which is exactly the bug a stored
-- position column produces the first time a cancellation is missed.
--
-- Note that the cancelled reservation on Neuromancer occupies no slot, and the
-- member who reserved it later is therefore second rather than third.
SELECT b.title,
       ROW_NUMBER() OVER (PARTITION BY r.book_id ORDER BY r.reserved_at) AS queue_position,
       m.full_name,
       r.reserved_at
  FROM reservations AS r
  JOIN books        AS b ON b.book_id   = r.book_id
  JOIN members      AS m ON m.member_id = r.member_id
 WHERE r.status = 'waiting'
 ORDER BY b.title, queue_position;

.print ''
.print '=== 8. Loans started per month, with a running total ==='
-- SUM(...) OVER (ORDER BY ...) is a running total: for each row, the sum of
-- every row up to and including this one in that order. The default frame when
-- ORDER BY is present is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW,
-- which is precisely a cumulative sum — worth stating rather than memorising,
-- because omitting the ORDER BY silently gives you the grand total on every
-- row instead.
--
-- The aggregate happens first, in the CTE; the window function then runs over
-- the aggregated rows. A window function cannot be nested inside an aggregate,
-- and this two-step shape is how you combine them.
WITH monthly AS (
  SELECT strftime('%Y-%m', borrowed_at) AS month,
         count(*)                       AS loans_started
    FROM loans
   GROUP BY month
)
SELECT month,
       loans_started,
       sum(loans_started) OVER (ORDER BY month) AS running_total
  FROM monthly
 ORDER BY month;

.print ''
.print '=== 9. Everything under Fiction, at any depth, with book counts ==='
-- A recursive CTE. This is the question a join cannot answer, because the
-- number of joins you would need is the depth of the tree, and you do not know
-- the depth of the tree.
--
-- The anchor selects the starting row. The recursive part joins the CTE to
-- itself to find the children of everything found so far, and stops when a
-- pass adds no rows. The depth column is carried along by hand: SQL will not
-- tell you how many passes it took.
WITH RECURSIVE subtree(category_id, name, depth) AS (
      SELECT category_id, name, 0
        FROM categories
       WHERE name = 'Fiction'
  UNION ALL
      SELECT c.category_id, c.name, s.depth + 1
        FROM categories AS c
        JOIN subtree    AS s ON c.parent_id = s.category_id
)
SELECT s.depth,
       s.name                              AS category,
       count(b.book_id)                    AS books_in_collection
  FROM subtree AS s
  LEFT JOIN books AS b
         ON b.category_id  = s.category_id
        AND b.withdrawn_at IS NULL
 GROUP BY s.category_id, s.depth, s.name
 ORDER BY s.depth, s.name;

.print ''
.print '=== 10. Authors none of whose books have ever been borrowed ==='
-- NOT EXISTS again, this time with a two-table correlated subquery. Compare
-- the alternatives honestly:
--
--   NOT IN (SELECT author_id FROM ...)  — right answer here, but returns
--     nothing at all if that subquery ever yields a single NULL.
--   LEFT JOIN ... WHERE loan_id IS NULL — also correct, but it builds every
--     author-book-loan pair and then throws almost all of them away.
--   NOT EXISTS                          — says what the sentence says.
SELECT a.author_id, a.name
  FROM authors AS a
 WHERE NOT EXISTS (
         SELECT 1
           FROM book_authors AS ba
           JOIN loans        AS l ON l.book_id = ba.book_id
          WHERE ba.author_id = a.author_id
       )
 ORDER BY a.author_id;
