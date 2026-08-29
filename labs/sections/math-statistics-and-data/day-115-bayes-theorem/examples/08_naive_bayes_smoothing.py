"""Exercise 8 -- Naive Bayes from scratch, and the one-word veto that
Laplace smoothing exists to prevent.

Trained on three spam documents and three ham documents -- small enough to
read the whole vocabulary and every word count by hand. Classified with and
without Laplace (add-one) smoothing, on documents chosen specifically to
show the difference: two clean cases where smoothing changes nothing, and
one case built around a single word absent from one class's training data,
where the unsmoothed classifier's probability for that class collapses to
exactly zero and the decision is decided by an accident of iteration order
instead of by the evidence.
"""

import dataset as D
import naive_bayes as NB

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


model = NB.train({"spam": D.SPAM_DOCS, "ham": D.HAM_DOCS})

print("Training corpus")
print("-" * 60)
print("  spam:", D.SPAM_DOCS)
print("  ham: ", D.HAM_DOCS)
print(f"  vocabulary: {len(model.vocabulary)} words -- {sorted(model.vocabulary)}")
print(f"  total words per class: {model.total_words}")

print()
print("'watches' and 'review' never cross class lines in training")
print("-" * 60)
watches_in_ham = model.word_counts["ham"]["watches"]
review_in_spam = model.word_counts["spam"]["review"]
print(f"  count('watches', ham)  = {watches_in_ham}")
print(f"  count('review', spam)  = {review_in_spam}")
check("'watches' never appears in the ham training documents", watches_in_ham == 0)
check("'review' never appears in the spam training documents", review_in_spam == 0)

print()
print("Two clean held-out documents -- smoothed and unsmoothed agree")
print("-" * 60)
for doc in (D.HELD_OUT_CLEAR_SPAM, D.HELD_OUT_CLEAR_HAM):
    smoothed_winner, smoothed_scores = NB.classify(model, doc, alpha=D.LAPLACE_ALPHA)
    unsmoothed_winner, unsmoothed_scores = NB.classify(model, doc, alpha=0)
    print(f"  {doc!r}: smoothed -> {smoothed_winner}, unsmoothed -> {unsmoothed_winner}")
    check(f"{doc!r} classifies the same way smoothed and unsmoothed", smoothed_winner == unsmoothed_winner)

expected_spam_winner, _ = NB.classify(model, D.HELD_OUT_CLEAR_SPAM, alpha=D.LAPLACE_ALPHA)
expected_ham_winner, _ = NB.classify(model, D.HELD_OUT_CLEAR_HAM, alpha=D.LAPLACE_ALPHA)
check(f"{D.HELD_OUT_CLEAR_SPAM!r} is correctly classified spam", expected_spam_winner == "spam")
check(f"{D.HELD_OUT_CLEAR_HAM!r} is correctly classified ham", expected_ham_winner == "ham")

print()
print("The veto case: three ham words and one spam word, mixed")
print("-" * 60)
print(f"  document: {D.HELD_OUT_VETO_CASE!r}")

smoothed_winner, smoothed_scores = NB.classify(model, D.HELD_OUT_VETO_CASE, alpha=D.LAPLACE_ALPHA)
print(f"  WITH Laplace smoothing (alpha={D.LAPLACE_ALPHA}):")
for cls, score in smoothed_scores.items():
    print(f"    P({cls}) x P(words|{cls}) = {score}  ({float(score):.3e})")
print(f"    winner: {smoothed_winner}")

unsmoothed_winner, unsmoothed_scores = NB.classify(model, D.HELD_OUT_VETO_CASE, alpha=0)
print(f"  WITHOUT smoothing (alpha=0):")
for cls, score in unsmoothed_scores.items():
    print(f"    P({cls}) x P(words|{cls}) = {score}  ({float(score):.3e})")
print(f"    winner: {unsmoothed_winner}")

check("with smoothing, the veto-case document is correctly classified ham", smoothed_winner == "ham")
check(
    "without smoothing, ham's score collapses to EXACTLY zero because of one absent word",
    unsmoothed_scores["ham"] == 0,
)
check(
    "without smoothing, spam's score ALSO collapses to exactly zero, from the other absent word",
    unsmoothed_scores["spam"] == 0,
)
check(
    "with both scores tied at zero, the unsmoothed classifier picks a class by tie-break order, not evidence",
    unsmoothed_winner != smoothed_winner,
)

print()
print("What just happened")
print("-" * 60)
print("  'watches' has never been seen in a ham document, so its unsmoothed")
print("  P(watches | ham) is exactly 0 -- and multiplying anything by 0 gives")
print("  0, no matter how strongly 'please', 'review' and 'schedule' point")
print("  toward ham. One unseen word vetoed three words of real evidence.")
print("  Laplace smoothing gives every word in the vocabulary a small")
print("  nonzero probability under every class, so a single absence can")
print("  never single-handedly decide the outcome.")

print()
if all(ok for _, ok in checks_held):
    print(f"08_naive_bayes_smoothing.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
