# Flexible-functions design worksheet

Fill this in *before* writing code for the practice assignment. Designing each
function on paper first — its signature, what it gathers or captures, and its
edge cases — is exactly the discipline this lesson teaches. One row per
function.

## The functions

| Function | Signature | Uses *args / **kwargs / closure? | What it gathers or captures | Returns |
| -------- | --------- | -------------------------------- | --------------------------- | ------- |
| (variadic aggregator) |  |  |  |  |
| (closure factory)     |  |  |  |  |
| (**kwargs config merge) |  |  |  |  |

## Calls and edge cases

For each function, write one ordinary call and one edge case (empty input, an
override, or a second independent instance) with the value you expect.

1. Aggregator — good call / edge case:
2. Closure factory — good call / edge case (prove it remembers state or that two
   instances are independent):
3. Config merge — good call / edge case (an override that wins over a default):

## Scope check

For your closure factory, answer in one line each:

- What variable does the inner function capture, and from which scope?
- Does the inner function need `nonlocal`? Why or why not?
- Do two instances made by two factory calls share state or not? Why?

## Recorded behaviour (fill in after you build it)

- The demo output of `python3 <your-file>.py`:
- The three `assert` lines you wrote and that they all passed (script exited 0):
