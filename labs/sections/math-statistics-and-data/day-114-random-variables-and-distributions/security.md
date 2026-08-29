# Security notes

## What this lab does

It computes and prints. It writes no files, opens no network connection
after the one-time `pip install`, needs no credentials, no `sudo` and no
elevated permissions, and touches nothing outside its own directory. Every
number it works with is invented and is stated to be invented: the dice
events, the sample sizes, the rate parameters and the sweep of `n` values
are all written out in `examples/dataset.py`.

Section 7 of `tests/run_tests.sh` greps every source file in `examples/`
and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and
`https://` and fails if any of them appears.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory,
so nothing installed here can affect the rest of your machine, and `rm -rf
.venv` is a complete undo. The two packages are pinned to exact versions in
`requirements/requirements.txt`, and section 1 of the harness reads the
installed version back and compares it against that file rather than
trusting that the install did what it said.

Pinning is a security property as much as a reproducibility one: an
unpinned `numpy` in a lab that a few thousand people will run is an
invitation you did not mean to send.

## Three things worth carrying away from this particular day

**A sampled quantity is only as trustworthy as the seed and tolerance
behind it, and both should be visible, not implicit.** Every simulation and
every sampler in this lab is compared against a tolerance derived from a
standard error, never against a number chosen because it happened to make
the test pass -- and every random draw goes through an explicit
`numpy.random.default_rng(seed)` rather than a hidden global state. A
system that reports "the model assigns this token probability 0.83" is
making exactly the same kind of claim this lab's exercises make, and the
same discipline applies: what generated that number, and how far can it be
trusted to be reproduced?

**A density greater than 1 is not a bug and is not a probability.**
Exercise 10 makes this concrete: Uniform(0, 0.5) has density 2 everywhere
on its support. Code that asserts "this value looks like a probability
because it is between 0 and 1" and then treats a density the same way will
silently accept nonsense the moment the support narrows below 1 -- and a
narrow support is exactly what a well-calibrated, confident model produces.
Knowing which quantity in your pipeline is a probability and which is a
density is a correctness property, not a style preference.

**The from-scratch samplers in this lab (`sample_discrete_inverse_cdf` and
`sample_exponential_scratch`) exist to demystify what a library's random
number generator is doing, not to replace it.** `numpy.random.Generator`'s
built-in distribution methods are implemented in optimized native code, are
more numerically careful at the extremes than the versions here, and are
what you should reach for in real code. Writing the inverse-CDF method
yourself once is what lets you read and trust the library's implementation
afterward, rather than treating it as an opaque black box.

## What this lab deliberately does not claim

`scipy.stats` and `pandas` are not installed here and **no output from
either is reproduced anywhere** in this lab or its lesson. `scipy.stats` is
described from its documentation in the lesson's Tools section and marked
as not run here.
