# Troubleshooting — Week 47 project

## The second ingest run scans documents again

The cursor is not advancing, or it is advancing only on success. It must advance on every outcome including a dead letter — otherwise the poison document is retried forever and the pipeline never moves past it.

## `test_identifiers_are_redacted_before_indexing` fails

You are redacting after chunking, or not at all. Redaction must run before the content hash, before chunking and before embedding. This is an ordering bug with an expensive consequence: identifiers inside vectors can only be removed by re-embedding.

## An edited document produces duplicate chunks

Your chunk ids are not stable, or you are not deleting the chunks that the new version no longer produces. Ids must be `f"{doc_id}::{position}"`, and after writing the new set you must remove any remaining chunk of that document that is not in it.

## `test_erased_document_can_be_reingested_cleanly` fails

You deleted the chunks but left the content hash. A later re-ingest then compares against the stale hash, concludes nothing changed, and never restores the document. Clearing the hash is part of the erasure.

## `verified` reports `True` for the cache when an answer still cites the document

You are checking whether the delete ran rather than reading back. Recompute from the actual cache contents after clearing.

## Retrieval does not appear in the cost breakdown

`retrieve` must append to the same ledger that `answer` uses. If retrieval has its own accounting, a recall setting stops being visible as a cost setting, and the cap does not bound the whole request.

## The budget refusal reports a negative remainder

Retrieval has already spent past the cap by the time generation is priced. Clamp the reported remainder at zero — and note this is a real property, not a display bug: a stage that spends before the check can push you over on its own.

## Retrieval ranks the wrong document first

Check the embedding dimension. At `dim=8` unrelated words are forced into the same buckets and similarity becomes noise; an early version of this project used `dim=24` and ranked the SLA page above the refunds page for "what is the refund window". Collision rate is a retrieval-quality parameter.

## `NotImplementedError` on most tests

Expected. The starter stubs `ingest`, `answer` and `erase` — see `expected-output/starter-run.txt`, which also names the four tests that pass without them.
