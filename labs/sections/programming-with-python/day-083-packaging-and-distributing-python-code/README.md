# Day 083 lab — Build a Real Package and Install It

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Packaging and Distributing Python Code
- **Day number:** 83 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-083-packaging-and-distributing-python-code
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-083-packaging-and-distributing-python-code` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 83 of the course, and the day your code stops being something you run and
starts being something someone else installs.

You take a small library with a command-line front end, give it a complete
`pyproject.toml`, build it into the two artifacts Python distributes — an
sdist and a wheel — open both of them and read what is inside, then install
the wheel into a brand-new throwaway environment and run the command it puts
on your path.

By the end you will have seen, with your own eyes rather than on trust:

- that a wheel is a zip file with a metadata directory, and what every entry
  in it is for;
- that the sdist carries files the wheel deliberately does not;
- that one line of TOML is the entire difference between shipping a module and
  shipping a **command**;
- that with a `src` layout, the installed copy of your package is the copy
  Python imports even while you are standing inside the project — and that in
  a flat layout it silently is not.

**Nothing in this lab is uploaded anywhere.** No package index is contacted,
not once. Publishing is described accurately in the lesson and its commands
are shown, and then the lab stops before running them. Every `pip install`
here passes `--no-index`, which forbids pip from talking to any index at all,
and `tests/run_tests.sh` checks that claim mechanically rather than just
asserting it. The reason is not squeamishness: a version number published to
a public index can never be reused, so an accidental upload is a mistake with
no undo.

## Learning objectives

- Read a complete `pyproject.toml` and say what each table and each field is
  for, and which of them are standardised and which belong to one tool.
- Build both artifacts with one command and inspect them with `tar` and
  `unzip`.
- Explain the difference between a distribution name and an import name, and
  find both in a built wheel.
- Turn a Python function into an installed console command with
  `[project.scripts]`.
- Demonstrate that a `src` layout makes the installed copy win the import, and
  that a flat layout does not.
- Predict and then verify what happens when required metadata is missing.

## Prerequisites

- Day 43 — virtual environments and `pip` from the consumer side. Today you
  are on the other side of the same transaction.
- Day 59 — modules, imports, and project layout. The `src` layout here is that
  lesson's question answered properly.
- Day 71 to Day 77 — pytest, and the `pyproject.toml` you wrote on Day 77 to
  configure quality tools. Today the same file also carries package metadata.
- Day 80 — `argparse` and a `main(argv) -> int`. The console script installed
  here calls exactly that function.
- Comfort running bash commands and editing a TOML file.

## Supported operating systems

- macOS (verified: macOS 26.5.1 on Apple Silicon).
- Linux (any distribution with Python 3.10 or newer, `bash`, `tar` and
  `unzip`).
- Windows via WSL. Native Windows differs in two visible ways: environment
  binaries live in `Scripts\` rather than `bin/`, and an installed console
  script is `wordtally.exe` rather than a shebang script. Both scripts here
  are bash, so WSL is the supported route.

## Hardware requirements

Any machine that runs Python. The whole lab builds two archives of a few
kilobytes each and creates one virtual environment; disk use stays under
about 50 MB and the full test run finishes in a few seconds.

## Required software

- Python 3.10 or newer (verified on 3.14.0).
- `bash`, `tar`, `unzip` — all present by default on macOS and Linux.
- The three pinned Python packages in `requirements/requirements.txt`:
  `build==1.5.0`, `setuptools==83.0.0`, `pytest==9.1.1`.

## Free and open-source options

Everything used here is free and open source, and there is no paid tier of
anything in this lab. `build`, `setuptools` and `pytest` are all
permissively licensed and install with `pip`.

The alternatives discussed in the lesson — `hatch`/`hatchling`, `flit`,
`poetry`, `uv`, `pipx` and `conda` — are also all free and open source. None
of them is installed on the authoring machine, so this lab quotes no output
and no timing figures for them; where the lesson describes them it says so
plainly.

Publishing to the public index is free for open-source projects. Private
indexes, whether self-hosted or commercial, are the paid case, and the lesson
covers when that is the right answer.

## Installation

```bash
cd labs/sections/programming-with-python/day-083-packaging-and-distributing-python-code
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python -m build --version
.venv/bin/pytest --version
```

That install is the only step that needs a network. Everything afterwards —
every build, every inspection, every install into the throwaway environment —
runs offline.

`requirements/README.md` explains all three packages, and explains why
`setuptools` is pinned here even though a real project would let the build
frontend fetch it.

## File structure

```
day-083-packaging-and-distributing-python-code/
├── README.md                       this file
├── metadata.yml                    every command this lab runs
├── troubleshooting.md
├── security.md
├── requirements/
│   ├── requirements.txt            build, setuptools, pytest — pinned
│   └── README.md                   what each one is for
├── examples/
│   ├── build_and_inspect.sh        the whole flow in one script
│   ├── sample.txt                  input for the installed command
│   └── wordtally-tools/            the FINISHED reference project
│       ├── pyproject.toml          a complete, commented package definition
│       ├── MANIFEST.in             sdist-only inclusions
│       ├── LICENSE
│       ├── README.md               becomes the long description in METADATA
│       ├── src/wordtally/          src layout: the importable package
│       │   ├── __init__.py         single-sourced __version__
│       │   ├── core.py             the library
│       │   ├── cli.py              the argparse front end
│       │   └── data/stopwords.txt  packaged data, shipped in the wheel
│       └── tests/                  in the sdist, not in the wheel
├── starter/
│   └── wordtally-tools/            same code, ten numbered exercises in
│                                   pyproject.toml
├── tests/
│   └── run_tests.sh                87 checks
└── expected-output/                real captures from the authoring machine
```

`workspace/` is created by the scripts, holds every build product and the
throwaway environment, and is deleted again. It is ignored by version control,
so nothing you build here can be committed by accident.

## How to run

The whole thing, in one script:

```bash
bash examples/build_and_inspect.sh
```

Or step by step, which is the better way to learn it. Build:

```bash
cd examples/wordtally-tools
python3 -m build --no-isolation
ls dist/
```

Look inside both artifacts:

```bash
tar -tzf dist/wordtally_tools-0.3.1.tar.gz
unzip -l dist/wordtally_tools-0.3.1-py3-none-any.whl
unzip -p dist/wordtally_tools-0.3.1-py3-none-any.whl \
  wordtally_tools-0.3.1.dist-info/METADATA
