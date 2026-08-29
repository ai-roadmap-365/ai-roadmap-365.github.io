-- 01 — WHERE: comparison and boolean operators, IN, BETWEEN
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/01-filters.sql

.print '--- 1.1 science books published this century, longest first'
SELECT title, published_year, pages
FROM books
WHERE genre = 'science' AND published_year >= 2000
ORDER BY pages DESC;

.print ''
.print '--- 1.2 two genres AND a year, with the brackets that make it mean that'
SELECT title, genre, published_year
FROM books
WHERE (genre = 'science' OR genre = 'history') AND published_year >= 2015
ORDER BY published_year;

.print ''
.print '--- 1.2b the same words without brackets: AND binds tighter than OR, so it means'
.print '         science-of-any-year OR history-since-2015 — a different question'
SELECT COUNT(*) AS with_brackets
FROM books
WHERE (genre = 'science' OR genre = 'history') AND published_year >= 2015;

SELECT COUNT(*) AS without_brackets
FROM books
WHERE genre = 'science' OR genre = 'history' AND published_year >= 2015;

.print ''
.print '--- 1.3 IN is the readable form of a chain of ORs'
SELECT title, genre
FROM books
WHERE genre IN ('poetry', 'mystery')
ORDER BY genre, title;

.print ''
.print '--- 1.4 BETWEEN is inclusive at BOTH ends'
SELECT title, published_year
FROM books
WHERE published_year BETWEEN 2015 AND 2018
ORDER BY published_year, title;

.print ''
.print '--- 1.5 the same range written out, to prove BETWEEN includes the edges'
SELECT COUNT(*) AS between_count
FROM books
WHERE published_year BETWEEN 2015 AND 2018;

SELECT COUNT(*) AS explicit_count
FROM books
WHERE published_year >= 2015 AND published_year <= 2018;

.print ''
.print '--- 1.6 NOT IN: everything except two genres (watch what happens to NULL genres)'
SELECT COUNT(*) AS not_in_count
FROM books
WHERE genre NOT IN ('poetry', 'mystery');
