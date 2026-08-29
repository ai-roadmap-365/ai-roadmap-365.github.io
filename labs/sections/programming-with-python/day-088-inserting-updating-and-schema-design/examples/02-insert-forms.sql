-- Day 088 lab, demonstration 2 — every useful shape of INSERT, plus
-- RETURNING and UPSERT.
--
--   cp library.db scratch.db
--   sqlite3 scratch.db < examples/02-insert-forms.sql

PRAGMA foreign_keys = ON;
.mode list
.headers off

-- ---------------------------------------------------------------------------
-- 1. One row. Always name the columns.
-- ---------------------------------------------------------------------------
-- INSERT INTO books VALUES (...) without a column list is a bug waiting for
-- somebody to add a column. Naming the columns makes the statement survive
-- schema change, which is the whole subject of today.
SELECT '--- 1. single row ---';
INSERT INTO books (isbn, title, author, copies)
VALUES ('978-0596517748', 'JavaScript: The Good Parts', 'Douglas Crockford', 2);
SELECT 'inserted ' || changes() || ' row(s), new id ' || last_insert_rowid();

-- ---------------------------------------------------------------------------
-- 2. Many rows in ONE statement.
-- ---------------------------------------------------------------------------
-- This is not only shorter. It is one statement, so it is one implicit
-- transaction: all four rows arrive or none of them do. Four separate INSERT
-- statements are four transactions, and an interruption can land between them.
SELECT '';
SELECT '--- 2. multi-row VALUES ---';
INSERT INTO books (isbn, title, author, copies) VALUES
    ('978-0321751041', 'The Art of Computer Programming', 'Donald Knuth',    1),
    ('978-1491950357', 'Building Microservices',          'Sam Newman',      2),
    ('978-0134494166', 'Clean Architecture',              'Robert C. Martin',1),
    ('978-1617294136', 'Grokking Algorithms',             'Aditya Bhargava', 3);
SELECT 'inserted ' || changes() || ' row(s) in one statement';

-- ---------------------------------------------------------------------------
-- 3. INSERT INTO ... SELECT — rows built from rows you already have.
-- ---------------------------------------------------------------------------
-- No round trip to your program. The rows never leave the database.
SELECT '';
SELECT '--- 3. INSERT INTO ... SELECT ---';
CREATE TABLE loan_archive (
    loan_id     INTEGER PRIMARY KEY,
    member_name TEXT    NOT NULL,
    book_title  TEXT    NOT NULL,
    borrowed_on TEXT    NOT NULL,
    archived_on TEXT    NOT NULL
) STRICT;

INSERT INTO loan_archive (loan_id, member_name, book_title, borrowed_on, archived_on)
SELECT l.id, m.name, b.title, l.borrowed_on, '2026-08-16'
FROM   loans l
JOIN   members m ON m.id = l.member_id
JOIN   books   b ON b.id = l.book_id
WHERE  l.returned = 1;
SELECT 'archived ' || changes() || ' returned loan(s)';

-- ---------------------------------------------------------------------------
-- 4. RETURNING — get back what the database decided.
-- ---------------------------------------------------------------------------
-- The id, the DEFAULT-filled column, the generated value: all of them are
-- decided by the database, and RETURNING hands them straight back instead of
-- making you guess or run a second SELECT that might race with somebody else.
SELECT '';
SELECT '--- 4. RETURNING ---';
.mode column
.headers on
INSERT INTO members (name, email)
VALUES ('Gita Prasad', 'gita@library.test')
RETURNING id, name, joined_on;
.mode list
.headers off
SELECT 'joined_on above was filled in by the DEFAULT, not by this statement';

-- ---------------------------------------------------------------------------
-- 5. UPSERT — insert, or update if it is already there.
-- ---------------------------------------------------------------------------
-- The catalogue feed arrives again. Two of these books are already known by
-- ISBN and one is new. Without UPSERT you would either get a UNIQUE violation
-- or you would have to ask first and then decide -- and between the asking and
-- the deciding, somebody else can insert the row.
SELECT '';
SELECT '--- 5. UPSERT: before ---';
SELECT isbn || ' copies=' || copies FROM books
WHERE isbn IN ('978-0131103627', '978-0201633610', '978-1098100964') ORDER BY isbn;

INSERT INTO books (isbn, title, author, copies) VALUES
    ('978-0131103627', 'The C Programming Language', 'Kernighan and Ritchie', 5),
    ('978-0201633610', 'Design Patterns',            'Gamma and others',      6),
    ('978-1098100964', 'Fundamentals of Data Engineering', 'Reis and Housley', 2)
ON CONFLICT(isbn) DO UPDATE SET
    copies = excluded.copies,
    title  = excluded.title;

SELECT '';
SELECT '--- 5. UPSERT: after ---';
SELECT isbn || ' copies=' || copies FROM books
WHERE isbn IN ('978-0131103627', '978-0201633610', '978-1098100964') ORDER BY isbn;
SELECT 'two rows updated, one inserted, in ONE statement and ONE trip';

-- excluded.copies is the value this INSERT WANTED to write. Plain "copies"
-- inside DO UPDATE still means the value already in the table. That single
-- distinction is the whole of UPSERT, and getting it backwards is the usual
-- first mistake.

-- ---------------------------------------------------------------------------
-- 6. ON CONFLICT DO NOTHING — the other half.
-- ---------------------------------------------------------------------------
SELECT '';
SELECT '--- 6. DO NOTHING ---';
INSERT INTO books (isbn, title, author, copies)
VALUES ('978-0131103627', 'A DIFFERENT TITLE ENTIRELY', 'Nobody', 99)
ON CONFLICT(isbn) DO NOTHING;
SELECT 'rows changed: ' || changes() || ' (the existing row was left alone)';
SELECT 'title is still: ' || (SELECT title FROM books WHERE isbn = '978-0131103627');
