# Week 09 project — Flashcard Study App

This week was about **functions and program design**: defining functions,
scope and closures, modules and project layout, the standard library, readable
code, recursion, and how to design a small program well. This project is where
you stop writing one long script and start building a **small, well-structured
application** — the habit every later course depends on.

## What you are building

A **command-line flashcard study app** with **spaced repetition**: you add
cards (question/answer), study the ones that are due, and grade each recall;
the app schedules the next review further out for cards you know and sooner for
cards you miss. Cards persist to a JSON file. The point of *this* project is not
the algorithm — it is the **structure**: clean modules, documented functions,
and a testable core separated from input/output.

## Requirements

Show this week's skills:

- **Clean module layout** (Day 59): organise the code as a small package —
  e.g. a pure-logic module (scheduling + card model), a storage module (JSON
  load/save), and a CLI/entry module with the `if __name__ == "__main__":`
  guard. No single giant file.
- **Documented functions** (Days 57, 61): every function has a docstring and,
  where it helps, type hints; names are meaningful; functions are small and do
  one thing (single responsibility).
- **Functional core, imperative shell** (Day 63): the scheduling logic is
  **pure** (given a card + a grade, return the updated card) with no printing
  or file access, so it can be unit-tested directly; I/O lives in the shell.
- **Standard library only** (Day 60): use `json`, `datetime`/`date`, and
  `pathlib`; `argparse` for the CLI. No third-party dependency required.
- **Spaced repetition** (Days 50–56 carried in): a simple, documented scheme is
  fine — e.g. an interval that grows on correct recall (1 → 3 → 7 → … days) and
  resets on a miss; "due" = next-review date on or before today.
- **Tested** (Days 47–49): tests target the pure core (scheduling, due
  selection) and run non-interactively against a temp store.

## Steps

1. Write the spec and two examples first (Day 63): a card is
   `{"q","a","interval","due","..."}`; grading `good` grows the interval,
   `again` resets it. Note 3 edge cases before coding.
2. Design the modules and function signatures (docstrings first), then fill in
   bodies.
3. Implement the **pure** scheduler: `schedule(card, grade, today) -> card`.
4. Implement storage (JSON load/save; missing file → empty deck; corrupt →
   clear error).
5. Implement the CLI: `add`, `study` (iterate due cards, prompt or accept
   grades non-interactively for tests), `list`, `stats`.
6. Write tests for the core and for due-selection; run them.
7. Validate against the checklist.

## Expected output

- `cards add -q "2+2?" -a "4"` → the deck JSON gains one card due today.
- `cards study --grade good` (or piped grades) → advances due cards; a graded
  card's next due date moves out by its new interval.
- A missed card (`again`) resets to the shortest interval and is due again soon.
- `cards list` / `cards stats` → show the deck and how many are due today,
  built with the collection idioms from Week 8.
- Re-running later only surfaces cards whose due date has arrived.

## Validation

- [ ] Code is a small package of modules by responsibility, not one file.
- [ ] The scheduling core is a **pure function** unit-tested without I/O.
- [ ] Cards persist to JSON; missing store starts empty; corrupt store errors
      clearly (no traceback).
- [ ] `add` / `study` / `list` work from the command line; study advances due
      dates correctly for good vs again.
- [ ] Every function has a docstring; names are clear; no `eval`.
- [ ] Tests cover scheduling and due-selection and run non-interactively.

## Troubleshooting

- Core hard to test? Make sure `schedule(...)` takes `today` as an argument and
  returns a new/updated card — no `print`, no file access, no `date.today()`
  inside it (pass the date in) so tests are deterministic.
- Everything due at once? Compare `due <= today` using ISO date strings or
  `date` objects consistently; store dates as `date.isoformat()`.
- Intervals not growing? Keep the interval on the card and compute the next due
  as `today + timedelta(days=interval)` after grading.
- CLI can't be tested? Accept grades via args/stdin in `study` so a test can
  drive a whole session without typing.
