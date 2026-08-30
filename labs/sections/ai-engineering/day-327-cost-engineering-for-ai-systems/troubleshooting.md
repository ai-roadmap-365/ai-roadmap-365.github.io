# Troubleshooting — Day 327

## Spend exceeds the budget

You are recording the call before checking the cap, or checking after the call returns. The check must be `spent() + cost > budget` **before** anything is appended to the ledger. Checking afterwards means the cap can be exceeded by the size of the last request — or without limit, if the caller retries.

## The cache never hits

Your key does not include the trimmed context, or it includes something that varies between calls. Two identical prompts with identical context must produce the same key. Build it from the prompt plus the kept chunks, after trimming.

## Cache hits do not appear in `by model`

You are returning early on a hit without appending a `Call`. Record the hit as a zero-cost call with `cached=True` instead — otherwise the hit rate is invisible in exactly the place you need it when attributing spend.

## Everything routes to the large model

Your heuristic is matching too eagerly. Lower the prompt once and test each hard word as a substring; do not compare the whole prompt for equality, and check the length threshold is `> 200` estimated tokens rather than characters.

## `trim_context` returns more than the budget allows

You are adding the chunk and then checking, rather than checking and then adding. Compute `used + size > budget_tokens` first and break.

## `trim_context` skips a large chunk and keeps a later small one

That is the packing behaviour, and this lab deliberately does not want it. Chunks arrive in priority order, so stopping at the first one that does not fit keeps the context contiguous in relevance. `test_trim_stops_rather_than_skipping_to_a_smaller_chunk` asserts this.

## `ZeroDivisionError` in `unit_economics`

A fresh ledger with zero requests is a normal state, not an edge case. Return zeros.

## `cost_of` returns 0.0 for a model you have not priced

You are using `PRICES.get(model, (0, 0))`. Raise `KeyError` instead — silently pricing an unknown model at zero is how a newly added model escapes accounting entirely, and the bill is the first anyone hears of it.

## The demo numbers do not match

The workload and prices are fixed, so a correct implementation reproduces the table exactly. Differences usually come from the assumed output token count (120), the token estimator (four characters per token), or from trimming before rather than after building the cache key.

## `NotImplementedError` on most tests

Expected. The starter stubs five functions — see `expected-output/starter-run.txt`, which also lists the three tests that pass without them.
