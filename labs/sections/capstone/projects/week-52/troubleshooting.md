# Troubleshooting — Week 52 project

## `NotImplementedError` on every test

Expected. The starter stubs seven functions and nothing passes by accident — even "is this evidence checkable" is task 1. See `expected-output/starter-run.txt`.

Fix them in order. Task 2 is the one to get right first.

## Undated evidence comes out fresh

The dangerous bug. `age_days` must treat missing `verified_on` as ancient, not as zero. An undated claim is one nobody remembers checking, and defaulting it to today lets the least verified evidence in the delivery pass silently.

`test_evidence_with_no_date_is_treated_as_ancient` pins this.

## A `COMMAND` with an empty detail passes as checkable

A checkable *kind* is not enough. `Kind.COMMAND` with no command in it is nobody's evidence. Test the detail as well, and strip it — whitespace is not a command.

## The verdict changes when evidence is listed in a different order

`evidence_for` is returning the first match instead of the best. A requirement backed by both an assertion and a command is backed by the command, and the order somebody typed them in must not decide it.

`Kind` is declared in ascending order of worth, so `list(Kind)` gives you the ranking directly.

## A requirement appears in two categories

The categories are exclusive. Use `elif`, and check in the order missing, weak, stale, solid — the advice differs per category, and a requirement with no evidence is missing rather than stale even though it has no date.

## Everything is a blocker, including the optional requirements

`blockers` filters on `req.blocking`. An optional requirement still appears in `missing` or `weak` and still generates a finding; it just does not stop delivery.

## `test_blockers_are_ordered_missing_then_weak_then_stale` fails

You are iterating the requirements list rather than the three category lists. Iterate `missing`, then `weak`, then `stale`, which is the order the work should be done in — and de-duplicate, because a requirement can only be in one category but the guard makes the intent explicit.

## The demo exits non-zero

Correct. The fixture delivery is not ready, and the demo returns 1 to say so. A gate that always exits 0 is not a gate.

## The gate says ready and you know the capstone is not

Then the manifest is wrong, not the gate. Almost always it is a requirement backed by a `FILE` that should be a `COMMAND` — a document describing a check is not the check — or a requirement that is not in the list at all. Add it, and mark it blocking.
