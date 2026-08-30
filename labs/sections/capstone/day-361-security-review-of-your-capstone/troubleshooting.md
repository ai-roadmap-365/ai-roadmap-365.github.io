# Troubleshooting — Day 361

## The sound posture reports findings

Most often `check_tool_permissions` matching `read:docs`. `DESTRUCTIVE_SCOPES` must be tested as a **prefix** — `s.startswith(DESTRUCTIVE_SCOPES)` — not as a substring search, or any scope containing those characters matches.

## A single configuration change trips several checks

Your checks are reading overlapping fields. Each should own one area and consult only its own settings. This matters beyond tidiness: if one change lights up four findings, the report cannot tell you which decision to reverse.

## A confirmed destructive scope still reports HIGH

Compare the risky scopes against `tools_require_confirmation` before choosing the severity. Present-and-confirmed is `LOW`; present-and-unconfirmed is `HIGH`.

## `test_one_missing_cap_is_less_severe_than_both` fails

Severity accumulates. Both caps missing is `HIGH`; exactly one missing is `MEDIUM`. Count the missing caps rather than returning a fixed severity whenever any is absent.

## The verdict passes with a MEDIUM finding

Only `OK` and `LOW` pass. Check the comparison in `summary` — `worst in (Severity.OK, Severity.LOW)`.

## `test_findings_that_fail_carry_remediation` fails

Every non-OK finding needs a remediation, with one deliberate exception: the `LOW` tool-permissions finding, which records a confirmed destructive scope and has nothing to fix. If yours fails on a different check, that check is producing a complaint rather than a review.

## `test_secrets_in_the_repository_is_high_and_mentions_rotation` fails

The remediation must contain the word "rotate". This is not a formatting requirement — deleting a committed secret does not remove it from history, so rotation is the actual first step and the finding should say so.

## `test_the_weak_posture_trips_every_check` fails

Precision as well as recall. All seven checks must report a problem on `WEAK` and none on `SOUND`. If a check reports OK on the weak posture, it is reading a field the weak posture does not change.

## `NotImplementedError` on every test

Expected. The starter stubs all seven checks, and every test runs at least one of them — including the tests asserting the sound posture passes, since those still have to run the checks to find out.
