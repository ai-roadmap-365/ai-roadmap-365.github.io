-- 05 — the five aggregates, and what NULL does to each of them
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/05-aggregates.sql
--
-- The rule that explains everything below: every aggregate except COUNT(*)
-- IGNORES NULL inputs. It does not treat them as zero. It does not treat them
-- as anything. They are removed before the arithmetic starts.

.print '--- 5.1 COUNT(*) counts ROWS; COUNT(column) counts NON-NULL VALUES in that column'
SELECT COUNT(*)               AS rows_total,
       COUNT(rating)          AS rows_with_a_rating,
       COUNT(genre)           AS rows_with_a_genre,
       COUNT(*) - COUNT(rating) AS unrated_books
FROM books;

.print ''
.print '--- 5.2 COUNT(DISTINCT column) counts distinct non-NULL values'
SELECT COUNT(author)          AS author_cells,
       COUNT(DISTINCT author) AS distinct_authors,
       COUNT(DISTINCT genre)  AS distinct_genres_excluding_null
FROM books;

.print ''
.print '--- 5.3 AVG over a column with NULLs divides by the NON-NULL count'
SELECT ROUND(AVG(rating), 4)                  AS avg_ignoring_nulls,
       ROUND(SUM(rating) / COUNT(rating), 4)  AS same_thing_by_hand,
       ROUND(SUM(rating) / COUNT(*), 4)       AS avg_if_nulls_counted_as_zero
FROM books;

.print ''
.print '--- 5.4 and the version people mean when they "fix" the NULLs — a different number'
SELECT ROUND(AVG(COALESCE(rating, 0.0)), 4) AS avg_with_nulls_as_zero
FROM books;

.print ''
.print '--- 5.5 SUM of an all-NULL set is NULL, not 0. TOTAL is the same sum returning 0.0'
SELECT SUM(rating)   AS sum_of_no_rows,
       TOTAL(rating) AS total_of_no_rows,
       COUNT(*)      AS matching_rows
FROM books
WHERE genre = 'no-such-genre';

.print ''
.print '--- 5.6 MIN and MAX also skip NULLs entirely'
SELECT MIN(rating) AS lowest_rating,
       MAX(rating) AS highest_rating,
       MIN(published_year) AS earliest_year,
       MAX(published_year) AS latest_year
FROM books;

.print ''
.print '--- 5.7 an aggregate over zero rows still returns exactly one row'
SELECT COUNT(*) AS n, AVG(rating) AS avg_rating, MAX(pages) AS longest
FROM books
WHERE published_year = 1066;
