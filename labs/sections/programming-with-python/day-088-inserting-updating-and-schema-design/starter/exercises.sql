-- YOUR WORK — six SQL exercises on changing data without destroying it.
--
-- Build yourself a throwaway database first, so that every mistake is free:
--
--   sqlite3 practice.db < examples/seed.sql
--   cp practice.db practice-backup.db
--   sqlite3 practice.db
--
-- Then work through the exercises below. After each one, check your answer
-- against the "expected" line in the comment. The finished versions of all six
-- are spread across examples/01 to examples/07 -- try each yourself first.
--
-- The habit this file is really teaching: before every UPDATE and every
-- DELETE, write the SELECT, run it, and read the row count.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- EXERCISE 1 — measure the damage of the missing WHERE clause.
-- ---------------------------------------------------------------------------
-- On a COPY of the database, run `UPDATE loans SET returned = 1;` with no
-- WHERE clause, and report how many rows it changed using changes().
--
-- Then work out, from the seed data, how many of those rows were changed
-- WRONGLY -- that is, how many were correct before and are now wrong.
--
-- expected: 12 rows changed, 8 of them wrongly (4 were already returned)

-- your answer here


-- ---------------------------------------------------------------------------
-- EXERCISE 2 — the SELECT-first discipline.
-- ---------------------------------------------------------------------------
-- Loan 4 has come back. Write the SELECT that identifies exactly the rows you
-- intend to change, run it, then convert it into the UPDATE by keeping the
-- WHERE clause byte-for-byte and changing only the head of the statement.
-- Do it inside BEGIN ... COMMIT and check changes() before committing.
--
-- expected: SELECT matches 1 row, UPDATE changes 1 row

-- your answer here


-- ---------------------------------------------------------------------------
-- EXERCISE 3 — UPSERT.
-- ---------------------------------------------------------------------------
-- The catalogue feed sends this row again with a new copy count:
--
--   isbn 978-0262033848, title 'Introduction to Algorithms', copies 9
--
-- Write ONE statement that inserts it if the ISBN is new and updates the copy
-- count if it is not. Use ON CONFLICT(isbn) DO UPDATE, and use excluded.copies
-- rather than copies -- then work out, in a comment, what the statement would
-- have done if you had written plain `copies` instead.
--
-- expected: 1 row changed, book 3 now has 9 copies

-- your answer here


-- ---------------------------------------------------------------------------
-- EXERCISE 4 — prove a rollback changes nothing.
-- ---------------------------------------------------------------------------
-- Take a checksum of the database file. Then open a transaction, run three
-- destructive statements of your choosing, confirm inside the transaction that
-- they took effect, ROLLBACK, and take the checksum again.
--
--   shasum -a 256 practice.db
--
-- expected: the two checksums are identical, character for character

-- your answer here


-- ---------------------------------------------------------------------------
-- EXERCISE 5 — make each constraint fire.
-- ---------------------------------------------------------------------------
-- Write one INSERT or UPDATE that is rejected by each of these, and record the
-- exact error message SQLite gives you:
--
--   a) NOT NULL on members.name
--   b) UNIQUE on books.isbn
--   c) CHECK (copies >= 0) on books
--   d) CHECK (due_on >= borrowed_on) on loans
--   e) the FOREIGN KEY on loans.book_id
--   f) STRICT type checking on books.copies
--
-- expected: six different messages, each naming the constraint that fired

-- your answer here


-- ---------------------------------------------------------------------------
-- EXERCISE 6 — a rebuild of your own.
-- ---------------------------------------------------------------------------
-- Add a constraint to `books` saying an ISBN must be at least 10 characters.
-- ALTER TABLE cannot portably add a CHECK, so use the documented rebuild:
-- turn foreign keys off, BEGIN, create books_new with the full definition plus
-- the new rule, copy the rows, drop books, rename books_new to books, COMMIT,
-- run PRAGMA foreign_key_check, turn foreign keys back on.
--
-- Two things to get right, and both are easy to miss:
--   * loans references books(id). What happens to that reference across the
--     drop and rename? Check it with PRAGMA foreign_key_list('loans').
--   * the full definition means EVERY column and EVERY existing constraint.
--     Whatever you forget to retype is gone.
--
-- expected: 9 books preserved, foreign_key_check reports 0 violations,
--           and an INSERT with isbn '123' is now refused

-- your answer here
