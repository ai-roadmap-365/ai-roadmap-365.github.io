-- Day 087 · Step 4 — the SQLite fact that surprises everybody.
--
-- SQLite compiles foreign-key support in, but leaves ENFORCEMENT OFF by
-- default, for backwards compatibility. Every connection starts with it off
-- and must turn it on for itself. A REFERENCES clause you never enforce is a
-- comment with punctuation.
--
-- This script proves it twice: once by inserting a loan pointing at a member
-- who does not exist, and once by trying the identical insert with the pragma
-- on. Run it as one shell session so both halves share ONE connection:
--
--   sqlite3 library.db < examples/04_foreign_keys.sql

.headers on
.mode column

.print ''
.print '--- 1. what the pragma says on a brand-new connection ---'
SELECT 'PRAGMA foreign_keys' AS setting, foreign_keys AS value FROM pragma_foreign_keys;

.print ''
.print '--- 2. insert a loan for member 999, who does not exist ---'
INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, returned_on)
VALUES (900, 101, 999, '2026-08-16', NULL);
SELECT changes() AS rows_inserted;

.print ''
.print '--- 3. the orphan row is really there ---'
SELECT loan_id, book_id, member_id FROM loans WHERE loan_id = 900;

.print ''
.print '--- 4. and the database will tell you, if you ask it to check ---'
PRAGMA foreign_key_check;

.print ''
.print '--- 5. clean up, enable enforcement, and try the identical insert ---'
DELETE FROM loans WHERE loan_id = 900;
PRAGMA foreign_keys = ON;
SELECT 'PRAGMA foreign_keys' AS setting, foreign_keys AS value FROM pragma_foreign_keys;

.print ''
.print '--- 6. the same statement, now rejected ---'
INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, returned_on)
VALUES (900, 101, 999, '2026-08-16', NULL);
