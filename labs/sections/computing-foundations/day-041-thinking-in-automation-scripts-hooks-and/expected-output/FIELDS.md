# Expected output — what a correct run produces (all platforms)

This directory holds real captured runs from the authoring machine (macOS,
Apple Silicon, 2026-07-12). Your paths will differ; the shape must match.

## `bash examples/hook_demo.sh` must show, in order

1. `Hook installed at .git/hooks/pre-commit (executable).`
2. A **blocked** bad commit: the hook prints `pre-commit: trailing whitespace in bad.sh`, then `pre-commit: commit rejected.`, and the demo reports `Result: the hook BLOCKED the bad commit`.
3. An **allowed** clean commit: `pre-commit: quality gate passed.` followed by `Result: the hook ALLOWED the clean commit.`
4. The pipeline run green (all four stages, then `Pipeline succeeded: every stage green.`) and then forced to fail (stops after `test`, printing `Pipeline stopped at 'test'.`).

The two lines that prove the gate works in both directions are
`BLOCKED the bad commit` and `ALLOWED the clean commit`.

## `bash examples/pipeline.sh` (no argument)

Prints `lint`, `test`, `build`, `deploy`, then `Pipeline succeeded: every stage green.` — exit code `0`.

## `bash examples/pipeline.sh test`

Prints `lint`, then `test`, then the failure and `Pipeline stopped at 'test'. Later stages did not run.` — `build` and `deploy` never appear — exit code `1`. This is failing fast.

## `bash tests/run_tests.sh`

Ends with `6 checks, 0 failure(s).` and exits `0`.

## Platform notes

- **macOS and Linux:** identical output; the lab needs only `git` and `bash`, both preinstalled or trivially installed.
- **Temporary paths:** every script works in a `mktemp -d` directory and deletes it on exit, so the path printed after "Temporary repository at" changes on every run and differs between macOS (`/var/folders/...`) and Linux (`/tmp/...`). That line is the only run-to-run difference.
- **Windows:** run inside WSL (Windows Subsystem for Linux) and the Linux output applies. Native PowerShell is not supported for this lab.
