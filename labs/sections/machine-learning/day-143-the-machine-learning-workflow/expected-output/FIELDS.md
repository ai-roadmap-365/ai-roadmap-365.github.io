# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

These are structural facts about the pipeline, not measurements that
happened to come out a certain way.

- **The step logs.** `load, split, select, fit_and_score, baseline` for
  the honest pipeline and `load, select, split, fit_and_score, baseline`
  for the leaky one. These are the orders the two stage lists are written
  in, and nothing random touches them.
- **`StageContractError` naming `'select'` and `folds`.** The leaky
  pipeline puts `select` before `split`, and `select` declares `folds`
  among its requirements. The runner checks requirements against the keys
  present, which is pure dictionary arithmetic. This fires on every seed,
  on every machine, forever — check 8 of the harness runs it at five
  different seeds to make that concrete.
- **The stage line counts** — `load` 5, `split` 2, `select` 10,
  `fit_and_score` 9, `baseline` 4, total 30. These come from
  `inspect.getsource` over source files that ship in this directory. They
  will change if you edit the library, which is intended: the measurement
  is of *this* pipeline.
- **The confusion matrix summing to 2000**, and the accuracy recomputed
  from it agreeing with `accuracy_score`. Arithmetic.
- **The majority baseline having recall exactly 0.0.** A model that never
  predicts the positive class catches none of them, by definition.
- **Two runs at the same seed producing the same manifest.** This is what
  determinism means. If it ever fails, something genuinely non-deterministic
  has entered the pipeline and that is a real bug, not a version drift.
- **Every wrong-order score exceeding its honest counterpart** in the
  `inflation_by_k` table, and every honest score sitting at or below
  chance. The specific values move with the pins; the direction does not,
  because the wrong order fits the feature selection to the answers.

## Exact under these pins, and only these

Everything else depends on NumPy's `default_rng` bit stream and on
scikit-learn's estimator internals. **NumPy's own documentation states
that `Generator` carries no stream-compatibility guarantee across
versions**, so seeding makes these reproducible under the pins in
`requirements/requirements.txt` and not beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| `0.5000` | 2 | honest cross-validated accuracy on 100 rows of pure noise |
| `0.5400` | 2 | majority-class baseline — 100 coin flips do not land exactly even |
| `[0.5, 0.55, 0.5, 0.4, 0.55]` | 2 | the five per-fold scores behind that 0.5 |
| `0.7300` | 3 | the leaky pipeline's score, contracts disabled |
| `0.2300` | 3 | accuracy invented purely by transposing two stages |
| the `inflation_by_k` table | 3b | wrong and right scores at k = 5, 10, 20, 50 |
| `0.9200` / `0.0000` | 4 | the majority baseline's accuracy and recall |
| `0.9435` / `0.4813` | 4 | logistic regression at its default threshold |
| `0.8685` / `0.8438` | 4 | the same model with balanced class weights |
| `0.9360`, `0.9275` | 4 | 5-NN and the depth-3 tree |
| `[[1810, 30], [83, 77]]` | 5 | the confusion matrix |
| `51b0a421bd652dd2` and the other three hashes | 6 | the manifest |
| `160` positives in `2000` rows | 4 | the test set's composition |

The manifest hashes deserve a note of their own. They are SHA-256 over the
raw bytes of the arrays, so they depend on the exact float values, which
depend on the generator stream. A different NumPy will give you four
different hashes and the two-runs-agree property will still hold. **That
property is the one worth asserting; the literal hashes are a convenience
for spotting silent drift on this machine.**

## Sampled, and therefore soft even here

- **The honest score of `0.5000` is not a guarantee that the method is
  unbiased**, only that it landed on chance for this seed. The per-fold
  scores range from 0.40 to 0.55, which is what 20 test rows per fold buys
  you: a standard error of roughly 0.11. The point of the exercise is the
  *gap* between 0.50 and 0.73, not the 0.50.
- **`0.39` and `0.38`, the honest scores at k=5 and k=50, are below
  chance.** That is not a bug and it is not evidence of anti-learning. With
  100 rows and 5 folds, an estimate of a 0.5 quantity wanders, and it
  wanders below as readily as above. The lab asserts `right <= 0.5` rather
  than `right == 0.5` for exactly this reason.

## Timings

No timing is asserted anywhere in this lab. The heaviest step is computing
5000 correlations five times over, which takes a few seconds here and will
take longer elsewhere without changing a single assertion, because every
assertion is about a shape or a value.
