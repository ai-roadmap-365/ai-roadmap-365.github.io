-- Day 088 lab — the library database used by every demonstration.
--
-- Run it with:   sqlite3 library.db < examples/seed.sql
--
-- Two things to notice before you read the schema.
--
-- 1. PRAGMA foreign_keys = ON is the FIRST line. SQLite ships with foreign
--    key enforcement OFF by default (Day 87). A schema full of REFERENCES
--    clauses that is opened without this pragma is decoration: the clauses
--    parse, they are stored, and nothing checks them. The pragma is per
--    connection, not per database, so it must be set every single time you
--    connect. There is no way to store "enforce my foreign keys" in the file.
--
-- 2. Every table is STRICT. In an ordinary SQLite table a column declared
--    INTEGER will happily store the string 'banana'. STRICT turns that into
--    an error. It costs nothing and it removes a whole category of surprise.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS members;

-- ---------------------------------------------------------------------------
-- members
-- ---------------------------------------------------------------------------
-- Each constraint below is a sentence about the world, written so the database
-- can enforce it. Read them as documentation that cannot go out of date.
CREATE TABLE members (
    id        INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL,
    email     TEXT    NOT NULL UNIQUE,
    joined_on TEXT    NOT NULL DEFAULT (date('now')),

    -- A name that is empty, or nothing but spaces, is not a name.
    CHECK (length(trim(name)) > 0),
    -- A deliberately loose email shape: something, an @, something, a dot,
    -- something. It is not a validator. It is a tripwire for obvious rubbish.
    CHECK (email LIKE '_%@_%._%')
) STRICT;

-- ---------------------------------------------------------------------------
-- books
-- ---------------------------------------------------------------------------
CREATE TABLE books (
    id     INTEGER PRIMARY KEY,
    isbn   TEXT    NOT NULL UNIQUE,
    title  TEXT    NOT NULL,
    author TEXT    NOT NULL,
    -- You cannot own a negative number of copies of anything.
    copies INTEGER NOT NULL DEFAULT 1 CHECK (copies >= 0)
) STRICT;

-- ---------------------------------------------------------------------------
-- loans
-- ---------------------------------------------------------------------------
-- The two foreign keys deliberately have DIFFERENT delete rules, because the
-- two questions they answer are different.
--
--   book_id   ON DELETE RESTRICT — deleting a book that is on loan is a
--                                  mistake, so refuse it and make somebody
--                                  think about it.
--   member_id ON DELETE CASCADE  — deleting a member should take their loan
--                                  history with them, because a loan with no
--                                  borrower is not a fact about anything.
--
-- Choosing between these two is a modelling decision, not a style preference.
CREATE TABLE loans (
    id          INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(id)   ON DELETE RESTRICT,
    member_id   INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    borrowed_on TEXT    NOT NULL DEFAULT (date('now')),
    due_on      TEXT    NOT NULL,
    returned    INTEGER NOT NULL DEFAULT 0 CHECK (returned IN (0, 1)),

    -- Time runs forwards. A loan cannot be due before it was borrowed.
    CHECK (due_on >= borrowed_on)
) STRICT;

-- ---------------------------------------------------------------------------
-- Data. Fixed dates, so every capture in expected-output/ is reproducible.
-- ---------------------------------------------------------------------------
INSERT INTO members (id, name, email, joined_on) VALUES
    (1, 'Ada Okonkwo',    'ada@library.test',    '2025-01-14'),
    (2, 'Bruno Sartori',  'bruno@library.test',  '2025-02-03'),
    (3, 'Chen Wei',       'chen@library.test',   '2025-03-27'),
    (4, 'Divya Ramanan',  'divya@library.test',  '2025-05-11'),
    (5, 'Emeka Balogun',  'emeka@library.test',  '2025-06-02'),
    (6, 'Farida Haddad',  'farida@library.test', '2025-09-19');

INSERT INTO books (id, isbn, title, author, copies) VALUES
    (1, '978-0131103627', 'The C Programming Language',  'Kernighan and Ritchie', 3),
    (2, '978-0201633610', 'Design Patterns',             'Gamma and others',      2),
    (3, '978-0262033848', 'Introduction to Algorithms',  'Cormen and others',     4),
    (4, '978-1449355739', 'Learning Python',             'Mark Lutz',             2),
    (5, '978-0596007126', 'Head First Design Patterns',  'Freeman and Robson',    1),
    (6, '978-0134685991', 'Effective Java',              'Joshua Bloch',          2),
    (7, '978-1593279509', 'Eloquent JavaScript',         'Marijn Haverbeke',      3),
    (8, '978-0132350884', 'Clean Code',                  'Robert C. Martin',      1);

-- 12 loans. 4 are already returned, 8 are still out. Those two numbers matter:
-- they are what the WHERE-less UPDATE in exercise 1 destroys.
INSERT INTO loans (id, book_id, member_id, borrowed_on, due_on, returned) VALUES
    ( 1, 1, 1, '2026-06-01', '2026-06-22', 1),
    ( 2, 3, 1, '2026-07-14', '2026-08-04', 0),
    ( 3, 2, 2, '2026-06-09', '2026-06-30', 1),
    ( 4, 5, 2, '2026-07-30', '2026-08-20', 0),
    ( 5, 4, 3, '2026-05-18', '2026-06-08', 1),
    ( 6, 7, 3, '2026-08-01', '2026-08-22', 0),
    ( 7, 6, 3, '2026-08-04', '2026-08-25', 0),
    ( 8, 8, 4, '2026-07-07', '2026-07-28', 1),
    ( 9, 1, 4, '2026-08-10', '2026-08-31', 0),
    (10, 3, 5, '2026-08-11', '2026-09-01', 0),
    (11, 2, 5, '2026-08-12', '2026-09-02', 0),
    (12, 7, 6, '2026-08-14', '2026-09-04', 0);
