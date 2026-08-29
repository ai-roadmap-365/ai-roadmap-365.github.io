-- Day 088 lab, demonstration 7 — the create-new-table, copy, drop, rename
-- dance: how to make a schema change that ALTER TABLE cannot make.
--
--   cp library.db scratch.db
--   sqlite3 scratch.db < examples/07-table-rebuild.sql
--
-- The goal: add a constraint to loans saying a loan may not be due more than
-- 90 days after it was borrowed. There is no portable ALTER TABLE that adds a
-- CHECK constraint, so the documented procedure is to build the table you
-- wanted, move the rows into it, and swap the names.
--
-- Every step below is inside ONE transaction. That is not a nicety. Between
-- "DROP TABLE loans" and "ALTER TABLE loans_new RENAME TO loans" there is a
-- moment when your database has no loans table at all. If the power fails
-- there and the work was not in a transaction, you have destroyed the table.
-- Inside a transaction that moment is invisible to everyone, including you.

.mode list
.headers off

SELECT '--- before ---';
SELECT 'loans = ' || count(*) FROM loans;
SELECT 'schema still says: ' ||
       CASE WHEN (SELECT sql FROM sqlite_schema WHERE name = 'loans')
                 LIKE '%90%' THEN 'has the 90-day rule'
            ELSE 'no 90-day rule' END;

-- ---------------------------------------------------------------------------
-- Step 0. Turn foreign keys OFF for the rebuild.
-- ---------------------------------------------------------------------------
-- This is the step everyone skips and it is the one that bites. With
-- enforcement on, DROP TABLE loans would fire the delete rules of anything
-- referencing loans. The documented procedure turns enforcement off, does the
-- swap, and turns it back on -- and it must be done OUTSIDE the transaction,
-- because PRAGMA foreign_keys is a no-op inside one.
PRAGMA foreign_keys = OFF;

BEGIN;

-- ---------------------------------------------------------------------------
-- Step 1. Create the table you actually wanted, under a temporary name.
-- ---------------------------------------------------------------------------
-- Copy the ENTIRE definition, not just the new bit. Every column, every
-- default, every existing constraint, every foreign key. Anything you forget
-- to type here is silently dropped from your schema forever.
CREATE TABLE loans_new (
    id          INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(id)   ON DELETE RESTRICT,
    member_id   INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    borrowed_on TEXT    NOT NULL DEFAULT (date('now')),
    due_on      TEXT    NOT NULL,
    returned    INTEGER NOT NULL DEFAULT 0 CHECK (returned IN (0, 1)),

    CHECK (due_on >= borrowed_on),
    -- The whole point of this rebuild:
    CHECK (julianday(due_on) - julianday(borrowed_on) <= 90)
) STRICT;

-- ---------------------------------------------------------------------------
-- Step 2. Copy the rows across, naming every column explicitly.
-- ---------------------------------------------------------------------------
-- If any existing row violates the new constraint, THIS is where it fails, and
-- the whole transaction rolls back. That is the behaviour you want: you find
-- out that your data disagrees with your new rule before you have committed to
-- the rule, not afterwards.
INSERT INTO loans_new (id, book_id, member_id, borrowed_on, due_on, returned)
SELECT id, book_id, member_id, borrowed_on, due_on, returned FROM loans;
SELECT 'copied ' || changes() || ' row(s) into the new table';

-- ---------------------------------------------------------------------------
-- Step 3. Drop the old table.
-- ---------------------------------------------------------------------------
DROP TABLE loans;

-- ---------------------------------------------------------------------------
-- Step 4. Rename the new table into the old name.
-- ---------------------------------------------------------------------------
ALTER TABLE loans_new RENAME TO loans;

COMMIT;

-- ---------------------------------------------------------------------------
-- Step 5. Check the foreign keys still resolve, THEN turn enforcement back on.
-- ---------------------------------------------------------------------------
-- Enforcement was off for the whole rebuild, so nothing was checking. This is
-- the audit that tells you whether the rebuild left anything dangling.
SELECT '';
SELECT '--- after the rebuild ---';
SELECT 'foreign_key_check violations: ' || count(*) FROM pragma_foreign_key_check;

PRAGMA foreign_keys = ON;

SELECT 'loans = ' || (SELECT count(*) FROM loans);
SELECT 'schema now says: ' ||
       CASE WHEN (SELECT sql FROM sqlite_schema WHERE name = 'loans')
                 LIKE '%90%' THEN 'has the 90-day rule'
            ELSE 'no 90-day rule' END;

-- The foreign keys survived the rename, because they were retyped in step 1.
SELECT 'foreign keys on the rebuilt table: '
       || (SELECT count(*) FROM pragma_foreign_key_list('loans'));

-- The new rule is live. A 200-day loan is now impossible; the harness runs one
-- and captures the error. A 60-day loan is still fine.
INSERT INTO loans (book_id, member_id, borrowed_on, due_on)
VALUES (1, 1, '2026-08-16', '2026-10-15');
SELECT 'a 60-day loan still inserts fine: ' || changes() || ' row(s)';
SELECT 'loans = ' || (SELECT count(*) FROM loans);
