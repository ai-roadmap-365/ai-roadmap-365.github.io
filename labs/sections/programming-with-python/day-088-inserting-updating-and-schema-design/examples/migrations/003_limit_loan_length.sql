-- 003 — a loan may not run longer than 90 days.
--
-- There is no portable ALTER TABLE that adds a CHECK constraint, so this is
-- the documented create-copy-drop-rename rebuild. The runner has already
-- turned foreign keys off and wrapped this file in a transaction, so all four
-- steps either happen together or not at all.
--
-- Note step 1: the ENTIRE table definition is retyped, including both foreign
-- keys and every existing constraint. Anything omitted here is silently lost.

CREATE TABLE loans_new (
    id          INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL REFERENCES books(id)   ON DELETE RESTRICT,
    member_id   INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    borrowed_on TEXT    NOT NULL DEFAULT (date('now')),
    due_on      TEXT    NOT NULL,
    returned    INTEGER NOT NULL DEFAULT 0 CHECK (returned IN (0, 1)),

    CHECK (due_on >= borrowed_on),
    CHECK (julianday(due_on) - julianday(borrowed_on) <= 90)
) STRICT;

INSERT INTO loans_new (id, book_id, member_id, borrowed_on, due_on, returned)
SELECT id, book_id, member_id, borrowed_on, due_on, returned FROM loans;

DROP TABLE loans;

ALTER TABLE loans_new RENAME TO loans;
