# Quality worksheet — Day 37 lab

Fill this in for `examples/samples/buggy.sh` after running the quality check.
Record real line numbers from the output. Keep this file — it seeds the
Week 6 project (formatting and linting on every commit).

## 1. One issue `bash -n` catches (syntax)

`bash -n` only reports problems the shell cannot even parse. The sample as
shipped is syntactically valid, so to see this check *fire*, introduce a
syntax error on purpose (for example, delete the `fi` on line 11), run
`bash -n examples/samples/buggy.sh`, record the message, then undo the edit.

- Syntax error I introduced: `________________________________`
- What `bash -n` reported (message + line): `________________________________`

## 2. One issue ShellCheck catches — or would (lint / pattern)

If ShellCheck is installed, run it and record a real finding with its SC
code. If it is not installed, describe one bug from the lesson that it
*would* catch (the unquoted `$name` in the `[ ]` test, or the unused
`unused_greeting`).

- Rule code (if you have ShellCheck), e.g. `SC2086` or `SC2034`: `____________`
- The line and what is wrong with it: `________________________________`
- Why running the script does NOT reveal this bug: `____________________`

## 3. One formatting issue (whitespace check)

Run `bash examples/quality_check.sh examples/samples/buggy.sh` and read
section [3/3].

- Line number with trailing whitespace: `______`
- Line number with tab indentation: `______`

## 4. Short paragraph: why "it parses" is not "it's correct"

Write 4–6 sentences, in your own words, explaining why a script can pass the
syntax check (`bash -n`) yet still be full of the bugs a linter finds. Tie it
to the difference between "the shell can parse this" and "this will behave
correctly for every input."

```
(your paragraph here)
```
