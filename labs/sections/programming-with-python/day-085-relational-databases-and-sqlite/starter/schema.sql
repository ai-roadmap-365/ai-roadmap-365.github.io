-- Day 085 starter — build library.db yourself.
--
-- The books table below is complete. Read it as a worked model: every line is
-- either a fact the database will store or a rule it will refuse to break.
-- Then write the two tables underneath it.
--
-- Apply what you have at any point with:
--
--     sqlite3 library.db < schema.sql
--     sqlite3 library.db ".schema"
--
-- As shipped, this file applies cleanly and creates ONE table. That is on
-- purpose: you should be able to run it, see something work, and then add to
-- it. Delete library.db and re-apply after every change.
--
-- Eight numbered exercises. Each one names the exact thing to write and the
-- check in tests/run_tests.sh that will confirm it.

PRAGMA foreign_keys = ON;

-- ===========================================================================
-- The worked model.
-- ===========================================================================
CREATE TABLE books (
    book_id  INTEGER PRIMARY KEY,
    title    TEXT    NOT NULL,
    author   TEXT    NOT NULL,
    year     INTEGER,
    copies   INTEGER NOT NULL DEFAULT 1 CHECK (copies >= 0)
);

-- ===========================================================================
-- EXERCISE 1 — the members table.
--
-- Write CREATE TABLE members with four columns:
--     member_id  INTEGER PRIMARY KEY
--     name       TEXT, never NULL
--     email      TEXT, never NULL, and UNIQUE
--     joined_on  TEXT, never NULL
--
-- Checked by: "members has a primary key and a unique email"
-- ===========================================================================


-- ===========================================================================
-- EXERCISE 2 — the email is a CANDIDATE KEY, not the primary key.
--
-- Nothing to type here. Write your answer as a comment on the line below:
-- why did we choose member_id as the primary key when email would also
-- identify the row uniquely? (Hint: what happens to every loan row when
-- somebody changes their address?)
--
-- your answer:
-- ===========================================================================


-- ===========================================================================
-- EXERCISE 3 — the loans table, and the constraint that is the whole point.
--
-- Write CREATE TABLE loans with:
--     loan_id     INTEGER PRIMARY KEY
--     book_id     INTEGER, never NULL, REFERENCES books(book_id)
--     member_id   INTEGER, never NULL, REFERENCES members(member_id)
--     borrowed_on TEXT, never NULL
--     due_on      TEXT, never NULL
--     returned_on TEXT, nullable — NULL means "still out"
--
-- The two REFERENCES clauses are the reason this lab exists. They are what
-- makes a typo'd member id an error at write time rather than a mystery
-- three months later.
--
-- Checked by: "loans refuses a member_id that does not exist"
-- ===========================================================================


-- ===========================================================================
-- EXERCISE 4 — a CHECK constraint the schema enforces for you.
--
-- Add a table-level CHECK to loans so that due_on can never be earlier than
-- borrowed_on. Write it inside the CREATE TABLE above, after the last column:
--
--     CHECK (due_on >= borrowed_on)
--
-- Then convince yourself it works by trying to insert a loan due yesterday.
--
-- Checked by: "loans refuses a due date before the borrow date"
-- ===========================================================================


-- ===========================================================================
-- EXERCISE 5 — an index, and what it is not.
--
-- Add:  CREATE INDEX loans_by_member ON loans(member_id);
--
-- Then write, as a comment, the answer to this: does adding an index change
-- any answer the database gives? If not, what does it change?
--
-- your answer:
--
-- Checked by: "an index named loans_by_member exists"
-- ===========================================================================


-- ===========================================================================
-- EXERCISE 6 — a STRICT table, and what it buys you.
--
-- Add a second, separate table:
--
--     CREATE TABLE readings (
--         reading_id INTEGER PRIMARY KEY,
--         book_id    INTEGER NOT NULL REFERENCES books(book_id),
--         pages      INTEGER NOT NULL
--     ) STRICT;
--
-- Then try to insert the text 'lots' into pages in both this table and a
-- non-STRICT one, and watch only one of them refuse.
--
-- Checked by: "readings is declared STRICT and refuses a text page count"
-- ===========================================================================


-- ===========================================================================
-- EXERCISE 7 — seed your database.
--
-- Write INSERT statements for at least three books, two members and three
-- loans, wrapped in a single BEGIN; ... COMMIT; so that either all of them
-- land or none does. At least one loan must be unreturned and overdue as of
-- 2026-08-16, so exercise 8 has something to find.
--
-- Checked by: "the seeded database has books, members and loans"
-- ===========================================================================


-- ===========================================================================
-- EXERCISE 8 — the question the JSON file could not answer cheaply.
--
-- Write, as a comment below, one SELECT that returns every loan still out and
-- overdue as of 2026-08-16. Then run it in the shell:
--
--     sqlite3 library.db ".mode box" ".headers on"
--
-- and paste your statement at the sqlite> prompt.
--
-- your query:
--
-- Checked by: "the overdue query returns only unreturned, past-due loans"
-- ===========================================================================
