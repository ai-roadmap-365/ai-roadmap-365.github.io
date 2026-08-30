"""A project, the README that documents it well, and one that has drifted."""

from __future__ import annotations

from doccheck import Project

PROJECT = Project(
    commands=("make install", "make run", "make test"),
    captured_outputs={
        "make test": "12 passed in 0.4s",
        "make run": "listening on 127.0.0.1:8080",
    },
    known_limitations=(
        "English only",
        "no multi-tenant isolation",
    ),
)

GOOD_README = """
# Support Assistant

## What it does
Answers questions from your own documentation, with citations.

## Install
```bash
make install
```

## Run
```bash
make run
```

make run ->

```
listening on 127.0.0.1:8080
```

## Architecture
Ingestion writes chunks to a local index. A query embeds, retrieves the top
three chunks, and asks the model to answer using only those.

## Tests
```bash
make test
```

make test ->

```
12 passed in 0.4s
```

## Limitations
English only. There is no multi-tenant isolation, so one deployment serves one
team.

## Troubleshooting
If `make run` reports a port in use, set `PORT` and retry.
"""

DRIFTED_README = """
# Support Assistant

## What it does
Answers questions from your own documentation, with citations.

## Install
```bash
make setup
```

## Run
```bash
make serve
```

make run ->

```
listening on 0.0.0.0:9000
```

## Architecture
To be written.

## Troubleshooting
Under construction.
"""
