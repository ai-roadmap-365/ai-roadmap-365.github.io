# Troubleshooting — Day 040 lab

## `python3: command not found`

The percentile step and the trace reconstruction use `python3`. It ships with
macOS and nearly every Linux distribution; if it is missing, install it from
your package manager (for example `sudo apt install python3` on Debian/Ubuntu),
then re-run. Check with `python3 --version`.

## The p95 line prints nothing or an error

You are probably feeding whole log lines into python instead of just the
numeric latency. Extract the number first with the provided `sed` step:

```bash
grep '"event":"request_complete"' "${logfile}" | sed -n 's/.*"latency_ms":\([0-9]*\).*/\1/p'
```

That should print one integer per line. If it prints nothing, your `sed`
pattern does not match the log format — copy it exactly, including the quotes.

## The error rate is always `0.00%` (or `FILL_ME`)

Your error count is matching nothing. Confirm you are searching for the exact
string `"level":"ERROR"` — with the quotes and capital ERROR — as it appears in
the log file. In the starter, this is Exercise 2; you must replace the
`errors="FILL_ME"` line with the real `grep -c` command.

## `Permission denied` when running the script

Run it through bash explicitly rather than executing the file directly:

```bash
bash examples/observe.sh
```

If you prefer `./examples/observe.sh`, first make it executable with
`chmod +x examples/observe.sh`.

## `value too great for base` from bash

This happens if a request-id number is treated as octal. The scripts already
guard against it with `10#` (forcing base-10 arithmetic). If you copied the
`emit_log` function and removed that, restore the `10#${rid##*-}` form.

## The trace durations look wrong or the spans are out of order

The trace is reconstructed by pairing each `span_start` with its `span_end` by
name. If you edited `run_traced_request`, make sure every span that starts also
ends, and that `total_request` starts first and ends last so it is the parent.

## Tests fail with `FILL_ME` still present

That is expected until you finish the starter: the tests run the reference
strictly and check the starter's structure only while `FILL_ME` remains. Once
you replace all four `FILL_ME` markers, the tests hold your starter to the full
strict standard.

## Windows

Use WSL (`wsl --install`, then open Ubuntu) and run the Linux commands
unmodified. The scripts are plain bash + python3 and run identically under WSL.
