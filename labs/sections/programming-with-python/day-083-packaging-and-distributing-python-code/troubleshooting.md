# Troubleshooting — Day 083 lab

## `No module named build`

The `build` package is not installed for the interpreter you invoked. `python3`
on your `PATH` and `.venv/bin/python` are different interpreters with different
packages.

```bash
.venv/bin/python -m build --no-isolation
# or, for the harness:
PYTHON=.venv/bin/python bash tests/run_tests.sh
```

If `.venv/` does not exist yet, follow the Installation section of `README.md`.

## `Backend 'setuptools.build_meta' is not available`

You passed `--no-isolation` and setuptools is not installed in that
environment. Two fixes, and they teach opposite lessons:

```bash
.venv/bin/pip install -r requirements/requirements.txt   # install the backend
```

or drop the flag and let the frontend build its own isolated environment:

```bash
python3 -m build          # needs a network the first time
```

The second is what a real release does. The first is what this lab does, so
that every run is offline and reproducible.

## The build tries to reach the network and hangs or fails

You omitted `--no-isolation`. `python -m build` creates a fresh environment per
build and installs the packages listed in `[build-system] requires` into it,
which means contacting an index. Add `--no-isolation` back.

## `error: Multiple top-level packages discovered in a flat-layout`

setuptools found more than one importable directory in the project root and
refuses to guess. Either move the package under `src/` (the layout this lab
argues for) or say explicitly what to package:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

## `configuration error: 'project' must contain ['name', 'version'] properties`

A required metadata field is missing from `[project]`. This is not a bug — it
is exercise 9, and section 9 of the harness reproduces it deliberately. Put the
field back.

## The wheel built, but `wordtally` is not a command after installing

`[project.scripts]` is missing or misspelled. Check what actually landed in the
artifact:

```bash
unzip -p dist/wordtally_tools-0.3.1-py3-none-any.whl \
  wordtally_tools-0.3.1.dist-info/entry_points.txt
```

If that file does not exist, the declaration never made it into the build. The
value must be `"import.path:callable"` — a colon, not a dot, before the
function name.

## `FileNotFoundError` mentioning `stopwords.txt` after installing

The data file was not shipped. Files inside your package directory are **not**
included just because they are there. Declare them:

```toml
[tool.setuptools.package-data]
wordtally = ["data/*.txt"]
```

Rebuild and confirm:

```bash
unzip -l dist/wordtally_tools-0.3.1-py3-none-any.whl | grep stopwords
```

This is the most common packaging bug there is, and it is invisible until
somebody installs your package somewhere other than your machine — which is
precisely why the lab installs into a fresh environment rather than trusting
the source tree.

## `import wordtally` resolves to a path inside my project, not the environment

Expected in a flat layout, and the reason this lab uses `src`. Python puts the
script's directory (or, for `python -c`, the current directory) at the front of
`sys.path`, so a `wordtally/` folder in the working directory wins over the
installed copy. Check what you actually have:

```bash
ls            # is there a bare wordtally/ directory here?
python3 -c "import wordtally; print(wordtally.__file__)"
```

Section 6 of the harness demonstrates both outcomes side by side.

## `pip install --no-index` fails with `Could not find a version that satisfies`

The wheel you named does not exist at that path, or the project you built
declares a dependency that is not available locally. The reference project
declares none deliberately, so an offline install is always possible; if you
added one as an extension exercise, that failure is the correct and instructive
result.

## The version number in the filenames is not what I expected

Artifact names come from `[project] version`, and stale artifacts are not
deleted by a new build. If `dist/` holds several versions, remove it and
rebuild:

```bash
rm -rf dist && python3 -m build --no-isolation && ls dist/
```

## `unzip: command not found`

The harness opens the wheel with `unzip` on purpose, because seeing a wheel
open as an ordinary archive is the point. Install it (`apt install unzip`,
`dnf install unzip`), or look inside with Python instead:

```bash
python3 -m zipfile -l dist/wordtally_tools-0.3.1-py3-none-any.whl
```

## The harness fails only on the `17 passed` check

You edited the packaged project's test suite, which is fine — the harness pins
the count so that a silently disappearing test cannot pass unnoticed. Update
the expected number in `tests/run_tests.sh` to match your suite.

## Everything passes but `workspace/` is still there

`tests/run_tests.sh` removes it in an `EXIT` trap, so a normal run cleans up
even after a failure. If you interrupted the run with a signal the trap may not
have fired: `rm -rf workspace`.

## Windows

Use WSL. Native Windows differs in ways that break the paths in this lab:
environment binaries live in `Scripts\` rather than `bin/`, an installed
console script is `wordtally.exe` rather than a shebang script, and both
scripts here are bash.
