# Security notes

## What this lab does

It computes and prints. It writes no files, opens no network connection after
the one-time `pip install`, needs no credentials, no `sudo` and no elevated
permissions, and touches nothing outside its own directory. Every number it
works with is invented and is stated to be invented: the gear ratios, the three
currency rates, the five chain stages, the two-path graph and all nine network
parameters are written out in `examples/dataset.py`.

Section 7 of `tests/run_tests.sh` greps every source file in `examples/` and
`starter/` for `urlopen`, `requests.`, `socket.`, `http://` and `https://` and
fails if any of them appears.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory, so
nothing installed here can affect the rest of your machine, and `rm -rf .venv`
is a complete undo. The two packages are pinned to exact versions in
`requirements/requirements.txt`, and section 1 of the harness reads the
installed version back and compares it against that file rather than trusting
that the install did what it said.

Pinning is a security property as much as a reproducibility one: an unpinned
`numpy` in a lab that a few thousand people will run is an invitation you did
not mean to send.

## Three things worth carrying away from this particular day

**A gradient that is silently wrong is worse than one that crashes.** The
`+=`-versus-`=` bug in the autodiff engine is the model case. Change one
character and the engine still runs, still returns numbers of a plausible size,
and is wrong on every graph where any value is used twice — which is every real
network. Nothing raises. Nothing warns. The loss even goes down for a while,
because a wrong gradient still has some correlation with the right one. This is
the shape of the most expensive class of bug in numerical code: correct types,
correct shapes, plausible magnitudes, wrong answers. The only defence is the
one this lab uses throughout — check the analytic result against an independent
numerical one that shares none of its assumptions.

**Reverse mode's speed is paid for in memory, and memory is an availability
concern.** A backward pass needs every intermediate value from the forward pass
still alive, because the local derivatives are written in terms of them. The
lab measures it: a fifty-operation chain holds 101 nodes, and a
ten-thousand-operation chain holds 20,001. On a real model that stored-activation
cost dominates memory use and scales with batch size and sequence length —
which means an input that is merely *large* rather than malicious can exhaust a
training or inference host. If you ever accept user-controlled input lengths
into something that differentiates, that bound is a limit you have to set
explicitly rather than discover.

**A product of many factors leaves the useful numeric range fast, in both
directions.** The lab shows fifty factors of 0.25 collapsing to `7.9e-31`,
where adding the result to a weight of 1 changes nothing at all, and fifty
factors of 2.0 reaching `1.1e+15`. Neither raises an exception. Underflow
silently produces zero, and a large enough product silently produces
`inf`, after which every subsequent arithmetic operation propagates it and the
model's parameters become `nan` in one step. Gradient clipping exists partly for
this reason, and a training loop that does not check its own loss for
finiteness will happily spend hours computing with `nan`.

## What this lab deliberately does not claim

No deep-learning framework is installed here and **no output from PyTorch, JAX,
TensorFlow or SymPy is reproduced anywhere** in this lab or its lesson. They are
described from their documentation and marked as not run here. The engine you
build is the same idea as theirs and differs in engineering, not in concept —
but "the same idea" is a claim about design, and "here is what it printed" is a
claim about a measurement, and this lab only makes the first one.
