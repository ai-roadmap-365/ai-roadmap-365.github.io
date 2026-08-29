# Iteration pattern worksheet — Day 051

Use this sheet for the **practice assignment**: design a sixth pattern of
your own *before* you code it, then record how it behaved. Designing the loop
on paper first is the habit that prevents infinite loops and off-by-one
errors. Keep this file — the collections you meet on Days 52-54 give you
richer things to iterate over with exactly these patterns.

## 1. What one job does your new pattern do?

One sentence:

> _e.g. Report the largest number and the index where it first appeared._

## 2. Which loop shape, and why?

- [ ] `for` loop — I am visiting each item of a known collection once
- [ ] `while` loop — I am repeating until a condition becomes false

Reason:

> _________________________________________________________________________

## 3. Accumulator design

| Question | Answer |
| -------- | ------ |
| What variable(s) build up the result? |  |
| What neutral value does each start at? (0, "", [], None, ...) |  |
| What happens to it on each pass? |  |
| Do you `break` early? If so, on what condition? |  |

## 4. Inputs and outputs

- Input source (stdin / a fixed sample / argv): ____________________
- On success, it prints: ____________________  (exit code ____)
- On bad input, it prints (to stderr): ____________________  (exit code ____)

## 5. Edge cases — at least two

| Edge case | What the loop should do |
| --------- | ----------------------- |
| empty input (no numbers) |  |
| a single-item input |  |
| _(your choice)_ |  |

## 6. Behaviour on real inputs (fill in after building)

- One NORMAL input you ran: `___________________`
  - What it printed: `___________________`
  - Exit code: ____
- One EDGE-CASE input you ran: `___________________`
  - What it printed: `___________________`
  - Exit code: ____

## 7. Cost check

If your pattern used a nested loop, how many times would the inner body run
on an input of N items? (Use the outer-times-inner rule.)

> _________________________________________________________________________
