# Week 08 project — Terminal Task Manager

This week you learned control flow and every core collection: conditionals and
boolean logic, loops and iteration patterns, lists, dictionaries, tuples and
sets, comprehensions and iterators, and how to wrap it all in a data-driven
CLI. This project combines all of it into one real, useful tool you will
actually want to keep.

## What you are building

A **command-line to-do manager** that stores tasks in a JSON file and supports
`add`, `list`, `complete`, and `delete` commands. Each task is a dictionary
(id, text, done, created); all tasks are a list persisted to disk. It must be a
*real* program — argparse subcommands, input validation, graceful errors on
stderr, proper exit codes, and its own non-interactive tests.

## Requirements

Show each of this week's skills:

- **Collections done right** (Days 52–54): tasks are a **list of dicts**; use
  dictionary access idioms (`.get`, membership) and pick the right collection
  for each job (e.g. a **set** to detect duplicate task text if you add that).
- **Control flow** (Days 50–51): `complete`/`delete` find a task by id with a
  loop or comprehension and branch cleanly (guard clauses, no deep nesting);
  `list` filters by status (`--all`, `--done`, `--pending`).
- **Comprehensions / iterator thinking** (Day 55): use a comprehension to
  filter or transform tasks for display and for the "pending count" summary.
- **A data-driven CLI** (Day 56): **argparse** subcommands; persist to a
  **JSON** file (`json.load`/`dump`); read the store path from an option or a
  sensible default; never `eval`.
- **Robustness** (Course 02 so far): a missing or empty store starts clean; a
  corrupt store fails with a clear message, not a traceback; unknown ids exit
  non-zero with a message on stderr.
- **Testable** (Days 47–49): every command works from `sys.argv` against a
  temp store so tests run non-interactively.

## Steps

1. Design the data first: one task = `{"id": int, "text": str, "done": bool,
   "created": str}`; the store = a JSON list of those. Write down three edge
   cases before coding.
2. Build the argparse parser with four subcommands and a `--store` option.
3. Implement load/save (missing file → `[]`; corrupt JSON → clear error).
4. Implement `add` (append with the next id), `list` (filter + format),
   `complete` (flip `done` by id), `delete` (remove by id).
5. Print clear output and return exit codes: `0` on success, non-zero on a bad
   id or bad input.
6. Write tests that drive it end to end against a temp file.
7. Validate against the checklist.

## Expected output

- `tasks add "Write the report"` → `Added task 1: Write the report`, and the
  JSON store now holds one task.
- `tasks list` → a numbered list showing status (`[ ]` / `[x]`) and a pending
  count summary line built from a comprehension.
- `tasks complete 1` → marks it done; `tasks list --pending` no longer shows it.
- `tasks delete 9` (no such id) → clear message on stderr, exit non-zero — no
  traceback.
- Deleting the last task leaves a valid empty store (`[]`), not a broken file.

## Validation

- [ ] Tasks persist to a JSON file (list of dicts) across separate runs.
- [ ] `add` / `list` / `complete` / `delete` all work from the command line.
- [ ] `list` filters by status and shows a comprehension-built pending count.
- [ ] Missing store starts clean; corrupt store gives a clear error (no
      traceback); unknown id exits non-zero on stderr.
- [ ] No `eval`; input is parsed and validated.
- [ ] `main()` + `if __name__ == "__main__":` guard; functions have docstrings.
- [ ] Tests run non-interactively against a temp store and cover good and bad
      input.

## Troubleshooting

- Store not persisting? Make sure you `json.dump` back to the **same** path you
  loaded from, and that `add` writes after appending.
- Traceback on first run? Treat a missing file as an empty list (`[]`) before
  reading it; wrap `json.load` and catch `JSONDecodeError` for a corrupt store.
- Ids drift after deletes? Compute the next id from `max(existing ids) + 1`
  (or a stored counter), not `len(tasks) + 1`.
- Interactive-only and hard to test? Keep all input in `sys.argv`/argparse so a
  test can call the CLI with a `--store` temp file.
