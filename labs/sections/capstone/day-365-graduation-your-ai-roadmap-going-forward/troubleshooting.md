# Troubleshooting — Day 365

## `NotImplementedError` on nearly every test

Expected. The starter stubs eight functions — see `expected-output/starter-run.txt`, which names the two tests that pass without them.

Fix them in order. Task 3, the load, produces the number the whole lab is about.

## "build up my understanding of evals" passes the actionability check

You are testing only for a leading action verb. That sentence starts with "build" and commits to nothing, and it is the single most common way of dressing a topic as an action.

A topic verb **anywhere** in the sentence disqualifies it, even when an action verb is also present. Check for topic verbs first and return early.

## `test_topic_verbs_are_listed_including_multiword_forms` fails

Your search is word-by-word, so the multi-word entries — "get better at", "read about" — never match. Test each entry as a substring of the lowered text, and check `startswith` as well so a sentence beginning with the verb is caught.

## `test_a_nonsensical_calibration_leaves_the_plan_alone` fails

A ratio of zero would silently zero every commitment's hours and report that the plan fits comfortably, which is the worst possible failure for this tool. Return the plan unchanged for any ratio at or below zero.

## `test_duplicate_commitments_are_not_confused_with_each_other` fails

`Commitment` is a frozen dataclass, so two identical commitments compare equal. A membership test like `c not in kept` therefore drops both. Compare by `id()`, or track indices.

## The trim shaves hours instead of dropping commitments

Deliberately not what this does. Six commitments at half the hours each is six things done badly; two at full hours is two things done. Drop whole commitments.

## A low-priority commitment survives while a high-priority one is cut

Correct, and worth understanding rather than fixing. The trim skips past a commitment too expensive to fit and carries on, because stopping would waste every remaining hour.

On the demo record the priority-2 open-source contribution is cut while the priority-2 writing survives, since 3.6 + 2.4 exceeds the 5.0 budget and 3.6 + 1.2 does not. The right response is usually to **split** the expensive commitment rather than accept the substitution — a judgement the tool cannot make for you.

## `review` reports a load that fits, but the demo says it does not

You are measuring the load before applying the calibration. Re-cost first, then measure everything — the load, the trim and the cuts — against the re-costed plan. Measuring the optimistic plan and then reporting a calibrated number is how a tool tells you something reassuring and wrong.

## The findings do not mention that calibration was applied

Add the disclosure line whenever the ratio is above 1.0. A reader looking at "needs 20.4h/week" is entitled to know those are your measured hours rather than the ones you wrote down.

## Everything is cut and the report is dispiriting

That is the finding. A plan four times over budget is not a discipline problem to be pushed through; it was impossible on the day it was written. Reduce the commitments, or reduce the hours each one claims, and run it again — the point of the check is that this conversation happens in week zero rather than week three.