unzip -p dist/wordtally_tools-0.3.1-py3-none-any.whl \
  wordtally_tools-0.3.1.dist-info/entry_points.txt
```

Install into a fresh environment and run the installed command:

```bash
cd ../..                                     # back to the lab directory
mkdir -p workspace
python3 -m venv workspace/tryout
workspace/tryout/bin/pip install --no-index \
  examples/wordtally-tools/dist/wordtally_tools-0.3.1-py3-none-any.whl
workspace/tryout/bin/wordtally --version
cp examples/sample.txt examples/wordtally-tools/sample.txt
cd examples/wordtally-tools
../../workspace/tryout/bin/wordtally count sample.txt
../../workspace/tryout/bin/wordtally top sample.txt -n 3
```

And the check the whole lab exists for — where did the import come from?

```bash
../../workspace/tryout/bin/python -c "import wordtally; print(wordtally.__file__)"
```

Then work through the ten numbered exercises in
`starter/wordtally-tools/pyproject.toml`, which walk the same path from a
two-field metadata block to a complete one.

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m build --no-isolation` | Runs the build **frontend**. It reads `[build-system]`, calls the backend named there (`setuptools.build_meta`), and writes an sdist and a wheel into `dist/`. `--no-isolation` reuses the installed setuptools instead of fetching one, which is what keeps this lab offline; a real release omits the flag. |
| `tar -tzf …tar.gz` | Lists the sdist. It is a gzipped tar of the project as a maintainer would want it: source, tests, licence, build instructions. |
| `unzip -l …whl` | Lists the wheel. It is an ordinary zip archive — this command is the whole proof — holding the package as the installer wants it plus a `.dist-info` metadata directory. |
| `unzip -p …whl …/METADATA` | Prints the metadata an index would display: name, version, summary, licence, classifiers, required Python, dependencies. Every line of it came from `[project]` in `pyproject.toml`. |
| `unzip -p …whl …/entry_points.txt` | Prints the console-script declaration. This is the file an installer reads to decide to create an executable called `wordtally`. |
| `python3 -m venv workspace/tryout` | Creates an empty environment. It has no packages beyond `pip`, which is the point: it cannot accidentally have your project on its path already. |
| `pip install --no-index …whl` | Installs the wheel by unpacking it. `--no-index` forbids contacting any package index; the install is local and offline. |
| `workspace/tryout/bin/wordtally --version` | Runs the command that installing created. Nothing put this on your path but `[project.scripts]`. |
| `python -c "import wordtally; print(wordtally.__file__)"` | Asks Python where it found the package. Run from inside the project directory, the answer must still be `site-packages`. |
| `bash tests/run_tests.sh` | The 87-check harness. |

