-- Day 091 — YOUR answers to the ten questions in starter/00_brief.md.
--
-- Exercises 7 to 16. Replace each placeholder SELECT with a query that answers
-- the question. The file runs as it stands, so you can check your progress
-- after every single one:
--
--   bash starter/03_check.sh
--
-- The checker runs this file and examples/06_answers.sql against the same
-- database and compares the ten blocks. It never looks at how you wrote the
-- query — only at whether the rows are right, in the right order, with the
-- right columns. There is more than one correct query for several of these.
--
-- Output contract, so the blocks can be compared:
--   * the dot-commands below set list mode with a pipe separator and no
--     headers. Leave them alone.
--   * each answer must produce EXACTLY the columns named in its comment, in
--     that order, and in the stated row order. No extra columns.
--   * the '### n' markers separate the blocks. Leave those alone too.

.mode list
.separator '|'
.headers off

-- ---------------------------------------------------------------------------
-- EXERCISE 7 (question 1) — How many books are on the shelves, and how many
-- of them are out on loan?
--
-- Columns: books_in_collection, loans_outstanding      Rows: exactly 1
--
-- Approach: two scalar subqueries in the SELECT list. A scalar subquery
-- returns one row and one column and can go anywhere a value can. Remember
-- that "on the shelves" excludes withdrawn books — the running cost of soft
-- delete is that every present-tense query has to say so.
-- ---------------------------------------------------------------------------
.print '### 1'
SELECT 'exercise 7 not answered yet', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 8 (question 2) — Which current members have never borrowed
-- anything?
--
-- Columns: full_name, tier      Order: by full_name
--
-- Approach: NOT EXISTS with a correlated subquery — the inner query mentions
-- the outer query's member_id. NOT IN would give the right answer here and
-- would return nothing at all the day a NULL appears in the subquery; the
-- LEFT JOIN ... IS NULL idiom from Day 87 also works. Pick one and be able to
-- say why.
-- ---------------------------------------------------------------------------
.print '### 2'
SELECT 'exercise 8 not answered yet', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 9 (question 3) — Which books have more than one author, and who
-- are they in credited order?
--
-- Columns: title, author_count, credited_order
-- Order: author_count descending, then title
--
-- Approach: join books to authors through your junction table, GROUP BY the
-- book, filter the aggregate with HAVING, and assemble the names with
-- group_concat(a.name, ', '). Getting the ORDER of the names right is the part
-- that depends on your schema having stored the credit position.
-- ---------------------------------------------------------------------------
.print '### 3'
SELECT 'exercise 9 not answered yet', '', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 10 (question 4) — Which loans are overdue as of
-- 2026-08-16T09:00:00Z, and by how many whole days?
--
-- Columns: full_name, title, days_overdue      Order: days_overdue descending
--
-- Approach: a loan is out when returned_at IS NULL and overdue when due_at is
-- earlier than the report instant — which, with ISO 8601 in UTC, is a plain
-- string comparison. For the number of days,
-- CAST(julianday(<now>) - julianday(l.due_at) AS INTEGER).
-- ---------------------------------------------------------------------------
.print '### 4'
SELECT 'exercise 10 not answered yet', '', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 11 (question 5) — How much does each member owe in fines, in
-- pounds, including members who have left?
--
-- Columns: full_name, standing, fine_pounds      Order: by fines, descending
--   standing is the text 'current' or 'left' — a CASE expression on left_at.
--   fine_pounds is printf('%.2f', sum(...) / 100.0).
-- Only rows where the total is greater than zero.
--
-- Approach: sum stays in integer pence right up to the display. Note that this
-- question deliberately does NOT filter out members who have left: a debt does
-- not stop existing because somebody cancelled their membership. Exercise 12
-- does filter them. Which soft-delete filter applies is a property of the
-- question, not of the table.
-- ---------------------------------------------------------------------------
.print '### 5'
SELECT 'exercise 11 not answered yet', '', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 12 (question 6) — Who are the two most active borrowers in each
-- membership tier, counting current members only?
--
-- Columns: tier, position, full_name, loan_count      Order: tier, position
--
-- Approach: this is top-N-per-group, and it is the question a plain GROUP BY
-- cannot answer — aggregation collapses the rows, so the name is gone by the
-- time you know the count is a winner. Use two CTEs: one that counts loans per
-- current member, one that adds
--   ROW_NUMBER() OVER (PARTITION BY tier ORDER BY loan_count DESC, full_name)
-- and then filter that to <= 2 in the outer query.
--
-- Two traps from Day 87 are waiting here: an INNER JOIN drops the member who
-- has borrowed nothing, and count(*) reports 1 for her instead of 0.
-- ---------------------------------------------------------------------------
.print '### 6'
SELECT 'exercise 12 not answered yet', '', '', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 13 (question 7) — For every book with people waiting, what is the
-- reservation queue, in order?
--
-- Columns: title, queue_position, full_name      Order: title, queue_position
--
-- Approach: ROW_NUMBER() OVER (PARTITION BY book_id ORDER BY reserved_at),
-- over the waiting reservations only. Notice that a cancelled reservation must
-- occupy no slot at all — which is exactly what a stored position column gets
-- wrong.
-- ---------------------------------------------------------------------------
.print '### 7'
SELECT 'exercise 13 not answered yet', '', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 14 (question 8) — How many loans started each month, and what is
-- the running total?
--
-- Columns: month, loans_started, running_total      Order: by month
--   month is strftime('%Y-%m', borrowed_at).
--
-- Approach: aggregate per month in a CTE, then run
-- sum(loans_started) OVER (ORDER BY month) across the aggregated rows. A
-- window function cannot be nested inside an aggregate, so the two steps have
-- to be separate. Omit the ORDER BY inside OVER and you silently get the grand
-- total on every row instead of a running one.
-- ---------------------------------------------------------------------------
.print '### 8'
SELECT 'exercise 14 not answered yet', '', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 15 (question 9) — What sits underneath the Fiction category, at any
-- depth, and how many books are in each?
--
-- Columns: depth, category, books_in_collection      Order: depth, category
--   Fiction itself is depth 0 and is included.
--   Withdrawn books do not count.
--
-- Approach: WITH RECURSIVE. The anchor selects the Fiction row with depth 0;
-- the recursive part joins categories to the CTE to find the children of
-- everything found so far. Then LEFT JOIN books to count them — LEFT, because
-- a category with no books must still appear with a count of 0, and the
-- withdrawn filter belongs in the ON clause rather than the WHERE clause for
-- exactly the reason Day 87 gave.
-- ---------------------------------------------------------------------------
.print '### 9'
SELECT 'exercise 15 not answered yet', '', '';

-- ---------------------------------------------------------------------------
-- EXERCISE 16 (question 10) — Which authors have never had any of their books
-- borrowed?
--
-- Columns: name      Order: by name
--
-- Approach: NOT EXISTS again, this time with a two-table subquery inside it —
-- from the author, through the junction table, to loans.
-- ---------------------------------------------------------------------------
.print '### 10'
SELECT 'exercise 16 not answered yet';

.print '### end'
