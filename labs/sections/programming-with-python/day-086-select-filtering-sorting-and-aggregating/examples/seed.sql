-- Day 086 lab — the seed for library.db
--
-- Everything in this lab runs against this one database. It is deliberately
-- small enough to check by hand and deliberately full of NULLs, because NULL
-- is where the day's real lessons live.
--
-- Build it with:
--   bash examples/build_db.sh
-- or directly:
--   rm -f examples/library.db && sqlite3 examples/library.db < examples/seed.sql
--
-- Three deliberate holes are drilled into the data, and every one of them is
-- an exercise later:
--   * books.rating is NULL for books nobody has rated yet
--   * books.genre is NULL for books that were never classified
--   * members.city is NULL for members who did not give one
--   * loans.returned_on is NULL for books that are still out
--
-- The last one carries the most weight: "still on loan" is not a value, it is
-- the absence of one, and that is why `returned_on <> ''` finds nothing.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS books;

CREATE TABLE books (
  book_id        INTEGER PRIMARY KEY,
  title          TEXT    NOT NULL,
  author         TEXT    NOT NULL,
  genre          TEXT,             -- NULL = never classified
  published_year INTEGER,          -- NULL = publication date unknown
  pages          INTEGER,
  rating         REAL,             -- NULL = not yet rated; 1.0 to 5.0 otherwise
  copies         INTEGER NOT NULL
);

CREATE TABLE members (
  member_id  INTEGER PRIMARY KEY,
  full_name  TEXT NOT NULL,
  joined_on  TEXT NOT NULL,        -- ISO-8601 date, stored as TEXT
  city       TEXT,                 -- NULL = not supplied
  email      TEXT
);

CREATE TABLE loans (
  loan_id     INTEGER PRIMARY KEY,
  book_id     INTEGER NOT NULL REFERENCES books(book_id),
  member_id   INTEGER NOT NULL REFERENCES members(member_id),
  borrowed_on TEXT NOT NULL,
  returned_on TEXT               -- NULL = still on loan
);

INSERT INTO books (book_id, title, author, genre, published_year, pages, rating, copies) VALUES
  (1,  'The Silent Archive',        'Priya Raman',      'mystery',    2018, 312, 4.5,  3),
  (2,  'Grammar of Machines',       'Ada Fenwick',      'science',    2011, 480, 4.8,  2),
  (3,  'Salt and Longitude',        'Tomas Berg',       'history',    1997, 528, 3.9,  1),
  (4,  'The Quiet Algorithm',       'Ada Fenwick',      'science',    2021, 264, NULL, 4),
  (5,  'Nine Rivers',               'Kofi Mensah',      'fiction',    2005, 398, 4.1,  2),
  (6,  'A Map of Small Errors',     'Priya Raman',      'mystery',    2022, 288, 4.4,  5),
  (7,  'Ledger of Tides',           'Marta Iglesias',   'fiction',    1988, 356, 3.2,  1),
  (8,  'The Glasshouse Problem',    'Ada Fenwick',      'science',    2016, 344, 4.6,  3),
  (9,  'Winter Counting',           'Hana Sato',        NULL,         2019, 210, 4.0,  2),
  (10, 'The Lost Cartographers',    'Tomas Berg',       'history',    2003, 612, 4.2,  1),
  (11, 'Field Notes on Rain',       'Hana Sato',        'poetry',     2014, 96,  NULL, 6),
  (12, 'Eleven Ways to Fail',       'Daniel Okoro',     'science',    2020, 302, 3.7,  2),
  (13, 'The Anchor Room',           'Marta Iglesias',   'mystery',    2012, 274, 4.3,  3),
  (14, 'Continental Drift Blues',   'Kofi Mensah',      'fiction',    2017, 421, 3.5,  1),
  (15, 'Small Gods of Arithmetic',  'Ada Fenwick',      NULL,         NULL, 198, 4.9,  1),
  (16, 'The Paper Observatory',     'Hana Sato',        'science',    2009, 366, 4.4,  2),
  (17, 'Coasts of Elsewhere',       'Tomas Berg',       'history',    2023, 455, NULL, 4),
  (18, 'A Winter Grammar',          'Priya Raman',      'poetry',     1999, 128, 3.8,  1),
  (19, 'The Long Instrument',       'Daniel Okoro',     'fiction',    2015, 512, 4.7,  2),
  (20, 'Notes Toward a Machine',    'Ada Fenwick',      'science',    2024, 240, NULL, 3),
  (21, 'The Weather in Numbers',    'Marta Iglesias',   'science',    2013, 288, 4.0,  2),
  (22, 'Wintering Grounds',         'Kofi Mensah',      NULL,         2007, 334, 3.4,  1),
  (23, 'The Second Archive',        'Priya Raman',      'mystery',    2025, 296, 4.6,  4),
  (24, 'Poems for a Dry Season',    'Hana Sato',        'poetry',     2021, 112, 4.2,  2);

