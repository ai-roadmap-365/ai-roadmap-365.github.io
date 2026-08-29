-- 002 — soft delete for members.
--
-- ADD COLUMN is one of the four things SQLite's ALTER TABLE has always been
-- able to do, and it is cheap: SQLite records the new column in the schema
-- and does not rewrite a single existing row.
--
-- deleted_at is deliberately nullable. NULL means "not deleted", which lets
-- one column carry both the flag and the date it happened.

ALTER TABLE members ADD COLUMN deleted_at TEXT;

-- A partial index so the common query -- "the members who still exist" --
-- stays fast without indexing the deleted ones.
CREATE INDEX members_active ON members(id) WHERE deleted_at IS NULL;
