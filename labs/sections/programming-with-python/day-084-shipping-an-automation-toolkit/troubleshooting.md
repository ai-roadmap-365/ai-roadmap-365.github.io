# Troubleshooting

## `feedkit: configuration error: no base URL configured`

The toolkit refuses to run without knowing where to fetch from, and it will not
guess. Set `FEEDKIT_BASE_URL` in the environment or pass `--base-url`. When you
are running through `bash tests/run_tests.sh` the harness sets it for you,
pointing at the fixture server it started; when you run `feedkit` by hand you
must set it yourself.

This is a design choice worth noticing rather than working around: a
deployment-specific address does not belong in a file that gets committed, so
there is no default for it to fall back to.

## `FAIL: pytest not found` or `FAIL: the 'requests' package is not importable`

The install has not run. From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The harness deliberately stops with instructions rather than skipping the
checks it cannot run. A test suite that silently does less than it claims is
worse than one that fails, because people trust it.

## `ModuleNotFoundError: No module named 'feedkit'`

You are running a module without telling Python where the package is. Either
install it (`.venv/bin/pip install -e examples --no-build-isolation`) or set the
path for one command:

```bash
PYTHONPATH=examples/src .venv/bin/python -m feedkit.cli --help
```

## The tests hang, or the fixture server never becomes ready

The harness waits up to five seconds for the server to print its port and
another five for `/health`. If it times out, run the server by hand and read
its errors:

```bash
.venv/bin/python tests/fixture_server.py --token demo-token-value
```

It should print a port number immediately. If it does not, something is
preventing a bind to 127.0.0.1 — most often an aggressive local firewall or a
container without a loopback interface.

## A test run left a `feedkit` process behind

It should not: the harness kills the server in a `trap` that fires on exit,
interrupt and termination. If one survives a hard kill of the harness itself:

```bash
pgrep -fl fixture_server.py
kill <the pid>
```

Nothing else in this lab starts a background process, and nothing is installed
into cron, launchd or systemd at any point.

## `feedkit fetch` says `new entries: 0` and you expected more

That is idempotence working. The state file records what has already been
processed, so a second run over unchanged sources correctly finds nothing. To
watch a first run again, delete the state file:

```bash
rm -f feedkit-state.json
```

Or point at a fresh one for a single run:

```bash
feedkit --state-file /tmp/scratch-state.json fetch
```

## `exit code 75` and `another run is in progress`

A lock file exists next to your state file. Either a run really is in progress,
or a previous one was killed before it could clean up. Check first, then
remove:

```bash
cat feedkit-state.json.lock          # the pid that created it
ps -p "$(cat feedkit-state.json.lock)"   # is that process still alive?
rm -f feedkit-state.json.lock            # only if it is not
```

Deleting a lock without checking is how two runs end up writing at once.

## `exit code 3` and you thought the run worked

Exit code 2 means **partial success**: some sources succeeded and at least one
did not. Read the `FAILED:` lines in the summary, which name the source and the
error. This is deliberate. An automation that exits 0 while quietly dropping a
source is one you will stop trusting the first time you notice, and you will
notice long after it started.

The watchdog (`feedkit status --max-age-minutes N`) also exits 3, for the same
reason: a non-zero exit is the only thing a scheduler can act on.

## `feedkit status` says `STALE` immediately after a successful run

Two possibilities. Either you passed `--max-age-minutes 0`, which makes
everything stale by definition — that is how the harness proves the watchdog
can fail — or your last run was *partial* rather than fully successful.
`last_success` is only updated when every source succeeded, on purpose: a
watchdog that counts partial runs as successes cannot see a source that has
been failing for a month.

## `state.json is not valid JSON. Refusing to overwrite it.`

Something truncated or corrupted the file — most likely an editor, or a program
other than this one writing to it. The toolkit stops rather than guessing,
because overwriting it would silently re-process everything. Move it aside and
start fresh:

```bash
mv feedkit-state.json feedkit-state.json.broken
```

If you find this happening on its own, that is a real bug worth chasing: the
atomic write exists precisely so it cannot.

## The scheduled job works by hand but does nothing on a schedule

Almost always one of three things, in this order of likelihood:

1. **`PATH`.** A scheduler does not read your shell profile. Use the absolute
   path to `feedkit-scheduled` — find it with `command -v feedkit-scheduled`.
2. **The working directory.** `state_file` defaults to a relative path, and a
   scheduled job does not start where you think. Set `FEEDKIT_STATE_FILE` to an
   absolute path.
3. **The environment.** `FEEDKIT_BASE_URL` and `FEEDKIT_TOKEN` are not there
   unless the schedule entry supplies them. Each file in `examples/schedule/`
   shows where its supervisor expects them.

Diagnose it by making the job log somewhere you can read, then running it
through the scheduler once with a short interval before setting the real one.

## `pip install -e examples` fails

The harness installs with `--no-build-isolation --no-deps` so that the step
needs no network. Both flags depend on `setuptools` and `requests` already
being present in the environment, which is what
`requirements/requirements.txt` guarantees. If you installed the requirements
into a different environment from the one `pip` resolves to, point the harness
at the right one:

```bash
PIP=/path/to/.venv/bin/pip PYTEST=/path/to/.venv/bin/pytest bash tests/run_tests.sh
```

## A `NotImplementedError` from the starter

That is the exercise waiting for you. The message names the file and the
exercise number, and the comment block immediately above it describes what to
write and which test to check it with.
