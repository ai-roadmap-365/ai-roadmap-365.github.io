-- Day 085 — the writes the database refuses, and the transaction that undoes
-- itself. This is what the JSON file could never do.
--
-- Run it:  sqlite3 library.db < constraints_demo.sql
--
-- EXPECT ERRORS. Every "Runtime error" below is the point of the file: the
-- engine rejecting a write that would have made the data untrue. The shell
-- reports each one, keeps going, and exits non-zero at the end. An exit code
-- of 1 here is success.

PRAGMA foreign_keys = ON;

.mode box
.headers on

.print '=== 1. A typo in a member id. There is no member 999. ==='
INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, due_on)
VALUES (99, 1, 999, '2026-08-16', '2026-09-06');

.print ''
.print '=== 2. A loan of a book that does not exist ==='
INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, due_on)
VALUES (98, 404, 1, '2026-08-16', '2026-09-06');

.print ''
.print '=== 3. A member with no name ==='
INSERT INTO members (member_id, name, email, joined_on)
VALUES (9, NULL, 'nobody@library.invalid', '2026-08-16');

.print ''
.print '=== 4. A second member with an address already in use ==='
INSERT INTO members (member_id, name, email, joined_on)
VALUES (10, 'Impostor', 'ada@library.invalid', '2026-08-16');

.print ''
.print '=== 5. A negative number of copies ==='
UPDATE books SET copies = -1 WHERE book_id = 1;

.print ''
.print '=== 6. A loan due before it was borrowed ==='
INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, due_on)
VALUES (97, 1, 1, '2026-08-16', '2026-08-01');

.print ''
.print '=== 7. The same primary key twice ==='
INSERT INTO books (book_id, title, author) VALUES (1, 'Duplicate', 'Nobody');

.print ''
.print '=== After seven refused writes, the data is exactly as it was ==='
SELECT
    (SELECT count(*) FROM books)   AS books,
    (SELECT count(*) FROM members) AS members,
    (SELECT count(*) FROM loans)   AS loans,
    (SELECT copies FROM books WHERE book_id = 1) AS copies_of_book_1;

.print ''
.print '=== 8. Atomicity: two writes, one transaction, one mistake ==='
.print 'Borrowing a book is really two facts: a new loan row, and one fewer'
.print 'copy on the shelf. Neither is true on its own.'
BEGIN;
INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, due_on)
VALUES (50, 3, 4, '2026-08-16', '2026-09-06');
UPDATE books SET copies = copies - 1 WHERE book_id = 3;
.print 'inside the transaction:'
SELECT (SELECT count(*) FROM loans) AS loans, (SELECT copies FROM books WHERE book_id = 3) AS copies_of_book_3;
ROLLBACK;
.print 'after ROLLBACK — the A in ACID, and it is all or nothing:'
SELECT (SELECT count(*) FROM loans) AS loans, (SELECT copies FROM books WHERE book_id = 3) AS copies_of_book_3;

.print ''
.print '=== 9. The same transaction, committed this time ==='
BEGIN;
INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, due_on)
VALUES (50, 3, 4, '2026-08-16', '2026-09-06');
UPDATE books SET copies = copies - 1 WHERE book_id = 3;
COMMIT;
SELECT (SELECT count(*) FROM loans) AS loans, (SELECT copies FROM books WHERE book_id = 3) AS copies_of_book_3;

.print ''
.print '=== 10. Put it back, so the lab is repeatable ==='
BEGIN;
DELETE FROM loans WHERE loan_id = 50;
UPDATE books SET copies = copies + 1 WHERE book_id = 3;
COMMIT;
SELECT (SELECT count(*) FROM loans) AS loans, (SELECT copies FROM books WHERE book_id = 3) AS copies_of_book_3;
