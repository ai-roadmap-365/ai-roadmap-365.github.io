-- Day 088 lab, demonstration 4 — UPDATE properly, DELETE carefully, and the
-- soft delete that is usually what you actually wanted.
--
--   cp library.db scratch.db
--   sqlite3 scratch.db < examples/04-update-and-delete.sql

PRAGMA foreign_keys = ON;
.mode list
.headers off

-- ---------------------------------------------------------------------------
-- 1. UPDATE with an EXPRESSION, not a literal.
-- ---------------------------------------------------------------------------
-- "copies = copies + 1" is computed by the database from the value that is
-- there at the moment of the write. "copies = 4" is computed by YOU, from a
-- value you read earlier, which may already be stale by the time you write it.
-- Between your SELECT and your UPDATE, somebody else can change the row. The
-- expression form has no gap for them to change it in.
SELECT '--- 1. UPDATE with an expression ---';
SELECT 'book 5 copies before = ' || (SELECT copies FROM books WHERE id = 5);
UPDATE books SET copies = copies + 2 WHERE id = 5;
SELECT 'book 5 copies after  = ' || (SELECT copies FROM books WHERE id = 5);
SELECT 'the database did the arithmetic, so no read-then-write gap existed';

-- ---------------------------------------------------------------------------
-- 2. UPDATE with a SUBQUERY — and a first taste of denormalization.
-- ---------------------------------------------------------------------------
-- We add a counter column to members. This value is DERIVED: it can always be
-- recomputed from loans, so storing it is a deliberate duplication. It buys a
-- fast answer to "how many loans has this member had?" and it costs you the
-- obligation to keep it true forever. That trade is the whole of
-- denormalization, and section 7 of the lesson is about when to accept it.
SELECT '';
SELECT '--- 2. UPDATE from a correlated subquery ---';
ALTER TABLE members ADD COLUMN loan_count INTEGER NOT NULL DEFAULT 0;

UPDATE members
SET    loan_count = (SELECT count(*) FROM loans WHERE loans.member_id = members.id);
SELECT 'updated ' || changes() || ' member row(s)';

.mode column
.headers on
SELECT id, name, loan_count FROM members ORDER BY id;
.mode list
.headers off

-- Check it against the truth it was derived from. If these two ever disagree,
-- the stored copy is lying, and nothing in the schema will tell you.
SELECT '';
SELECT 'stored total  = ' || (SELECT sum(loan_count) FROM members);
SELECT 'derived total = ' || (SELECT count(*) FROM loans);

-- ---------------------------------------------------------------------------
-- 3. DELETE, and why it is the least recoverable thing here.
-- ---------------------------------------------------------------------------
-- An UPDATE that goes wrong leaves rows you can inspect and often repair. A
-- DELETE that goes wrong leaves nothing at all. The row is not marked, not
-- hidden, not in a bin -- it is gone, and the only copy is your backup.
SELECT '';
SELECT '--- 3. a real DELETE ---';
SELECT 'loans before = ' || count(*) FROM loans;
DELETE FROM loans WHERE returned = 1 AND borrowed_on < '2026-06-01';
SELECT 'deleted ' || changes() || ' row(s)';
SELECT 'loans after  = ' || count(*) FROM loans;
SELECT 'those rows are not recoverable from this database';

-- ---------------------------------------------------------------------------
-- 4. Soft delete — the alternative you usually want.
-- ---------------------------------------------------------------------------
-- Instead of removing the row, mark it. The row stays, so foreign keys still
-- resolve, history still adds up, and an accident is one UPDATE away from
-- being undone. The cost is real and worth saying out loud: every query that
-- reads this table must now remember the filter, and the day somebody forgets
-- it, deleted members reappear in a report.
SELECT '';
SELECT '--- 4. soft delete ---';
ALTER TABLE members ADD COLUMN deleted_at TEXT;

-- Farida (id 6) leaves the library. We do not remove her.
UPDATE members SET deleted_at = '2026-08-16' WHERE id = 6;
SELECT 'marked ' || changes() || ' member(s) as deleted';

SELECT 'rows physically present = ' || (SELECT count(*) FROM members);
SELECT 'rows a normal query should see = '
       || (SELECT count(*) FROM members WHERE deleted_at IS NULL);

-- Her loans are still attached to a member that still exists. Had we run a
-- real DELETE, ON DELETE CASCADE would have taken her loan history with her --
-- correct behaviour, and completely irreversible.
SELECT 'her loans still resolve: '
       || (SELECT count(*) FROM loans WHERE member_id = 6) || ' row(s)';

-- Undo. This is the part a hard DELETE cannot offer at any price.
UPDATE members SET deleted_at = NULL WHERE id = 6;
SELECT 'undeleted, visible members back to '
       || (SELECT count(*) FROM members WHERE deleted_at IS NULL);

-- ---------------------------------------------------------------------------
-- 5. The safest destructive habit of all.
-- ---------------------------------------------------------------------------
-- Every one of the statements above could have been written wrong. The routine
-- that catches it costs about fifteen seconds:
--
--   1. Write it as a SELECT with the exact WHERE clause you intend.
--   2. Run it. Read the row count. Is that the number you expected?
--   3. Keep the WHERE clause byte-for-byte and swap the head of the statement.
--   4. Do it inside BEGIN ... so that step 5 is possible.
--   5. Check changes(). If it does not match step 2, ROLLBACK.
SELECT '';
SELECT '--- 5. the routine, once more, on a DELETE ---';
SELECT 'step 1-2 -- SELECT matches ' || count(*) || ' row(s)'
FROM loans WHERE member_id = 4 AND returned = 1;

BEGIN;
    DELETE FROM loans WHERE member_id = 4 AND returned = 1;
    SELECT 'step 5   -- DELETE changed ' || changes() || ' row(s)';
ROLLBACK;
SELECT 'rolled back anyway, because this was only a demonstration';
SELECT 'loans still = ' || (SELECT count(*) FROM loans);
