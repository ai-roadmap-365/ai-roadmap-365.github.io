# Troubleshooting — Day 330

## `NotImplementedError` on every test

Expected. The starter stubs twelve functions — see `expected-output/starter-run.txt`.

Fix them in order. `parse` comes first; nothing can be checked until instructions exist.

## `test_line_numbers_are_the_real_ones` fails

You are numbering the instructions you kept rather than the lines they came from. Comments and blank lines produce no layer but they do occupy lines, and the linter reports these numbers — an off-by-one sends the learner to the wrong line.

Track the line index while scanning, and record it when an instruction starts.

## A backslash continuation becomes several instructions

`RUN a \` / `&& b` is one instruction. Accumulate while a line ends with `\`, and only emit when it does not. Remember to record the line number of the **first** line of the group.

## `test_the_last_token_is_the_destination_not_a_source` fails

`COPY a.txt b.txt /dest/` has two sources and one destination. Drop the last token, and drop `--from=...` style flags before you do — otherwise `COPY --from=builder /wheels /wheels` reports the flag as a source.

## Everything after the first miss is still marked cached

The rule this lab exists for: a layer is reused only if **every layer before it** was reused as well. Once you record a miss, set a flag and mark the rest as misses regardless of their own inputs.

## The naive and ordered Dockerfiles rebuild in the same time

Check `_matches`. `COPY . .` must match every project path — if `.` only matches a file literally named `.`, the naive Dockerfile looks as good as the ordered one and the whole demonstration collapses.

## `test_a_change_to_a_file_nobody_copies_costs_nothing` fails

Editing `README.md` should cost nothing when no `COPY` reads it. If everything rebuilds, your matcher is treating an unrelated path as a match — most often by using `in` rather than a prefix test, so `src` matches `not-src/x.py`.

## `test_the_cold_builds_cost_about_the_same` fails

This is the honest part of the argument: reordering does not make a first build faster. If your cold builds differ by more than a few seconds, `plan_build` is skipping layers in cold mode instead of running all of them.

## The linter reports `apt-cache-kept` on a Dockerfile that does clean up

The cleanup must be in the **same** `RUN`. Check that your parser joined the backslash continuation into one instruction — if `&& rm -rf /var/lib/apt/lists/*` ended up as a separate entry, the check cannot see it.

## `test_a_correctly_ordered_dockerfile_is_clean` fails

Something is firing on the good Dockerfile. Print the findings and read them: the usual cause is `copy-before-install` triggering on `COPY requirements.txt .`, because the check is looking for any COPY rather than a **broad** one (`.` or `./`).
