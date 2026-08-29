# Troubleshooting — Day 37 lab

## `bash -n` printed nothing

That is success. `bash -n` reports only syntax it cannot parse; a valid
script produces no output and exits 0. Confirm with `echo $?` (it prints `0`).
To see the check *fire*, temporarily introduce a syntax error (delete the
`fi` on line 11 of the sample), run `bash -n`, then undo the edit.

## `shellcheck: command not found`

ShellCheck is optional. The quality check detects its absence and prints a
`SKIP` block describing what it would have caught, then continues. To gain the
lint step, install ShellCheck (free) per `requirements/README.md`
(`brew install shellcheck` on macOS, `sudo apt install shellcheck` on
Debian/Ubuntu), then re-run the quality check.

## The formatting check finds nothing on my own script

That means your script has no trailing whitespace or tab indentation — good.
To watch the check fire, add a space at the end of any line and re-run
`bash examples/quality_check.sh <your-script>`.

## `Permission denied` when running a script

Run it through bash explicitly, e.g. `bash examples/quality_check.sh ...`,
rather than `./examples/quality_check.sh`. If you prefer `./`, first make it
executable with `chmod +x examples/quality_check.sh`.

## The trailing-whitespace line looks blank in my terminal

Trailing spaces are invisible by design — that is exactly why the check
exists. The line number in the report tells you which line; open it in your
editor with "show whitespace" enabled (Day 36 covered this) to see the spaces.

## My editor keeps deleting the trailing whitespace in `buggy.sh`

Many editors strip trailing whitespace on save. If you edit `buggy.sh` and the
trailing-whitespace finding disappears, that is your editor "helpfully" fixing
it. Restore the sample from git (`git checkout -- examples/samples/buggy.sh`)
to get the intentional flaws back.

## Tests fail with a non-zero exit

Run `bash tests/run_tests.sh` and read which check says `FAIL`. Each check
names exactly what it verified (syntax handling, whitespace flagging, exit
code, graceful shellcheck skip). No check needs the network.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu) or Git Bash, and run the same
commands. Behaviour matches Linux.
