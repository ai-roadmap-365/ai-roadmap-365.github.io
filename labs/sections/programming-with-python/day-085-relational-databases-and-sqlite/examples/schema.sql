-- Day 085 — the finished schema for library.db
--
-- Read this as a written-down promise. Every line either names a fact the
-- database will store, or a rule the database will refuse to break. Nothing
-- here is advice: the engine enforces all of it, for every writer, forever.
--
-- Apply it with:   sqlite3 library.db < schema.sql

PRAGMA foreign_keys = ON;   -- SQLite defaults this OFF for backward
                            -- compatibility. Without it, REFERENCES below is
                            -- documentation rather than a rule. Turn it on in
                            -- every connection, every time.

-- ---------------------------------------------------------------------------
-- books: one row per title the library owns.
-- ---------------------------------------------------------------------------
CREATE TABLE books (
    book_id  INTEGER PRIMARY KEY,   -- the key: unique, never NULL, never reused
                                    -- while the row lives. In SQLite this exact
                                    -- spelling aliases the internal rowid.
    title    TEXT    NOT NULL,
    author   TEXT    NOT NULL,
    year     INTEGER,               -- nullable on purpose: we do not always know
    copies   INTEGER NOT NULL DEFAULT 1
                     CHECK (copies >= 0)   -- a negative number of copies is not
                                           -- a bug to find later; it is a write
                                           -- the database will refuse now
);

-- ---------------------------------------------------------------------------
-- members: one row per person who may borrow.
-- ---------------------------------------------------------------------------
CREATE TABLE members (
    member_id INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,  -- a candidate key: also unique, also
                                     -- identifies the row. We chose member_id
                                     -- as the primary key because an address
                                     -- can change and a key should not.
    joined_on TEXT NOT NULL          -- ISO-8601 'YYYY-MM-DD'. SQLite has no
                                     -- date type; see the CHECK below.
                   CHECK (joined_on LIKE '____-__-__')
);

-- ---------------------------------------------------------------------------
-- loans: one row per act of borrowing. This is the table that makes the
-- database earn its keep — it is where the typo'd member id used to live.
-- ---------------------------------------------------------------------------
CREATE TABLE loans (
    loan_id     INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(book_id),
    member_id   INTEGER NOT NULL REFERENCES members(member_id),
    borrowed_on TEXT NOT NULL CHECK (borrowed_on LIKE '____-__-__'),
    due_on      TEXT NOT NULL CHECK (due_on      LIKE '____-__-__'),
    returned_on TEXT          CHECK (returned_on LIKE '____-__-__'),  -- NULL
                                     -- means "still out". A NULL here is not
                                     -- missing data; it is a fact about the world.
    CHECK (due_on >= borrowed_on)
);

-- An index is not part of the model — the answers are identical with or
-- without it. It is a promise about speed, not about meaning.
CREATE INDEX loans_by_member ON loans(member_id);
CREATE INDEX loans_open      ON loans(returned_on) WHERE returned_on IS NULL;
