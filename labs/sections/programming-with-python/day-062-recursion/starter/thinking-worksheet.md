# Recursion design worksheet

Fill this in *before* writing code for the practice assignment. The whole
skill of recursion is naming the **base case** and the **recursive case**
before you touch the keyboard — this worksheet forces exactly that. One row
per function you design.

## The problem

- **What are you computing (one sentence):**
- **What is the input, and how is it "smaller" on each call:**
- **What does a single, plain (non-recursive) piece of the input look like:**

## Base case and recursive case

For each recursive function you write, fill one row.

| Function | Base case (when to STOP, and what to return) | Recursive case (the smaller subproblem, and how you combine it) |
| -------- | -------------------------------------------- | --------------------------------------------------------------- |
|          |                                              |                                                                 |
|          |                                              |                                                                 |

## Termination check

For each function, answer: **why is every recursive call guaranteed to move
closer to the base case?** (If you cannot answer this, the function may recurse
forever and hit `RecursionError`.)

1.
2.

## Recursion vs iteration

For each function, would a plain loop be simpler or clearer? Say which you
chose and why. (Recursion shines for tree/nested-structure problems; a loop
is often better for a flat sequence.)

-
-

## Recorded behaviour (fill in after you build it)

- One good run (command and its output):
- One rejected/edge run (command, message, and `echo $?`):
- If you wrote a Fibonacci-style function twice (naive and memoized), the two
  call counts you measured:
