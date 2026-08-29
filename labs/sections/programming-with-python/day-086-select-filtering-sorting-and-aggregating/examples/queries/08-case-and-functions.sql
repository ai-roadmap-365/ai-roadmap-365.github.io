-- 08 — computed columns, aliases, scalar functions and CASE
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/08-case-and-functions.sql
--
-- A scalar function takes one row's values and returns one value. An aggregate
-- takes many rows and returns one value. That single distinction decides which
-- clause each one is legal in.

.print '--- 8.1 a computed column with an alias'
SELECT title,
       pages,
       ROUND(pages / 250.0, 2) AS evenings_needed
FROM books
ORDER BY evenings_needed DESC
LIMIT 5;

.print ''
.print '--- 8.2 the string functions worth knowing'
SELECT UPPER(SUBSTR(author, 1, 1)) AS initial,
       LENGTH(title)               AS title_length,
       LOWER(genre)                AS genre_lower,
       REPLACE(title, 'The ', '')  AS title_without_the,
       TRIM('   padded   ')        AS trimmed
FROM books
WHERE book_id IN (1, 15)
ORDER BY book_id;

.print ''
.print '--- 8.3 concatenation is || in SQL, not + and not a function'
SELECT title || ' (' || author || ')' AS citation
FROM books
ORDER BY book_id
LIMIT 3;

.print ''
.print '--- 8.4 numeric and null-handling scalars'
SELECT ABS(-7)                    AS abs_value,
       ROUND(3.14159, 3)          AS rounded,
       CAST('42' AS INTEGER) + 1  AS cast_then_add,
       TYPEOF(rating)             AS rating_type,
       TYPEOF(NULL)               AS null_type
FROM books
WHERE book_id = 4;

.print ''
.print '--- 8.5 date functions: SQLite stores dates as text and reads them with these'
SELECT borrowed_on,
       STRFTIME('%Y-%m', borrowed_on)               AS month_bucket,
       JULIANDAY(returned_on) - JULIANDAY(borrowed_on) AS days_held
FROM loans
WHERE returned_on IS NOT NULL
ORDER BY loan_id
LIMIT 5;

.print ''
.print '--- 8.6 CASE turns a value into a label — the SQL equivalent of if/elif/else'
SELECT title,
       rating,
       CASE
         WHEN rating IS NULL  THEN 'unrated'
         WHEN rating >= 4.5   THEN 'excellent'
         WHEN rating >= 4.0   THEN 'good'
         WHEN rating >= 3.5   THEN 'fair'
         ELSE                      'poor'
       END AS band
FROM books
ORDER BY book_id
LIMIT 10;

.print ''
.print '--- 8.7 GROUP BY over a CASE expression: a histogram of rating bands'
SELECT CASE
         WHEN rating IS NULL  THEN 'unrated'
         WHEN rating >= 4.5   THEN 'excellent'
         WHEN rating >= 4.0   THEN 'good'
         WHEN rating >= 3.5   THEN 'fair'
         ELSE                      'poor'
       END AS band,
       COUNT(*) AS n
FROM books
GROUP BY band
ORDER BY n DESC, band;

.print ''
.print '--- 8.8 the WHEN order matters: put the NULL branch first or it never fires'
SELECT COUNT(*) AS mislabelled_as_poor
FROM books
WHERE rating IS NULL
  AND (CASE WHEN rating >= 4.0 THEN 'good' ELSE 'poor' END) = 'poor';
