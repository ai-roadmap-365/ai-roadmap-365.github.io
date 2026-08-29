# Security notes

## What this lab does

It computes and prints. It writes no files, opens no network connection
after the one-time `pip install`, needs no credentials, no `sudo` and no
elevated permissions, and touches nothing outside its own directory. Every
number it works with is invented and is stated to be invented: the test's
sensitivity and specificity, the prevalence, the correlation weight, and
the tiny spam/ham corpus are all written out in `examples/dataset.py`.

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

**A posterior is only as trustworthy as the prior and the independence
assumptions that produced it.** Exercise 7 builds a case where "multiply
the likelihood ratios" — the textbook move for combining two pieces of
evidence — silently assumes the two pieces of evidence are conditionally
independent, and shows the naive calculation reporting dramatically more
confidence than is justified when that assumption fails. In any system
that combines multiple signals into one risk score — fraud detection,
intrusion detection, automated moderation — treating correlated signals as
independent evidence is exactly this mistake, and it produces
overconfident, not merely imprecise, output.

**A classifier's output is a posterior, and a posterior trained on the
wrong base rate is confidently wrong at scale.** This lab's opening
example — a 99%-accurate test that is right about 9% of the time it fires
positive, because the condition is rare — is not specific to medicine. A
model trained on a class-balanced dataset and deployed against a real
population where the positive class is rare (fraud, intrusion, defect
detection) will overstate its own precision in exactly this way unless the
deployment-time base rate is accounted for, which is what calibration
exists to fix.

**A wrong probability calculation looks exactly like a right one until you
check it against an independent method.** Every exercise in this lab
computes something two ways — exact `Fraction` arithmetic against a
simulation, a formula against a from-scratch enumeration, a naive model
against a corrected one — because a probability bug produces a number that
is still between 0 and 1, still looks plausible, and gives no signal that
anything is wrong. The discipline this lab teaches is the general defence
against that entire class of mistake, in this lab and in any code that
reports a probability or a confidence score.

## What this lab deliberately does not claim

`scipy.stats`, scikit-learn's `MultinomialNB` and PyMC (or Stan) are not
installed here and **no output from any of them is reproduced anywhere**
in this lab or its lesson. Each is described from its public documentation
in the lesson's Tools section and marked as not run here.
