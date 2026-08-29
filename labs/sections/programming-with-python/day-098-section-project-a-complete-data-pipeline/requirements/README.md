# Why each pin exists, and what is deliberately absent

```
SQLAlchemy==2.0.51
pydantic==2.13.4
pytest==9.1.1
```

Three dependencies for a pipeline that fetches over HTTP, validates, stores in a
real schema, reports and logs. That is not an accident; it is the point of the
last section of this course. Every dependency is a version to pin, a
vulnerability feed to watch, and one more thing that can break the job that runs
while you are asleep. The bar for adding one is that it earns its place.

| Pin | What it does here | What it replaces |
| --- | --- | --- |
| `SQLAlchemy==2.0.51` | The declarative models, the schema with its constraints and index, and the `INSERT ... ON CONFLICT DO NOTHING` that makes the store idempotent | Hand-written SQL strings and hand-written parameter binding (Days 88-91 did that on purpose, so you know what is being replaced) |
| `pydantic==2.13.4` | The validation gate: types, ranges, the timezone requirement, `extra="forbid"`, and error objects with a field path and a message | A wall of `if not isinstance(...)` that never produces a usable error report |
| `pytest==9.1.1` | The starter exercises | Nothing; it is the runner from Week 11 |

## What is deliberately NOT here

**`requests`.** Day 78 taught it and it is an excellent library. This pipeline
makes one GET with a timeout and one header, and `urllib.request` in the
standard library does exactly that. `requests` earns its place the moment you
need connection pooling across many calls, a `Session` with shared headers, or
`urllib3`'s `Retry` with its `Retry-After` handling — none of which this
pipeline needs. `examples/ingest.py` says so in its module docstring.

**Airflow, Dagster, Prefect, dbt.** The lesson describes all four from their
documentation, states plainly that no output from any of them is reproduced,
and section 1 of `tests/run_tests.sh` asserts that none of them is importable
here — so the claim cannot go quietly stale if somebody installs one later.

**Alembic.** Schema migration is Day 88's subject and SQLAlchemy's migration
tool is worth knowing about; this lab creates its schema once with
`Base.metadata.create_all` and never changes it, so a migration tool would be
scaffolding around nothing.

## Installing

```bash
cd labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

That install is the only moment this lab needs the network. Everything after it
talks to a fixture server on 127.0.0.1, and section 10 of the harness asserts
that no URL anywhere in the lab points at anything else.
