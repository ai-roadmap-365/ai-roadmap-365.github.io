# Required output fields (all platforms)

`sample-run.txt` in this directory is a real captured run on the authoring
machine (macOS, Python 3.14, 2026-07-12). The behavior is identical on Linux
and inside WSL — Python's formatting and stream handling are the same
everywhere; only the shell prompt (`$`) may look different.

## On good input (`5 7`, by argument or by pipe)

A correct run of `io_demo.py` prints, on **standard output**, in order:

1. `Input values`
2. `  a` followed by the first number, right-aligned, two decimals (`5.00`)
3. `  b` followed by the second number, right-aligned, two decimals (`7.00`)
4. `Results`
5. `  sum` followed by the sum, two decimals (`12.00`)
6. `  product` followed by the product, two decimals (`35.00`)
7. `  mean` followed by the mean, two decimals (`6.00`)

The two number columns are right-aligned to a fixed width, so the decimal
points line up regardless of how many digits each value has. Argument mode
(`python3 io_demo.py 5 7`) and pipe mode (`echo "5 7" | python3 io_demo.py`)
produce byte-for-byte identical output.

## On bad input (e.g. `5 hello`, or only one number)

- **Nothing** is printed to standard output.
- A single line beginning `error:` is printed to **standard error**.
- The process exits with a **non-zero** code (`1`); `echo $?` confirms it.

This split — results on stdout, errors on stderr, non-zero exit on failure — is
what lets the tool sit safely in a shell pipeline.
