# Storage worksheet — Day 039

Fill this in as you complete `starter/storage_demo.sh` and read the lesson.

## 1. Your database query and its result

Write the exact `SELECT` you ran in Exercise 2 (the OH revenue-per-customer query):

```sql
-- paste your query here
```

Paste its result (one row per Ohio customer):

```text
-- paste the output rows here (e.g. ada|180.0)
```

One sentence: why can the database answer this precise question faster than
grepping the CSV file, once the table has many rows?

> _your answer_

## 2. The object key you generated

Paste the content key (SHA-256 hash) your blob was stored under in Exercise 3:

```text
-- paste the key here
```

One sentence: if you store the exact same bytes again, what key do they get,
and why does that give you deduplication for free?

> _your answer_

## 3. Which store would you pick, and why?

| Workload | Store you'd pick | Why (one sentence) |
| --- | --- | --- |
| A 5 GB training dataset | | |
| A user profile record (name, email, settings) | | |
| A hot counter incremented thousands of times per second | | |

## 4. One thing that surprised you

> _your answer_
