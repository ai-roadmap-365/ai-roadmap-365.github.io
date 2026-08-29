-- Day 085 — the first end-to-end walkthrough, in the sqlite3 shell.
--
-- Run it:  sqlite3 library.db < queries.sql
--
-- Everything before the first SELECT is a DOT-COMMAND. Dot-commands are not
-- SQL: they are instructions to the shell program, they take no semicolon,
-- and no other SQLite client understands them. Confusing the two is the
-- single most common first-day mistake.

-- Note: a dot-command takes the WHOLE line. A trailing "-- comment" after one
-- is read as an argument and the command fails with a usage message. Comments
-- about dot-commands go on their own line, like these.
--
-- .mode box       draw results in a box; the default is a pipe-separated list
-- .headers on     print column names above the rows
-- .nullvalue NULL show NULL as the word NULL instead of an empty cell
.mode box
.headers on
.nullvalue NULL

.print '=== .tables — what tables exist ==='
.tables

.print ''
.print '=== .schema books — the exact text of the promise ==='
.schema books

.print ''
.print '=== every book, newest first, NULL year last ==='
SELECT book_id, title, author, year, copies
  FROM books
 ORDER BY year IS NULL, year DESC;

.print ''
.print '=== the members table ==='
SELECT member_id, name, email, joined_on FROM members ORDER BY member_id;

.print ''
.print '=== the question the JSON file could not answer cheaply ==='
.print 'Which loans are overdue as of 2026-08-16, who has them, and how late?'
.print 'One statement. The engine decides how to find the rows.'
SELECT
    m.name                                   AS borrower,
    b.title                                  AS book,
    l.due_on                                 AS due,
    CAST(julianday('2026-08-16') - julianday(l.due_on) AS INTEGER) AS days_late
  FROM loans   AS l
  JOIN members AS m ON m.member_id = l.member_id
  JOIN books   AS b ON b.book_id   = l.book_id
 WHERE l.returned_on IS NULL
   AND l.due_on < '2026-08-16'
 ORDER BY days_late DESC;
-- JOIN is Day 87's subject. It is here on purpose: the point of today is
-- that a question spanning three tables is still ONE request, and you never
-- said how to answer it.

.print ''
.print '=== the same shape of question, one table, no join ==='
SELECT count(*) AS loans_still_out FROM loans WHERE returned_on IS NULL;

SELECT
    member_id,
    count(*) AS open_loans
  FROM loans
 WHERE returned_on IS NULL
 GROUP BY member_id
 ORDER BY open_loans DESC, member_id;

.print ''
.print '=== how the engine plans to run that overdue query ==='
.print 'EXPLAIN QUERY PLAN is the planner telling you what it chose.'
EXPLAIN QUERY PLAN
SELECT m.name, b.title
  FROM loans   AS l
  JOIN members AS m ON m.member_id = l.member_id
  JOIN books   AS b ON b.book_id   = l.book_id
 WHERE l.returned_on IS NULL;

.print ''
.print '=== what SQLite itself thinks its schema is ==='
.print 'sqlite_schema is an ordinary table you can query. The schema is data.'
SELECT type, name, tbl_name FROM sqlite_schema ORDER BY type, name;
