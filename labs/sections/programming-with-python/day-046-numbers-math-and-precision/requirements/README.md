# Dependencies — Day 046 lab

**Only Python 3 itself.** Everything this lab uses ships in the CPython
standard library — there is nothing to `pip install`:

- `python3` ≥ 3.8 (any modern CPython; the lab was executed on 3.14).
- The `decimal` module (standard library) — exact base-10 arithmetic.
- The `math` module (standard library) — `sqrt`, `floor`, `ceil`, `isclose`.
- `bash` (to run `tests/run_tests.sh`) — preinstalled on macOS and Linux.

Check your Python version:

```bash
python3 --version
```

If that prints `Python 3.x.y`, you are ready. There is deliberately no
`requirements.txt` here: the point of the lab is that precision-correct money
math needs no third-party library at all — the batteries are already
included. Course 3 of the course previews **NumPy**, which you *would*
install for array math, but this lab does not need it.
