# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

These are structural or arithmetic facts, not measurements that happened
to come out a certain way. Harness check 8 confirms the directional ones
at alphas and dataset seeds the lesson does not quote.

- **Ridge never produces an exact zero, at any alpha.** This follows from
  the L2 penalty's constraint region being smooth (a sphere in
  coefficient space) — its boundary never touches a coordinate axis except
  at a tangent point that would require infinite penalty. Confirmed across
  a 60-point sweep from alpha=0.001 to alpha=100, and re-confirmed at a
  different 25-point sweep from alpha=0.0001 to alpha=1000 in check 8.
- **Lasso's zero count never decreases as alpha grows.** The L1 penalty's
  feasible region shrinks monotonically as alpha grows, so the set of
  coefficients it can afford to keep nonzero can only shrink too.
- **Ridge and ElasticNet do not share an alpha scale**, because Ridge's
  objective sums the squared error and ElasticNet's averages it over
  `n_samples`. The correction factor is exactly `n_train`. This is
  arithmetic, not a measurement.
- **A model with `n_iter_ = None` (Ridge, by default) was solved directly;
  a model with a real `n_iter_` (Lasso, ElasticNet) was solved
  iteratively.** Structural, from how scikit-learn's estimators report
  themselves.
- **At a small enough alpha, both ridge and lasso agree with the
  unregularised (OLS) solution.** As alpha approaches zero, both penalty
  terms vanish and the optimisation problem becomes plain least squares.
  Confirmed to within 0.01 on the two-feature demo at alpha=0.001.

## Exact under these pins, and only these

Everything else is a specific coefficient, R2, alpha, or iteration count
from `Ridge`, `Lasso`, `LassoCV`, `ElasticNet`, or `LinearRegression`
fitted on `load_diabetes` or `make_regression`. Both scikit-learn's
internal coordinate-descent implementation and NumPy's linear-algebra
routines can change these values, even when the documented behaviour does
not change, between releases.

| Value | Exercise | What it is |
| --- | --- | --- |
| the four rows of the headline table | 1 | lasso and ridge zero counts and test R2 at alpha 0.001-1.0 |
| `alpha=0.07874`, `zeros=4`, `kept=['sex','bmi','bp','s1','s3','s5']` | 1b | LassoCV's own choice |
| the ten `zero_at` alphas, and that `s3` is first and `bmi` is last | 2, 2b | where each coefficient hits zero in the sweep |
| `precision=1.0`, `recall=1.0`, `n_selected=5` at alpha=1.0, noise=1.0 | 3 | sparse recovery, low noise |
| `recall=0.2` at noise=30, `recall=0.0` at noise=10, both alpha=80 | 3b | sparse recovery, too much penalty |
| mean precision `1.0` and `0.6792` over 10 seeds | 3b | sparse recovery across seeds |
| `n_kept = 10, 7, 3` for raw, standardized, sklearn's own scaling | 4 | scale-dependence |
| the seven-row ElasticNet sweep | 5 | zeros and R2 by l1_ratio |
| `[6.3098, 1.229, 22.6076]` and `[6.3097, 1.229, 22.6076]` | 5b | Ridge/ElasticNet after the n_train correction |
| `[3.048, 2.9742, 0.9944]` and `[5.0848, 0.0, 0.0]` at alpha=1.0 | 6 | ridge splits, lasso picks one |
| `[2.9724, 2.9646, 0.9664]` and `[0.0, 0.0, 0.0]` at alpha=10 | 6b | lasso zeros both, ridge still splits |
| `{0.001: 368, 0.01: 62, 0.1: 135, 1.0: 6}` | 7 | lasso iteration counts |
| `[1.9564, 1.9381]` (OLS) and the five-row corner table | 8, 8b | the two-feature demonstration |

## Sampled, and therefore soft even here

- **The near-duplicate split in exercise 6 is not guaranteed to be an
  EXACT zero at every dataset seed.** The two columns are built to
  correlate at roughly 0.9999, not to be identically collinear, so the
  precise floating-point split lasso's coordinate descent lands on can
  leave a tiny nonzero residual on the coefficient it is effectively
  dropping. Harness check 8 found `[5.0215, 0.0007]` at seed 3, rather
  than an exact `[x, 0.0]`. The lab's own claim at the quoted seed (0) IS
  an exact zero, and the harness's cross-seed check asserts the weaker
  but more honest "20x-or-greater asymmetric split" rather than an exact
  zero, because that is what holds at every seed tried.
- **The sparse-recovery numbers in exercise 3 depend on `make_regression`'s
  own seeded noise draw**, which is why exercise 3b reports a mean over
  ten seeds rather than trusting the one seed quoted in exercise 3.

## Timings

No timing is asserted anywhere in this lab. The heaviest step is the
60-point coefficient-path sweep in exercise 2, which refits twenty small
linear models sixty times over. It takes well under a second here and
will take longer elsewhere without changing a single assertion, because
every assertion is about a shape, a count, or a value — never a duration.
