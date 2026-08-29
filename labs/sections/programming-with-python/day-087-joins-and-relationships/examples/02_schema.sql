-- Day 087 · Step 2 — the same information, split into five tables.
--
-- Each table holds facts about exactly one kind of thing, and every fact is
-- written down in exactly one place. The relationships between the things are
-- carried by foreign keys.
--
--   authors        one row per person
--   books          one row per book
--   book_authors   the junction table: many books to many authors
--   members        one row per library member (self-referencing: who referred whom)
--   loans          one row per borrowing event (many loans to one book, many to one member)
--
-- Run with:  sqlite3 library.db < examples/02_schema.sql

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
  published_year INTEGER NOT NULL
);

-- The junction table. Its primary key is the PAIR, which is what stops the
-- same author being attached to the same book twice.
CREATE TABLE book_authors (
  book_id   INTEGER NOT NULL REFERENCES books(book_id)     ON DELETE CASCADE,
  author_id INTEGER NOT NULL REFERENCES authors(author_id) ON DELETE RESTRICT,
  PRIMARY KEY (book_id, author_id)
);

-- referred_by points back at this same table: a self-referencing foreign key.
-- It is nullable, because the first members were referred by nobody.
CREATE TABLE members (
  member_id   INTEGER PRIMARY KEY,
  name        TEXT    NOT NULL,
  joined_on   TEXT    NOT NULL,
  referred_by INTEGER REFERENCES members(member_id)
);

-- The key lives on the MANY side. One book has many loans, so book_id is here,
-- in loans — not a list of loans inside books.
CREATE TABLE loans (
  loan_id     INTEGER PRIMARY KEY,
  book_id     INTEGER NOT NULL REFERENCES books(book_id),
  member_id   INTEGER NOT NULL REFERENCES members(member_id),
  borrowed_on TEXT    NOT NULL,
  returned_on TEXT
);

-- A foreign key does not create an index. Without these, every join and every
-- referential-integrity check on the child side is a full table scan.
CREATE INDEX idx_book_authors_author ON book_authors(author_id);
CREATE INDEX idx_loans_book          ON loans(book_id);
CREATE INDEX idx_loans_member        ON loans(member_id);
