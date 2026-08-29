-- Day 085 — SQLite's type system, honestly.
--
-- Most databases check the type of a value against the type of the column and
-- refuse a mismatch. SQLite does not, by default. A column's declared type is
-- an AFFINITY: a preference the engine applies when it can, and abandons when
-- it cannot. The value keeps its own storage class regardless.
--
-- Run it:  sqlite3 typing.db < typing_demo.sql
--
-- Read every line of the output. Several of them will look like bugs. They
-- are documented behaviour, and knowing them is the difference between
-- trusting your data and hoping.

.mode box
.headers on

-- ---------------------------------------------------------------------------
.print '--- 1. An ordinary table. INTEGER affinity, no enforcement. ---'
CREATE TABLE loose (
    id    INTEGER PRIMARY KEY,
    year  INTEGER,      -- INTEGER affinity
    title TEXT          -- TEXT affinity
);

-- Text that LOOKS like a number is converted. Affinity applied successfully.
INSERT INTO loose (id, year, title) VALUES (1, '1970', 'converted to integer');

-- Text that does not look like a number is stored as text, in a column the
-- schema calls INTEGER. No error. No warning. No log line.
INSERT INTO loose (id, year, title) VALUES (2, 'not-a-number', 'stored as text');

-- A float in an INTEGER column, losslessly representable, becomes an integer.
INSERT INTO loose (id, year, title) VALUES (3, 1975.0, 'float that fits');

-- A float that would lose information keeps its own class.
INSERT INTO loose (id, year, title) VALUES (4, 1975.5, 'float that does not fit');

-- And an integer in a TEXT column goes the other way.
INSERT INTO loose (id, year, title) VALUES (5, 1968, 42);

.print ''
.print 'What is actually stored — typeof() reports the STORAGE CLASS:'
SELECT id, year, typeof(year) AS year_class, title, typeof(title) AS title_class
  FROM loose ORDER BY id;

.print ''
.print 'The consequence: a comparison that quietly finds nothing.'
.print 'Row 2 holds the TEXT value not-a-number. In SQLite every INTEGER sorts'
.print 'before every TEXT, so that row can never satisfy year < 2000.'
.print 'Five rows in, four rows out, and nothing anywhere said so.'
SELECT count(*) AS rows_matching_year_lt_2000 FROM loose WHERE year < 2000;
SELECT count(*) AS rows_total FROM loose;

-- ---------------------------------------------------------------------------
.print ''
.print '--- 2. The same table, declared STRICT. ---'
-- STRICT was added in SQLite 3.37.0 (2021). In a STRICT table every column
-- must be declared as one of INT, INTEGER, REAL, TEXT, BLOB or ANY, and the
-- engine enforces it.
CREATE TABLE tight (
    id    INTEGER PRIMARY KEY,
    year  INTEGER,
    title TEXT
) STRICT;

.print 'Lossless text-to-integer conversion still happens:'
INSERT INTO tight (id, year, title) VALUES (1, '1970', 'converted to integer');
SELECT id, year, typeof(year) AS year_class FROM tight;

.print ''
.print 'But the value that is genuinely not an integer is now REFUSED:'
INSERT INTO tight (id, year, title) VALUES (2, 'not-a-number', 'rejected');

.print ''
.print 'And the row was never written:'
SELECT count(*) AS rows_in_tight FROM tight;
