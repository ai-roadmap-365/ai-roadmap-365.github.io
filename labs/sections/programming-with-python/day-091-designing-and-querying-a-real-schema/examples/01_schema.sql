-- Day 091 — the reference physical schema for the Fenwick Road brief.
--
-- Read this AFTER you have written your own. Every decision below is one you
-- were asked to make, and the comment says why it went that way and what the
-- alternative would have cost.
--
-- Conventions used throughout, decided once so they never have to be argued
-- about again:
--
--   * Surrogate integer primary keys. In SQLite an INTEGER PRIMARY KEY is an
--     alias for the rowid, so it is the storage key as well as the logical one.
--   * Timestamps are ISO 8601 text in UTC: 'YYYY-MM-DDTHH:MM:SSZ'. SQLite has
--     no date type. Text in this exact shape sorts chronologically as a string,
--     which is the property the whole schema leans on.
--   * Money is an INTEGER count of pence. Never a REAL: 0.1 + 0.2 is not 0.3
--     in binary floating point, and a fines ledger that drifts is a fines
--     ledger nobody trusts.
--   * Small closed sets of values are CHECK constraints. Sets that will grow,
--     or that need a label and a sort order, get a lookup table instead.

PRAGMA foreign_keys = ON;   -- per connection, every connection (Day 87)

DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS book_authors;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS categories;

-- ---------------------------------------------------------------------------
-- categories — a hierarchy, modelled with a self-referencing parent
-- ---------------------------------------------------------------------------
-- "Fiction contains Science Fiction, which contains Cyberpunk" is a tree of
-- unknown depth. The adjacency-list model (one nullable parent_id) is the
-- simplest thing that holds it, and a recursive CTE walks it. The alternative
-- — a fixed set of columns, genre and subgenre — breaks the first time
-- somebody adds a third level, and moving a branch would mean rewriting rows
-- all the way down.
CREATE TABLE categories (
  category_id INTEGER PRIMARY KEY,
  name        TEXT    NOT NULL,
  -- NULL parent means "top level". This is a nullable column on purpose: it
  -- encodes a real fact about the world, not a missing value.
  parent_id   INTEGER REFERENCES categories(category_id) ON DELETE RESTRICT,
  -- Two siblings may not share a name. Two categories in different branches
  -- may: "Classics" under Fiction and "Classics" under Non-fiction are
  -- different shelves.
  --
  -- Honest caveat: SQL treats NULLs as distinct in a UNIQUE constraint, so
  -- this does NOT stop two top-level categories both being called "Fiction".
  -- The fix, if the library ever needs it, is a unique index on
  -- (coalesce(parent_id, -1), name). It is left as written here so that the
  -- limitation is visible rather than papered over.
  UNIQUE (parent_id, name),
  CHECK (parent_id IS NULL OR parent_id <> category_id)
);

-- ---------------------------------------------------------------------------
-- authors — an entity, not an attribute of a book
-- ---------------------------------------------------------------------------
-- The test for "is this an entity?": does it have a life of its own? An author
-- exists before we catalogue their first book and after we withdraw their
-- last, has attributes of its own, and is referenced by more than one book.
-- All three say entity.
CREATE TABLE authors (
  author_id  INTEGER PRIMARY KEY,
  name       TEXT    NOT NULL,
  -- Nullable, and the null means something specific: we do not know. Julie
  -- Sussman's year of birth is not published, and inventing one to avoid a
  -- NULL would put a false fact in the database to satisfy a preference about
  -- column definitions.
  birth_year INTEGER CHECK (birth_year IS NULL OR birth_year BETWEEN 1400 AND 2100)
);

-- ---------------------------------------------------------------------------
-- books — surrogate key, with the natural key kept as a UNIQUE constraint
-- ---------------------------------------------------------------------------
-- The ISBN is a genuine natural key: it is assigned by an external authority
-- and identifies the edition. It is still not the primary key, for two
-- reasons the brief states outright. Books printed before 1970 do not have
-- one, and a primary key cannot be NULL. And catalogue staff mistype them,
-- which under a natural key means updating every child row to correct one
-- character.
--
-- Keeping it as UNIQUE gets the integrity guarantee without the coupling.
CREATE TABLE books (
  book_id               INTEGER PRIMARY KEY,
  isbn13                TEXT    UNIQUE
                        CHECK (isbn13 IS NULL OR
                               isbn13 GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
  title                 TEXT    NOT NULL,
  published_year        INTEGER CHECK (published_year IS NULL OR published_year BETWEEN 1400 AND 2100),
  category_id           INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
  -- Money as integer minor units. £12.99 is 1299.
  acquisition_cost_pence INTEGER NOT NULL CHECK (acquisition_cost_pence >= 0),
  -- Soft delete. NULL means "on the shelves". A timestamp means withdrawn, and
  -- the row stays so that old loans still resolve to a title. The price is
  -- that every query about the current collection must remember to filter, and
  -- the one that forgets is wrong without erroring.
  withdrawn_at          TEXT    CHECK (withdrawn_at IS NULL OR withdrawn_at LIKE '____-__-__T__:__:__Z')
);

-- ---------------------------------------------------------------------------
-- book_authors — a junction table that earns columns of its own
-- ---------------------------------------------------------------------------
-- Many-to-many, so the relationship gets a table. The primary key is the pair,
-- which makes it impossible to credit the same author on the same book twice.
-- author_position is the point of this table in a design lesson: a junction
-- table is not always a pure link. The moment the relationship itself has an
-- attribute — here, the order the cover credits them in — that attribute has
-- nowhere else to live.
CREATE TABLE book_authors (
  book_id         INTEGER NOT NULL REFERENCES books(book_id)     ON DELETE CASCADE,
  author_id       INTEGER NOT NULL REFERENCES authors(author_id) ON DELETE RESTRICT,
  author_position INTEGER NOT NULL CHECK (author_position >= 1),
  PRIMARY KEY (book_id, author_id),
  -- Two authors cannot both be credited second on the same book.
  UNIQUE (book_id, author_position)
);

-- ---------------------------------------------------------------------------
-- members
-- ---------------------------------------------------------------------------
CREATE TABLE members (
  member_id INTEGER PRIMARY KEY,
  -- The other natural key in this schema, and the same treatment: UNIQUE, not
  -- PRIMARY KEY. People change their email address; a key you have to update
  -- is not a key.
  email     TEXT    NOT NULL UNIQUE CHECK (email LIKE '_%@_%._%'),
  full_name TEXT    NOT NULL,
  -- An enumeration of three values that changes about once a decade. A CHECK
  -- constraint costs one line and no join. If the library later wants a label,
  -- a loan allowance and a display order per tier, this becomes a lookup table
  -- — and that migration is one ALTER TABLE plus a backfill (Day 88).
  tier      TEXT    NOT NULL DEFAULT 'standard'
                    CHECK (tier IN ('standard', 'student', 'staff')),
  joined_at TEXT    NOT NULL CHECK (joined_at LIKE '____-__-__T__:__:__Z'),
  -- Soft delete again, and for a different reason from books: the brief says
  -- the money they owe has to survive. NULL means a current member.
  left_at   TEXT    CHECK (left_at IS NULL OR left_at LIKE '____-__-__T__:__:__Z'),
  CHECK (left_at IS NULL OR left_at >= joined_at)
);

-- ---------------------------------------------------------------------------
-- loans
-- ---------------------------------------------------------------------------
-- ON DELETE RESTRICT on both parents, deliberately. A hard DELETE of a book or
-- a member that still has loan history should fail loudly, because the brief
-- says that history must survive. Withdrawal and leaving are soft, and the
-- soft path is the one the application is supposed to take.
CREATE TABLE loans (
  loan_id     INTEGER PRIMARY KEY,
  book_id     INTEGER NOT NULL REFERENCES books(book_id)     ON DELETE RESTRICT,
  member_id   INTEGER NOT NULL REFERENCES members(member_id) ON DELETE RESTRICT,
  borrowed_at TEXT    NOT NULL CHECK (borrowed_at LIKE '____-__-__T__:__:__Z'),
  due_at      TEXT    NOT NULL CHECK (due_at      LIKE '____-__-__T__:__:__Z'),
  -- NULL means "still out". Not a sentinel date, not a separate boolean that
  -- could disagree with the date. One column, one meaning.
  returned_at TEXT             CHECK (returned_at IS NULL OR returned_at LIKE '____-__-__T__:__:__Z'),
  fine_pence  INTEGER NOT NULL DEFAULT 0 CHECK (fine_pence >= 0),
  -- Because timestamps are ISO 8601 in UTC, string comparison IS chronological
  -- comparison. This constraint is the payoff for that format decision.
  CHECK (due_at > borrowed_at),
  CHECK (returned_at IS NULL OR returned_at >= borrowed_at)
);

-- ---------------------------------------------------------------------------
-- reservations
-- ---------------------------------------------------------------------------
-- A queue. There is no position column, and that is the design decision worth
-- arguing about: a stored position has to be renumbered every time somebody
-- cancels, and a renumbering you forget leaves two people at position 3.
-- The position is derived at query time from reserved_at with ROW_NUMBER.
CREATE TABLE reservations (
  reservation_id INTEGER PRIMARY KEY,
  book_id        INTEGER NOT NULL REFERENCES books(book_id)     ON DELETE CASCADE,
  member_id      INTEGER NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
  reserved_at    TEXT    NOT NULL CHECK (reserved_at LIKE '____-__-__T__:__:__Z'),
  status         TEXT    NOT NULL DEFAULT 'waiting'
                         CHECK (status IN ('waiting', 'collected', 'cancelled', 'expired')),
  -- One member may not hold two live reservations on the same book. Partial
  -- indexes make this enforceable only for the status that matters.
  UNIQUE (book_id, member_id, reserved_at)
);

-- ---------------------------------------------------------------------------
-- Indexes (Day 89)
-- ---------------------------------------------------------------------------
-- Declaring a foreign key creates NO index. Every one below exists because a
-- query in 03_questions.sql joins or filters on that column.
CREATE INDEX idx_books_category      ON books(category_id);
CREATE INDEX idx_categories_parent   ON categories(parent_id);
CREATE INDEX idx_book_authors_author ON book_authors(author_id);
CREATE INDEX idx_loans_book          ON loans(book_id);
CREATE INDEX idx_loans_member        ON loans(member_id);
CREATE INDEX idx_reservations_book   ON reservations(book_id);
CREATE INDEX idx_reservations_member ON reservations(member_id);

-- A partial index: only the rows that are still out. Questions 1 and 4 are
-- both "what is out right now", and outstanding loans are a small and roughly
-- constant fraction of a loans table that grows forever.
CREATE INDEX idx_loans_outstanding ON loans(due_at) WHERE returned_at IS NULL;

-- Only one member may be at the front of a queue for a book at a time is NOT
-- what this says; it says one member may hold at most one *waiting*
-- reservation per book, while leaving their cancelled and expired history
-- alone. A plain UNIQUE could not express that.
CREATE UNIQUE INDEX idx_reservations_one_waiting
  ON reservations(book_id, member_id) WHERE status = 'waiting';

-- ---------------------------------------------------------------------------
-- A view: the saved query the reports lean on
-- ---------------------------------------------------------------------------
-- A view stores the query text, not its result. It buys a name for a piece of
-- reasoning — "what does the collection currently consist of" — and it buys
-- consistency, because every report that uses it filters withdrawn books the
-- same way. It does not buy speed: it is expanded into whatever query uses it
-- and runs afresh every time.
CREATE VIEW current_collection AS
  SELECT book_id, isbn13, title, published_year, category_id, acquisition_cost_pence
    FROM books
   WHERE withdrawn_at IS NULL;

CREATE VIEW current_members AS
  SELECT member_id, email, full_name, tier, joined_at
    FROM members
   WHERE left_at IS NULL;
