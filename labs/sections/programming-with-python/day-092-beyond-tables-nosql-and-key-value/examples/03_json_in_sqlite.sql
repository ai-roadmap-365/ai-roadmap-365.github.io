-- Day 092 · Step 3 — the same library as JSON documents, inside a relational
-- database.
--
-- This is the pragmatic middle path, and for most teams it is the one to try
-- before reaching for a separate document database. The whole book is one JSON
-- value in one column; the engine can still filter, sort, aggregate, join and
-- transact over it.
--
-- Run with:  sqlite3 docs.db < examples/03_json_in_sqlite.sql
--
-- Everything below uses only functions in SQLite's built-in JSON support. Check
-- what your build has before relying on it:
--
--   sqlite3 :memory: "select json_extract('{\"a\":1}','\$.a');"
--
-- The captures in expected-output/ were taken with the sqlite3 shell 3.51.0.

DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
  doc_id INTEGER PRIMARY KEY,
  body   TEXT NOT NULL CHECK (json_valid(body))
);

-- The CHECK is the one piece of schema left. It does not say what fields a
-- book has; it says only that the blob parses. That is the whole of what
-- "schema-on-read" leaves you at write time.

INSERT INTO documents (doc_id, body) VALUES
  (101, '{"book_id":101,"title":"The C Programming Language","published_year":1978,"shelf":"A3","authors":["Brian W. Kernighan","Dennis M. Ritchie"]}'),
  (102, '{"book_id":102,"title":"The Mythical Man-Month","published_year":1975,"shelf":"B1","authors":["Frederick P. Brooks Jr."]}'),
  (103, '{"book_id":103,"title":"Artificial Intelligence: A Modern Approach","published_year":1995,"shelf":"C2","authors":["Stuart J. Russell","Peter Norvig"]}'),
  (104, '{"book_id":104,"title":"The Practice of Programming","published_year":1999,"shelf":"A3","authors":["Brian W. Kernighan","Rob Pike"]}');

.mode column
.headers on

.print '--- 1. reach inside the document with json_extract ---'
SELECT doc_id,
       json_extract(body, '$.title')          AS title,
       json_extract(body, '$.published_year') AS year
  FROM documents
 ORDER BY doc_id;

.print ''
.print '--- 2. the -> and ->> operators say the same thing more briefly ---'
-- ->  returns JSON  (a quoted string stays quoted)
-- ->> returns a SQL value (text, integer, real or NULL)
SELECT doc_id,
       body ->  '$.published_year'         AS arrow_json,
       typeof(body ->  '$.published_year') AS arrow_type,
       body ->> '$.published_year'         AS arrow2_value,
       typeof(body ->> '$.published_year') AS arrow2_type
  FROM documents
 WHERE doc_id = 101;

.print ''
.print '--- 3. filter and aggregate on a field inside the document ---'
SELECT json_extract(body, '$.shelf') AS shelf, count(*) AS books
  FROM documents
 GROUP BY shelf
 ORDER BY shelf;

.print ''
.print '--- 4. json_each unrolls the nested array the relational model needed'
.print '       a junction table for ---'
SELECT author.value AS author, count(*) AS books
  FROM documents, json_each(documents.body, '$.authors') AS author
 GROUP BY author.value
 ORDER BY books DESC, author
 LIMIT 3;

.print ''
.print '--- 5. what the planner does without an index ---'
EXPLAIN QUERY PLAN
SELECT doc_id FROM documents WHERE json_extract(body, '$.shelf') = 'A3';

.print ''
.print '--- 6. an index on an EXTRACTED field, then the same plan again ---'
CREATE INDEX idx_documents_shelf ON documents (json_extract(body, '$.shelf'));
EXPLAIN QUERY PLAN
SELECT doc_id FROM documents WHERE json_extract(body, '$.shelf') = 'A3';

.print ''
.print '--- 7. the catch: the index only helps the EXACT expression it indexes'
.print '       (->> here spells the same question a different way) ---'
EXPLAIN QUERY PLAN
SELECT doc_id FROM documents WHERE body ->> '$.shelf' = 'A3';

.print ''
.print '--- 8. schema-on-read: the misspelled document is accepted ---'
INSERT INTO documents (doc_id, body) VALUES
  (105, '{"book_id":105,"titel":"Compilers: Principles, Techniques, and Tools","published_year":1986,"shelf":"C1","authors":["Alfred V. Aho","Ravi Sethi","Jeffrey D. Ullman"]}');
SELECT changes() AS rows_inserted;

.print ''
.print '--- 9. and it is invisible to every query that asks for a title ---'
SELECT count(*) AS documents_in_table,
       count(json_extract(body, '$.title')) AS documents_with_a_title
  FROM documents;

SELECT doc_id, json_extract(body, '$.title') AS title
  FROM documents
 WHERE json_extract(body, '$.title') LIKE '%Compilers%';

.print '(zero rows above: the book is in the table, and the query cannot see it)'
