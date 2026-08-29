# Refactoring worksheet — a suite that scales

Work through these in order, from the `starter/` directory. Every command
below is copy-pasteable. Replace `pytest` with `.venv/bin/pytest` if you
installed the dependency into a lab-local virtual environment.

Fill in the measurement table at the bottom as you go. The point of this lab
is not that you end up with fewer lines — it is that you can say, with
numbers, what changed and why it is better.

---

## Exercise 0 — measure the starting point

```bash
pytest -q
pytest --collect-only -q | tail -2
grep -c 'store = PracticeStore(path)' test_practice_store.py
```

Record the three numbers in the table. On the authoring machine they were
`13 passed`, `13 tests collected`, and `8`.

Read the file once, top to bottom, and write one sentence here saying what is
wrong with it. "It repeats itself" is not enough — say what the repetition
*costs*.

> Your sentence:

---

## Exercise 1 — name the arrangement before you extract it

Six lines of setup appear eight times. Before writing any code, give the two
distinct arrangements a name. Good fixture names are nouns describing the
*state of the world*, not verbs describing the setup procedure.

- The store with a header row and no sessions is called: ______________
- The store holding the three sample sessions is called: ______________

If you find yourself writing `setup_store` or `make_store_and_add_things`,
try again. `empty_store` and `loaded_store` are the shape you want.

---

## Exercise 2 — extract the first fixture

Create a new file `conftest.py` **next to** `test_practice_store.py`. You do
not import it anywhere; pytest finds it by location.

```python
from datetime import date

import pytest

from practice_store import PracticeStore, Session


@pytest.fixture
def store_path(tmp_path):
    return tmp_path / "practice.csv"


@pytest.fixture
def empty_store(store_path):
    return PracticeStore(store_path).initialise()
```

Now rewrite `test_a_new_store_is_empty` and `test_add_then_find_round_trips`
so they take `empty_store` as a parameter instead of `tmp_path`, and delete
their setup lines. Run:

```bash
pytest -q
```

Still `13 passed`. You have changed the arrangement and not the assertions,
which is exactly what a refactor is.

---

## Exercise 3 — build a fixture on top of another fixture

Add a third fixture that requests the second one:

```python
@pytest.fixture
def loaded_store(empty_store):
    empty_store.add(Session("S-001", date(2026, 5, 4), "python", 45))
    empty_store.add(Session("S-002", date(2026, 5, 5), "linear-algebra", 30))
    empty_store.add(Session("S-003", date(2026, 5, 6), "python", 60))
    return empty_store
```

Rewrite the six remaining store tests to request `loaded_store`. Run the suite
and then count the duplication again:

```bash
pytest -q
grep -c 'store = PracticeStore(path)' test_practice_store.py
```

That count should now be `0`, and the test count unchanged at `13`.

---

## Exercise 4 — five tests become one, and stay five

The five rejection tests at the bottom of the file differ only in their
inputs. Replace all five with a single parametrized test:

```python
@pytest.mark.parametrize(
    ("ref", "topic", "minutes"),
    [
        ("001", "python", 45),
        ("S-1", "python", 45),
        ("S-001", "Python", 45),
        ("S-001", "python", 0),
        ("S-001", "python", MAX_MINUTES + 1),
    ],
    ids=[
        "ref-without-prefix",
        "ref-too-short",
        "topic-not-lower-case",
        "minutes-zero",
        "minutes-over-the-cap",
    ],
)
def test_refuses_a_bad_value(ref, topic, minutes):
    with pytest.raises(InvalidSession):
        Session(ref, date(2026, 5, 4), topic, minutes)
```

Now the check that matters. One function, five cases — how many tests does
pytest think it has?

```bash
pytest --collect-only -q | tail -2
```

The answer must still be `13 tests collected`. If it says `9`, the decorator
did not expand and you have five cases hiding inside one test that stops at
the first failure. Also confirm the ids are readable:

```bash
pytest --collect-only -q | grep refuses_a_bad_value
```

Every line should end in a square-bracketed name you chose, not `[ref0]`.

> How many test ids did you see, and what were they?

---

## Exercise 5 — the cross product

Add one more test with **two** stacked `parametrize` decorators — three topics
and three durations:

```python
@pytest.mark.parametrize("topic", ["python", "linear-algebra", "statistics"])
@pytest.mark.parametrize("minutes", [1, 45, MAX_MINUTES])
def test_every_topic_accepts_every_legal_duration(topic, minutes):
    session = Session("S-001", date(2026, 5, 4), topic, minutes)
    assert session.topic == topic
```

Predict the collected count before you run it, then check:

```bash
pytest --collect-only -q | tail -2
```

> Predicted: ______  Actual: ______

---

## Exercise 6 — markers and selection

Add this to `pytest.ini`:

```ini
addopts = --strict-markers
markers =
    validation: a test of the Session value rules — fast, no files touched
```

Put `pytestmark = pytest.mark.validation` at the top of the module, or mark
individual tests, and then select:

```bash
pytest --collect-only -q -m validation | tail -2
pytest --collect-only -q -k refuses | tail -2
```

`-m` selects by marker; `-k` matches a substring of the test id, parameter
names included. Try `-k "refuses and not minutes"` and explain the result.

> What `-k` expression would run only the two cases about references?

---

## Exercise 7 — teardown that runs anyway

Add a fixture that yields, with a `print` after the yield:

```python
@pytest.fixture
def audited_store(loaded_store):
    before = len(loaded_store.all())
    yield loaded_store
    after = len(loaded_store.all())
    print(f"[audit] sessions before: {before}, after: {after}")
```

Write one test that uses it and passes. Then write one that uses it and
fails on purpose, marked so the suite still goes green:

```python
@pytest.mark.xfail(strict=True, reason="fails on purpose, to show teardown still runs")
def test_teardown_runs_even_when_the_test_fails(audited_store):
    assert len(audited_store.all()) == 99
```

Run with `-s` so print output is not swallowed:

```bash
pytest -s -q
```

> Did the `[audit]` line appear for the failing test as well? Why does that
> guarantee matter more than a `try`/`finally` you write yourself?

---

## Measurement table

| Measurement | Before | After |
| --- | --- | --- |
| Lines in `test_practice_store.py` | | |
| Copies of the store setup (`grep -c`) | | |
| Test functions written by hand | | |
| Test items pytest collects | | |
| Assertions lost in the refactor | | `0` |

That last row is not optional. If any assertion disappeared, the refactor was
a rewrite, and a rewrite of a test suite is how coverage quietly evaporates.

---

## The design question

Answer this last, in two or three sentences, once everything passes.

You now have four fixtures. Pick the one you would delete first if a reviewer
said "this suite has too much indirection — I cannot tell what a test sets
up", and say what you would write in its place. A fixture used by one test is
usually a helper function wearing a costume.

> Your answer:
