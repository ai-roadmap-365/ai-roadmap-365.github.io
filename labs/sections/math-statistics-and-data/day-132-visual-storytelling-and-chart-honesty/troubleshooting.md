# Troubleshooting

## `ModuleNotFoundError: No module named 'matplotlib'`

You are running the system Python rather than the lab's virtual
environment. Every command in this lab is prefixed with `.venv/bin/`
for exactly this reason:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest examples -q
```

If you would rather use a Python you already have, point the harness at
its pytest instead:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness checks each installed version against
`requirements/requirements.txt` and reports a mismatch rather than
producing different numbers in silence.

## `pytest starter` reports 22 skipped and nothing else

That is correct on an untouched checkout. Every function in
`starter/honesty.py` still raises `NotImplementedError`, and the starter
suite turns that into a skip rather than a failure so the skip count is
your progress bar. Write a function, re-run, and watch one or more skips
become passes.

## Never run `pytest examples starter` as one command

Run them as two:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Both directories ship a module called `honesty`, and pytest imports test
files by putting their directory on `sys.path`. Combining the two
directories in one invocation is unreliable in both directions across
labs in this course: it can silently let one suite import the other
directory's module — which would report your unwritten exercises as
passing — or it can abort collection outright with an import file
mismatch. Each directory's `conftest.py` guards against the first case,
and `tests/run_tests.sh` verifies the guard still works by checking that
the skip count is unchanged when both suites are collected together. Two
separate runs are well defined and need no guard at all.

## A test fails with a number close to but not equal to the expected one

Check which number. `expected-output/FIELDS.md` splits every captured
value into three groups, and the group tells you what to do:

- **Exact everywhere** — arithmetic and affine geometry. A mismatch here
  is a real bug in your implementation, not an environment difference.
- **Version-specific** — the tracking gaps in exercise 3 and the 3D
  drawn ratios in exercise 7. These depend on matplotlib's autoscale
  margins and on `Axes3D`'s projection internals, which have moved
  between releases. If you are not on matplotlib 3.11.1, expect the
  fourth decimal to differ; the *ordering* of the values is what the
  lesson claims.
- **Deliberately selected** — the two seeds, both disclosed.

## `RuntimeWarning: More than 20 figures have been opened`

Something is creating figures without closing them. Every helper in this
lab wraps its drawing in `try: … finally: plt.close(fig)` for this
reason. If you add a figure of your own, close it the same way. Day 128
covers the figure lifecycle in full.

## The 3D exercise gives a different ratio on your machine

Expected, and covered above. The projected areas depend on the camera:
this lab uses matplotlib's perspective projection at `focal_length=0.2`
with the default view angle. Change the focal length or the elevation and
the numbers move. What does not move is the finding — under perspective,
the drawn size of a bar depends on where it stands, so the comparison the
chart exists to support is the one the third dimension breaks. If you
want to see that directly, call `bar3d_projected_areas` with the depths
swapped and watch the ratio go from `2.34` to `4.20`.

## Windows

The commands above assume macOS or Linux paths. On Windows, the virtual
environment puts its executables in `.venv\Scripts\` rather than
`.venv/bin/`:

```
py -m venv .venv
.venv\Scripts\pip install -r requirements\requirements.txt
.venv\Scripts\pytest examples -q
```

`tests/run_tests.sh` is a bash script. Run it from Git Bash or WSL. It
was executed and captured on macOS only; the Windows path above is
documented from the standard Python packaging layout and was **not**
exercised on the authoring machine.
