# Security notes — Day 325

## What this lab does and does not touch

- **No network.** Source and index are in-memory dictionaries. No test opens a socket, and `requires_network` is `false`.
- **No credentials.** No API key, token or account anywhere.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## The delete guard is a security control, not just a safety net

`safe_to_delete` looks like defensive programming, and it is also a genuine containment measure. Consider what a failed source enumeration looks like:

- an expired credential returning `200 OK` with an empty result set;
- a paginated API that stops at page one because a cursor was dropped;
- a permissions change that silently narrows what the enumerating identity can see.

In every case the enumeration *looks* successful and reports far fewer documents than exist. Without a guard, reconciliation faithfully concludes that the missing documents were deleted and empties the index — while reporting complete success.

Refusing the whole run is the correct response rather than deleting a "safe" subset. If the enumeration is wrong, every classification derived from it is wrong, so partial action is still action on bad input.

## Privacy: this is where erasure is actually honoured

Deletion propagation is the difference between a compliance story and a compliance failure. A record deleted from the primary system under a right-to-erasure request remains retrievable and quotable until the derived index also drops it.

Three consequences for real systems:

- **Deletion deserves a shorter tolerance than staleness.** Being an hour behind on edits is usually fine; being an hour behind on deletions may not be.
- **It needs its own test and its own alert**, not a line in a general freshness dashboard.
- **Caches count too.** An index that dropped the document but a response cache that did not is still serving it.

## Access

A freshness check reads the complete id list from both sides, so it needs broad read access — worth a least-privilege review, and worth keeping separate from any identity that can write.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
