-- Day 085 — a small, deliberately reproducible dataset for library.db
--
-- Apply it with:   sqlite3 library.db < seed.sql
--
-- Every date here is a literal. Nothing uses date('now'), and that is a
-- deliberate choice: a fixture that depends on today's date produces a
-- capture that stops matching tomorrow. The lab's "today" is 2026-08-16,
-- written down rather than looked up.

PRAGMA foreign_keys = ON;

BEGIN;   -- one transaction: either every row below lands, or none does

INSERT INTO books (book_id, title, author, year, copies) VALUES
    (1, 'A Relational Model of Data',      'Edgar F. Codd',      1970, 2),
    (2, 'The Art of Computer Programming', 'Donald E. Knuth',    1968, 1),
    (3, 'Structure and Interpretation',    'Abelson and Sussman', 1985, 3),
    (4, 'The Mythical Man-Month',          'Frederick P. Brooks', 1975, 1),
    (5, 'A Discipline of Programming',     'Edsger W. Dijkstra',  1976, 1),
    (6, 'Notes on Data Storage',           'Anonymous',           NULL, 4);
    -- Row 6 has a NULL year. "We do not know" is a different fact from
    -- "the year is zero", and the schema lets us say so.

INSERT INTO members (member_id, name, email, joined_on) VALUES
    (1, 'Ada Lovelace',   'ada@library.invalid',     '2025-01-14'),
    (2, 'Grace Hopper',   'grace@library.invalid',   '2025-03-02'),
    (3, 'Alan Turing',    'alan@library.invalid',    '2026-02-20'),
    (4, 'Barbara Liskov', 'barbara@library.invalid', '2026-07-30');

INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, due_on, returned_on) VALUES
    -- returned, on time
    (1, 2, 1, '2026-05-01', '2026-05-22', '2026-05-19'),
    (2, 3, 2, '2026-06-10', '2026-07-01', '2026-06-28'),
    -- still out, not yet due
    (3, 1, 3, '2026-08-10', '2026-08-31', NULL),
    (4, 6, 4, '2026-08-14', '2026-09-04', NULL),
    -- still out, OVERDUE as of 2026-08-16
    (5, 4, 1, '2026-06-01', '2026-06-22', NULL),
    (6, 5, 2, '2026-07-05', '2026-07-26', NULL),
    (7, 3, 1, '2026-07-20', '2026-08-10', NULL);

COMMIT;
