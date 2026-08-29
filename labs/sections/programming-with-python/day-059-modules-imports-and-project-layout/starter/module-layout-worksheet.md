# Module-layout worksheet

Fill this in *before* you refactor `single_file.py`. Deciding the split on
paper first — which responsibility goes in which module, and which module
imports which — is exactly the discipline the lesson teaches. A layout you can
draw is a layout you can test.

## The program

- **What the whole program does (one sentence):**
- **Where the input comes from (file argument / standard input):**
- **What it prints:**

## Responsibilities → modules

List each distinct responsibility in the single-file program and the module it
will live in. One responsibility per module; a module should do one job.

| Responsibility (what it does) | Module (`.py` file) | Public functions |
| ----------------------------- | ------------------- | ---------------- |
| Text → list of words          | `tokens.py`         | `tokenize`       |
| Words → frequency numbers      | `stats.py`          | `count_words`, `top_n` |
| Read input, print the report   | `__main__.py`       | `report`, `main` |
| Define the package's public API | `__init__.py`      | (re-exports)     |

## Import direction (avoid circular imports)

Draw the arrows: which module imports which? They must never form a loop.

- `__main__.py` imports from: __________ and __________
- `__init__.py` imports from: __________ and __________
- `tokens.py` imports from: __________ (should be standard library only)
- `stats.py` imports from: __________ (should be standard library only)
- Is there any cycle (A imports B and B imports A)?  yes / no  → if yes, fix it.

## Import styles used

Name where in the package each style appears:

- `import name` (plain): __________
- `from module import name` (from-import): __________
- `import module as alias` (import-as): __________
- Relative import (leading dot, e.g. `from .tokens import tokenize`): __________
- Absolute import (full path, e.g. `from wordstats.tokens import tokenize`): __________

## The entry point

- Which file is run by `python3 -m wordstats`?  __________
- What line makes it run only when executed, not when imported?  __________
- Which function stays pure (no printing, no file reading) so it can be tested?
  __________

## Recorded behaviour (fill in after you build it)

- One good run (command and its output):
- One import (a `python3 -c "from wordstats import ..."` line and its output):
