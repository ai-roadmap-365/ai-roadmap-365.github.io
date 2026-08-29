-- Day 088 lab, demonstration 5 — constraints as executable documentation,
-- shown on a training-data table because that is where it costs the most.
--
--   sqlite3 training.db < examples/05-constraints.sql
--
-- The claim being tested: a table without constraints will accept a duplicated
-- example, a missing label, a leaked or misspelled split, an invented label and
-- the word 'banana' where a number belongs -- and it will accept every one of
-- them silently. Months later the model trained on that table behaves badly,
-- and the model gets blamed. Data quality is a schema decision.

.mode list
.headers off

DROP TABLE IF EXISTS examples_loose;
DROP TABLE IF EXISTS examples_strict;

-- ---------------------------------------------------------------------------
-- The loose table: what almost everybody writes the first time.
-- ---------------------------------------------------------------------------
-- Nothing here is wrong, exactly. It is just that the table makes no promises,
-- so every promise has to be kept by every piece of code that ever writes to
-- it -- including the script somebody runs by hand at midnight.
CREATE TABLE examples_loose (
    id          INTEGER PRIMARY KEY,
    text        TEXT,
    label       TEXT,
    split       TEXT,
    token_count INTEGER
);

SELECT '--- the loose table accepts all five mistakes ---';

-- Mistake 1: the same example twice. Duplicates inflate your reported accuracy
-- when the copy lands in both train and test.
INSERT INTO examples_loose (text, label, split, token_count) VALUES
    ('the film was a delight', 'positive', 'train', 5),
    ('the film was a delight', 'positive', 'train', 5);

-- Mistake 2: a row with no label at all. It will train on NULL, or crash a
-- data loader six weeks from now, whichever is less convenient.
INSERT INTO examples_loose (text, label, split, token_count) VALUES
    ('a baffling second act', NULL, 'train', 4);

-- Mistake 3: a split value nobody intended. 'Test', 'testing' and 'test ' are
-- three different strings, and every one of them silently escapes your filter
-- WHERE split = 'test'.
INSERT INTO examples_loose (text, label, split, token_count) VALUES
    ('gorgeous photography', 'positive', 'Testing', 2);

-- Mistake 4: a label that is not one of your classes.
INSERT INTO examples_loose (text, label, split, token_count) VALUES
    ('it was fine I suppose', 'neutralish', 'train', 5);

-- Mistake 5: the word 'banana' in a column declared INTEGER. In an ordinary
-- SQLite table the declared type is only an affinity -- a preference, not a
-- rule -- so this is stored exactly as given, and typeof() will tell you so.
INSERT INTO examples_loose (text, label, split, token_count) VALUES
    ('unmeasured line', 'negative', 'train', 'banana');

SELECT 'rows accepted by the loose table: ' || count(*) FROM examples_loose;
SELECT 'duplicated texts:  '
       || (SELECT count(*) FROM (SELECT text FROM examples_loose
                                 GROUP BY text HAVING count(*) > 1));
SELECT 'rows with no label: ' || (SELECT count(*) FROM examples_loose WHERE label IS NULL);
SELECT 'distinct split values: '
       || (SELECT group_concat(DISTINCT split) FROM examples_loose);
SELECT 'token_count declared INTEGER, actually holding: '
       || (SELECT group_concat(DISTINCT typeof(token_count)) FROM examples_loose);
SELECT 'not one of these raised an error';

-- ---------------------------------------------------------------------------
-- The strict table: the same intent, written where the database can enforce it.
-- ---------------------------------------------------------------------------
-- Read the constraints as sentences:
--   "every example has text"                 -> NOT NULL
--   "no example appears twice"               -> UNIQUE
--   "every example is labelled"              -> NOT NULL
--   "a label is one of exactly three values" -> CHECK ... IN
--   "a split is train, validation or test"   -> CHECK ... IN
--   "a token count is a positive whole number" -> STRICT plus CHECK
--   "rows record when they arrived"          -> DEFAULT
--
-- Each line is documentation that cannot drift from the code, because it IS
-- the code. And unlike a comment or a README, it applies to the intern's
-- one-off script exactly as much as to your careful loader.
CREATE TABLE examples_strict (
    id          INTEGER PRIMARY KEY,
    text        TEXT NOT NULL UNIQUE,
    label       TEXT NOT NULL CHECK (label IN ('positive', 'negative', 'neutral')),
    split       TEXT NOT NULL CHECK (split IN ('train', 'validation', 'test')),
    token_count INTEGER NOT NULL CHECK (token_count > 0),
    added_on    TEXT NOT NULL DEFAULT (date('now')),

    CHECK (length(trim(text)) > 0)
) STRICT;

SELECT '';
SELECT '--- the strict table accepts the good rows ---';
INSERT INTO examples_strict (text, label, split, token_count) VALUES
    ('the film was a delight',  'positive', 'train',      5),
    ('a baffling second act',   'negative', 'train',      4),
    ('gorgeous photography',    'positive', 'test',       2),
    ('it was fine I suppose',   'neutral',  'validation', 5);
SELECT 'inserted ' || changes() || ' clean row(s)';
SELECT 'every one of the five mistakes above is now impossible, and the';
SELECT 'test harness runs seven bad rows and captures each real error';
