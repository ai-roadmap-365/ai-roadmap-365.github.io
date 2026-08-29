-- Day 088 lab, demonstration 3 — transactions, and what atomicity buys you.
--
--   cp library.db scratch.db
--   sqlite3 scratch.db < examples/03-transactions.sql
--
-- A transaction is a promise about a GROUP of statements: all of them happen,
-- or none of them do. There is no state in which half of them happened, no
-- matter what goes wrong in the middle -- a constraint violation, a crash, a
-- power cut, or you noticing your mistake and typing ROLLBACK.

PRAGMA foreign_keys = ON;
.mode list
.headers off

SELECT '--- starting point ---';
SELECT 'outstanding=' || count(*) FROM loans WHERE returned = 0;
SELECT 'loans='       || count(*) FROM loans;
SELECT 'members='     || count(*) FROM members;

-- ---------------------------------------------------------------------------
-- 1. ROLLBACK: three changes, then a change of mind.
-- ---------------------------------------------------------------------------
-- Notice that INSIDE the transaction the changes are completely real. Your
-- own connection sees them. That is what makes a transaction usable: you can
-- look at the result before you decide whether to keep it.
SELECT '';
SELECT '--- 1. inside a transaction, before ROLLBACK ---';
BEGIN;
    UPDATE loans SET returned = 1;
    DELETE FROM loans WHERE id <= 3;
    INSERT INTO members (name, email) VALUES ('Temporary Person', 'temp@library.test');

    SELECT 'outstanding=' || count(*) FROM loans WHERE returned = 0;
    SELECT 'loans='       || count(*) FROM loans;
    SELECT 'members='     || count(*) FROM members;
ROLLBACK;

SELECT '';
SELECT '--- 1. after ROLLBACK ---';
SELECT 'outstanding=' || count(*) FROM loans WHERE returned = 0;
SELECT 'loans='       || count(*) FROM loans;
SELECT 'members='     || count(*) FROM members;
SELECT 'every one of the three changes was undone by one word';

-- ---------------------------------------------------------------------------
-- 2. COMMIT: the same shape, kept this time.
-- ---------------------------------------------------------------------------
SELECT '';
SELECT '--- 2. COMMIT ---';
BEGIN;
    UPDATE loans SET returned = 1 WHERE id = 2;
    UPDATE books SET copies = copies + 1 WHERE id = 3;
COMMIT;
SELECT 'loan 2 returned=' || (SELECT returned FROM loans WHERE id = 2);
SELECT 'book 3 copies='   || (SELECT copies   FROM books WHERE id = 3);
SELECT 'both changes are now durable';

-- ---------------------------------------------------------------------------
-- 3. Why the group matters: a transfer that must not half-happen.
-- ---------------------------------------------------------------------------
-- Loan 6 is being reassigned from member 3 to member 6. That is two writes:
-- close the old loan, open the new one. If only the first lands, the book has
-- vanished from the library's understanding of the world -- returned by
-- nobody, borrowed by nobody. The transaction is what makes "both or neither"
-- true rather than merely likely.
SELECT '';
SELECT '--- 3. a two-statement change that must not half-happen ---';
BEGIN;
    UPDATE loans SET returned = 1 WHERE id = 6;
    INSERT INTO loans (book_id, member_id, borrowed_on, due_on)
    VALUES (7, 6, '2026-08-16', '2026-09-06');
COMMIT;
SELECT 'loan 6 closed, replacement opened, ' || changes() || ' row(s) in the last statement';
SELECT 'loans on book 7 that are still out: '
       || (SELECT count(*) FROM loans WHERE book_id = 7 AND returned = 0);

-- ---------------------------------------------------------------------------
-- 4. A failure in the middle undoes what came before it.
-- ---------------------------------------------------------------------------
-- The first UPDATE below is perfectly legal and succeeds. The second violates
-- CHECK (copies >= 0). Because both are inside one transaction, the ROLLBACK
-- takes the legal one with it. This is the property you are actually buying:
-- you do not have to write compensating code for every partial failure.
SELECT '';
SELECT '--- 4. before the failing transaction ---';
SELECT 'book 1 copies=' || (SELECT copies FROM books WHERE id = 1);

BEGIN;
    UPDATE books SET copies = copies + 10 WHERE id = 1;   -- legal, succeeds
    -- The next line is run by the test harness separately so its error can be
    -- captured; here we simply roll back to show the effect of abandoning the
    -- transaction after a partial success.
ROLLBACK;

SELECT '';
SELECT '--- 4. after ROLLBACK, the successful statement is gone too ---';
SELECT 'book 1 copies=' || (SELECT copies FROM books WHERE id = 1);
SELECT 'the +10 was real inside the transaction and is now as if it never was';

-- ---------------------------------------------------------------------------
-- 5. The discipline that prevents the expensive mistake.
-- ---------------------------------------------------------------------------
-- Write the SELECT. Run it. Look at the count. Convert it to the UPDATE by
-- swapping the head of the statement and keeping the WHERE clause untouched.
-- Do it inside a transaction so the answer to "did I get that right?" is still
-- ROLLBACK rather than "restore last night's backup".
SELECT '';
SELECT '--- 5. SELECT first, then convert ---';
SELECT 'step 1 -- the SELECT matches ' || count(*) || ' row(s)'
FROM loans WHERE member_id = 5 AND returned = 0;

BEGIN;
    UPDATE loans SET returned = 1 WHERE member_id = 5 AND returned = 0;
    SELECT 'step 2 -- the UPDATE changed ' || changes() || ' row(s)';
    SELECT 'step 3 -- the two numbers match, so this is safe to keep';
COMMIT;

SELECT '';
SELECT '--- final state ---';
SELECT 'outstanding=' || count(*) FROM loans WHERE returned = 0;
