-- Day 088 lab, demonstration 1 — the most expensive mistake in SQL.
--
-- Run against a THROWAWAY COPY of the database:
--   cp library.db scratch.db
--   sqlite3 scratch.db < examples/01-the-expensive-mistake.sql
--
-- Nothing here is clever. That is the point. The single most damaging
-- statement most people ever run is four words long and looks finished.

PRAGMA foreign_keys = ON;
.mode list
.headers off

SELECT '--- before: how many loans are outstanding? ---';
SELECT 'outstanding=' || count(*) FROM loans WHERE returned = 0;
SELECT 'returned=' || count(*)    FROM loans WHERE returned = 1;

-- What you MEANT to say. Loan 2 came back today.
SELECT '';
SELECT '--- the SELECT you should write first ---';
SELECT 'the SELECT matches ' || count(*) || ' row(s)' FROM loans WHERE id = 2;

-- What actually gets typed at 17:55 on a Friday. The WHERE clause is missing.
-- SQLite does not warn you. There is no confirmation prompt. It simply
-- succeeds, quickly and completely.
SELECT '';
SELECT '--- the statement with the WHERE clause forgotten ---';
UPDATE loans SET returned = 1;
SELECT 'UPDATE changed ' || changes() || ' row(s)';

SELECT '';
SELECT '--- after ---';
SELECT 'outstanding=' || count(*) FROM loans WHERE returned = 0;
SELECT 'returned=' || count(*)    FROM loans WHERE returned = 1;

-- Read those numbers next to each other. The intended change was one row.
-- The change that happened was twelve. And the eight rows that were destroyed
-- were not overwritten with rubbish that you could spot -- they were
-- overwritten with a PLAUSIBLE value. Nothing looks wrong afterwards. The
-- library simply believes every book has come back.
--
-- That is what makes this the expensive one: not that it is destructive, but
-- that it is destructive and silent at the same time.
SELECT '';
SELECT '--- what was lost ---';
SELECT 'rows intended: 1, rows changed: 12, rows silently wrong: 11';
