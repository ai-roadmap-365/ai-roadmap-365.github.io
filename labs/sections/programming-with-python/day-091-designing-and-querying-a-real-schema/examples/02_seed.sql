-- Day 091 — seed data for the Fenwick Road brief.
--
-- The books and the authors are real published works and their real authors.
-- EVERYTHING ELSE IS INVENTED: the library does not exist, the six members do
-- not exist, their email addresses are on the reserved .invalid domain so they
-- can never be delivered to anybody, and no real borrowing record was used.
-- A library loan record ties a named person to what they read, which is
-- exactly the kind of data you do not practise on.
--
-- The data deliberately contains the awkward cases, because a seed where every
-- question has a tidy answer teaches nothing:
--
--   * a member who has never borrowed anything      (Eli Nakamura)
--   * a member who has left but still owes money    (Farida Haddad)
--   * a book with two authors and a book with three (101 and 103)
--   * a book with no ISBN, printed before they existed (108, Frankenstein)
--   * an author whose year of birth is not published (Julie Sussman)
--   * a withdrawn book that still has to resolve in history (107)
--   * two overdue loans and two that are out but not yet due
--   * a reservation queue three deep, plus a cancelled and a collected one
--
-- The ISBN-13 values below are the identifiers of widely held editions of
-- these works, and each one passes the ISBN-13 checksum. They are here to give
-- the natural-key discussion something real to argue about; if you are
-- cataloguing your own shelf, take the numbers off the books in front of you
-- rather than from this file.

PRAGMA foreign_keys = ON;

BEGIN;

-- Categories: a tree. Fiction > Science Fiction > Cyberpunk is three levels
-- deep, which is what makes question 9 need recursion rather than a join.
INSERT INTO categories (category_id, name, parent_id) VALUES
  (1, 'Fiction',              NULL),
  (2, 'Non-fiction',          NULL),
  (3, 'Science Fiction',      1),
  (4, 'Cyberpunk',            3),
  (5, 'Gothic',               1),
  (6, 'Computing',            2),
  (7, 'Programming',          6),
  (8, 'Software Engineering', 6);

INSERT INTO authors (author_id, name, birth_year) VALUES
  (1,  'Brian W. Kernighan',      1942),
  (2,  'Dennis M. Ritchie',       1941),
  (3,  'Frederick P. Brooks Jr.', 1931),
  (4,  'Harold Abelson',          1947),
  (5,  'Gerald Jay Sussman',      1947),
  (6,  'Julie Sussman',           NULL),   -- not published; NULL means unknown
  (7,  'Rob Pike',                1956),
  (8,  'Ursula K. Le Guin',       1929),
  (9,  'William Gibson',          1948),
  (10, 'Donald E. Knuth',         1938),
  (11, 'Mary Shelley',            1797);

INSERT INTO books
  (book_id, isbn13, title, published_year, category_id, acquisition_cost_pence, withdrawn_at)
VALUES
  (101, '9780131103627', 'The C Programming Language',                        1978, 7, 3499, NULL),
  (102, '9780201835953', 'The Mythical Man-Month',                            1975, 8, 2899, NULL),
  (103, '9780262510875', 'Structure and Interpretation of Computer Programs',  1985, 7, 5250, NULL),
  (104, '9780201615869', 'The Practice of Programming',                        1999, 7, 3199, NULL),
  (105, '9780441478125', 'The Left Hand of Darkness',                          1969, 3,  899, NULL),
  (106, '9780441569595', 'Neuromancer',                                        1984, 4,  999, NULL),
  -- Withdrawn: off the shelves, still referenced by nothing yet, still a row.
  (107, '9780201896831', 'The Art of Computer Programming, Volume 1',          1968, 7, 6995, '2026-06-01T10:00:00Z'),
  -- Printed in 1818. There is no ISBN, and no honest value to put here but NULL.
  (108, NULL,            'Frankenstein',                                       1818, 5,  650, NULL);

INSERT INTO book_authors (book_id, author_id, author_position) VALUES
  (101, 1, 1), (101, 2, 2),
  (102, 3, 1),
  (103, 4, 1), (103, 5, 2), (103, 6, 3),
  (104, 1, 1), (104, 7, 2),
  (105, 8, 1),
  (106, 9, 1),
  (107, 10, 1),
  (108, 11, 1);

-- Invented people. The .invalid top-level domain is reserved precisely so that
-- an address using it cannot resolve or be delivered to.
INSERT INTO members (member_id, email, full_name, tier, joined_at, left_at) VALUES
  (1, 'ada.okafor@fenwick.invalid',     'Ada Okafor',     'standard', '2024-01-15T10:00:00Z', NULL),
  (2, 'bruno.salgado@fenwick.invalid',  'Bruno Salgado',  'student',  '2024-03-02T10:00:00Z', NULL),
  (3, 'chandra.iyer@fenwick.invalid',   'Chandra Iyer',   'staff',    '2023-11-20T10:00:00Z', NULL),
  (4, 'dana.whitfield@fenwick.invalid', 'Dana Whitfield', 'standard', '2025-02-10T10:00:00Z', NULL),
  (5, 'eli.nakamura@fenwick.invalid',   'Eli Nakamura',   'student',  '2025-06-01T10:00:00Z', NULL),
  -- Left in March, and still owes £3.00 from a book returned two weeks late.
  (6, 'farida.haddad@fenwick.invalid',  'Farida Haddad',  'staff',    '2022-09-05T10:00:00Z', '2026-03-01T10:00:00Z');

INSERT INTO loans
  (loan_id, book_id, member_id, borrowed_at, due_at, returned_at, fine_pence)
VALUES
  (1,  101, 1, '2026-05-04T10:15:00Z', '2026-05-25T10:15:00Z', '2026-05-20T09:00:00Z',   0),
  (2,  102, 1, '2026-06-02T11:00:00Z', '2026-06-23T11:00:00Z', '2026-07-04T16:30:00Z', 220),
  (3,  103, 2, '2026-06-10T09:30:00Z', '2026-07-01T09:30:00Z', '2026-06-28T14:00:00Z',   0),
  -- Out and overdue as of the report time.
  (4,  105, 2, '2026-07-15T13:00:00Z', '2026-08-05T13:00:00Z', NULL,                     0),
  (5,  106, 3, '2026-07-20T10:00:00Z', '2026-08-10T10:00:00Z', NULL,                     0),
  -- Out, not yet due.
  (6,  101, 3, '2026-08-01T09:00:00Z', '2026-08-22T09:00:00Z', NULL,                     0),
  (7,  102, 4, '2026-04-12T15:00:00Z', '2026-05-03T15:00:00Z', '2026-05-01T10:00:00Z',   0),
  (8,  104, 1, '2026-07-02T10:00:00Z', '2026-07-23T10:00:00Z', '2026-08-01T11:00:00Z', 190),
  (9,  105, 3, '2026-03-05T09:00:00Z', '2026-03-26T09:00:00Z', '2026-03-20T12:00:00Z',   0),
  (10, 108, 2, '2026-05-18T14:00:00Z', '2026-06-08T14:00:00Z', '2026-06-05T09:00:00Z',   0),
  (11, 103, 4, '2026-08-03T11:00:00Z', '2026-08-24T11:00:00Z', NULL,                     0),
  -- Farida's, from before she left. The fine survives her membership.
  (12, 106, 6, '2026-01-10T10:00:00Z', '2026-01-31T10:00:00Z', '2026-02-15T10:00:00Z', 300),
  (13, 101, 2, '2026-02-14T10:00:00Z', '2026-03-07T10:00:00Z', '2026-03-02T10:00:00Z',   0),
  (14, 104, 3, '2026-06-20T10:00:00Z', '2026-07-11T10:00:00Z', '2026-07-09T10:00:00Z',   0);

INSERT INTO reservations (reservation_id, book_id, member_id, reserved_at, status) VALUES
  -- Book 105 is out until further notice; three people are waiting for it.
  (1, 105, 1, '2026-08-01T09:00:00Z', 'waiting'),
  (2, 105, 3, '2026-08-03T10:00:00Z', 'waiting'),
  (3, 105, 4, '2026-08-07T11:00:00Z', 'waiting'),
  -- Book 106: one waiting, one cancelled (which must not occupy a queue slot),
  -- and a later one that is therefore second and not third.
  (4, 106, 2, '2026-08-05T12:00:00Z', 'waiting'),
  (5, 106, 4, '2026-08-06T08:00:00Z', 'cancelled'),
  (6, 106, 1, '2026-08-10T15:00:00Z', 'waiting'),
  -- Already collected, so book 103 has nobody waiting at all.
  (7, 103, 1, '2026-07-28T09:00:00Z', 'collected');

COMMIT;
