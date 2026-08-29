# Decision-engine design worksheet

Design your program *before* you code it. Fill in every section for a decision
engine of your own choosing (spam-or-not filter, loan pre-check, support-ticket
priority router, temperature alert — anything with clear rules). Then implement
it with the same shape as `triage.py`.

## 1. The job (one sentence)

> Example: Route a model prediction to AUTO_ACCEPT, REVIEW, or REJECT based on
> its confidence score and whether an upstream check passed.

_Your job:_

## 2. Inputs (what arrives, and from where)

List each input, its type, and where it comes from (command-line argument,
file, etc.).

| Input | Type | Source | Example |
| ----- | ---- | ------ | ------- |
| _e.g. score_ | _float 0.0-1.0_ | _sys.argv[1]_ | _0.95_ |
|  |  |  |  |

## 3. Rules (each as a boolean condition)

Write every rule as a condition, using `and` / `or` / `not`. Mark which one is
a **guard clause** (checked first, exits early) and note any **chained
comparison** (e.g. `0.0 <= score <= 1.0`).

- Guard clause: _________________________________________________
- Rule 1: _______________________________________________________
- Rule 2: _______________________________________________________
- Rule 3: _______________________________________________________

## 4. Outcomes (categories, and which rule leads to each)

| Outcome | Reached when | Exit code |
| ------- | ------------ | --------- |
| _e.g. AUTO_ACCEPT_ | _score >= 0.9 and verified_ | _0_ |
|  |  |  |

## 5. Edge cases you will reject

List at least three inputs your program must refuse, and the message it prints.

1.
2.
3.

## 6. Where a ternary fits

Name one place a conditional (ternary) expression makes a clean two-way (or
nested three-way) value choice.

>
