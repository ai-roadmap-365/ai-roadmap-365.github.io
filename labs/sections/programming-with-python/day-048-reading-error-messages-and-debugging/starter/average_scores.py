# average_scores.py — YOUR COPY TO FIX.
# Run it (python3 average_scores.py), read the traceback bottom-up, then fix
# the one line marked BUG so the program runs cleanly. Record your work in
# debug-worksheet.md.
scores = [88, 92, 79, 95]

for i in range(len(scores) + 1):  # BUG: read the traceback, then correct this line
    print(f"Student {i + 1}: {scores[i]}")

average = sum(scores) / len(scores)
print(f"Average: {average}")
