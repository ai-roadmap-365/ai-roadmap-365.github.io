-- Day 091 — the design that was written first, tried, and thrown away.
--
--   sqlite3 rejected.db < examples/04_rejected_design.sql
--
-- The reference schema stores no queue position. That was not obvious at the
-- time; the first attempt stored one, because "position 1, 2, 3" is how a
-- human describes a queue and copying the human's words into columns is the
-- most natural mistake in schema design.
--
-- This file builds that first attempt, breaks it in three lines of ordinary
-- application traffic, and then shows the revision. Nothing here is
-- hypothetical: every output below is produced by running this file.

.mode column
.headers on
.width 0

.print '=== ATTEMPT 1: store the queue position as a column ==='

CREATE TABLE reservations_v1 (
  reservation_id INTEGER PRIMARY KEY,
  book_id        INTEGER NOT NULL,
  member_id      INTEGER NOT NULL,
  reserved_at    TEXT    NOT NULL,
  -- This is the decision under test.
  queue_position INTEGER NOT NULL CHECK (queue_position >= 1),
  status         TEXT    NOT NULL DEFAULT 'waiting'
);

-- Three members join the queue for book 105, in order. So far it looks fine,
-- and it looks fine for as long as nothing ever changes.
INSERT INTO reservations_v1 VALUES
  (1, 105, 1, '2026-08-01T09:00:00Z', 1, 'waiting'),
  (2, 105, 3, '2026-08-03T10:00:00Z', 2, 'waiting'),
  (3, 105, 4, '2026-08-07T11:00:00Z', 3, 'waiting');

SELECT reservation_id, member_id, queue_position, status FROM reservations_v1 ORDER BY queue_position;

.print ''
.print '--- the member at position 2 cancels ---'
-- The application does the obvious thing: mark it cancelled. It does NOT
-- renumber, because renumbering is a second statement that somebody has to
-- remember to write, in every code path that can cancel a reservation.
UPDATE reservations_v1 SET status = 'cancelled' WHERE reservation_id = 2;

SELECT reservation_id, member_id, queue_position, status
  FROM reservations_v1 WHERE status = 'waiting' ORDER BY queue_position;

.print ''
.print '--- so the queue now reads 1, 3: there is no position 2 ---'
SELECT group_concat(queue_position, ', ') AS positions_now
  FROM reservations_v1 WHERE status = 'waiting';

.print ''
.print '--- a fourth member joins, and the code appends "count of waiting + 1" ---'
-- A perfectly reasonable line of application code: there are two people
-- waiting, so the new one is third. It is also wrong, because the positions
-- stopped being 1..n the moment a cancellation punched a hole in them.
INSERT INTO reservations_v1 (reservation_id, book_id, member_id, reserved_at, queue_position, status)
  SELECT 4, 105, 2, '2026-08-09T09:00:00Z',
         (SELECT count(*) + 1 FROM reservations_v1 WHERE book_id = 105 AND status = 'waiting'),
         'waiting';

SELECT reservation_id, member_id, queue_position, status
  FROM reservations_v1 WHERE status = 'waiting' ORDER BY queue_position, reservation_id;

.print ''
.print '--- the damage, stated as a number: duplicate positions in one queue ---'
SELECT queue_position, count(*) AS members_at_this_position
  FROM reservations_v1
 WHERE status = 'waiting'
 GROUP BY queue_position
HAVING count(*) > 1;

.print ''
.print '=== WHY IT FAILED ==='
.print 'queue_position is DERIVED data: it is a function of reserved_at and status.'
.print 'Storing derived data means promising to recompute it everywhere either'
.print 'input changes, forever, in every code path, including the ones written'
.print 'next year by somebody who has not read this file. That promise is not'
.print 'enforceable by the database, so it is not a promise — it is a hope.'
.print 'No error was raised at any point above.'

.print ''
.print '=== ATTEMPT 2: do not store it. Derive it. ==='

CREATE TABLE reservations_v2 (
  reservation_id INTEGER PRIMARY KEY,
  book_id        INTEGER NOT NULL,
  member_id      INTEGER NOT NULL,
  reserved_at    TEXT    NOT NULL,
  status         TEXT    NOT NULL DEFAULT 'waiting'
                          CHECK (status IN ('waiting','collected','cancelled','expired'))
);

INSERT INTO reservations_v2 VALUES
  (1, 105, 1, '2026-08-01T09:00:00Z', 'waiting'),
  (2, 105, 3, '2026-08-03T10:00:00Z', 'cancelled'),
  (3, 105, 4, '2026-08-07T11:00:00Z', 'waiting'),
  (4, 105, 2, '2026-08-09T09:00:00Z', 'waiting');

-- One window function, and the numbering is right by construction. There is
-- no update to forget, because there is nothing stored to be wrong.
SELECT member_id,
       ROW_NUMBER() OVER (PARTITION BY book_id ORDER BY reserved_at) AS queue_position,
       reserved_at
  FROM reservations_v2
 WHERE status = 'waiting'
 ORDER BY queue_position;

.print ''
.print '--- and it stays right when another cancellation happens ---'
UPDATE reservations_v2 SET status = 'cancelled' WHERE reservation_id = 3;
SELECT member_id,
       ROW_NUMBER() OVER (PARTITION BY book_id ORDER BY reserved_at) AS queue_position
  FROM reservations_v2
 WHERE status = 'waiting'
 ORDER BY queue_position;

.print ''
.print '=== THE RULE THIS BOUGHT ==='
.print 'Store what you are told. Derive what follows from it. A column that can'
.print 'be computed from other columns is a column that can disagree with them.'
.print 'The exception is deliberate denormalisation for measured performance —'
.print 'and then you write down every path that must maintain it (Day 88).'
