# Troubleshooting

## `pytest: command not found`

You have not created the `.venv`, or you are calling bare `pytest`
instead of `.venv/bin/pytest`. From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest examples -q
```

The harness also accepts `PYTEST=/path/to/pytest bash tests/run_tests.sh`
if your virtual environment lives somewhere else.

## `import file mismatch`

You ran `pytest examples starter` (or any command naming both
directories) in one invocation. `examples/test_calc.py` and
`starter/test_calc.py` share a module name, and so do
`test_notebooks.py` in each — pytest collects test modules by dotted
name, and two files with the same name in one run collide. Run them as
two separate commands, always:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Section 5 of `tests/run_tests.sh` runs the combined form on purpose and
asserts that it fails this way, so this is checked, not just claimed.

## `No such kernel named python3`

`ipykernel` registers a `python3` kernel spec automatically the first
time it is imported in a fresh virtual environment; if you copied a
`.venv` from elsewhere without reinstalling `ipykernel` inside it, the
registration may be missing. Reinstalling
(`.venv/bin/pip install --force-reinstall ipykernel`) fixes it. You can
confirm what kernels nbclient can see with
`.venv/bin/python3 -c "from jupyter_client.kernelspec import find_kernel_specs; print(find_kernel_specs())"`.

## `[IPKernelApp] WARNING | Kernel is running over TCP without encryption`

This prints on every kernel start in this lab and is expected — see
`security.md`. It is not a failure; the tests do not check for its
absence.

## A test hangs instead of failing

Every kernel this lab starts talks over loopback only and shuts down
when its context manager exits. If a test genuinely hangs (rather than
just being slow — the first kernel start in a run is the slowest step,
typically one to two seconds), interrupt it with Ctrl-C and check that
nothing else on your machine is already bound to an unusual port range;
`nbclient` picks its own ports automatically and does not need a
specific one free.

## The environment-record exercise (9) fails after you changed a pin

That is expected if you changed a version in
`requirements/requirements.txt` without reinstalling — the exercise
compares the *live* installed versions (via `nb_lib.record_environment`)
against what the notebook records, and if your installed packages no
longer match what `pip freeze` last put in your `.venv`, the two will
disagree. Reinstall with `.venv/bin/pip install -r
requirements/requirements.txt` and the exercise should pass again.
