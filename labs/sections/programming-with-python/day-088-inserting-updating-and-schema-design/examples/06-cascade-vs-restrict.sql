-- Day 088 lab, demonstration 6 — ON DELETE CASCADE versus ON DELETE RESTRICT,
-- and the pragma that decides whether either of them means anything.
--
--   cp library.db scratch.db
--   sqlite3 scratch.db < examples/06-cascade-vs-restrict.sql

.mode list
.headers off

-- ---------------------------------------------------------------------------
-- 0. First, the trap. Foreign keys are OFF by default.
-- ---------------------------------------------------------------------------
-- Day 87 introduced this and it is worth proving rather than believing. With
-- the pragma off, a REFERENCES clause is a comment with punctuation.
PRAGMA foreign_keys = OFF;

SELECT '--- 0. with foreign_keys OFF ---';
SELECT 'foreign_keys = ' || (SELECT * FROM pragma_foreign_keys);

BEGIN;
    -- Member 1 has loans. Deleting her should either cascade or be refused.
    -- With enforcement off it does NEITHER: the member goes, the loans stay,
    -- and they now point at a member that does not exist.
    DELETE FROM members WHERE id = 1;
    SELECT 'deleted member 1: ' || changes() || ' row(s)';
    SELECT 'her loans still present: '
           || (SELECT count(*) FROM loans WHERE member_id = 1);
    SELECT 'those loans are now orphans, and nothing objected';
ROLLBACK;

-- Prove the damage would have been silent and permanent by asking the database
-- to audit itself. This is the command to reach for after any bulk load done
-- with enforcement off.
SELECT '';
SELECT '--- 0b. the self-audit command ---';
SELECT 'foreign_key_check finds ' || count(*) || ' violation(s) right now'
FROM pragma_foreign_key_check;

-- ---------------------------------------------------------------------------
-- 1. Turn it on. Everything below behaves completely differently.
-- ---------------------------------------------------------------------------
PRAGMA foreign_keys = ON;
SELECT '';
SELECT '--- 1. with foreign_keys ON ---';
SELECT 'foreign_keys = ' || (SELECT * FROM pragma_foreign_keys);

-- ---------------------------------------------------------------------------
-- 2. ON DELETE CASCADE — the child rows go with the parent.
-- ---------------------------------------------------------------------------
-- loans.member_id is declared ON DELETE CASCADE, because a loan with no
-- borrower is not a fact about anything. Deleting the member takes the loans.
SELECT '';
SELECT '--- 2. CASCADE: deleting a member ---';
SELECT 'loans total before      = ' || (SELECT count(*) FROM loans);
SELECT 'member 3 loans before   = ' || (SELECT count(*) FROM loans WHERE member_id = 3);

BEGIN;
    DELETE FROM members WHERE id = 3;
    SELECT 'members deleted        = ' || changes();
    SELECT 'loans total after      = ' || (SELECT count(*) FROM loans);
    SELECT 'member 3 loans after   = ' || (SELECT count(*) FROM loans WHERE member_id = 3);
    SELECT 'the three child rows went with the parent, in one statement';
ROLLBACK;

SELECT 'rolled back, loans total = ' || (SELECT count(*) FROM loans);

-- Note what changes() reported: only the members row. The cascade is real but
-- it is not counted, which is exactly why a cascade you did not intend is so
-- easy to miss. The row count you read back does not mention the damage.

-- ---------------------------------------------------------------------------
-- 3. ON DELETE RESTRICT — the delete is refused.
-- ---------------------------------------------------------------------------
-- loans.book_id is declared ON DELETE RESTRICT, because deleting a book that
-- somebody is holding is a mistake, and the right response to a mistake is to
-- stop and make a person think.
--
-- The failing statement is run by the test harness so its exact error message
-- can be captured. Here we show the safe question to ask BEFORE deleting.
SELECT '';
SELECT '--- 3. RESTRICT: the question to ask first ---';
SELECT 'book 8 is referenced by ' || count(*) || ' loan(s)'
FROM loans WHERE book_id = 8;
SELECT 'so DELETE FROM books WHERE id = 8 will be refused';

-- A book nobody has borrowed deletes without complaint. Same rule, same table,
-- different data: RESTRICT only refuses when there is actually a child row.
INSERT INTO books (isbn, title, author, copies)
VALUES ('978-0000000000', 'Never Borrowed', 'Nobody At All', 1);

BEGIN;
    DELETE FROM books WHERE isbn = '978-0000000000';
    SELECT 'unreferenced book deleted: ' || changes() || ' row(s), no complaint';
ROLLBACK;

-- ---------------------------------------------------------------------------
-- 4. Choosing between them.
-- ---------------------------------------------------------------------------
-- The question is never "which is safer". It is "what does the child row MEAN
-- once the parent is gone?"
--
--   If the child is meaningless without the parent   -> CASCADE.
--     A loan without a borrower. An order line without an order.
--
--   If the child is evidence that the parent is busy -> RESTRICT.
--     A book that is out on loan. An account with a balance.
--
--   If the child survives but loses a detail         -> SET NULL.
--     An article whose author's account was closed.
--
-- Getting this wrong in the CASCADE direction is the expensive one, because it
-- deletes rows nobody asked about and reports only the row you named.
-- Final state. Every destructive step above was rolled back, so members and
-- loans are exactly as they started. Books is 9 rather than 8 because the
-- 'Never Borrowed' row was inserted OUTSIDE a transaction, on purpose: it is
-- the one change in this script that was meant to survive.
SELECT '';
SELECT '--- 4. final state ---';
SELECT 'members=' || (SELECT count(*) FROM members)
       || ' books=' || (SELECT count(*) FROM books)
       || ' loans=' || (SELECT count(*) FROM loans);
SELECT 'members and loans unchanged; books +1 from the deliberate insert';
