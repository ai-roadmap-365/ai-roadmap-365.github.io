# Troubleshooting

Every symptom below was produced deliberately on the authoring machine while
building this lab, so the messages are the real ones.

## `ModuleNotFoundError: No module named 'numpy'`

You are running a Python that does not have the lab's dependencies. The system
`python3` on most machines has the standard library only.

```bash
cd labs/sections/math-statistics-and-data/day-099-vectors-direction-magnitude-and-meaning
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Then run everything through `.venv/bin/python3` and `.venv/bin/pytest`, not
through bare `python3`.

## `FAIL: pytest not found.` from the test harness

`tests/run_tests.sh` looks for its tools in three places, in order: the
`PYTEST` environment variable, `./.venv/bin/pytest`, and then `PATH`. If none
of the three has it, the harness stops rather than skipping silently. Either
create the virtual environment above, or point the harness at one you already
have:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'vectors'` when running an example

The example scripts import `vectors`, which lives beside them in `examples/`.
Both of these work, because Python puts the script's own directory on
`sys.path`:

```bash
cd examples && ../.venv/bin/python3 byhand.py    # the form metadata.yml uses
.venv/bin/python3 examples/byhand.py             # also fine, from the lab root
```

What does *not* work is importing the module from a Python session started
somewhere else, or copying one example out of the directory and leaving
`vectors.py` behind. If you want to experiment interactively, start the
interpreter from inside `examples/`:

```bash
cd examples && ../.venv/bin/python3
>>> from vectors import l2_norm
>>> l2_norm([3, 4])
5.0
```

## `pytest starter` collects nothing

Run it from the lab directory, not from inside `starter/`:

```bash
.venv/bin/pytest starter -q
```

`starter/pytest.ini` sets `pythonpath = .` so that `import vectors` finds
`starter/vectors.py`. If you invoke pytest from somewhere else, that ini file
may not be the one in effect.

## A test fails with `assert False` and no other information

That is `assert close(...)` returning False. Print the two numbers to see how
far apart they are:

```python
print(repr(mine.l2_norm([3, 4])))
```

If the answer is `25.0` rather than `5.0`, you forgot the square root. If it is
a list rather than a number, `l2_norm` is returning the squares instead of
their sum. Both are the two most common ways to get exercise 5 wrong.

## `TypeError: object of type 'NoneType' has no len()`

An earlier exercise is still returning `None` and a later one is calling it.
`distance` depends on `subtract` and `l2_norm`; `nearest` depends on
`distance`. Work through the exercises in order, and run
`python3 starter/vectors.py` to see which ones are still unfinished.

## `ValueError: dimension mismatch: 2 and 3`

Working as intended. You tried to combine a 2-component vector with a
3-component one, which is not a slightly wrong answer but a meaningless
question. Check which vector you passed.

## `ValueError: cannot normalise the zero vector: it has no direction`

Also working as intended. The zero vector has magnitude 0, so scaling it to
magnitude 1 would mean dividing by zero. In real code this usually means an
item ended up with all-zero features — an article that mentioned none of the
four words — and the fix is upstream, not here.

## My assertion about a normalised magnitude fails, but the maths looks right

Almost certainly you wrote `== 1.0`. Run:

```bash
cd examples && ../.venv/bin/python3 normalise.py
```

On the authoring machine, three of the seven vectors in that table normalise to
`0.9999999999999999` rather than `1.0`, including `[2, 3, 6]` whose magnitude
is exactly `7.0`. Use `math.isclose(value, 1.0, rel_tol=1e-9, abs_tol=1e-12)`.
This is the bug the lab exists to teach and it is not a defect in your code.

## `numpy.allclose` returns True but I expected False

`allclose` has generous defaults (`rtol=1e-05`). This lab always passes its
tolerance explicitly — `rtol=1e-9, atol=1e-12` — precisely so that nobody has
to remember what the default is. Pass yours too.

## `RuntimeWarning: invalid value encountered in divide` from NumPy

You divided a NumPy array by a zero norm. Unlike this lab's `normalise`, NumPy
does not raise: it returns `nan` for each component and carries on, and the
`nan` then poisons every comparison downstream, because `nan` is not equal to
anything including itself. Guard the zero case yourself.

## `__pycache__` directories appear inside the lab

Set `PYTHONDONTWRITEBYTECODE=1`, which `tests/run_tests.sh` does for you. To
clean up what is already there:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
```

## Windows

The Python is identical; only the paths differ. Use
`py -3 -m venv .venv`, then `.venv\Scripts\python.exe` and
`.venv\Scripts\pytest.exe`. `tests/run_tests.sh` is a bash script: run it under
Git Bash or WSL. Everything it checks can also be checked by hand with the
`run_commands` in `metadata.yml`.
