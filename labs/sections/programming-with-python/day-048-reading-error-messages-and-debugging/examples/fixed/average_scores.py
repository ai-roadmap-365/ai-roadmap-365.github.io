# average_scores.py — FIXED: the loop now stops at the last valid index.
scores = [88, 92, 79, 95]

for i in range(len(scores)):  # FIX: range(len(scores)) yields 0..len-1, all valid
    print(f"Student {i + 1}: {scores[i]}")

average = sum(scores) / len(scores)
print(f"Average: {average}")
