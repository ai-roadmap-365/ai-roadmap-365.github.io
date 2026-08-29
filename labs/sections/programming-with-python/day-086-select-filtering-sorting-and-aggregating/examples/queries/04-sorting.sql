-- 04 — ORDER BY, DISTINCT, LIMIT and OFFSET
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/04-sorting.sql

.print '--- 4.1 two sort keys: genre ascending, then rating descending inside each genre'
SELECT genre, title, rating
FROM books
WHERE genre IS NOT NULL AND rating IS NOT NULL
ORDER BY genre ASC, rating DESC
LIMIT 12;

.print ''
.print '--- 4.2 where NULLs sort in SQLite: first when ascending, last when descending'
SELECT title, rating
FROM books
ORDER BY rating ASC
LIMIT 6;

.print ''
.print '--- 4.3 the same column descending — the NULLs move to the end'
SELECT title, rating
FROM books
ORDER BY rating DESC
LIMIT 6;

.print ''
.print '--- 4.4 forcing NULLs last regardless of direction'
SELECT title, rating
FROM books
ORDER BY rating IS NULL, rating ASC
LIMIT 6;

.print ''
.print '--- 4.5 SQLite also spells it out: NULLS LAST'
SELECT title, rating
FROM books
ORDER BY rating ASC NULLS LAST
LIMIT 6;

.print ''
.print '--- 4.6 ORDER BY can use a SELECT alias, on every engine, because it runs after SELECT'
SELECT title, pages * 2 AS reading_minutes
FROM books
WHERE pages > 400
ORDER BY reading_minutes DESC;

.print ''
.print '--- 4.6b SQLite ALSO allows the alias in WHERE, as an extension. Standard SQL does'
.print '         not, and PostgreSQL rejects it. Portable code repeats the expression.'
SELECT COUNT(*) AS accepted_by_sqlite
FROM (SELECT title, pages * 2 AS reading_minutes FROM books WHERE reading_minutes > 800);

SELECT COUNT(*) AS the_portable_spelling
FROM (SELECT title, pages * 2 AS reading_minutes FROM books WHERE pages * 2 > 800);

.print ''
.print '--- 4.7 DISTINCT removes duplicate ROWS, not duplicate values in one column'
SELECT DISTINCT author FROM books ORDER BY author;

.print ''
.print '--- 4.8 DISTINCT over two columns keeps a row per distinct PAIR'
SELECT DISTINCT author, genre FROM books ORDER BY author, genre;

.print ''
.print '--- 4.9 top-N: LIMIT without ORDER BY is a coin toss, so always pair them'
SELECT title, rating
FROM books
ORDER BY rating DESC NULLS LAST, title ASC
LIMIT 5;

.print ''
.print '--- 4.10 page two of the same list, via OFFSET'
SELECT title, rating
FROM books
ORDER BY rating DESC NULLS LAST, title ASC
LIMIT 5 OFFSET 5;
