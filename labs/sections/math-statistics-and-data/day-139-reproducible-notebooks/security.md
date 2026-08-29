# Security notes

## Network

Exactly one network connection in this entire lab: the `pip install` in
"Installation." Every test, every exercise and the whole harness run
after that with no further network access. Nothing in `examples/`,
`starter/` or `tests/` opens a socket to anything other than the local
kernel it starts (see below).

## What a Jupyter kernel actually is here

`nbclient.NotebookClient` starts a real `ipykernel` process for every
notebook it executes and talks to it over ZeroMQ on `127.0.0.1`
(loopback only — never `0.0.0.0`, never a routable address). ipykernel
prints one warning on every start:

```
[IPKernelApp] WARNING | Kernel is running over TCP without encryption. ...
```

That warning is accurate and harmless for this lab: the "TCP" in
question is loopback-only TCP between two processes on the same
machine, not a connection reachable from outside it. No lesson or lab
file in this course reaches this kernel from anywhere but the process
that started it, and every kernel this lab starts is shut down when its
`with client.setup_kernel():` block exits or `client.execute()` returns.

## What runs, and with what privileges

Every notebook this lab builds runs arbitrary Python — that is what a
notebook is. All of that code is written by this lab (`nb_lib.py`,
`calc.py`, and the code inside the test files) and never derived from
untrusted input. No cell in this lab reads a file outside its own
directory, writes anywhere outside a `pytest` temporary directory (only
`tests/run_tests.sh` section 6 uses `mktemp`, and it deletes what it
creates), or shells out. Nothing needs `sudo`. Nothing binds a listening
port. No credential, token or API key is used, read or required anywhere
in this lab.

## Data

Every value in this lab is a small literal (`[3, 12, 7, 15, 2]`,
`x = 100`) invented for the exercise. No real dataset, no personal data
and no third-party data of any kind appears anywhere in this lab.

## What is written to disk

Nothing, deliberately. Every notebook in this lab is an in-memory
`nbformat.NotebookNode` object; none is ever passed to `nbformat.write`
or saved as a `.ipynb` file, which is why the harness can assert that no
`.ipynb` file and no `.ipynb_checkpoints` directory exist anywhere in
this lab after a run. `__pycache__` and `.pytest_cache` are the only
things Python itself creates, and the harness removes both.
