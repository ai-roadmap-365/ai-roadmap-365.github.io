# Security notes

## What this lab does

It computes and prints. It writes no files, opens no network connection
after the one-time `pip install`, needs no credentials, no `sudo` and no
elevated permissions, and touches nothing outside its own directory. Every
number it works with is invented and is stated to be invented: the urn
compositions, the dice events and the sample sizes are all written out in
`examples/dataset.py`.

Section 5 of `tests/run_tests.sh` greps every source file in `examples/` and
`starter/` for `urlopen`, `requests.`, `socket.`, `http://` and `https://`
and fails if any of them appears.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory, so
nothing installed here can affect the rest of your machine, and `rm -rf
.venv` is a complete undo. The two packages are pinned to exact versions in
`requirements/requirements.txt`, and section 1 of the harness reads the
installed version back and compares it against that file rather than
trusting that the install did what it said.

Pinning is a security property as much as a reproducibility one: an unpinned
`numpy` in a lab that a few thousand people will run is an invitation you did
not mean to send.

## Three things worth carrying away from this particular day

**A probability claim is a number with an error bar, and reporting it
without one is a form of overclaiming.** Every simulation in this lab is
compared against a tolerance derived from `sqrt(p(1-p)/n)`, never against a
number chosen because it happened to make the test pass. When a system
downstream of you reports "the model is 92% confident", that number came
from *some* estimation process, and the honest question is always the one
this lab asks of its own simulations: estimated from how many samples, and
with what standard error?

**Randomness that is not reproducible is a debugging liability, not a
convenience.** `numpy.random.seed()` mutates global state shared by every
piece of code in the process; two runs that should be identical for
debugging purposes can silently diverge because an unrelated import called
`seed()` first, or because two functions drew from the shared generator in a
different order. `default_rng(seed)` hands back an independent object with
no shared state, which is what makes exercise 9's reproducibility guarantee
possible at all. In any system where a random decision needs to be
explainable after the fact — which includes most machine learning pipelines
— this is not a stylistic preference.

**A wrong probability calculation looks exactly like a right one until you
check it against an independent method.** The lab's structure — exact
enumeration against a closed-form probability, or a simulation against an
exact fraction — exists because a probability bug produces a number that is
still between 0 and 1, still looks plausible, and gives no signal that
anything is wrong. De Méré himself had exactly this experience: his reasoning
was internally consistent and produced two numbers that both looked like
probabilities, and only comparing them against real outcomes at the gaming
table revealed the error. The discipline this lab teaches — compute it two
ways and assert they agree — is the general defence against that entire
class of mistake, in this lab and in any code that reports a probability.

## What this lab deliberately does not claim

`scipy.stats` and `pandas` are not installed here and **no output from
either is reproduced anywhere** in this lab or its lesson. `scipy.stats` is
described from its documentation in the lesson's Tools section and marked
as not run here.
