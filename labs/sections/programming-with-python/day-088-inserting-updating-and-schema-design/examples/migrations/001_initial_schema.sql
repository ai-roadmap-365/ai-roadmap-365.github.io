-- 001 — the starting schema: members, books, loans.
--
-- This file takes an empty database to version 1. It never changes again.
-- That is the discipline that makes a migration set trustworthy: an applied
-- migration is history, and you edit history by adding to it, not by going
-- back and altering what people have already run.

CREATE TABLE members (
    id        INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL,
    email     TEXT    NOT NULL UNIQUE,
    joined_on TEXT    NOT NULL DEFAULT (date('now')),

    CHECK (length(trim(name)) > 0),
    CHECK (email LIKE '_%@_%._%')
) STRICT;

CREATE TABLE books (
    id     INTEGER PRIMARY KEY,
    isbn   TEXT    NOT NULL UNIQUE,
    title  TEXT    NOT NULL,
    author TEXT    NOT NULL,
    copies INTEGER NOT NULL DEFAULT 1 CHECK (copies >= 0)
) STRICT;

CREATE TABLE loans (
    id          INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(id)   ON DELETE RESTRICT,
    member_id   INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    borrowed_on TEXT    NOT NULL DEFAULT (date('now')),
    due_on      TEXT    NOT NULL,
    returned    INTEGER NOT NULL DEFAULT 0 CHECK (returned IN (0, 1)),

    CHECK (due_on >= borrowed_on)
) STRICT;
