-- Day 087 · Step 5 — every join in the lesson, against the seeded library.
--
-- Run with:  sqlite3 library.db < examples/05_joins.sql

PRAGMA foreign_keys = ON;
.headers on
.mode column

.print ''
.print '=== 1. INNER JOIN — books with their authors (many-to-many, two hops) ==='
SELECT b.title,
       a.name AS author
  FROM books AS b
  JOIN book_authors AS ba ON ba.book_id   = b.book_id
  JOIN authors      AS a  ON a.author_id  = ba.author_id
 ORDER BY b.title, a.name;

.print ''
.print '=== 2. the same result written the old comma-join way ==='
SELECT b.title,
       a.name AS author
  FROM books b, book_authors ba, authors a
 WHERE ba.book_id  = b.book_id
   AND a.author_id = ba.author_id
 ORDER BY b.title, a.name;

.print ''
.print '=== 3. CROSS JOIN — the accidental cartesian product (4 x 7 = 28) ==='
SELECT count(*) AS every_book_paired_with_every_author
  FROM books CROSS JOIN authors;

.print ''
.print '=== 4. LEFT OUTER JOIN — every author, whether or not they have a book ==='
SELECT a.name        AS author,
       b.title       AS title,
       b.published_year
  FROM authors AS a
  LEFT JOIN book_authors AS ba ON ba.author_id = a.author_id
  LEFT JOIN books        AS b  ON b.book_id    = ba.book_id
 ORDER BY a.name, b.title;

.print ''
.print '=== 5. LEFT JOIN + IS NULL — authors with no catalogued book ==='
SELECT a.author_id, a.name
  FROM authors AS a
  LEFT JOIN book_authors AS ba ON ba.author_id = a.author_id
 WHERE ba.author_id IS NULL
 ORDER BY a.name;

.print ''
.print '=== 6. LEFT JOIN + IS NULL — books never borrowed ==='
SELECT b.book_id, b.title
  FROM books AS b
  LEFT JOIN loans AS l ON l.book_id = b.book_id
 WHERE l.loan_id IS NULL
 ORDER BY b.title;

.print ''
.print '=== 7. the LEFT JOIN trap — loans per member, zeroes included ==='
SELECT m.name                 AS member,
       count(l.loan_id)       AS loans
  FROM members AS m
  LEFT JOIN loans AS l ON l.member_id = m.member_id
 GROUP BY m.member_id, m.name
 ORDER BY loans DESC, member;

.print ''
.print '=== 7b. count(*) instead of count(l.loan_id) — the wrong answer ==='
SELECT m.name           AS member,
       count(*)         AS loans_wrong
  FROM members AS m
  LEFT JOIN loans AS l ON l.member_id = m.member_id
 GROUP BY m.member_id, m.name
 ORDER BY loans_wrong DESC, member;

.print ''
.print '=== 7c. INNER JOIN instead — the member with zero loans vanishes ==='
SELECT m.name           AS member,
       count(l.loan_id) AS loans
  FROM members AS m
  JOIN loans AS l ON l.member_id = m.member_id
 GROUP BY m.member_id, m.name
 ORDER BY loans DESC, member;

.print ''
.print '=== 8. ON versus WHERE on an outer join — ON keeps every member ==='
SELECT m.name AS member, l.loan_id, l.returned_on
  FROM members AS m
  LEFT JOIN loans AS l
         ON l.member_id = m.member_id
        AND l.returned_on IS NULL
 ORDER BY m.name, l.loan_id;

.print ''
.print '=== 8b. the same predicate moved to WHERE — the outer join collapses ==='
SELECT m.name AS member, l.loan_id, l.returned_on
  FROM members AS m
  LEFT JOIN loans AS l ON l.member_id = m.member_id
 WHERE l.returned_on IS NULL
 ORDER BY m.name, l.loan_id;

.print ''
.print '=== 9. SELF JOIN — who referred whom (LEFT, so the unreferred survive) ==='
SELECT m.name          AS member,
       r.name          AS referred_by
  FROM members AS m
  LEFT JOIN members AS r ON r.member_id = m.referred_by
 ORDER BY m.member_id;

.print ''
.print '=== 10. FOUR tables at once — who has what out on loan right now ==='
SELECT m.name  AS member,
       b.title AS title,
       a.name  AS author,
       l.borrowed_on
  FROM loans        AS l
  JOIN members      AS m  ON m.member_id  = l.member_id
  JOIN books        AS b  ON b.book_id    = l.book_id
  JOIN book_authors AS ba ON ba.book_id   = b.book_id
  JOIN authors      AS a  ON a.author_id  = ba.author_id
 WHERE l.returned_on IS NULL
 ORDER BY m.name, a.name;

.print ''
.print '=== 11. join + GROUP BY — times borrowed per book, zeroes included ==='
SELECT b.title,
       count(l.loan_id) AS times_borrowed
  FROM books AS b
  LEFT JOIN loans AS l ON l.book_id = b.book_id
 GROUP BY b.book_id, b.title
 ORDER BY times_borrowed DESC, b.title;

.print ''
.print '=== 12. the query the Python join is checked against ==='
SELECT l.loan_id, m.name AS member, l.borrowed_on
  FROM loans   AS l
  JOIN members AS m ON m.member_id = l.member_id
 ORDER BY l.loan_id;
