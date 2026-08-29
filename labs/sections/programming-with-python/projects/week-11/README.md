# Week 11 project — Tested Utility Library

This week was about **testing and code quality**: why we test and pytest
basics, fixtures and parametrization, test-driven development, mocking and
testing boundaries, static typing with mypy, linting and formatting with Ruff,
and assembling quality gates. This project is where those seven days stop being
seven separate tools and become one habit: a small library you would let a
stranger depend on, with a single command that says whether it is safe to
change.

## What you are building

A **text utilities library** called `textkit`, built test-first, typed strictly,
linted clean, and guarded by one `check.sh` that runs every gate in order. The
library itself is deliberately modest — six or seven honest functions — because
the deliverable this week is not the feature list. It is the evidence: a suite
that provably fails when the code is wrong, annotations a checker has actually
read, and a gate that a change cannot sneak past.

The functions are chosen because each one hides an edge case that a careless
test would miss, and one of them touches a boundary, so you have something real
to inject rather than something to mock.

## Requirements

Show this week's skills:

- **Test-first, with recorded evidence** (Day 73): every function begins as a
  failing test. Keep a short `CYCLES.md` noting, per function, the failure you
  saw before the code existed. A red you never saw is a red you cannot claim.
- **Tests that provably bite** (Day 71): for at least three functions, break the
  implementation on purpose in a scratch copy, confirm the suite goes red, and
  record which test caught it. A test that survives a broken implementation is
  not a test.
- **Fixtures and parametrization doing real work** (Day 72): the edge-case
  tables — empty string, whitespace only, unicode, an already-clean input, a
  pathological long input — belong in `@pytest.mark.parametrize` with readable
  `ids`, not in seven copy-pasted functions. Use `tmp_path` where you need a
  file, and register any custom marker.
- **A boundary you injected rather than patched** (Day 74): one function depends
  on the clock or on a source of randomness. Pass it in. The test then needs no
  patching at all, and you should be able to say in one sentence why that is
  better than `patch`. Use `unittest.mock` somewhere too, with `autospec`, so
  you have exercised both approaches and can compare them honestly.
- **Strict typing that found something** (Day 75): the package is annotated and
  passes mypy under strict settings. At least one `X | None` return exists and
  is narrowed at every call site. Record one error mypy caught that the tests
  did not — if you genuinely hit none, say so and explain what the checker is
  covering instead.
- **Lint and format as configuration, not vibes** (Day 76): a real
  `[tool.ruff]` section with a rule set you chose deliberately, per-file ignores
  for `tests/` if you want them, and any suppression carrying a specific rule
  code. `ruff format --check` passes.
- **One gate, five stages, honest ordering** (Day 77): `check.sh` runs format,
  lint, types, tests, coverage — cheapest first — and exits non-zero if any
  stage fails. One `pyproject.toml` configures all of it. Set a coverage floor
  you can actually hold, and be able to explain why the number is an alarm and
  not a goal.

## Steps

1. Write the function list and, beside each, the edge case you expect to be
   the one that bites. Keep the list; you will check it at the end.
2. Set up the project layout — `src/textkit/`, `tests/`, `pyproject.toml` — and
   get an empty suite running green before writing any feature.
3. Build `check.sh` with a single stage (tests) and confirm it exits non-zero
   when a test fails. Add the other stages only after each one has failed once
   on purpose.
4. Take the first function through a full red-green-refactor cycle, recording
   the red. Resist writing the second test before the first is green.
5. Convert the edge cases into parametrized tables as soon as you have three
   near-identical tests.
6. Add annotations as you go, not at the end, and run mypy often enough that it
   never reports more than a handful of errors at once.
7. Introduce the boundary function last, injected from the start, and write its
   test with a hand-written fake before you try a mock.
8. Turn on the coverage stage, look at what is uncovered, and decide honestly
   which gaps deserve a test and which are noise.
9. Break the library in three different ways and confirm the gate catches each.

## Expected output

- `bash check.sh` on the finished library → each stage reported in order and a
  final success line, exit code 0.
- `bash check.sh` with a deliberately misformatted file → the format stage
  fails, later stages do not run, exit code non-zero.
- `bash check.sh` with an unused import added → the lint stage fails naming the
  rule code, exit code non-zero.
- `bash check.sh` with a return annotation changed to the wrong type → the type
  stage fails naming the mypy error code, exit code non-zero.
- `bash check.sh` with one function's arithmetic altered → the test stage fails,
  naming the test that caught it and showing both sides of the assertion.
- `bash check.sh` with a new untested function appended → the coverage stage
  fails, reporting the total against the floor.
- `pytest --collect-only -q` → an item count noticeably larger than the number
  of test functions you wrote, because the parametrized tables expanded.
- `mypy src/` → no issues found, under the strict settings recorded in
  `pyproject.toml`.

## Validation

- [ ] Every public function has a type annotation, a docstring, and at least one
      test that fails when the function is broken.
- [ ] `CYCLES.md` records a real observed failure for each function, and the
      three break-it experiments name the test that caught each break.
- [ ] Edge cases live in parametrized tables with readable ids; no three
      near-identical test functions remain.
- [ ] The boundary-dependent function takes its dependency as a parameter, and
      its primary test uses no patching.
- [ ] `autospec` is used somewhere, and you can state what an un-specced mock
      would have let through.
- [ ] `mypy` passes under strict settings; no bare `type: ignore` exists — every
      suppression carries a specific code.
- [ ] `ruff check` and `ruff format --check` both pass; the rule set was chosen
      deliberately and you can justify each rule you disabled.
- [ ] `check.sh` is one command, runs the five stages in cost order, and exits
      non-zero if any stage fails.
- [ ] Each of the five stages has been observed failing at least once, on
      purpose — a gate you have never seen fail is a gate you cannot trust.
- [ ] The coverage floor is set to a number the library currently holds, and you
      can explain why chasing a higher number would not necessarily help.

## Troubleshooting

- Gate passes but the library is broken? Your tests execute the code without
  asserting on it. Check whether any test has no `assert` at all — coverage will
  happily call that line covered.
- Coverage at 100% and you still shipped a bug? Coverage measures lines
  executed, never claims checked. Look for the branch you never took, not the
  line you never ran.
- mypy reporting nothing on a file you know is wrong? Something in the path is
  `Any` — a missing annotation on a parameter is enough to silence checks
  downstream of it. Turn on `disallow_untyped_defs` and look again.
- Ruff and the formatter disagreeing forever? You have a lint rule fighting the
  formatter. Formatting rules belong to the formatter; remove the overlapping
  lint rule rather than adding a suppression to every file.
- A test that passes alone and fails in the suite? Shared mutable state between
  tests. A module-level list or a session-scoped fixture being mutated is the
  usual culprit; make the fixture function-scoped and see if the failure moves.
- Patching a name and nothing happening? You patched where the function is
  defined, not where it is looked up. Patch the name in the module that calls
  it — and consider whether injecting it would remove the problem entirely.
- The gate takes long enough that you skip it? That is data, not a character
  flaw. Move the slow stage out of the pre-commit path and keep it in the full
  run; a gate people bypass protects nothing.
