# Troubleshooting — Day 329

## The broken assistant passes a check it should fail

Your check is looking at the wrong place. Three specific traps:

- **`redaction_before_indexing`** must inspect `bot.chunks`, not the source documents. The broken assistant redacts nothing, so the identifier is in the chunk text.
- **`shared_budget`** must inspect `bot.ledger`. The broken assistant records retrieval into `side_ledger`, which is exactly the defect — a paid stage the cap does not see.
- **`erasure_is_complete`** must read all three stores back *after* erasing. The broken assistant clears the chunks and hashes correctly and leaves the cache, so a check that stops at the index passes.

## The audit fails checks on the conformant assistant

Usually a fixture problem rather than a check problem. `check_erasure_is_complete` must ask a question before erasing, or the cache is empty and the check proves nothing. `check_no_orphans_on_shrink` needs the first document to produce more than one chunk, or there is nothing to orphan.

## `test_it_names_exactly_the_three_planted_defects` fails

Your audit is failing more than the three planted defects. Precision matters as much as recall: an auditor that fails everything is as useless as one that fails nothing. Look at which extra check fired and why — most often it is a check that reports failure on an empty result rather than on a genuine violation.

## A failing check has no detail

Every `FAIL` should name what was found — the offending chunk ids, the missing ledger stage, the stores still holding the subject. A bare `FAIL` is a bug report nobody can act on. Build the detail string from the actual finding, not a fixed message.

## `AttributeError` on `side_ledger`

Only `BrokenAssistant` has it. Your check is reaching for it directly instead of inspecting `bot.ledger`, which is the surface the `AssistantLike` protocol defines. Audit the protocol, not the implementation.

## The cursor check passes on both assistants

That is correct. `BrokenAssistant` inherits the cursor behaviour and is not broken in that respect — only three of the five properties are violated. If your version fails it on the conformant assistant, check that you are comparing against seq 3, the dead-lettered document.

## `NotImplementedError` on most tests

Expected. The starter stubs all five check functions — see `expected-output/starter-run.txt`, which also names the five tests that pass without them.
