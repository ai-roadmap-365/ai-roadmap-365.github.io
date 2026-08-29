# Day 142 lab brief — Three Kinds of Feedback

Yesterday you learned what a model score does not mean. Today you learn
what kind of question you are even asking, and the answer turns out not
to depend on the algorithm at all. It depends on the **feedback signal**
your learner is given.

There are exactly three shapes of feedback, and every named branch of the
field falls out of them:

| Setting | What you are told | What you are never told |
| --- | --- | --- |
| Supervised | the correct output, for every input | nothing — you have the answer key |
| Unsupervised | nothing | whether any answer you found is right |
| Reinforcement | how good the action you took was | what the best action would have been |

That third row is the one people underestimate. **Evaluative feedback is
not weak supervision; it is a different kind of information.** A
supervised learner is told the answer. A reinforcement learner is told a
score for the one thing it tried, and must work out the counterfactual on
its own — by trying something else, which costs it reward.

## The three claims you are here to measure

1. **Unsupervised learning has no answer key, and pretending otherwise
   produces nonsense.** The same k-means partition of iris scores `0.24`
   or `0.8933` depending only on how you number the clusters. Sixty-five
   accuracy points, from arithmetic that has nothing to do with the data.
2. **A reinforcement learner that never explores never finds out.** A
   purely greedy agent on a ten-armed bandit takes the best arm 31% of
   the time. Spending 10% of its pulls on random exploration raises that
   to 71%. It is the same algorithm, the same problem, one parameter.
3. **A log of what a policy did is not a supervised dataset.** Eight
   greedy agents each produce two thousand rows of clean, honest, correct
   data — and five of the eight logs name the wrong arm as best. Four of
   them contain exactly one arm. There is no model that can fix that,
   because the missing rows were never collected.

## Two things you will find that the textbook does not say

Both were measured while building this lab, and both are in the exercises
because they are more instructive than the tidy version.

- **Standardising the features makes k-means *worse* on iris** (adjusted
  Rand index 0.620 scaled against 0.730 raw). "Always scale before
  clustering" is good default advice and it loses here, because iris's
  four features are already in the same unit and standardising promotes
  the noisiest of them. Exercise 4 measures it.
- **`np.argmax` decides whether your agent learns at all.** It returns
  the *lowest* index attaining the maximum, so on a Q-table that starts
  at all zeros the greedy branch of an ε-greedy agent is a constant
  action. The agent in exercise 7 reaches the goal in **0 of 300**
  episodes with `np.argmax` and **300 of 300** with random tie-breaking.
  Nothing throws. Nothing warns. The agent simply never learns, and the
  only symptom is a flat curve.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_feedback_lib.py`) and fifteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helpers and the exact values to assert. None of it is
   guesswork.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `feedback_lib.py`, `test_feedback_lib.py` and
`test_feedback_claims.py`; pytest aborts on the module-name collision.
Run them separately, always.

## The exercises

| # | What it establishes |
| --- | --- |
| 1 | Supervised learning means an answer exists for every training row |
| 2 | Cluster ids are arbitrary; raw accuracy against them is meaningless |
| 3 | What k-means actually found on iris — one species clean, two blended |
| 4 | Structure is not unique: standardising changes it, and here for the worse |
| 5 | Inertia cannot choose k, and silhouette chooses the wrong one |
| 6 | Evaluative feedback: the measured price of never exploring |
| 6b | A bandit reveals only the arm you pulled |
| 7 | Delayed credit — and the tie-breaking bug that silently prevents learning |
| 7b | The reward travels backwards exactly one state per episode |
| 8 | A log records only what the logging policy chose |
| 8b | A greedy log confirms whatever it locked onto |
| 8c | The winner's curse: why even a well-explored log gets one wrong |
| 9 | Labels are the expensive part, and clustering makes them go further |
| 10 | Naming the setting before choosing an algorithm |
| 10b | A function that refuses an incomplete description |

Exercise 8c is worth lingering on. The log that gets it wrong pulled the
genuinely best arm 1524 times and a slightly worse arm 274 times. More
data made the good arm's estimate *more accurate*, so it landed slightly
under its true mean, while the thinly-sampled arm landed over. Taking an
argmax over noisy estimates systematically favours whichever estimate is
most inflated. You will meet that exact effect again on Day 144, wearing
different clothes and called model-selection bias.
