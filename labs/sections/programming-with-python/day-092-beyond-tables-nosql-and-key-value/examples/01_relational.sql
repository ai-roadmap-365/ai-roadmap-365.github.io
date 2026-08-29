-- Day 092 · Step 1 — the relational baseline.
--
-- This is the shape you spent Week 13 learning: one table per kind of thing,
-- every fact written down once, the relationships carried by foreign keys.
-- Everything that follows in this lab models THE SAME library four ways, so
-- that you can compare like with like.
--
-- Three things are worth watching for here, because the other three shapes
-- give each of them up:
--
--   * the column list is a contract, checked on every write (schema-on-write)
--   * a foreign key refuses a reference to a row that is not there
--   * a query can filter and aggregate on ANY column, not just the key
--
-- Run with:  sqlite3 library.db < examples/01_relational.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS book_authors;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;

CREATE TABLE authors (
  author_id  INTEGER PRIMARY KEY,
  name       TEXT    NOT NULL UNIQUE,
  birth_year INTEGER
);

CREATE TABLE books (
  book_id        INTEGER PRIMARY KEY,
  title          TEXT    NOT NULL,
  published_year INTEGER NOT NULL,
  shelf          TEXT    NOT NULL
);

CREATE TABLE book_authors (
  book_id   INTEGER NOT NULL REFERENCES books(book_id)     ON DELETE CASCADE,
  author_id INTEGER NOT NULL REFERENCES authors(author_id) ON DELETE RESTRICT,
  PRIMARY KEY (book_id, author_id)
);

CREATE TABLE members (
  member_id INTEGER PRIMARY KEY,
  name      TEXT    NOT NULL,
  joined_on TEXT    NOT NULL
);

CREATE TABLE loans (
  loan_id     INTEGER PRIMARY KEY,
  book_id     INTEGER NOT NULL REFERENCES books(book_id),
  member_id   INTEGER NOT NULL REFERENCES members(member_id),
  borrowed_on TEXT    NOT NULL,
  returned_on TEXT
);

CREATE INDEX idx_book_authors_author ON book_authors(author_id);
CREATE INDEX idx_loans_book          ON loans(book_id);
CREATE INDEX idx_loans_member        ON loans(member_id);

-- The books and their authors are real and checkable. The members and the
-- loans are invented for this lab; no real borrowing history is used anywhere.
INSERT INTO authors (author_id, name, birth_year) VALUES
  (1, 'Brian W. Kernighan',      1942),
  (2, 'Dennis M. Ritchie',       1941),
  (3, 'Frederick P. Brooks Jr.', 1931),
  (4, 'Stuart J. Russell',       1962),
  (5, 'Peter Norvig',            1956),
  (6, 'Rob Pike',                1956);

INSERT INTO books (book_id, title, published_year, shelf) VALUES
  (101, 'The C Programming Language',                 1978, 'A3'),
  (102, 'The Mythical Man-Month',                     1975, 'B1'),
  (103, 'Artificial Intelligence: A Modern Approach', 1995, 'C2'),
  (104, 'The Practice of Programming',                1999, 'A3');

INSERT INTO book_authors (book_id, author_id) VALUES
  (101, 1), (101, 2), (102, 3), (103, 4), (103, 5), (104, 1), (104, 6);

INSERT INTO members (member_id, name, joined_on) VALUES
  (1, 'Ada Okafor',    '2026-01-05'),
  (2, 'Bruno Salgado', '2026-01-19'),
  (3, 'Chandra Iyer',  '2026-02-02');

INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, returned_on) VALUES
  (1, 101, 1, '2026-05-04', '2026-05-18'),
  (2, 102, 1, '2026-05-20', NULL),
  (3, 101, 2, '2026-06-01', '2026-06-14'),
  (4, 103, 3, '2026-06-03', NULL);

.mode column
.headers on

.print '--- 1. fetch one book by its key: the thing every store can do ---'
SELECT book_id, title, published_year, shelf FROM books WHERE book_id = 101;

.print ''
.print '--- 2. filter on a NON-key column: the thing only some stores can do ---'
SELECT book_id, title, published_year FROM books WHERE published_year < 1990 ORDER BY book_id;

.print ''
.print '--- 3. join and aggregate across tables ---'
SELECT a.name AS author, count(*) AS books
  FROM authors AS a
  JOIN book_authors AS ba ON ba.author_id = a.author_id
 GROUP BY a.author_id, a.name
 ORDER BY books DESC, author
 LIMIT 3;

.print ''
.print '--- 4. schema-on-write: a misspelled column is refused, now, loudly ---'
-- The next statement FAILS on purpose. "titel" is not a column of books, and
-- the database will not invent one. Remember this line; three shapes from now,
-- the same mistake will be accepted in silence.
INSERT INTO books (book_id, titel, published_year, shelf)
VALUES (105, 'Compilers: Principles, Techniques, and Tools', 1986, 'C1');
