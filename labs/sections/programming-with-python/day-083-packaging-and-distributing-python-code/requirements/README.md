# Dependencies — Day 083 lab

Three packages. All free, all open source, none needs an account, an API key,
or a paid plan. After the one-time install, everything in this lab runs
completely offline — including the builds and the installs.

```
build==1.5.0
setuptools==83.0.0
pytest==9.1.1
```

| Package | Role | What it does | Licence |
| --- | --- | --- | --- |
| `build` | build **frontend** | `python -m build` reads `[build-system]` from `pyproject.toml`, calls the backend it names, and writes an sdist and a wheel into `dist/`. It builds nothing itself — it is the thing that knows how to ask. | MIT, per the package metadata |
| `setuptools` | build **backend** | The thing that actually turns a source tree into artifacts. Named in this project's `[build-system] requires` and `build-backend`. | MIT, per the package metadata |
| `pytest` | test runner | Runs the packaged project's own suite, and is the runner the lab harness resolves. Introduced on Day 71. | MIT, per the pytest documentation |

The versions above were installed and verified on the authoring machine on
2026-07-19. `python -m build --version` reported `build 1.5.0`, `pip --version`
reported `pip 25.2`, and `pytest --version` reported `pytest 9.1.1`, on
Python 3.14.0.

## Why setuptools is pinned here, when a real project would not pin it

Normally you never install a build backend yourself. `python -m build` creates
a fresh, isolated environment for each build and installs whatever
`[build-system] requires` asks for — usually from an index, over the network.
That isolation is a genuinely good default: it means the build cannot
accidentally depend on something you happen to have installed.

This lab builds with `python3 -m build --no-isolation`, which reuses the
`setuptools` already installed instead of fetching one. Two reasons, both
honest:

- **The lab must run offline.** A test suite that downloads a build backend on
  every run is slow, is flaky on a train, and fails the day an index has a bad
  afternoon.
- **The result is then deterministic.** Every learner builds with the same
  backend version, so the captured output in `expected-output/` is something
  you can actually compare against.

A real release uses plain `python -m build`. The lesson says so, and the
lab README shows both commands side by side.

## Deliberately not installed

- **twine** — the standard upload client. It is described in the lesson,
  its commands are shown, and it is never run here, because **this lab
  uploads nothing to any index**. Installing an upload tool into a teaching
  environment invites an accident that cannot be undone: a version number
  published to an index can never be reused.
- **hatch**, **flit**, **poetry** and **uv** — all free and open source, all
  covered in the lesson's Alternatives section. None is installed on the
  authoring machine, so the lesson describes them from their documented
  behaviour and quotes no output for them and no benchmark numbers. Where a
  claim could not be checked here, the lesson says so.

## One-time install

```bash
cd labs/sections/programming-with-python/day-083-packaging-and-distributing-python-code
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python -m build --version
.venv/bin/pytest --version
```

You created a virtual environment for the first time on Day 43; this is the
same procedure. `.venv/` is ignored by version control and never committed.

`tests/run_tests.sh` finds these tools automatically: an explicit override
first (`PYTHON=/path/to/python3 bash tests/run_tests.sh`), then this lab's
`.venv/bin/`, then whatever is on your `PATH`. If a tool is missing the script
stops with install instructions rather than skipping the check.

## Windows

Run everything inside WSL and follow the Linux path. `run_tests.sh` and
`build_and_inspect.sh` are bash scripts, the environment layout differs on
native Windows (`.venv\Scripts\` rather than `.venv/bin/`), and the console
script an installer creates there is `wordtally.exe` rather than a shebang
script.
