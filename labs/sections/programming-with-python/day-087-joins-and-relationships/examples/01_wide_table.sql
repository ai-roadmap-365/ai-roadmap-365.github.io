-- Day 087 · Step 1 — the single wide table, and the three anomalies it causes.
--
-- This is the "before" picture. One table holds everything the library knows
-- about a book AND everything it knows about that book's author, so an author
-- who wrote two books has their details written down twice.
--
-- Run with:  sqlite3 library.db < examples/01_wide_table.sql

DROP TABLE IF EXISTS catalog_wide;

CREATE TABLE catalog_wide (
  title             TEXT    NOT NULL,
  published_year    INTEGER NOT NULL,
  author_name       TEXT    NOT NULL,
  author_birth_year INTEGER NOT NULL
);

INSERT INTO catalog_wide (title, published_year, author_name, author_birth_year) VALUES
  ('The C Programming Language',  1978, 'Brian W. Kernighan',      1942),
  ('The C Programming Language',  1978, 'Dennis M. Ritchie',       1941),
  ('The Practice of Programming', 1999, 'Brian W. Kernighan',      1942),
  ('The Practice of Programming', 1999, 'Rob Pike',                1956),
  ('The Mythical Man-Month',      1975, 'Frederick P. Brooks Jr.', 1931);

.mode column
.headers on

.print ''
.print '--- the wide table: note Kernighan appears twice ---'
SELECT * FROM catalog_wide ORDER BY title, author_name;

-- ANOMALY 1 — UPDATE. The library learns the author prefers the shorter form
-- of his name. Someone updates "the C book" and stops, because that is the row
-- they were looking at.
.print ''
.print '--- update anomaly: rename the author on one book only ---'
UPDATE catalog_wide
   SET author_name = 'Brian Kernighan'
 WHERE title = 'The C Programming Language'
   AND author_name = 'Brian W. Kernighan';

-- The database now holds two different names for one human being, with no
-- error, no warning and nothing marking which one is right.
SELECT DISTINCT author_name, author_birth_year
  FROM catalog_wide
 WHERE author_birth_year = 1942;

-- ANOMALY 2 — INSERT. Record an author the library has catalogued no books for.
-- There is no way to do it: every column about a book is NOT NULL, because a
-- row in this table IS a book. The author cannot exist without one.
.print ''
.print '--- insertion anomaly: an author with no catalogued book has no home ---'
.print 'no row can be written for Donald E. Knuth without inventing a book'

-- ANOMALY 3 — DELETE. The library withdraws its only copy of the Brooks book.
-- Deleting the book deletes the only record that Frederick P. Brooks Jr. exists.
.print ''
.print '--- deletion anomaly: withdraw a book, lose an author ---'
DELETE FROM catalog_wide WHERE title = 'The Mythical Man-Month';
SELECT count(*) AS brooks_rows_remaining
  FROM catalog_wide
 WHERE author_name LIKE '%Brooks%';
