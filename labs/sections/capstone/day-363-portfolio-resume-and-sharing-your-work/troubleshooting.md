# Troubleshooting — Day 363

## "from 0.71 to 0.94" is not detected as a measurement

Your pattern requires a unit. A ratio, a rate or a score is a legitimate measurement without one, and a stated change between two figures is the clearest form of all.

This lab had that bug: an earlier version graded the rewritten strong claim as `WEAK`, which would have pushed writers into padding sentences with units that do not fit the quantity. Add a case for `from <number> ... to <number>`.

## "state-of-the-art" is not flagged

Your vague-word list has the spaced form only. Both spellings are common in the wild; include them both.

## Every claim comes out `VAGUE`

You are grading `VAGUE` whenever a vague word appears. Vague requires **both** a vague word and no measurement — that is the claim which sounds like a result and contains none. A measured claim with a stray adjective is `WEAK`, because it is a small edit away from being strong.

## A local path passes the evidence check

Test the prefixes explicitly. `http://localhost`, `file://` and a bare leading `/` are all unopenable by a reader, and none of them is caught by simply checking for `http`.

Include the loopback IPs as well. `http://127.0.0.1:8080` and `https://[::1]` are exactly as unopenable as the name they stand for, and people write both — a checker that knows only the word `localhost` passes the numeric form straight through.

## `test_every_missing_property_is_named` fails

"Built a robust system." should produce exactly four reasons: vague wording, no measurement, unattributed, and no evidence link. If you get three, check that the measurement branch runs independently of the vague-word branch rather than inside an `elif`.

## `attribution` returns "mine" for "We improved my model"

That is correct — both singular and team wording are present, so the answer should be `mixed`. If yours returns `mine`, you are returning early on the first match instead of testing both before deciding.

## The measurement pattern matches a version number

`v1.2` and `Python 3.14` are numbers and are not results. This is a real limitation of a regular-expression approach and the reference implementation shares it: the unit requirement suppresses most cases, and a claim like "upgraded to 3.14" can still slip through. Worth knowing rather than worth over-engineering around.

## `NotImplementedError` on nearly every test

Expected. The starter stubs five functions — see `expected-output/starter-run.txt`, which also names the one test that passes without them.
