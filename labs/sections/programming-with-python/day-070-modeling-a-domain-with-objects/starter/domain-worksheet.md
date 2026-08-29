# Domain worksheet — Northside Gym

Fill this in **before** you write any code, using `examples/domain-rules.md`
only. Modelling happens on this page; the classes are just the transcript.

Keep the owner's words. If you write "user record" where the owner wrote
"member", you have already started drifting away from the domain.

---

## Part 1 — Nouns and verbs

Read the eleven rules and list every noun and every verb you find. Do not
filter yet; a bad candidate costs nothing on paper and a missed one costs an
afternoon.

### Nouns (candidate entities and value objects)

| Noun | Which rule(s) | First guess: entity, value object, or neither? |
| --- | --- | --- |
| club | 1, 10 |  |
| member | 2, 3 |  |
| membership number | 2, 3 |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

### Verbs (candidate behaviours) — and which object should own each one

| Verb | Which rule(s) | Owner (which class should have this method?) |
| --- | --- | --- |
| enrol a member | 2 |  |
| check in | 6, 7 |  |
| switch plans | 8 |  |
|  |  |  |
|  |  |  |
|  |  |  |

---

## Part 2 — Entities versus value objects

For each noun you kept, decide and **justify in one sentence**. The two
questions that settle it every time:

- *Would I still call it the same thing after all its values changed?* If
  yes it has identity → **entity**.
- *Would two of them with identical values be interchangeable?* If yes →
  **value object**.

| Noun | Entity or value object | One-sentence justification |
| --- | --- | --- |
| Member |  |  |
| MembershipNumber |  |  |
| Money |  |  |
| Plan |  |  |
| CheckIn |  |  |
| DateRange |  |  |
| Club |  |  |

Anything you classified as a value object must end up as a **frozen**
dataclass. Anything you classified as an entity keeps an identity field and
compares on it.

---

## Part 3 — Invariants and where each one is enforced

An invariant is a sentence that must be true of a valid model at all times.
Write each one in **one sentence**, then say exactly which line of code
refuses to let it break. If you cannot name the enforcement point, the rule
is not enforced — it is a hope.

| # | Invariant (one sentence) | Enforced where (class + method) | Error raised |
| --- | --- | --- | --- |
| 1 | A membership number looks like GYM-#### |  |  |
| 2 | A price is never negative |  |  |
| 3 | Two currencies are never added |  |  |
| 4 | No two members share a number |  |  |
| 5 | A basic member checks in at most 12 times a month |  |  |
| 6 | A billing period never ends before it starts |  |  |
| 7 |  |  |  |

---

## Part 4 — Boundaries

Draw the line. Fill in which module each responsibility lives in.

| Responsibility | Module | Is it allowed to do file I/O? |
| --- | --- | --- |
| The rules of the gym | `gym_core.py` | No |
| Turning the club into JSON and back | `gym_repository.py` | Yes |
| Printing the roster, choosing an exit code | `demo.py` | Yes |

Now answer in your own words:

1. Which direction do the imports run, and why must they never run the other
   way?

2. What can you test about the rules of this gym without creating a single
   file?

---

## Part 5 — The anti-pattern checklist

Run this against **your own design**, honestly. Answer each with a short
sentence, not a single word — the sentence is where the learning is.

1. **God object.** Does any one class know about more than its own job? Which
   class in your design is largest, and can you say in one sentence what it is
   responsible for?

2. **Anemic model.** Do your classes hold data only, with all the rules living
   in loose functions elsewhere? Name one rule that lives *inside* an object
   in your design and say why that is the right home for it.

3. **Primitive obsession.** Is there anywhere you used a `float` for money, a
   `str` for a date, or a `str` for something with a fixed set of values? List
   every place, or write "none, and here is what I used instead: ...".

4. **Premature inheritance.** Did you create any base class with exactly one
   subclass? If so, what would you lose by deleting it and using a plain
   function or composition instead?

5. **Stringly typed.** Could a typo in a string sail through your code and
   fail somewhere far away? Which construct prevents that in your design?

6. **Leaky boundary.** Search your own `gym_core.py` for `json`, `open`,
   `print`, `Path`, and `input`. Record the result here. If the search finds
   anything, the boundary has leaked and the fix is to move that code out.

---

## Part 6 — Evidence

Paste the real output of these two commands after you finish the exercises.

```text
$ bash tests/run_tests.sh
(paste the final line here)

$ python3 starter/demo.py club.json
(paste the first four lines here)
```