## Expected output

Captured on the authoring machine (macOS 26.5.1, Apple Silicon, Python 3.14.0,
bash 3.2.57, build 1.5.0, setuptools 83.0.0, pip 25.2, pytest 9.1.1) on
2026-07-19. Absolute paths appear as `<repo>`.

The build:

```
* Building sdist...
* Building wheel from sdist...
Successfully built wordtally_tools-0.3.1.tar.gz and wordtally_tools-0.3.1-py3-none-any.whl
```

The wheel, opened:

```
Archive:  dist/wordtally_tools-0.3.1-py3-none-any.whl
  Length      Date    Time    Name
---------  ---------- -----   ----
      912  07-19-2026 13:24   wordtally/__init__.py
     2775  07-19-2026 13:24   wordtally/cli.py
     2427  07-19-2026 13:24   wordtally/core.py
      132  07-19-2026 13:24   wordtally/data/stopwords.txt
     1079  07-19-2026 13:24   wordtally_tools-0.3.1.dist-info/licenses/LICENSE
     1656  07-19-2026 13:24   wordtally_tools-0.3.1.dist-info/METADATA
       91  07-19-2026 13:24   wordtally_tools-0.3.1.dist-info/WHEEL
       49  07-19-2026 13:24   wordtally_tools-0.3.1.dist-info/entry_points.txt
       10  07-19-2026 13:24   wordtally_tools-0.3.1.dist-info/top_level.txt
      846  07-19-2026 13:24   wordtally_tools-0.3.1.dist-info/RECORD
---------                     -------
     9977                     10 files
```

No `pyproject.toml`, no `MANIFEST.in`, no `tests/`, and no `src/` prefix. The
sdist has all four.

The installed command, and where it imported from:

```
wordtally 0.3.1
12
     3  mat
     1  cat
<repo>/labs/sections/programming-with-python/day-083-packaging-and-distributing-python-code/workspace/tryout/lib/python3.14/site-packages/wordtally/__init__.py
```

Full captures, including the sdist listing, the complete `METADATA`, the
editable-install comparison and the deliberate build failures, are in
`expected-output/`. `expected-output/FIELDS.md` explains each file and lists
the behaviour the harness requires.

## Validation steps

1. `dist/` holds exactly two files, and both filenames contain `0.3.1`.
2. `unzip -t` on the wheel reports no errors — it really is a valid zip.
3. The wheel listing contains `wordtally/core.py` and
   `wordtally/data/stopwords.txt`, and does not contain `pyproject.toml` or
   `tests/test_core.py`.
4. The sdist listing contains all four of those.
5. `workspace/tryout/bin/wordtally` exists, is executable, and
   `wordtally --version` prints `wordtally 0.3.1` and exits 0.
6. Run from inside `examples/wordtally-tools`,
   `import wordtally; print(wordtally.__file__)` prints a path inside
   `workspace/tryout/lib/`, not a path inside the project.
7. Deleting the `name` line from `pyproject.toml` makes `python3 -m build`
   exit non-zero and print a message naming the missing field, and leaves no
   `dist/` behind.
