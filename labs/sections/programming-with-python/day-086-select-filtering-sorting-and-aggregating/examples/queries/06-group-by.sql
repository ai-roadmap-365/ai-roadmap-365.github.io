-- 06 — GROUP BY: one output row per distinct grouping key
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/06-group-by.sql
--
-- GROUP BY collapses the rows that survived WHERE into buckets. After it runs,
-- the only things you may ask for are the grouping key itself and aggregates
-- over the bucket — because there is no longer one row to take a value from.

.print '--- 6.1 how many books per genre, commonest first'
SELECT genre, COUNT(*) AS n
FROM books
GROUP BY genre
ORDER BY n DESC, genre;

.print ''
.print '--- 6.2 GROUP BY puts all the NULLs in ONE bucket — the one place NULLs are treated as equal'
SELECT IFNULL(genre, '(unclassified)') AS genre_label, COUNT(*) AS n
FROM books
GROUP BY genre
ORDER BY n DESC, genre_label;

.print ''
.print '--- 6.3 two aggregates per bucket, and the COUNT gap that reveals the NULLs'
SELECT IFNULL(genre, '(unclassified)') AS genre_label,
       COUNT(*)                        AS books,
       COUNT(rating)                   AS rated,
       ROUND(AVG(rating), 3)           AS avg_rating
FROM books
GROUP BY genre
ORDER BY books DESC, genre_label;

.print ''
.print '--- 6.4 grouping by an EXPRESSION rather than a column: books per decade'
SELECT (published_year / 10) * 10 AS decade, COUNT(*) AS n
FROM books
WHERE published_year IS NOT NULL
GROUP BY decade
ORDER BY decade;

.print ''
.print '--- 6.5 grouping by two keys gives one row per combination that actually occurs'
SELECT author, IFNULL(genre, '(unclassified)') AS genre_label, COUNT(*) AS n
FROM books
GROUP BY author, genre
ORDER BY author, genre_label;

.print ''
.print '--- 6.6 the loans table: who borrows most'
SELECT member_id, COUNT(*) AS loans_taken
FROM loans
GROUP BY member_id
ORDER BY loans_taken DESC, member_id
LIMIT 5;

.print ''
.print '--- 6.7 an aggregate over a CASE is how you count a subset inside a bucket'
SELECT member_id,
       COUNT(*)                                      AS loans_taken,
       SUM(CASE WHEN returned_on IS NULL THEN 1 ELSE 0 END) AS still_out,
       COUNT(returned_on)                            AS returned
FROM loans
GROUP BY member_id
ORDER BY still_out DESC, member_id;

.print ''
.print '--- 6.8 WHERE runs BEFORE GROUP BY, so this counts only the loans of 2026 Q1'
SELECT member_id, COUNT(*) AS q1_loans
FROM loans
WHERE borrowed_on BETWEEN '2026-01-01' AND '2026-03-31'
GROUP BY member_id
ORDER BY q1_loans DESC, member_id
LIMIT 5;
