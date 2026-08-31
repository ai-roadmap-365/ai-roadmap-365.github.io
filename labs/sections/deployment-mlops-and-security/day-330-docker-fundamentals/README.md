# Day 330 Lab: Docker Fundamentals

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose

Model Docker's build cache so you can see what an edit actually costs — without installing Docker, and without waiting three minutes to discover you were wrong.

The cache follows one rule, and almost everyone gets it wrong at least once:

> a layer is reused only if every layer before it was reused, **and** its own inputs are unchanged

You will build a parser, a cache model and a linter, then measure the difference the rule makes on two Dockerfiles that install the same packages from the same base image.

## Learning objectives

- Parse a Dockerfile into layers, joining continuations and keeping real line numbers.
- Decide which sources a `COPY` reads, and which project files those cover.
- Apply the cache rule, including the part where a layer misses because something above it did.
- Explain why instruction order changes warm-build time but not cold-build time.
- Detect the ordering, pinning, cleanup and privilege mistakes that cost time or ship a risk.

## Prerequisites

- Day 329, "Section Project: A Production Assistant".
- Comfortable with Python dataclasses and basic regular expressions.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU, no container runtime. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

**Docker is not required.** This lab is about the rule the cache follows, which you can reason about on paper — and reasoning about it is what stops you burning ten minutes per rebuild for a year. If you do have Docker installed, the extension exercises suggest checking the model against a real build.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no registry login, no network. Docker Engine itself is Apache-2.0; Podman and Buildah are drop-in, daemonless alternatives that read the same Dockerfiles.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/layer_cache.py    your work: twelve stubbed tasks
examples/layer_cache.py   reference implementation
examples/cache_demo.py    two Dockerfiles, one edited file
tests/test_layer_cache.py grouped by what the cache model decides
tests/run_tests.sh        suite entry point
expected-output/          real captured output and measured values
requirements/             pinned dependency
```

## How to run

```bash
python3 examples/cache_demo.py   # compare two Dockerfiles after one edit
bash tests/run_tests.sh          # run the suite
```

To work on the exercise, edit `starter/layer_cache.py`, then copy it over the reference:

```bash
cp starter/layer_cache.py examples/layer_cache.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/cache_demo.py` parses two Dockerfiles that build the same application, plans a cold build and a warm build after one source file changes, prints which layer missed first and why, and lints both.

`bash tests/run_tests.sh` runs `pytest` over twenty-eight tests grouped by what the model decides: parsing, cost, copied paths, the cache rule, linting and the digest.

## Expected output

```text
--- naive: COPY . . then install ---
  cold build   0/6 layers cached  rebuild 76.0s
  after edit   2/6 layers cached  rebuild 76.0s
  first miss   line 3: COPY . .
               reads changed file(s): src/app.py
--- ordered: manifest, install, then source ---
  cold build   0/8 layers cached  rebuild 77.0s
  after edit   4/8 layers cached  rebuild 1.0s
--- the cost of one edit ---
  naive 76.0s vs ordered 1.0s
  ordering the same instructions is 76x faster to rebuild
```

Same base image, same packages, same application. Only the order differs — and the cold builds are within a second of each other, so the ordering costs nothing to adopt.

## Validation steps

1. `bash tests/run_tests.sh` reports `28 passed`.
2. The two cold builds must be within a few seconds of each other. If reordering appears to speed up a *first* build, `plan_build` is skipping layers in cold mode.
3. Editing `README.md` must cost `0.0s` in the ordered Dockerfile and the full `76.0s` in the naive one — `COPY . .` reads the README too.
4. Changing `requirements.txt` must re-run the install in **both** files. That is correct: the install genuinely depends on it.
5. The linter must report nothing on the ordered Dockerfile and three findings on the naive one.

## Tests

Twenty-eight tests in six groups:

- **parsing** — comments and blanks produce no layer; line numbers are the real ones; a backslash continuation is one instruction; the verb is uppercased and the arguments are not.
- **cost** — an install dwarfs a copy; metadata instructions are free; a `RUN` that installs nothing is cheap.
- **copied paths** — the last token is the destination; flags are not sources; a `RUN` has no sources.
- **the cache rule** — a cold build reuses nothing; an untouched project reuses everything; `COPY . .` puts the install downstream of every file; copying the manifest first protects it; everything after the first miss also misses; an unread file costs nothing; the cold builds match.
- **lint** — each rule fires when it should and stays quiet when it should not; findings carry the line to look at.
- **digest** — stable across comments and spacing, different when an instruction changes.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no Docker, no network, no credentials — and the reason a secret you `COPY` and later `rm` is still fully readable in the image.

## Extension exercises

1. **Add `.dockerignore`.** Give `plan_build` a set of ignored patterns and exclude matching files from what a broad `COPY` reads. Then measure how much of the naive Dockerfile's penalty it removes — the answer is instructive, because it is not all of it.
2. **Model multi-stage builds.** `COPY --from=builder` reads from an earlier stage rather than the project. Track stages by their `AS` name and let a stage's cache state depend on the stage it copies from.
3. **Check the model against reality.** If you have Docker or Podman, build both Dockerfiles, touch one source file, rebuild, and compare the real timings with the predicted ratio. Record where the model is wrong — it will be, and knowing how is the point.

## Navigation

- [Lesson](../../../../content/sections/deployment-mlops-and-security/day-330-docker-fundamentals/README.md)
- Previous: Day 329 — Section Project: A Production Assistant
- Next: Day 331 — Dockerizing an AI Application
