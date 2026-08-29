# Pipeline design worksheet — Day 055

Design your second pipeline *before* you code it (practice assignment). Pick
a different set of records — books, transactions, songs — and plan the same
five pieces you built for the sample data. Keep this file; the Week 8 project
(Terminal Task Manager) reuses these transform-and-filter habits.

## 1. Your records

Write 5-8 sample rows and the fields each one has.

| Field | Type | Example |
| ----- | ---- | ------- |
|       |      |         |
|       |      |         |
|       |      |         |
|       |      |         |

## 2. List comprehension (map + filter)

- What do you keep (the `if`)? ____________________
- What do you build for each kept item (the output expression)? ____________________
- The one line:

```python

```

## 3. Dict comprehension (a lookup)

- Key: ____________________  Value: ____________________
- The one line:

```python

```

## 4. Set comprehension (distinct values)

- Which field's distinct values? ____________________
- The one line:

```python

```

## 5. Lazy generator pipeline

- Stage 1 — reader (`yield` one parsed record): ____________________
- Stage 2 — filter (`yield` only records that qualify): ____________________
- Aggregate computed at the end (sum or average of what?): ____________________
- The `assert` that proves the lazy result equals the plain-loop result:

```python
assert lazy_result == loop_result
```

## 6. itertools.islice

- Paste the line that prints just the first two items of your reader, and
  what it printed:

```text

```

## 7. What the program printed (fill in after building)

```text

```
