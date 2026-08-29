# Bias You Can Measure — the nine exercises

Today's lab is an ethics lab, and ethics labs usually fail in one of two
ways: they hand you a list of principles you cannot act on, or they preach.
Neither is on offer here. Every exercise below is either **something you
compute** or **something you write down and check**. Where a question is
genuinely a value judgement rather than a calculation — and exercise 5 is
exactly that — the lab says so explicitly and asks you to assert the
*disagreement*, not a winner.

## Everything here is synthetic, deliberately

No real dataset about real people appears anywhere in this lab. Every
table is constructed in `ethics.py` from a seeded `numpy` generator. Two
reasons, and both matter:

1. A lesson about who is missing from a dataset should not be taught on
   people who never agreed to be in one.
2. A synthetic population has a property no real one has: **its true
   composition is known exactly.** That turns "the west looks
   under-represented" into "the west appears at 0.104 of its population
   share", which is a fact you can assert rather than an impression you
   can argue about.

## The files

| File | What it is |
| --- | --- |
| `ethics.py` | Every measurement function, grouped into bias measurement, fairness accounting, disclosure risk and documentation. Read this first |
| `fixtures.py` | The survey counts, the reference population, the two datasheets, and a list of named proxies |
| `conftest.py` | Four session fixtures: `register`, `generalised`, `fairness_pop`, `versions` |
| `test_ethics.py` | Your nine exercises. Each currently calls `pytest.skip` |

Replace each `pytest.skip(...)` with real assertions and delete the skip
line. Run `pytest starter -v` as often as you like. **Never run
`pytest examples starter` in one command** — both directories hold a module
named `test_ethics.py` and pytest aborts collection on the clash. Run them
as two separate commands.

---

## Exercise 1 — more data does not fix a biased frame

The centrepiece, and the strongest argument in the whole day, because it is
arithmetic rather than opinion.

Group B is **10% of the population** and the sampling frame reaches it with
probability **1%** — a telephone survey run during working hours, say. Both
groups have the same slope and the same noise; group B's outcome simply
sits six units higher at every x.

Fit one pooled straight line and measure the signed prediction error for
each group, over 40 replicate samples, at n = 500, 5,000 and 50,000.

You are proving three things at once:

- the **in-sample RMSE looks fine** at every n, so nothing in the usual
  model report says anything is wrong;
- the **bias for group B does not move**. It sits at
  `6.0 × (1 − 0.01) = 5.94` and is still 5.94 after a hundredfold more
  data;
- the **variance does move**, falling by roughly `sqrt(10)` per tenfold
  increase — the confidence interval tightens around an answer that stays
  wrong.

This is Day 117's bias-versus-error distinction with consequences. Sampling
error shrinks with n. Sampling bias does not.

## Exercise 2 — coverage mismatch, computed

The sampling frame is a claim about who is in the world. When you have a
**reference distribution** — a census, a published statistical abstract —
the mismatch between frame and population stops being a worry and becomes
a subtraction.

`coverage_report` returns two things on purpose. The **total variation
distance** is a single summary and reads as 0.0896 here, which is small
enough to be reassuring and is exactly why it is not the number that
matters. The **representation ratio** per group is: the west appears at
0.104 of its population share, a tenfold shortfall, named by group.

Assert both, and then assert the check can say "fine" on a sample that
mirrors the reference — a check that never passes teaches nothing.

## Exercise 3 — the proxy gap

**The proxy is not the thing.** Arrests are not offences; clicks are not
interest; a billed diagnosis code is not a disease; prior spending on care
is not need for care.

Here, both groups are drawn from the *same* true-need distribution, but the
proxy records group B's need at 85% of its true level because group B
interacts with the recording system less. The proxy still correlates with
the target at above 0.9 — it passes the check most people run.

Select the top 500 by proxy, and separately the top 500 by true need.
Assert that group B's share of the selection collapses from about 0.25 to
under 0.10, that the true need served for group B falls to under 35% of
what a target-ranked selection would have served — and then assert the part
that explains why nobody notices: **total** need served falls by less than
3%. The aggregate barely moves while one group is gutted.

## Exercise 4 — aggregation bias

Day 116's Simpson's paradox, now with stakes. Group A lives at low x with a
low intercept; group B at high x with a much higher one. **Both groups
trend downward.** Pooled, the between-group offset dominates and the fitted
slope comes out positive.

