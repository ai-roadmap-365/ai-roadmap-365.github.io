-- 004 — generated columns: values the database computes, never stores wrongly.
--
-- A generated column is defined by an expression over the other columns of the
-- same row. You cannot write to it, so it cannot disagree with the data it is
-- derived from -- which is exactly the failure the denormalized loan_count in
-- demonstration 4 is exposed to.
--
-- VIRTUAL means "computed when read": no disk cost, a little processing cost.
-- STORED means "computed when written": the reverse trade. ALTER TABLE ADD
-- COLUMN can only add VIRTUAL generated columns, because adding a STORED one
-- would mean rewriting every existing row, and ADD COLUMN never does that.

ALTER TABLE loans ADD COLUMN loan_days INTEGER
    GENERATED ALWAYS AS (CAST(julianday(due_on) - julianday(borrowed_on) AS INTEGER)) VIRTUAL;

ALTER TABLE loans ADD COLUMN is_open INTEGER
    GENERATED ALWAYS AS (CASE WHEN returned = 0 THEN 1 ELSE 0 END) VIRTUAL;
