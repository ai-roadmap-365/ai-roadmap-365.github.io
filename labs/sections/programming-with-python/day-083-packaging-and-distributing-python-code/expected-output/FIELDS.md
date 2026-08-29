# Expected output — Day 083 lab

Every file in this directory is a real capture from the authoring machine
(macOS 26.5.1, Apple Silicon, Python 3.14.0, bash 3.2.57, 2026-07-19) with
`build` 1.5.0, `setuptools` 83.0.0, `pip` 25.2 and `pytest` 9.1.1. Absolute
paths appear as `<repo>`; the interpreter that ran the build appears as
`<env>`. On your machine both are real paths.

**Nothing in these captures uploaded anything to any index.** Every install
shown passes `--no-index`, except the one editable install in
`import-resolution.txt`, which is labelled in the capture itself and needs a
network only because `pip install -e .` builds with isolation.

Nothing in this lab reads the clock, the network, or a random number, so the
listings and the counts below are the same on any machine running the pinned
tool versions. Only the timestamps inside the archive listings differ.

## Files

- `build-and-inspect.txt` — a full run of `bash examples/build_and_inspect.sh`:
  build, sdist listing, wheel listing, metadata, entry points, a fresh
  environment, the installed command, and the resolved `__file__`. If you read
  one file here, read this one.
- `artifact-contents.txt` — the two artifacts opened side by side, plus the
  complete `METADATA`, `WHEEL`, `RECORD`, `entry_points.txt` and
  `top_level.txt` files from inside the wheel.
- `import-resolution.txt` — the three-way comparison the lab exists for: the
  same import, in a src layout with the wheel installed, in a flat layout with
  the same wheel installed, and under an editable install.
- `build-failures.txt` — `name` and then `version` removed from `[project]`.
  Both builds fail, both name the missing field, and neither leaves a `dist/`
  behind.
- `starter-build.txt` — the starter built exactly as shipped, showing the three
  gaps exercises 1 to 5 close.
- `test-run.txt` — a full run of `bash tests/run_tests.sh`: 87 checks, 0
  failures, exit 0.

## Required behaviour of the reference project

| Command, run in the project directory | Result |
| --- | --- |
| `python3 -m build --no-isolation` | exit 0, two files in `dist/` |
| `ls dist/` | `wordtally_tools-0.3.1-py3-none-any.whl` and `wordtally_tools-0.3.1.tar.gz` |
| `unzip -t dist/…whl` | no errors: the wheel is a valid zip |
| `unzip -Z1 dist/…whl \| wc -l` | 10 entries |
| `unzip -p dist/…whl …/entry_points.txt` | `[console_scripts]` then `wordtally = wordtally.cli:main` |
| `tar -tzf dist/…tar.gz \| wc -l` | 24 entries |

## What is in which artifact

| Path | In the sdist | In the wheel | Why |
| --- | --- | --- | --- |
| `src/wordtally/core.py` | yes, with the `src/` prefix | yes, flattened to `wordtally/core.py` | a wheel is unpacked straight into `site-packages` |
| `wordtally/data/stopwords.txt` | yes | yes | declared in `[tool.setuptools.package-data]`; the installed code reads it at runtime |
| `pyproject.toml` | yes | no | build instructions; the wheel is already built |
| `MANIFEST.in` | yes | no | it only ever controlled the sdist |
| `tests/test_core.py` | yes | no | users install a package, not a test suite |
| `PKG-INFO` | yes | no | the sdist's metadata file; the wheel uses `METADATA` instead |
| `…dist-info/METADATA` | no | yes | the installed metadata, and what an index displays |
| `…dist-info/RECORD` | no | yes | the manifest an uninstall reads |

## Required behaviour after installing

| Command | Result |
| --- | --- |
| `pip install --no-index …whl` | exit 0, no index contacted |
| `workspace/tryout/bin/wordtally --version` | `wordtally 0.3.1`, exit 0 |
| `wordtally count sample.txt` | `12`, exit 0 |
| `wordtally top sample.txt -n 2` | `     3  mat` then `     1  cat`, exit 0 |
| `wordtally count no-such-file.txt` | a message on standard error, exit 2 |
| `python -c "import wordtally_tools"` | `ModuleNotFoundError` — the distribution name is not an import name |
| `python -c "import wordtally; print(wordtally.__file__)"` from the project | a path inside `workspace/tryout/lib/python3.14/site-packages/` |

## The src-layout proof

| Layout | `wordtally.__file__`, evaluated inside the project |
| --- | --- |
| `src` layout, wheel installed | `…/workspace/tryout/lib/python3.14/site-packages/wordtally/__init__.py` |
| flat layout, same wheel installed | `…/workspace/flat/wordtally/__init__.py` |
| `src` layout, editable install | `…/workspace/demo/src/wordtally/__init__.py` |

Row one is what you want when you test. Row two is the accident the src layout
prevents: the installed copy is present and loses anyway, so the suite passes
against code that is not what anyone receives. Row three is deliberate and
correct — an editable install is *supposed* to point at your working tree.

## Required behaviour of the starter

| Check on the starter's wheel, as shipped | Result |
| --- | --- |
| artifacts exist | `wordtally_tools-0.1.0-*` — its own declared version |
| `METADATA` size | 103 bytes, five lines |
| `entry_points.txt` present | no — exercise 4 is real work |
| `wordtally/data/stopwords.txt` present | no — exercise 5 is real work |

## Platform notes

- **Linux** produces identical listings. The wheel tag stays `py3-none-any`
  because the project is pure Python; only the intermediate
  `build/bdist.macosx-26.0-arm64/` directory name in the verbose build log is
  platform-specific, and it does not appear in any artifact.
- **Windows**: run everything inside WSL. On native Windows the environment
  layout is `Scripts\` rather than `bin/`, and the installed console script is
  `wordtally.exe` rather than a shebang script, so the shebang check in
  section 5 of the harness does not apply there.
- **Different tool versions** will change wording and byte sizes. setuptools'
  error text for missing metadata, pip's install summary and the exact file
  sizes all move between releases. The exit codes, the artifact names, the set
  of files inside each archive and the resolved `__file__` will not — which is
  why `tests/run_tests.sh` asserts on those and not on prose.
- The harness builds everything under `workspace/` and removes it in an `EXIT`
  trap, so a completed run — passing or failing — leaves nothing behind.
