-- Day 086 lab — the model answers to starter/exercises.sql.
--
-- Run:  sqlite3 examples/library.db < examples/exercise-answers.sql
--
-- Read this AFTER you have tried the exercises, not before. Each answer below
-- is one line of the form exNN|value, the same shape starter/exercises.sql
-- emits, so `bash starter/check.sh` can compare the two directly.
--
-- The point of each fix is written above it. In every single case the broken
-- version ran without complaint and returned a plausible number: that is the
-- thing to take away from this file.

.mode list
.headers off

-- 1. `= NULL` is UNKNOWN for every row, so the broken version counted nothing.
--    IS NULL is the only test for absence.
SELECT 'ex01|' || (
  SELECT COUNT(*) FROM loans WHERE returned_on IS NULL
);

-- 2. `city <> 'Pune'` is UNKNOWN where city is NULL, and WHERE keeps only TRUE,
--    so the two members with no city vanished from a question they belong in.
SELECT 'ex02|' || (
  SELECT COUNT(*) FROM members WHERE city IS NULL OR city <> 'Pune'
);

-- 3. GLOB is case-sensitive; LIKE folds case for ASCII letters. Same intent,
--    different matcher.
SELECT 'ex03|' || (
  SELECT COUNT(*) FROM books WHERE title LIKE '%archive%'
);

-- 4. BETWEEN is inclusive at both ends; the strict inequalities dropped 2015
--    and 2018 silently.
SELECT 'ex04|' || (
  SELECT COUNT(*) FROM books WHERE published_year BETWEEN 2015 AND 2018
);

-- 5. AVG already ignores NULLs. COALESCE(rating, 0.0) invents four ratings of
--    zero and drags the average down by more than half a point.
SELECT 'ex05|' || (
  SELECT ROUND(AVG(rating), 2) FROM books
);

-- 6. COUNT(*) counts rows; COUNT(rating) counts non-NULL ratings. The gap
--    between them is exactly the number of unrated books.
SELECT 'ex06|' || (
  SELECT COUNT(*) - COUNT(rating) FROM books
);

-- 7. Ascending order puts NULLs first in SQLite, so the broken version returned
--    a book with no rating as the worst-rated book.
SELECT 'ex07|' || (
  SELECT title FROM books WHERE rating IS NOT NULL ORDER BY rating ASC LIMIT 1
);

-- 8. COUNT(DISTINCT genre) skips NULL. GROUP BY collects all the NULLs into one
--    bucket, which is the bucket the question asked about.
SELECT 'ex08|' || (
  SELECT COUNT(*) FROM (SELECT genre FROM books GROUP BY genre)
);

-- 9. ORDER BY defaults to ASC, which answers the opposite question. DESC, and a
--    tie-break so the answer is deterministic.
SELECT 'ex09|' || (
  SELECT author FROM books GROUP BY author ORDER BY COUNT(*) DESC, author ASC LIMIT 1
);

-- 10. "How many titles this author has" is a property of the GROUP, so only
--     HAVING can filter on it. WHERE runs before the groups exist.
SELECT 'ex10|' || (
  SELECT COUNT(*) FROM (
    SELECT author FROM books GROUP BY author HAVING COUNT(*) > 3
  )
);

-- 11. Both columns are TEXT. Subtracting them coerces each string to the number
--     at its front — 2026 minus 2026 — and confidently returns 0.
SELECT 'ex11|' || (
  SELECT JULIANDAY(returned_on) - JULIANDAY(borrowed_on) FROM loans WHERE loan_id = 2
);

-- 12. `rating >= 4.5` is UNKNOWN when rating is NULL, so every unrated book fell
--     through to the ELSE and was labelled 'poor'. The NULL branch has to come
--     first, because CASE stops at the first WHEN that is TRUE.
SELECT 'ex12|' || (
  SELECT COUNT(*) FROM (
    SELECT CASE
             WHEN rating IS NULL THEN 'unrated'
             WHEN rating >= 4.5  THEN 'excellent'
             WHEN rating >= 4.0  THEN 'good'
             ELSE                     'poor'
           END AS band
    FROM books
  )
  WHERE band = 'unrated'
);
