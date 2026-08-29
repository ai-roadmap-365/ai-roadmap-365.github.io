-- Day 086 lab — YOUR WORK. Twelve numbered exercises.
--
-- Run them at any time, from the lab directory:
--   sqlite3 examples/library.db < starter/exercises.sql
-- Score them:
--   bash starter/check.sh
--
-- Every exercise below RUNS right now. None of them is blank, and none of them
-- is an error. Each one is a query somebody wrote in a hurry, which returns a
-- confident, well-formatted, WRONG answer. Your job is to make each one right.
--
-- That is the shape of the whole day. SQL almost never tells you that you asked
-- the wrong question; it just answers the one you actually asked.
--
-- Each statement prints one line: exNN|value. `bash starter/check.sh` compares
-- those values to the required answers and tells you which are still wrong.
-- Do NOT change the exNN label or the number of statements.

.mode list
.headers off

-- ---------------------------------------------------------------------------
-- Exercise 1 — How many loans are still outstanding?
-- A book that is still out has no returned_on date at all.
-- Required answer: 15
-- Hint: NULL is never equal to anything, including NULL.
-- ---------------------------------------------------------------------------
SELECT 'ex01|' || (
  SELECT COUNT(*) FROM loans WHERE returned_on = NULL
);

-- ---------------------------------------------------------------------------
-- Exercise 2 — How many members are NOT from Pune?
-- A member who never told us their city is certainly not from Pune.
-- Required answer: 10
-- Hint: `city <> 'Pune'` is UNKNOWN when city is NULL, and WHERE keeps only TRUE.
-- ---------------------------------------------------------------------------
SELECT 'ex02|' || (
  SELECT COUNT(*) FROM members WHERE city <> 'Pune'
);

-- ---------------------------------------------------------------------------
-- Exercise 3 — How many titles contain the word "archive", in any case?
-- Required answer: 2
-- Hint: GLOB is case-sensitive. One of SQLite's two pattern matchers is not.
-- ---------------------------------------------------------------------------
SELECT 'ex03|' || (
  SELECT COUNT(*) FROM books WHERE title GLOB '*archive*'
);

-- ---------------------------------------------------------------------------
-- Exercise 4 — How many books were published in 2015, 2016, 2017 or 2018?
-- Required answer: 4
-- Hint: BETWEEN includes both endpoints. Strict inequalities do not.
-- ---------------------------------------------------------------------------
SELECT 'ex04|' || (
  SELECT COUNT(*) FROM books WHERE published_year > 2015 AND published_year < 2018
);

-- ---------------------------------------------------------------------------
-- Exercise 5 — What is the average rating of the books that HAVE a rating,
-- rounded to two decimal places?
-- Required answer: 4.16
-- Hint: an unrated book is not a book rated zero. Do not invent data.
-- ---------------------------------------------------------------------------
SELECT 'ex05|' || (
  SELECT ROUND(AVG(COALESCE(rating, 0.0)), 2) FROM books
);

-- ---------------------------------------------------------------------------
-- Exercise 6 — How many books have never been rated?
-- Required answer: 4
-- Hint: COUNT(*) and COUNT(column) count different things. The gap is the answer.
-- ---------------------------------------------------------------------------
SELECT 'ex06|' || (
  SELECT COUNT(rating) FROM books
);

-- ---------------------------------------------------------------------------
-- Exercise 7 — What is the title of the LOWEST-rated book that has a rating?
-- Required answer: Ledger of Tides
-- Hint: ascending order puts the NULLs first in SQLite, and a NULL is not a
-- low rating — it is no rating.
-- ---------------------------------------------------------------------------
SELECT 'ex07|' || (
  SELECT title FROM books ORDER BY rating ASC LIMIT 1
);

-- ---------------------------------------------------------------------------
-- Exercise 8 — How many genre buckets does the catalogue have, counting the
-- unclassified books as one bucket of their own?
-- Required answer: 6
-- Hint: COUNT(DISTINCT genre) skips NULL. GROUP BY does not.
-- ---------------------------------------------------------------------------
SELECT 'ex08|' || (
  SELECT COUNT(DISTINCT genre) FROM books
);

-- ---------------------------------------------------------------------------
-- Exercise 9 — Which author has the most titles in the catalogue?
-- Required answer: Ada Fenwick
-- Hint: ORDER BY defaults to ascending, which gives you the answer to the
-- opposite question.
-- ---------------------------------------------------------------------------
SELECT 'ex09|' || (
  SELECT author FROM books GROUP BY author ORDER BY COUNT(*) LIMIT 1
);

-- ---------------------------------------------------------------------------
-- Exercise 10 — How many authors have MORE THAN THREE titles?
-- Required answer: 3
-- Hint: "how many titles this author has" is a fact about a group, not about a
-- row, so WHERE cannot see it. There is exactly one clause that can.
-- ---------------------------------------------------------------------------
SELECT 'ex10|' || (
  SELECT COUNT(DISTINCT author) FROM books
);

-- ---------------------------------------------------------------------------
-- Exercise 11 — For how many days was loan 2 held?
-- Required answer: 28.0
-- Hint: SQLite has no date type. Those two columns are TEXT, and subtracting
-- one piece of text from another gives you arithmetic on whatever number the
-- engine can squeeze out of the front of each string.
-- ---------------------------------------------------------------------------
SELECT 'ex11|' || (
  SELECT returned_on - borrowed_on FROM loans WHERE loan_id = 2
);

-- ---------------------------------------------------------------------------
-- Exercise 12 — How many books land in the 'unrated' band of this histogram?
-- Required answer: 4
-- Hint: CASE evaluates its WHEN branches in order and stops at the first TRUE.
-- A comparison against NULL is never TRUE, so it falls through to the ELSE.
-- ---------------------------------------------------------------------------
SELECT 'ex12|' || (
  SELECT COUNT(*) FROM (
    SELECT CASE
             WHEN rating >= 4.5 THEN 'excellent'
             WHEN rating >= 4.0 THEN 'good'
             ELSE                    'poor'
           END AS band
    FROM books
  )
  WHERE band = 'unrated'
);