8. `bash tests/run_tests.sh` prints `87 checks, 0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

87 checks in eleven sections. The harness is deterministic and offline: it
copies the reference project into `workspace/`, builds it, opens both
artifacts, creates a fresh environment, installs the wheel with `--no-index`,
runs the installed command, and compares the resolved `__file__` against a
flat-layout copy of the same code. It also removes a required metadata field
and demands that the build fail, and it checks that `metadata.yml` declares no
publishing command anywhere.

The three checks worth reading the source for are the `src`-versus-flat
comparison in section 6, the wheel contents in section 3, and the failing
build in section 9.

Every check that runs a tool resolves it first: `PYTHON=…` or `PYTEST=…` if
you set them, then this lab's `.venv/bin/`, then your `PATH`. A missing tool
stops the run with install instructions rather than skipping quietly.

## Cleanup

```bash
rm -rf workspace
rm -rf examples/wordtally-tools/dist examples/wordtally-tools/build
find examples/wordtally-tools/src -type d -name '*.egg-info' -prune -exec rm -rf -- {} +
rm -rf starter/wordtally-tools/dist starter/wordtally-tools/build
find starter/wordtally-tools/src -type d -name '*.egg-info' -prune -exec rm -rf -- {} +
rm -f examples/wordtally-tools/sample.txt
git checkout -- starter/     # optional: reset your work on the exercises
```

`tests/run_tests.sh` already removes `workspace/` on the way out, including
when a check fails, so a test run leaves nothing behind. The commands above
matter if you built by hand in `examples/` or `starter/`. Nothing here is
installed system-wide and nothing was installed outside the environments you
created, so there is nothing else to undo.

## Troubleshooting

See `troubleshooting.md` for the full list. The three most common:

- **`No module named build`** — the requirements are not installed for the
  Python you are running. Use `.venv/bin/python -m build`, or set
  `PYTHON=.venv/bin/python`.
- **`Backend 'setuptools.build_meta' is not available`** with
  `--no-isolation` — setuptools is not installed in that environment. Install
  the requirements, or drop `--no-isolation` and let the frontend fetch a
  backend (that needs a network).
- **`import wordtally` prints a path inside the project rather than inside the
  environment** — you are almost certainly in a flat-layout directory, or you
  have a stray `wordtally/` folder in your working directory. That is the
  failure the `src` layout exists to prevent, and section 6 of the harness
  reproduces it on purpose.

## Security notes

See `security.md`. In short: this lab contacts no index and uploads nothing;
it never asks for a token and there is nowhere to put one; installing a
package runs the publisher's code, which is why the throwaway environment is
throwaway; and a version number, once published, cannot be reused or quietly
replaced.

## Extension exercises

1. Add a second console script — `wordtally-count` mapped to a new
   `wordtally.cli:count_main` — rebuild, and confirm two entries appear in
   `entry_points.txt` and two executables appear after installing.
2. Give the package a real runtime dependency, rebuild, and read the
   `Requires-Dist` line that appears in `METADATA`. Then try installing the
   wheel with `--no-index` and watch it fail, which is exactly what a
   dependency means.
3. Delete the `[tool.setuptools.package-data]` table, rebuild, install, and
   run `wordtally top`. Read the traceback carefully: this is the single most
   common packaging bug, and now you know its shape.
4. Change `version` to `0.3.2`, rebuild without deleting `dist/`, and note
   that you now have four artifacts. Which one would `pip install dist/*.whl`
   pick, and why is that a good argument for building into a clean directory?
5. Build the same project with a different backend. Replace `[build-system]`
   with hatchling's, adjust the tool-specific tables, and compare the two
   wheels file by file. They should be nearly identical — which is the whole
   point of a standardised interface.
6. Write a `MANIFEST.in` that excludes the tests from the sdist, rebuild, and
   argue for or against shipping tests in an sdist. There are real projects on
   both sides.

## Navigation

- Previous lab: `../day-082-a-first-web-api-with-fastapi/`
- Next lab: `../day-084-shipping-an-automation-toolkit/`
- Section index: `../README.md`
