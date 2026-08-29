-- 07 — HAVING: the filter that WHERE cannot express
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/07-having.sql
--
-- WHERE filters ROWS before grouping. HAVING filters GROUPS after grouping.
-- "Authors with more than three books" is not a fact about any single row, so
-- WHERE cannot see it. There is no row that knows how many books its author
-- wrote — only the bucket knows.

.print '--- 7.1 authors with more than three books in the catalogue'
SELECT author, COUNT(*) AS titles
FROM books
GROUP BY author
HAVING COUNT(*) > 3
ORDER BY titles DESC, author;

.print ''
.print '--- 7.2 the attempt WHERE cannot make (kept as a comment, because it is an error)'
--  SELECT author, COUNT(*) AS titles FROM books WHERE COUNT(*) > 3 GROUP BY author;
--  -> Error: in prepare, misuse of aggregate: COUNT()
.print '     see the comment in this file, and section 3 of tests/run_tests.sh'

.print ''
.print '--- 7.3 WHERE and HAVING in the same query, each doing its own job'
SELECT genre, COUNT(*) AS n, ROUND(AVG(rating), 3) AS avg_rating
FROM books
WHERE published_year >= 2000        -- throws away rows
GROUP BY genre
HAVING COUNT(*) >= 2                -- throws away buckets
ORDER BY n DESC, genre;

.print ''
.print '--- 7.4 HAVING on an aggregate that is not in the SELECT list at all'
SELECT genre
FROM books
GROUP BY genre
HAVING AVG(pages) > 350
ORDER BY genre;

.print ''
.print '--- 7.5 books borrowed more than twice — the classic popularity query'
SELECT book_id, COUNT(*) AS times_borrowed
FROM loans
GROUP BY book_id
HAVING COUNT(*) > 2
ORDER BY times_borrowed DESC, book_id;

.print ''
.print '--- 7.6 HAVING on an expression built from TWO aggregates: two or more books still out'
SELECT member_id,
       COUNT(*)                     AS loans_taken,
       COUNT(*) - COUNT(returned_on) AS still_out
FROM loans
GROUP BY member_id
HAVING COUNT(*) - COUNT(returned_on) >= 2
ORDER BY still_out DESC, member_id;

.print ''
.print '--- 7.7 SQLite lets a bare column ride along in an aggregate query; most engines do not'
SELECT genre, title, COUNT(*) AS n
FROM books
GROUP BY genre
ORDER BY genre;
.print '     the title above is ONE arbitrary row from each bucket, not a summary.'
.print '     PostgreSQL rejects this query outright. Do not rely on it.'
