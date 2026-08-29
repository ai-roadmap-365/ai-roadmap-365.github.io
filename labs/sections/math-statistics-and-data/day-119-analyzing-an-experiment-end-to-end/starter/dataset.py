"""Every parameter used to generate the two shipped experiments.

Nothing here is fetched or read from the network. `generate_data.py` in this
same directory imports these constants, draws every row from
`numpy.random.default_rng(<seed>)`, and writes the result to
`../data/exp_a.csv` and `../data/exp_b.csv`. The CSVs in `data/` are already
checked into this lab so the reader never has to run the generator -- but
running it again with the same seeds reproduces the identical files, which is
the whole point of writing the generator down instead of just shipping data.

Both experiments simulate a checkout-page change: does a redesigned "Buy now"
button change whether a visitor converts (buys)? `converted` (0/1) is the
primary metric. `latency_ms` (page-render time) is a guardrail: it must not
get worse. `time_on_page_sec` is a secondary continuous metric used only to
show how a few extreme sessions (bots, abandoned tabs) drag a mean away from
a median.

Dataset A is what a well-run experiment looks like: a clean 50/50 split, a
uniform +1.8 percentage point true lift in every segment, and a guardrail
that holds. Dataset B *looks* the same shape -- same columns, same nominal
experiment -- but carries two planted problems: the realised split drifted to
48/52 (a sample-ratio mismatch), and the segment mix is confounded with the
group assignment so that every individual segment has a NEGATIVE true effect
while the pooled numbers show a positive one. Nothing about B's arithmetic is
wrong; the process that produced the data is broken in ways the arithmetic
cannot see.
"""

from __future__ import annotations

SEED_A = 119_001
SEED_B = 119_002

PLANNED_SPLIT = 0.5

# ---------------------------------------------------------------------------
# Dataset A -- clean. Segment shares are IDENTICAL in both arms, and the true
# effect is the same +1.8 percentage points in every segment, so the pooled
# effect is also +1.8pp with no reversal possible.
# ---------------------------------------------------------------------------

A_TRUE_LIFT_PP = 0.010

# (segment, n_control, n_treatment, control_rate)
A_SEGMENTS = (
    ("desktop", 3200, 3200, 0.110),
    ("mobile", 3600, 3600, 0.090),
    ("tablet", 1200, 1200, 0.100),
)

A_LATENCY_CONTROL = (220.0, 30.0)  # (mean ms, sd ms)
A_LATENCY_TREATMENT = (219.0, 30.0)  # very slightly BETTER -- guardrail holds

# ---------------------------------------------------------------------------
# Dataset B -- haunted. Segment sizes are confounded with group on purpose:
# treatment is stuffed with the high-base-rate "desktop" segment and starved
# of the low-base-rate "mobile" segment, control is the mirror image. Within
# every segment the true effect is NEGATIVE. The totals below sum to a
# control/treatment split of 9600/10400 -- 48%/52%, not the planned 50/50.
#
# (segment, n_control, n_treatment, control_rate, treatment_rate)
# ---------------------------------------------------------------------------

B_SEGMENTS = (
    ("desktop", 1200, 7000, 0.200, 0.150),
    ("mobile", 6900, 2400, 0.050, 0.030),
    ("tablet", 1500, 1000, 0.090, 0.060),
)

B_LATENCY_CONTROL = (220.0, 30.0)
B_LATENCY_TREATMENT = (221.0, 30.0)  # trivially different -- not the problem here

# ---------------------------------------------------------------------------
# The continuous metric shared by both datasets: a lognormal "time on page"
# with a small planted fraction of bot-like outlier sessions in every group.
# ---------------------------------------------------------------------------

TIME_ON_PAGE_MU = 3.9  # log-space mean -> median about 49.4s
TIME_ON_PAGE_SIGMA = 0.5
OUTLIER_FRACTION = 0.004
OUTLIER_RANGE_SEC = (3000.0, 6000.0)

GUARDRAIL_TOLERANCE_MS = 5.0
PEEK_CHECKPOINT_EVERY = 500
ALPHA = 0.05
SRM_ALPHA = 0.001
