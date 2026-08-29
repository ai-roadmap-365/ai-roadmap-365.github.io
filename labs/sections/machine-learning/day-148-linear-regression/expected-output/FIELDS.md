# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

- **Everything in section 1 (the BMI model).** `sklearn.datasets.
  load_diabetes(scaled=False)` returns a fixed, bundled array — not a
  random draw. There is no seed involved in fitting it. The slope
  (`10.2331`), intercept (`-117.7734`), R-squared (`0.3439`), standard
  error (`0.6738`), confidence interval, and the fact that the predicted
  value at `mean(bmi)` equals `mean(y)` to within `1e-8` are all exact on
  any working install of these three packages, on any operating system.
- **The residuals of any least-squares fit with an intercept sum to
  (essentially) zero.** This is a property of the normal equations, not
  an observation — it holds on any dataset.
- **A least-squares line with an intercept passes through the point
  `(mean(x), mean(y))` exactly.** Same reason.
- **The direction of every result.** The slope-recovery error strictly
  decreases as n grows; a straight line fitted to curved data leaves
  residuals that trace the curve; heteroscedastic noise produces a larger
  residual spread in the high-x half than the low-x half; a high-leverage
  point moves the fitted slope; forcing `fit_intercept=False` on data
  whose true intercept is far from zero increases RMSE. Harness check 8
  confirms four of these at seeds the lesson does not quote.
- **Leverage exceeds `1/n` for every point**, and is strictly larger for a
  point further from `mean(x)`. This is the formula
  `h = 1/n + (x - xbar)^2 / sum((x - xbar)^2)` evaluated, not measured.

## Exact under these pins, and only these

Three figures in this lab are averages over seeded draws from
`numpy.random.default_rng`, and NumPy's own documentation states that
`Generator` carries no stream-compatibility guarantee across versions.
Under the exact pins above, these are reproducible to four decimal places:

| Value | Exercise | What it is |
| --- | --- | --- |
| `(20, 0.2315), (50, 0.1556), (200, 0.078), (1000, 0.0357), (5000, 0.0159)` | 2 | mean absolute error of the recovered slope, at each n, over 200 replications |
| the curved-data R-squared `0.852` and the binned residual means | 3 | one draw from `curved_dataset(seed=1)` |
| the quadratic-fit R-squared on the curved residuals, `0.3558` | 3b | derived from the same draw |
| the heteroscedastic R-squared `0.5723` and the two half-spreads `4.7427`, `12.0684` | 4 | one draw from `heteroscedastic_dataset(seed=2)` |
| the leverage-point slopes `1.5196` and `0.2138`, and the leverage values `0.8048` and `0.0299` | 5, 5b | one draw from `leverage_dataset(seed=3)` plus one fixed added point |
| the intercept-cost RMSEs `6.1401` and `9.7878` | 6 | one draw from `intercept_dataset(seed=4)` |
| the BMI residuals' quadratic R-squared `0.0002` and skewness `0.156` | 7 | derived from the exact section-1 fit, so only the diagnostic arithmetic (not the data) depends on the pins |

## Sampled, and therefore soft even here

- **The slope-recovery table (exercise 2) is averaged over 200
  replications per n**, for the reason Days 117-118 and Day 144 both
  established: a single fit's error is an anecdote. A lone replication at
  n=20 produced anything from 0.02 to 0.6 while this lab was being built.
  Exercise 2b therefore asserts a *range* around the one-over-root-n
  prediction (0.25 to 0.40, and 0.04 to 0.09) rather than an exact ratio.
- **`0.8520` is a good-looking R-squared on data with real, substantial
  curvature.** That is the honest finding of exercise 3: the summary
  statistic does not warn you. A different seed would give a different
  R-squared, not necessarily this respectable-looking, but the shape of
  the binned residuals — positive, negative, positive — holds at every
  seed the harness checked.
- **`26.94` (the leverage ratio) depends on both the base dataset's
  spread and the added point's exact x-value.** Move the added point
  closer to `mean(x)` and the ratio shrinks; this lab fixed `x_new=40.0`
  specifically because the base data lives in `[0, 10]`, so the point is
  four times the range away.

## Timings

No timing is asserted anywhere in this lab. The heaviest step is exercise
2's 1,000 total fits (200 replications at five sample sizes, the largest
being 5,000 rows), which completes in well under a second on the capture
machine and will take longer elsewhere without changing a single
assertion, because every assertion is about a shape or a value.
