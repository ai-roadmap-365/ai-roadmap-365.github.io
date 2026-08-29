-- 03 — NULL and three-valued logic: the traps, and the correct forms
--
-- Run:  sqlite3 -header -column examples/library.db < examples/queries/03-null-traps.sql
--
-- NULL is not a value. It is the absence of one. Every comparison against it
-- returns UNKNOWN, and WHERE keeps only rows where the predicate is TRUE.
-- UNKNOWN is not TRUE, so those rows silently disappear.

.print '--- 3.1 the truth, straight from the engine: NULL = NULL is not true'
SELECT NULL = NULL           AS null_eq_null,
       NULL <> NULL          AS null_ne_null,
       NULL IS NULL          AS null_is_null,
       (NULL AND 0)          AS null_and_false,
       (NULL AND 1)          AS null_and_true,
       (NULL OR 1)           AS null_or_true,
       (NULL OR 0)           AS null_or_false,
       (NOT NULL)            AS not_null;

.print ''
.print '--- 3.2 THE TRAP: books still on loan, written the wrong way'
SELECT COUNT(*) AS wrong_still_out
FROM loans
WHERE returned_on = NULL;

.print ''
.print '--- 3.3 the same wrong idea in its other popular disguise'
SELECT COUNT(*) AS also_wrong_still_out
FROM loans
WHERE returned_on <> '';

.print ''
.print '--- 3.4 the only correct test'
SELECT COUNT(*) AS still_out
FROM loans
WHERE returned_on IS NULL;

.print ''
.print '--- 3.5 the mirror trap: "not from Pune" quietly drops members with no city'
SELECT COUNT(*) AS naive_not_pune
FROM members
WHERE city <> 'Pune';

SELECT COUNT(*) AS honest_not_pune
FROM members
WHERE city IS NULL OR city <> 'Pune';

SELECT COUNT(*) AS total_members FROM members;

.print ''
.print '--- 3.6 IS NOT DISTINCT FROM: the NULL-safe equality, spelled IS in SQLite'
SELECT COUNT(*) AS unrated_via_is
FROM books
WHERE rating IS NULL;

.print ''
.print '--- 3.7 COALESCE and IFNULL substitute a value for the absence of one'
SELECT title,
       rating                       AS raw_rating,
       COALESCE(rating, 0.0)        AS rating_as_zero,
       IFNULL(genre, 'unclassified') AS genre_filled
FROM books
WHERE rating IS NULL OR genre IS NULL
ORDER BY book_id;

.print ''
.print '--- 3.8 NULLIF is the inverse: turn a sentinel value back into NULL'
SELECT NULLIF(0, 0) AS zero_becomes_null, NULLIF(5, 0) AS five_stays_five;
