# Troubleshooting — Day 323

## The index doubles on the second run

Your chunk id depends on something that varies between runs — a global counter, a timestamp, `uuid4()`, or `id()`. A stable id must be derived from the document id plus the chunk's position within that document, so the same input always produces the same id and the write becomes an update.

Check with:

```bash
python3 -c "
import sys; sys.path.insert(0,'examples')
from ingest import chunk_document
a=[c.chunk_id for c in chunk_document('d','x '*100)]
b=[c.chunk_id for c in chunk_document('d','x '*100)]
print('stable' if a==b else 'NOT STABLE')"
```

## Run 2 re-embeds everything

Either you are comparing modification times instead of content hashes, or you are hashing something that varies. Hash the normalised body only — `" ".join(text.split())` before digesting — so a source that reformats whitespace on read does not look changed.

## `test_crash_resumes_from_last_committed_cursor` fails

You are committing the cursor before the batch is written. Move `checkpoint.cursor = record.seq` to after the `index.upsert(...)` call. Committing first means a crash between the two silently skips the record forever.

## One bad document ends the run

`extract()` raises `ExtractionError` for `doc-3`, which has no payload. Wrap the call in `try/except ExtractionError`, append a `DeadLetter(doc_id, error=type(exc).__name__)`, count it, advance the cursor and `continue`. If you re-raise, the run dies and the four healthy documents never index.

## `test_shrinking_document_leaves_no_orphaned_chunks` fails

Upserting the new chunks is not enough. After writing, call `index.delete_orphans(doc_id, keep)` with the set of chunk ids you just wrote, so chunks from the longer previous version are removed. Orphans stay retrievable and produce stale answers.

## `NotImplementedError` everywhere

Expected. The starter stubs `content_hash`, `chunk_document` and `run_once`. See `expected-output/starter-run.txt` — an untouched starter fails 10 of 11 tests, and the one that passes does not depend on the stubs.

## `ModuleNotFoundError: No module named 'ingest'`

Run the tests through `bash tests/run_tests.sh`, which changes into the lab root first. The test file inserts `examples/` onto `sys.path` relative to its own location, so running `pytest` from elsewhere can miss it.

## `TypeError` on `str | None`

You are on Python 3.9 or older. This lab needs 3.10 or newer for that type syntax. Check with `python3 --version`.
