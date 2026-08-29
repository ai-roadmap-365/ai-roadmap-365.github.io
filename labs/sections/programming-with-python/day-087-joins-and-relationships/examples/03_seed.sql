-- Day 087 · Step 3 — seed the five tables.
--
-- The books and authors are real and checkable. The members and the loans are
-- invented for this lab; no real person's borrowing history is used anywhere.
--
-- Three deliberate gaps are built into this data, because they are what the
-- outer joins later in the lab are for:
--
--   * Donald E. Knuth is an author with NO catalogued book  (the insertion
--     anomaly, now possible)
--   * "The Practice of Programming" has NEVER been borrowed
--   * Eli Nakamura is a member who has NEVER borrowed anything
--
-- Run with:  sqlite3 library.db < examples/03_seed.sql

PRAGMA foreign_keys = ON;

DELETE FROM loans;
DELETE FROM book_authors;
DELETE FROM members;
DELETE FROM books;
DELETE FROM authors;

INSERT INTO authors (author_id, name, birth_year) VALUES
  (1, 'Brian W. Kernighan',      1942),
  (2, 'Dennis M. Ritchie',       1941),
  (3, 'Frederick P. Brooks Jr.', 1931),
  (4, 'Stuart J. Russell',       1962),
  (5, 'Peter Norvig',            1956),
  (6, 'Rob Pike',                1956),
  (7, 'Donald E. Knuth',         1938);

INSERT INTO books (book_id, title, published_year) VALUES
  (101, 'The C Programming Language',                 1978),
  (102, 'The Mythical Man-Month',                     1975),
  (103, 'Artificial Intelligence: A Modern Approach', 1995),
  (104, 'The Practice of Programming',                1999);

INSERT INTO book_authors (book_id, author_id) VALUES
  (101, 1),
  (101, 2),
  (102, 3),
  (103, 4),
  (103, 5),
  (104, 1),
  (104, 6);

INSERT INTO members (member_id, name, joined_on, referred_by) VALUES
  (1, 'Ada Okafor',     '2026-01-05', NULL),
  (2, 'Bruno Salgado',  '2026-01-19', 1),
  (3, 'Chandra Iyer',   '2026-02-02', 1),
  (4, 'Dana Whitfield', '2026-03-11', 2),
  (5, 'Eli Nakamura',   '2026-04-01', NULL);

INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, returned_on) VALUES
  (1, 101, 1, '2026-05-04', '2026-05-18'),
  (2, 102, 1, '2026-05-20', NULL),
  (3, 101, 2, '2026-06-01', '2026-06-14'),
  (4, 103, 3, '2026-06-03', NULL),
  (5, 101, 4, '2026-07-07', '2026-07-20'),
  (6, 102, 2, '2026-07-15', NULL);
