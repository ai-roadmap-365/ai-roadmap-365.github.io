# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | Exactly one thing: reading float64's machine epsilon from `numpy.finfo` rather than writing the literal `2.220446049250313e-16` and hoping. The vanishing-gradient section compares products against that epsilon, so it matters that the number is read from the platform rather than remembered. |
| `pytest` | 9.1.1 | MIT | The reference suite (235 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 7 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/` to
prove that nothing else does.

## If you cannot install anything at all

You can still do almost all of this lab, which is unusual and worth saying
plainly.

The autodiff engine — the most valuable thing here — needs `math` and nothing
else. So do all fourteen functions in `starter/chainrule.py`, the whole
two-layer network, the hand-worked backward pass, every composition, the
five-stage chain, the two-path example and the vanishing and exploding
products. Run the reference scripts directly with any Python 3.10 or later and
they will print their working and assert every claim they make:

```bash
cd examples && python3 01_gears_and_rates.py
```

What you lose is:

- `pytest`, so no running score and no skip-versus-fail distinction — you would
  read the numbers yourself instead;
- the epsilon cross-check, since `dataset.py` imports `numpy` at the top. If
  you want to run without NumPy, replace that import and the `EPSILON` line
  with `EPSILON = sys.float_info.epsilon`, which is the same value from the
  standard library. The lab does not ship it that way because reading it from
  two independent sources and comparing them is a better habit than reading it
  from one.

## What is deliberately *not* installed

PyTorch, JAX, TensorFlow and SymPy all do this job, and none of them is
installed here. **No output from any of them is reproduced anywhere in this lab
or its lesson.** They are described from their documentation, and the lesson's
Alternatives section marks them as not run here.

That is not a limitation to apologise for. The engine you write in
`starter/autodiff.py` is the same idea as `torch.autograd`: a graph of
operations, a local derivative at each node, and one reverse walk applying the
chain rule. The difference between the two is engineering — tensors instead of
scalars, fused kernels, GPU dispatch, memory planning — and not concept. Having
written the seventy-line version, you will read the documentation of the real
one differently.
