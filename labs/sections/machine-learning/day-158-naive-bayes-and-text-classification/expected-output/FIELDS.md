# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The Laplace smoothing formula `(N_cj + alpha) / (N_c + alpha * V)`** is an exact closed-form algebraic formula.
- **Log-sum probabilities `log P(y) + sum x_j log P(x_j|y)`** evaluate identically across platforms.
- **CountVectorizer integer token frequencies** are deterministic for regex `\b\w+\b`.

## Exact under these pins, and only these

- **MultinomialNB spam posterior probability on query 'urgent cash prize meeting'** evaluates to `0.8524` (85.24% Spam).
