-- Day 091 — YOUR schema for the Fenwick Road brief.
--
-- Read starter/00_brief.md first. Then work down this file.
--
-- Three of the seven tables are already written, in full, as worked examples.
-- They establish the conventions the rest of the schema follows, and each one
-- carries the reasoning in its comments. Copy the style, not just the syntax.
--
-- Four tables, the indexes and the views are yours: exercises 1 to 6.
--
-- Check your progress at any point with:
--
--   bash starter/03_check.sh
--
-- It reports "N of 16 exercises complete." and exits non-zero until N is 16.
-- Before you start it will say 0, and it will tell you exactly what is missing.
--
-- IMPORTANT: the column names below are not suggestions. starter/03_check.sh
-- loads the shared seed file (examples/02_seed.sql) into your schema, so your
-- column names have to be the ones the seed inserts into. The DESIGN decisions
-- — which keys, which constraints, which columns may be NULL, what happens on
-- delete — are entirely yours, and are what you are being marked on.

PRAGMA foreign_keys = ON;   -- per connection, every connection (Day 87)

-- ===========================================================================
-- WORKED EXAMPLE 1 — categories
-- ===========================================================================
-- The brief says categories nest to an unknown depth and get moved around.
-- That is a tree, and the adjacency-list model — one nullable parent_id
-- pointing at another row of the same table — is the simplest thing that holds
-- one. A recursive CTE walks it later, in question 9.
--
-- parent_id IS NULL is not a missing value. It means "this is a top-level
-- shelf", which is a real fact about the world.
CREATE TABLE categories (
  category_id INTEGER PRIMARY KEY,
  name        TEXT    NOT NULL,
  parent_id   INTEGER REFERENCES categories(category_id) ON DELETE RESTRICT,
  UNIQUE (parent_id, name),
  CHECK (parent_id IS NULL OR parent_id <> category_id)
);

-- ===========================================================================
-- WORKED EXAMPLE 2 — authors
-- ===========================================================================
-- An author is an entity, not an attribute of a book: it exists before we
-- catalogue their first book, it has attributes of its own, and more than one
-- book refers to it. Any one of those three would be enough.
--
-- birth_year is nullable ON PURPOSE. One author in the seed has no published
-- year of birth, and inventing one to avoid a NULL would put a false fact in
-- the database to satisfy a preference about column definitions.
CREATE TABLE authors (
  author_id  INTEGER PRIMARY KEY,
  name       TEXT    NOT NULL,
  birth_year INTEGER CHECK (birth_year IS NULL OR birth_year BETWEEN 1400 AND 2100)
);

-- ===========================================================================
-- WORKED EXAMPLE 3 — members
-- ===========================================================================
-- Note three decisions you are about to have to make for yourself:
--
--   * email is a real natural key — unique, externally meaningful — and it is
--     still not the PRIMARY KEY, because people change their email address and
--     a key you have to update is not a key. UNIQUE gets the guarantee without
--     the coupling.
--   * tier is an enumeration of three values that changes about once a decade,
--     so it is a CHECK constraint rather than a lookup table. One line, no
--     join. If it ever needs a label and a loan allowance per tier, that
--     becomes a table, and the migration is ordinary (Day 88).
--   * left_at is a SOFT DELETE. NULL means a current member. The brief says
--     the money they owe has to survive them leaving, so the row cannot go.
CREATE TABLE members (
  member_id INTEGER PRIMARY KEY,
  email     TEXT    NOT NULL UNIQUE CHECK (email LIKE '_%@_%._%'),
  full_name TEXT    NOT NULL,
  tier      TEXT    NOT NULL DEFAULT 'standard'
                    CHECK (tier IN ('standard', 'student', 'staff')),
  joined_at TEXT    NOT NULL CHECK (joined_at LIKE '____-__-__T__:__:__Z'),
  left_at   TEXT    CHECK (left_at IS NULL OR left_at LIKE '____-__-__T__:__:__Z'),
  CHECK (left_at IS NULL OR left_at >= joined_at)
);

