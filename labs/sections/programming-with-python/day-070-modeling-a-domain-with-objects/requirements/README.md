# Dependencies — Day 070 lab

**Python 3 only. No third-party packages, no network, no API key.**

- `python3` (3.8 or newer; tested on 3.14.0). You set this up on Day 43.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only, and the split is the lesson in miniature:

| Module | Used in | Why |
| --- | --- | --- |
| `dataclasses` | `gym_core.py` | `frozen=True` value objects, `field(default_factory=list)`, `__post_init__` validation |
| `enum` | `gym_core.py` | `PlanTier` as a closed set, so a misspelled tier is impossible |
| `datetime` | `gym_core.py`, `gym_repository.py`, `demo.py` | real `date` objects, never date-shaped strings |
| `re` | `gym_core.py` | the membership-number pattern `GYM-####` |
| `json` | `gym_repository.py` **only** | the storage format — a repository concern, never a model concern |
| `pathlib` | `gym_repository.py` **only** | reading and writing the file |
| `sys` | `demo.py` **only** | command-line arguments, standard error, exit codes |

Read that table as a picture of the boundary. The four modules the core uses
can all be described as "ways of writing down a value". The three it does not
use can all be described as "ways of touching the world". That separation is
not a style preference — it is why the test suite can run every rule of this
gym from a directory containing no files at all.

There is deliberately no `requirements.txt`. Python ships everything a small
domain model needs, and adding a dependency to a hundred-and-eighty-line
model is a habit worth resisting.

The lesson's Alternatives section covers what you would reach for when a model
outgrows this: `sqlite3` (also standard library, so still nothing to install),
SQLAlchemy for a real relational schema, and pydantic for validating untrusted
input at a boundary. Both of those last two are free and open source and
install with `pip`. None is needed here, and the point of the repository class
is that adopting one later means rewriting one file.

Check your Python is present and new enough:

```bash
python3 --version
```

If that prints `Python 3.8` or higher, you are ready.

Windows users: run the commands inside WSL, or use `python` in place of
`python3` if that is how Python is exposed on your system. One cosmetic
difference is worth knowing: the roster header printed by `demo.py` contains
an em dash, so a terminal set to a legacy code page may show a replacement
character there. The numbers, the errors, and the JSON are byte-identical
everywhere.