INSERT INTO members (member_id, full_name, joined_on, city, email) VALUES
  (1,  'Anita Desai',      '2021-03-14', 'Pune',      'anita.desai@library.invalid'),
  (2,  'Ben Oyelaran',     '2022-07-02', 'Lagos',     'ben.oyelaran@library.invalid'),
  (3,  'Chen Wei',         '2020-11-30', 'Singapore', NULL),
  (4,  'Dana Kowalski',    '2023-01-19', NULL,        'dana.k@library.invalid'),
  (5,  'Elif Demir',       '2019-05-08', 'Izmir',     'elif.demir@library.invalid'),
  (6,  'Farid Nazari',     '2024-02-11', 'Pune',      NULL),
  (7,  'Grace Mwangi',     '2022-09-23', 'Nairobi',   'grace.mwangi@library.invalid'),
  (8,  'Hugo Almeida',     '2018-08-16', NULL,        NULL),
  (9,  'Ines Moreau',      '2023-10-05', 'Lyon',      'ines.moreau@library.invalid'),
  (10, 'Jonas Lindqvist',  '2025-04-27', 'Uppsala',   'jonas.l@library.invalid'),
  (11, 'Keiko Tanaka',     '2021-12-01', 'Sendai',    'keiko.tanaka@library.invalid'),
  (12, 'Luis Ferreira',    '2024-06-30', 'Porto',     NULL);

INSERT INTO loans (loan_id, book_id, member_id, borrowed_on, returned_on) VALUES
  (1,  1,  1,  '2026-01-05', '2026-01-19'),
  (2,  2,  1,  '2026-01-05', '2026-02-02'),
  (3,  6,  2,  '2026-01-11', '2026-01-25'),
  (4,  8,  3,  '2026-01-14', NULL),
  (5,  5,  4,  '2026-01-18', '2026-02-01'),
  (6,  13, 5,  '2026-01-20', '2026-01-27'),
  (7,  1,  6,  '2026-01-22', NULL),
  (8,  19, 7,  '2026-01-26', '2026-02-16'),
  (9,  4,  2,  '2026-02-01', '2026-02-15'),
  (10, 11, 8,  '2026-02-03', NULL),
  (11, 16, 9,  '2026-02-04', '2026-02-18'),
  (12, 2,  10, '2026-02-07', '2026-02-21'),
  (13, 23, 1,  '2026-02-09', NULL),
  (14, 6,  11, '2026-02-10', '2026-02-24'),
  (15, 3,  12, '2026-02-12', '2026-03-05'),
  (16, 8,  4,  '2026-02-14', '2026-02-28'),
  (17, 21, 5,  '2026-02-15', NULL),
  (18, 6,  7,  '2026-02-17', '2026-03-03'),
  (19, 10, 3,  '2026-02-19', '2026-03-12'),
  (20, 1,  9,  '2026-02-21', '2026-03-07'),
  (21, 24, 2,  '2026-02-23', NULL),
  (22, 19, 6,  '2026-02-25', '2026-03-11'),
  (23, 13, 10, '2026-03-01', '2026-03-15'),
  (24, 6,  12, '2026-03-02', NULL),
  (25, 20, 1,  '2026-03-04', '2026-03-18'),
  (26, 9,  8,  '2026-03-06', '2026-03-20'),
  (27, 2,  11, '2026-03-08', NULL),
  (28, 17, 5,  '2026-03-09', '2026-03-23'),
  (29, 1,  4,  '2026-03-11', '2026-03-25'),
  (30, 12, 7,  '2026-03-13', NULL),
  (31, 6,  9,  '2026-03-15', '2026-03-29'),
  (32, 8,  1,  '2026-03-17', '2026-03-31'),
  (33, 23, 2,  '2026-03-19', NULL),
  (34, 5,  3,  '2026-03-21', '2026-04-04'),
  (35, 19, 12, '2026-03-23', '2026-04-06'),
  (36, 16, 6,  '2026-03-25', NULL),
  (37, 1,  11, '2026-03-27', '2026-04-10'),
  (38, 13, 8,  '2026-03-29', '2026-04-12'),
  (39, 6,  10, '2026-04-01', NULL),
  (40, 21, 4,  '2026-04-03', '2026-04-17'),
  (41, 2,  5,  '2026-04-05', NULL),
  (42, 23, 9,  '2026-04-07', '2026-04-21'),
  (43, 8,  7,  '2026-04-09', NULL),
  (44, 6,  1,  '2026-04-11', '2026-04-25'),
  (45, 15, 3,  '2026-04-13', NULL);

-- A last sanity line so a successful build is visible rather than silent.
SELECT 'seeded: ' || (SELECT COUNT(*) FROM books) || ' books, '
                  || (SELECT COUNT(*) FROM members) || ' members, '
                  || (SELECT COUNT(*) FROM loans) || ' loans';
