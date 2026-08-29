# average_scores.py — prints each student's score, then the average.
scores = [88, 92, 79, 95]

for i in range(len(scores) + 1):  # BUG: + 1 makes the loop walk past the last index
    print(f"Student {i + 1}: {scores[i]}")

average = sum(scores) / len(scores)
print(f"Average: {average}")
