-- Day 091 — the same ten answers, in machine-readable form.
--
-- 03_questions.sql is the version to read: column mode, headers, and a comment
-- above every query explaining which construct the question forced. THIS file
-- is the version to compare against: no headers, no padding, pipe-separated,
-- and a '### n' marker before each answer so a script can split the output
-- into ten blocks.
--
-- starter/03_check.sh runs this file and the learner's starter/02_questions.sql
-- against the same database and compares the blocks. The reference answers are
-- therefore computed, never typed in — if the seed changes, both sides move
-- together and nothing silently rots.
--
--   sqlite3 library.db < examples/06_answers.sql

.mode list
.separator '|'
.headers off

.print '### 1'
SELECT (SELECT count(*) FROM books WHERE withdrawn_at IS NULL),
       (SELECT count(*) FROM loans WHERE returned_at IS NULL);

.print '### 2'
SELECT m.full_name, m.tier
  FROM members AS m
 WHERE m.left_at IS NULL
   AND NOT EXISTS (SELECT 1 FROM loans AS l WHERE l.member_id = m.member_id)
 ORDER BY m.full_name;

.print '### 3'
SELECT b.title, count(*), group_concat(a.name, ', ')
  FROM books        AS b
  JOIN book_authors AS ba ON ba.book_id  = b.book_id
  JOIN authors      AS a  ON a.author_id = ba.author_id
 GROUP BY b.book_id, b.title
HAVING count(*) > 1
 ORDER BY count(*) DESC, b.title;

.print '### 4'
SELECT m.full_name, b.title,
       CAST(julianday('2026-08-16T09:00:00Z') - julianday(l.due_at) AS INTEGER)
  FROM loans   AS l
  JOIN members AS m ON m.member_id = l.member_id
  JOIN books   AS b ON b.book_id   = l.book_id
 WHERE l.returned_at IS NULL
   AND l.due_at < '2026-08-16T09:00:00Z'
 ORDER BY 3 DESC;

.print '### 5'
SELECT m.full_name,
       CASE WHEN m.left_at IS NULL THEN 'current' ELSE 'left' END,
       printf('%.2f', sum(l.fine_pence) / 100.0)
  FROM members AS m
  JOIN loans   AS l ON l.member_id = m.member_id
 GROUP BY m.member_id, m.full_name
HAVING sum(l.fine_pence) > 0
 ORDER BY sum(l.fine_pence) DESC;

.print '### 6'
WITH per_member AS (
  SELECT m.member_id, m.full_name, m.tier, count(l.loan_id) AS loan_count
    FROM members AS m
    LEFT JOIN loans AS l ON l.member_id = m.member_id
   WHERE m.left_at IS NULL
   GROUP BY m.member_id, m.full_name, m.tier
),
ranked AS (
  SELECT tier, full_name, loan_count,
         ROW_NUMBER() OVER (PARTITION BY tier ORDER BY loan_count DESC, full_name) AS position
    FROM per_member
)
SELECT tier, position, full_name, loan_count
  FROM ranked
 WHERE position <= 2
 ORDER BY tier, position;

.print '### 7'
SELECT b.title,
       ROW_NUMBER() OVER (PARTITION BY r.book_id ORDER BY r.reserved_at),
       m.full_name
  FROM reservations AS r
  JOIN books        AS b ON b.book_id   = r.book_id
  JOIN members      AS m ON m.member_id = r.member_id
 WHERE r.status = 'waiting'
 ORDER BY b.title, 2;

.print '### 8'
WITH monthly AS (
  SELECT strftime('%Y-%m', borrowed_at) AS month, count(*) AS loans_started
    FROM loans
   GROUP BY month
)
SELECT month, loans_started, sum(loans_started) OVER (ORDER BY month)
  FROM monthly
 ORDER BY month;

.print '### 9'
WITH RECURSIVE subtree(category_id, name, depth) AS (
      SELECT category_id, name, 0 FROM categories WHERE name = 'Fiction'
  UNION ALL
      SELECT c.category_id, c.name, s.depth + 1
        FROM categories AS c
        JOIN subtree    AS s ON c.parent_id = s.category_id
)
SELECT s.depth, s.name, count(b.book_id)
  FROM subtree AS s
  LEFT JOIN books AS b
         ON b.category_id  = s.category_id
        AND b.withdrawn_at IS NULL
 GROUP BY s.category_id, s.depth, s.name
 ORDER BY s.depth, s.name;

.print '### 10'
SELECT a.name
  FROM authors AS a
 WHERE NOT EXISTS (
         SELECT 1
           FROM book_authors AS ba
           JOIN loans        AS l ON l.book_id = ba.book_id
          WHERE ba.author_id = a.author_id
       )
 ORDER BY a.name;

.print '### end'
