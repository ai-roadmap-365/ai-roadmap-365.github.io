# Troubleshooting — Day 048 lab

## `python3: command not found`

Python may be installed as `python` on your system, or not installed at all.
Try `python examples/buggy/average_scores.py`, and confirm your version with
`python3 --version` or `python --version`. If neither works, revisit Day 43
(installing Python). On Windows, use `py` or `python`.

## Reading a traceback: which line is the error on?

Read the traceback **from the bottom up**:

1. The **last line** names the exception type and message — the *what*
   (for example `KeyError: 'Germany'`).
2. The **bottom-most `File "..."` line** names the file and the line number —
   the *where*. The line printed just beneath it is that exact line of code.

Everything above the bottom frame is the chain of calls that led there; you
only need it when the cause hides in a function that called the failing one.

## The error line vs the real cause

The line named in a traceback is where the program **broke**, which is not
always where it went **wrong**. In `average_scores.py` the crash is on the
`print(...)` line, but the real mistake is the loop range on the line above it:
`range(len(scores) + 1)` counts one position too far. Fix the *cause* (the
range), not the symptom (the print). When a value is wrong, ask where it was
set — often several lines, or a whole function, earlier.

## "My fixed program still crashes"

Read the **new** traceback. A fix can reveal a second bug that the first crash
was hiding, or introduce a new one. That is normal — run the debugging loop
again on the new error.

## The test script says a buggy program "did not fail"

You probably edited a file inside `examples/buggy/` by mistake; those must stay
broken so the walkthrough and tests work. Do your fixing in `starter/` only.
Restore the reference samples with `git checkout -- examples/buggy`.

## `Permission denied` running a script

Run scripts through their interpreter explicitly: `bash tests/run_tests.sh`,
`python3 starter/total_price.py`. You do not need to `chmod +x` anything.

## The caret marks (`~~~^^^`) are missing from my traceback

Those under-line marks pointing at the failing sub-expression appear on Python
3.11 and newer. On older Python they are absent, but the exception type,
message, and line number are the same — which is all you need.

## Windows: `bash` is not recognized

Run the Python files directly (`python starter\average_scores.py`), or use WSL
(`wsl --install`, then follow the Linux path), or Git Bash for the `.sh`
scripts.