-- ===========================================================================
-- EXERCISE 1 — books
-- ===========================================================================
-- Write CREATE TABLE books. Columns, in this order and with these names:
--
--   book_id                 the surrogate primary key
--   isbn13                  the ISBN. The brief says the very old books have
--                           none, so decide what that means for NOT NULL and
--                           for whether this could ever be the primary key.
--                           Add a UNIQUE constraint, and a CHECK that it is
--                           thirteen digits when present — GLOB '[0-9]' thirteen
--                           times is the SQLite spelling.
--   title                   never absent
--   published_year          may be unknown
--   category_id             which shelf. Not null; references categories.
--                           Decide the ON DELETE behaviour and say why.
--   acquisition_cost_pence  money. INTEGER pence, never REAL pounds (Day 70).
--                           Constrain it to be non-negative.
--   withdrawn_at            soft delete: NULL means on the shelves, otherwise
--                           the ISO 8601 UTC instant it was withdrawn. The
--                           brief says withdrawn books must still resolve in
--                           old loan records, which is what rules out DELETE.
--
-- The timestamp shape check used above is: LIKE '____-__-__T__:__:__Z'
-- (underscore matches exactly one character in LIKE).



-- ===========================================================================
-- EXERCISE 2 — book_authors
-- ===========================================================================
-- Many-to-many: a book has several authors, an author has several books.
-- Neither table can hold the key, so the relationship needs a table.
--
-- Columns: book_id, author_id, author_position.
--
-- Three decisions, and the checker tests all three:
--
--   a) The PRIMARY KEY is the PAIR (book_id, author_id). That is what makes it
--      impossible to credit the same author twice on one book.
--   b) author_position exists because the brief says the credit order matters.
--      This is the point of the exercise: a junction table is not always a
--      pure link. When the relationship itself has an attribute, that
--      attribute has nowhere else to live.
--   c) Deleting a book should take its authorship rows with it (CASCADE);
--      deleting an author who still has books should be refused (RESTRICT).
--      Write both, and be able to say why they differ.
--
-- Consider also: can two authors both be credited second on the same book?



-- ===========================================================================
-- EXERCISE 3 — loans
-- ===========================================================================
-- Columns: loan_id, book_id, member_id, borrowed_at, due_at, returned_at,
--          fine_pence.
--
--   * returned_at NULL means "still out". Resist the temptation to add an
--     is_returned boolean as well: two columns that encode one fact are two
--     columns that can disagree.
--   * fine_pence is money. Integer, non-negative, default 0.
--   * Because timestamps are ISO 8601 in UTC, string comparison IS
--     chronological comparison — so you can write a table-level
--     CHECK (due_at > borrowed_at). Add it, and a second one saying a book
--     cannot be returned before it was borrowed. This is the payoff for the
--     format decision, and it is why the format decision was not cosmetic.
--   * The brief says loan history must survive a book being withdrawn or a
--     member leaving. What does that imply about ON DELETE here?



-- ===========================================================================
-- EXERCISE 4 — reservations
-- ===========================================================================
-- Columns: reservation_id, book_id, member_id, reserved_at, status.
--
-- status is an enumeration: waiting, collected, cancelled, expired. CHECK it.
--
-- The decision worth arguing about: there is NO queue_position column, and
-- there must not be. The position is a function of reserved_at and status, so
-- storing it means promising to recompute it in every code path that can ever
-- cancel a reservation, forever. Run examples/04_rejected_design.sql to watch
-- that promise break in three ordinary statements, with no error raised.
--
-- Question 7 derives the position with ROW_NUMBER instead.



-- ===========================================================================
-- EXERCISE 5 — indexes
-- ===========================================================================
-- Declaring a foreign key creates NO index (Day 87), so every join across one
-- scans the whole table (Day 89). Create an index on every foreign-key column
-- in the schema:
--
--   books(category_id), categories(parent_id), book_authors(author_id),
--   loans(book_id), loans(member_id),
--   reservations(book_id), reservations(member_id)
--
-- book_authors(book_id) and the other leading columns of composite primary
-- keys already have one — the primary key index — so they are not repeated.
--
-- Then two indexes that are about the questions rather than the keys:
--
--   * A PARTIAL index on loans(due_at) WHERE returned_at IS NULL. Questions 1
--     and 4 both ask what is out right now, and outstanding loans stay a small
--     fraction of a loans table that grows forever.
--   * A partial UNIQUE index on reservations(book_id, member_id)
--     WHERE status = 'waiting', so one member cannot hold two live
--     reservations on the same book while their cancelled history is left
--     alone. A plain UNIQUE constraint could not express that.



-- ===========================================================================
-- EXERCISE 6 — two views
-- ===========================================================================
-- Soft delete has a running cost: every query about the present has to
-- remember to filter. A view gives that filter a name and one definition.
--
--   CREATE VIEW current_collection AS ... books that are not withdrawn
--   CREATE VIEW current_members    AS ... members who have not left
--
-- Be clear about what this does and does not buy you. It buys a name for a
-- piece of reasoning and it buys consistency between reports. It does not buy
-- speed: a view stores the query text, not the result, and runs afresh every
-- time it is used.