Assert the sign flip, and then assert the thing that matters more: the
pooled model's RMSE is worse **for every subgroup**, not worse on average.
One model for a heterogeneous population can be wrong for everybody in it
while looking like a confident fit.

## Exercise 5 — the fairness tension, demonstrated

Read this one slowly, because it is the exercise where measurement
genuinely runs out.

The population is integer-exact and hand-built: in every score bin, the
observed positive rate **is** the score, in both groups. The score is
perfectly calibrated. The two groups have different base rates — 0.66 and
0.34 — and that single fact is the whole engine of what follows.

Three policies, three criteria:

| Policy | Selection rate | True-positive rate | Precision among selected |
| --- | --- | --- | --- |
| One threshold at 0.5 | differs by 0.50 | differs by 0.31 | differs by 0.12 |
| Equalise selection rate | **equal** | differs by 0.11 | differs by 0.33 |
| Equalise true-positive rate | differs by 0.12 | **equal** | differs by 0.30 |

Assert that each policy closes its own gap *exactly* and opens at least one
other, and that `any_policy_satisfies_all` is `False`.

**Assert the incompatibility, not a preferred answer.** When base rates
differ between groups, demographic parity, equal opportunity and equal
precision cannot generally all hold at once. That is a theorem about
arithmetic. *Which* of them your system should satisfy is a value judgement
about what the system is for and who bears the cost of being wrong — and
reasonable, well-informed people disagree about it. Your job as an analyst
is to make the choice **visible and declared**, not to let a library
default make it silently.

## Exercise 6 — re-identification risk

"Anonymised" is a claim about a threat model, not a property of a file.

The synthetic register carries no name, no address and no identifier —
only birth year, postcode, sex, and a diagnosis. Count how many rows are
the **only** row with their combination of the first three. It is 2,723 out
of 5,000: over half the table can be singled out by anyone who knows three
ordinary facts about a person.

Then coarsen **one** field — exact birth year to a ten-year band — and count
again. It falls to 13. Assert both counts and the two-orders-of-magnitude
drop. Generalisation is cheap and it works; the reason it is not applied by
default is that nobody counted first.

## Exercise 7 — k-anonymity as a check with limits

A table is *k-anonymous* when every combination of quasi-identifiers that
appears at all appears at least k times. Generalisation alone does not get
you there: after coarsening, the smallest class here still holds one
person. Suppressing every class smaller than 5 does — at a cost of **794
rows**, roughly one in six people, and every one of them somebody in an
unusual combination. Say that cost out loud; it is frequently the people
the analysis was supposed to be about.

Then the limit. `homogeneous_table()` is 4-anonymous by construction, and
it still discloses: one of its classes has four members who all share the
same diagnosis. Knowing that someone is a 1970s-born woman in postcode 1001
and appears in the table reveals her diagnosis exactly. **No
re-identification was required.** k-anonymity held; the secret came out
anyway.

Assert the technique *and* its limit. A check you trust past its stated
guarantee is worse than no check, because it buys confidence it did not
earn.

## Exercise 8 — a datasheet contract

A dataset without provenance is not a dataset; it is a rumour with columns.

`check_datasheet` tests a record against eleven required fields — collector,
collection period, purpose, population definition, sampling frame, inclusion
and exclusion criteria, known gaps, licence, version, changelog. Assert that
the incomplete record fails and that the failure **names each missing field**,
because "documentation incomplete" is not actionable and "no
`exclusion_criteria` recorded" is. Note that an empty string and an explicit
`None` both count as unanswered: a field that is present but blank tells a
reader nothing.

Then assert the complete record passes — and that its `known_gaps` field
documents exercise 2's coverage shortfall in prose, where the next reader
will actually find it.

## Exercise 9 — version drift

Two releases of one dataset. The measured column is byte-for-byte
identical, so **every** summary statistic — count, mean, standard
deviation, minimum, median, maximum — matches exactly between them. A
reader diffing `describe()` output sees nothing at all.

What changed is who is in the file: group B's quota went from half the
sample to a quarter. Assert the composition shift, assert that the summary
hides it, and then assert the only thing that makes it visible — the
sampling-frame field differs and the changelog gained one entry saying why.

That is the day's deliverable in one exercise. The documentation is not
paperwork attached to the analysis. On this comparison it is the *only*
place the change exists.
