# Week 07 project — Command-Line Calculator

The first week of Python taught you environments, types, strings, numbers
and precision, input/output, debugging, and how to structure a complete
program. This project combines all of it into one real, well-built tool.

## What you are building

A command-line calculator that parses an arithmetic expression, evaluates it
**safely** (no `eval`), handles bad input gracefully, and prints a clearly
formatted result. It should be a *real* program: a `main()` function, the
`if __name__ == "__main__":` guard, docstrings, input validation, and its
own tests.

## Requirements

Show each of this week's skills:

- **Runs in a venv** (Day 43): a `requirements.txt` (even if empty, stdlib
  only) and a note to run inside a virtual environment.
- **Correct number handling** (Day 46): integer vs float division, and use
  `decimal.Decimal` for exact results where it matters; compare floats with
  `math.isclose`, never `==`.
- **String parsing** (Day 45): read the expression, split/clean it, and
  build the output with f-strings and sensible formatting.
- **Safe input** (Days 44, 47): take the expression from `sys.argv` or
  stdin so it's testable non-interactively; convert and validate; **never
  `eval` user input** — parse it yourself or use a safe evaluator you write.
- **Graceful errors** (Day 48): division by zero, malformed input, and
  unknown operators produce a clear message on stderr and a non-zero exit —
  no raw traceback dumped at the user.
- **Real structure** (Day 49): functions with docstrings, a `main()` guard,
  and a small set of tests (assertions or a `tests/` script) that run
  non-interactively.

## Steps

1. Design first (Day 49): inputs → parse → evaluate → format → errors. Write
   down 3 edge cases before coding.
2. Implement a safe evaluator (support at least `+ - * /` with correct
   precedence, or accept space-separated `a op b` to start simple).
3. Add input validation and clear error handling.
4. Format the output with f-strings; use Decimal for exact division where
   appropriate.
5. Write tests that run it on known good and bad inputs.
6. Validate against the checklist.

## Expected output

- `calc.py "2 + 3 * 4"` (or `echo "2 + 3 * 4" | python3 calc.py`) prints
  `14` with correct precedence.
- A division prints an exact or sensibly-rounded result, not a float-noise
  value like `4.199999999999999`.
- Bad input (`2 + `, `2 / 0`, `2 ^ 3`) prints a clear error to stderr and
  exits non-zero — never a raw traceback.

## Validation

- [ ] No `eval()` on user input anywhere (safety).
- [ ] Correct operator precedence, or a documented simpler grammar.
- [ ] Exact/clean numeric output (Decimal or sensible rounding; `isclose`
      for float comparisons).
- [ ] Division by zero and malformed input handled gracefully (stderr +
      non-zero exit).
- [ ] `main()` + `if __name__ == "__main__":` guard; functions have
      docstrings.
- [ ] Tests run non-interactively and cover good and bad inputs.
- [ ] A `requirements.txt` and a note to run in a venv.

## Troubleshooting

- Never `eval()` — it's a remote-code-execution risk. Parse the expression
  (a small shunting-yard or recursive parser), or start with `a op b`.
- Float surprises? Use `decimal.Decimal("...")` (from strings, not floats)
  for exact math, and `math.isclose` to compare (Day 46).
- Testing an interactive program? Feed input via `sys.argv` or a pipe so
  tests are non-interactive (Day 47).
- Getting a traceback at the user? Catch the exception at the top of
  `main()`, print a friendly message to stderr, and `sys.exit(1)` (Day 48).
