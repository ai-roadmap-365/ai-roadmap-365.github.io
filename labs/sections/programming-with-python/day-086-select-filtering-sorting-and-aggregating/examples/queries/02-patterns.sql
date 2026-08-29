-- 02 — LIKE and GLOB: two pattern matchers with different rules
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/02-patterns.sql
--
-- LIKE uses % (any run of characters) and _ (exactly one character), and for
-- ASCII letters it is CASE-INSENSITIVE by default in SQLite.
-- GLOB uses * and ?, plus [character classes], and is always CASE-SENSITIVE.

.print '--- 2.1 LIKE: every title containing "archive", in any case'
SELECT title
FROM books
WHERE title LIKE '%archive%'
ORDER BY title;

.print ''
.print '--- 2.2 GLOB with the same intent, lower case — case-sensitive, so it finds nothing'
SELECT COUNT(*) AS glob_lowercase_matches
FROM books
WHERE title GLOB '*archive*';

.print ''
.print '--- 2.3 GLOB spelled the way the data is spelled'
SELECT title
FROM books
WHERE title GLOB '*Archive*'
ORDER BY title;

.print ''
.print '--- 2.4 the underscore matches exactly one character — five of them, for "Quiet"'
SELECT title
FROM books
WHERE title LIKE 'The _____ Algorithm';

.print ''
.print '--- 2.4b four underscores is one too few, and the result is silence, not an error'
SELECT COUNT(*) AS four_underscores
FROM books
WHERE title LIKE 'The ____ Algorithm';

.print ''
.print '--- 2.5 GLOB character classes, which LIKE has no equivalent for'
SELECT title
FROM books
WHERE title GLOB '[AN]*'
ORDER BY title;

.print ''
.print '--- 2.6 anchored prefix search: authors whose surname starts with a letter range'
SELECT DISTINCT author
FROM books
WHERE author GLOB '* [A-M]*'
ORDER BY author;
