# Troubleshooting — Day 328

## A stray `+` remains after redacting a phone number

A word boundary cannot match before `+`, because `+` is not a word character, so a pattern starting `\b\+?` begins matching at the first digit and leaves the country code behind. Use a negative lookbehind on word characters instead: `(?<![\w+])`.

The leftover `+` is cosmetic on its own. Treat it as a signal that the match was partial — the same class of bug that leaves half a card number in the text.

## A card number is reported as a phone number

Your detectors run in the wrong order. `ORDER` puts the longer, more specific patterns first, and each match claims its span so later detectors skip anything overlapping. Without that, the phone matcher takes a slice of the card and the remaining digits stay in the output while the run reports success.

## Pseudonyms differ for the same value

You are generating a fresh salt per call, or including the match position in the hash. The same value must always produce the same token, or records stop linking and the redacted data loses its debugging value.

## A test asserting a fragment is absent fails on correct output

Check whether the fragment is valid hexadecimal. A SHA-256 digest is hex, so short lowercase-hex strings such as `ada`, `beef` or `cafe` appear inside tokens by coincidence. This happened while writing this lab: an assertion that the token did not contain `"ada"` failed against a perfectly correct redactor.

Assert on the whole identifier, and on fragments containing non-hex characters such as `@` or a dot. A privacy test that raises false alarms gets muted, and a muted test protects nothing.

## Erasure reports `COMPLETE` when stores still hold the subject

You are building the report from the return values of the delete calls. Re-read `flow.where(subject_id)` *after* deleting and put whatever comes back in `still_present`. "We ran the deletion" and "the data is gone" are different claims, and only the read-back supports the second.

## `erase` deletes from stores it should not

Passing `stores=None` targets every store in the flow, which is what a full erasure wants. Pass an explicit list when you deliberately want a partial run — the demo does this to show the failure.

## Redaction shifts the wrong characters

You are applying replacements front to back, so each substitution invalidates the offsets of the ones after it. Apply them from the end of the string backwards.

## `NotImplementedError` on most tests

Expected. The starter stubs `pseudonym`, `redact`, `erase` and `minimise` — see `expected-output/starter-run.txt`, which also names the three tests that pass without them.
