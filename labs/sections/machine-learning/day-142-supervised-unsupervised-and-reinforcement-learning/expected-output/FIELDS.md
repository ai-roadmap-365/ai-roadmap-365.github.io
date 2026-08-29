# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

These are arithmetic or structural facts about the data, not measurements
that happened to come out a certain way.

- **`0.24` versus `0.8933…` — the two cluster accuracies (exercise 2).**
  The *gap* is the point, and the gap is structural: `raw_cluster_accuracy`
  compares k-means' internal cluster numbering to the species codes, and
  those numberings have no reason on earth to agree. Any implementation
  that numbers its clusters differently gives a different raw figure; what
  never changes is that the raw figure is uninformative and the
  best-permutation figure is the one people mean.
- **The confusion table sums (exercise 3).** Each row of
  `cluster_confusion` sums to exactly 50 because iris carries exactly 50
  rows per species. The harness asserts the row totals as well as the
  entries.
- **Inertia falls monotonically in k (exercise 5).** This is a theorem, not
  a measurement: the k-means objective at `k+1` is bounded above by the
  objective at `k` (take the `k` solution and split one cluster). So
  "choose the k that minimises inertia" always answers `k = n`, on every
  dataset, forever. The specific values are version-dependent; the
  monotonicity is not.
- **`8` — the shortest path across a 5×5 grid (exercise 7).** Four moves
  down and four moves right, in any order. Arithmetic.
- **`0/300` versus `300/300` — the tie-breaking result (exercise 7).**
  `np.argmax` is *documented* to return the first occurrence of the
  maximum. On an all-zero Q-row that is always index 0, which in this
  action table is "up". An agent whose greedy branch is a constant "up"
  cannot reach a goal in the bottom-right corner of an open grid within
  200 steps, on any machine, under any seed. The exact figure `0` is
  therefore not luck.
- **`2000` — total pulls in a logged dataset (exercise 8).** The loop runs
  exactly `steps` times.
- **The four verdicts from `classify_problem` (exercise 10).** Pure
  branching logic over three booleans.

## Exact under these pins, and only these

Every remaining number depends on NumPy's `default_rng` bit stream and on
scikit-learn's estimator internals. **NumPy's own documentation states
that `Generator` carries no stream-compatibility guarantee across
versions**, so seeding makes these numbers reproducible under the pins in
`requirements/requirements.txt` and not beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| `0.9200` | 1 | 5-NN accuracy on a 100/50 iris split at seed 142 |
| `0.8933333333333333`, mapping `(1, 0, 2)` | 2 | best-permutation accuracy of k-means at k=3, seed 0 |
| `[0, 50, 0]`, `[48, 0, 2]`, `[14, 0, 36]` | 3 | the cluster confusion table |
| `0.8036117420390129` | 4 | adjusted Rand index between the raw and standardised clusterings |
| `0.7302382722834697`, `0.6201351808870379` | 4 | those two clusterings against the true species |
| `[152.348, 78.851, 57.228, 46.446, 39.04]` | 5 | inertia at k = 2…6 |
| `[0.681, 0.5528, 0.4981, 0.4887, 0.3648]` | 5 | mean silhouette at k = 2…6 |
| `0.9838` / `0.3130`, `1.1314` / `0.4336`, `1.2800` / `0.7080` | 6 | mean reward and optimal-action rate at ε = 0, 0.01, 0.1 |
| `46.8`, `10.4` | 7 | mean gridworld episode length over the first and last ten episodes |
| `[1, 2, 3, 5, 10, 18, 20, 21, 22]` | 7 | states carrying a non-zero value after n episodes |
| `1813`, `187`, `30` | 8 | pull counts in the ε=0.1 log at seed 0 |
| `3/8`, `4/8`, `7/8` | 8 | how often a log names the truly best arm |
| `1524`, `274`, `0.9054`, `0.8216`, `0.8634`, `0.9262` | 8 | the winner's-curse figures at seed 1 |
| `[0.6455, 0.778, 0.896, 0.924, 0.947]` | 9 | accuracy against label budget, averaged over 40 splits |
| `[0.64, 0.92, 0.92, 0.86, 0.96]` | 9 | the same curve on a single split — deliberately not monotone |
| `0.876`, `0.9535` | 9 | three chosen labels, and every row labelled |

## Sampled, and therefore soft even here

- **The bandit figures in exercise 6 are averages over 200 independent
  problems**, which is the standard way this comparison is reported. A
  single run of a single 10-armed bandit is dominated by which arms
  happened to be good, and reading a conclusion off one run would be
  exactly the mistake Day 141 spent a whole lesson on. Two hundred runs is
  enough to separate `0.313` from `0.708` decisively; it is not enough to
  defend the fourth decimal place as anything but a seeded artefact.
- **The label-budget curve in exercise 9 is averaged over 40 splits** for
  the same reason, and the lab keeps the single-split version beside it
  precisely so the reader can see how badly one split misleads: on split
  142 alone, five labels beat twenty.

## Timings

No timing is asserted anywhere in this lab. The whole harness runs in a
few seconds here; on a slower machine it will take longer and every
assertion will still hold, because every assertion is about a shape or a
value.
