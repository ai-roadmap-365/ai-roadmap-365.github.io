-- Day 087 starter — six numbered SQL exercises.
--
-- Every query below RUNS as it stands. Each one is also wrong in one specific,
-- named way. Your job is to make each one right. The comment above each
-- exercise says exactly what is wrong, what to change, and which check in
-- tests/run_tests.sh verifies it.
--
--   bash starter/01_build.sh                          # once
--   sqlite3 starter/library.db < starter/02_exercises.sql
--
-- Compare your output with examples/05_joins.sql when you are stuck. Reading
-- the answer after you have tried is learning; reading it first is not.

PRAGMA foreign_keys = ON;
.headers on
.mode column

-- ============================================================================
-- EXERCISE 1 — join two hops across the junction table.
--
-- Wrong how: it joins books to book_authors and stops, so you get author IDs
-- instead of author names.
-- Change: add a second JOIN onto authors, matching a.author_id = ba.author_id,
-- and select a.name instead of ba.author_id.
-- Correct result: 7 rows, one per book-author pair, with real names.
-- Checked by: "exercise 1: books joined to author NAMES, 7 rows"
-- ============================================================================
.print ''
.print '--- exercise 1 ---'
SELECT b.title,
       ba.author_id AS author
  FROM books AS b
  JOIN book_authors AS ba ON ba.book_id = b.book_id
 ORDER BY b.title, author;

-- ============================================================================
-- EXERCISE 2 — find the authors with no catalogued book.
--
-- Wrong how: an INNER JOIN can never show you a row that has no match, so this
-- returns every author who DOES have a book — the exact opposite.
-- Change: make it a LEFT JOIN and add "WHERE ba.author_id IS NULL".
-- Correct result: exactly one row — Donald E. Knuth.
-- Checked by: "exercise 2: authors with no catalogued book"
-- ============================================================================
.print ''
.print '--- exercise 2 ---'
SELECT a.author_id, a.name
  FROM authors AS a
  JOIN book_authors AS ba ON ba.author_id = a.author_id
 ORDER BY a.name;

-- ============================================================================
-- EXERCISE 3 — books that have never been borrowed.
--
-- Wrong how: same shape as exercise 2, one table further out. This lists books
-- that HAVE been borrowed, and lists the popular ones several times over.
-- Change: LEFT JOIN loans, then keep only the rows where l.loan_id IS NULL.
-- Correct result: exactly one row — book 104, The Practice of Programming.
-- Checked by: "exercise 3: books never borrowed"
-- ============================================================================
.print ''
.print '--- exercise 3 ---'
SELECT b.book_id, b.title
  FROM books AS b
  JOIN loans AS l ON l.book_id = b.book_id
 ORDER BY b.title;

-- ============================================================================
-- EXERCISE 4 — loans per member, INCLUDING the members who have none.
--
-- Wrong how: two separate mistakes stacked on each other. The INNER JOIN drops
-- Eli Nakamura entirely, and count(*) would report 1 for her even after you fix
-- the join, because the NULL-extended row is still a row.
-- Change: LEFT JOIN, and count a column from the RIGHT table -
-- count(l.loan_id) - so that the all-NULL row counts as zero.
-- Correct result: 5 rows. Ada 2, Bruno 2, Chandra 1, Dana 1, Eli 0.
-- Checked by: "exercise 4: loans per member with a real zero for Eli"
-- ============================================================================
.print ''
.print '--- exercise 4 ---'
SELECT m.name           AS member,
       count(*)         AS loans
  FROM members AS m
  JOIN loans AS l ON l.member_id = m.member_id
 GROUP BY m.member_id, m.name
 ORDER BY loans DESC, member;

-- ============================================================================
-- EXERCISE 5 — who referred whom (a self-join).
--
-- Wrong how: it joins members to members with an INNER JOIN, which silently
-- drops the two members nobody referred.
-- Change: LEFT JOIN, so every member appears and referred_by comes back NULL
-- for the ones who joined on their own.
-- Correct result: 5 rows. Ada and Eli have an empty referred_by.
-- Checked by: "exercise 5: self-join keeps the members nobody referred"
-- ============================================================================
.print ''
.print '--- exercise 5 ---'
SELECT m.name AS member,
       r.name AS referred_by
  FROM members AS m
  JOIN members AS r ON r.member_id = m.referred_by
 ORDER BY m.member_id;

-- ============================================================================
-- EXERCISE 6 — everything currently out on loan, across four tables.
--
-- Wrong how: it stops at three tables, so you get the title but not who wrote
-- it, and it has no filter, so returned books are in the list too.
-- Change: add the two remaining joins (book_authors, then authors) and the
-- condition l.returned_on IS NULL.
-- Correct result: 4 rows. Chandra Iyer appears twice, because the book she has
-- out has two authors - that duplication is the many-to-many showing through,
-- not a bug.
-- Checked by: "exercise 6: four-table join of what is out on loan"
-- ============================================================================
.print ''
.print '--- exercise 6 ---'
SELECT m.name  AS member,
       b.title AS title,
       l.borrowed_on
  FROM loans   AS l
  JOIN members AS m ON m.member_id = l.member_id
  JOIN books   AS b ON b.book_id   = l.book_id
 ORDER BY m.name;
