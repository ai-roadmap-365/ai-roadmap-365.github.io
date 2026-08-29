# Security notes — Day 105 lab

## What this lab touches

| Resource | Used? | Detail |
| --- | --- | --- |
| Network | **Once**, to install | `pip install -r requirements/requirements.txt` fetches numpy, Pillow and pytest from the Python Package Index. Nothing else in the lab opens a socket, reads a URL or contacts a service. |
| Filesystem | Inside the lab, plus one temporary file | The lab reads its own source. It writes `.venv/` if you create it, and one PNG inside the operating system's temporary directory, which is removed by the context manager that created it. |
| Credentials | **None** | No API key, no token, no account, no login. `requires_api_key` is `false` in `metadata.yml`. |
| Elevated privileges | **None** | Nothing here needs `sudo` or an administrator prompt. If something asks, stop and read the command. |
| Ports | **None** | Nothing binds, listens or connects. |
| Environment variables | Two, both optional | `PYTEST` points the harness at a specific pytest binary; `D105_SELF_TEST` is set by the harness on itself in section 6 and is not for you to set. |

Section 7 of `tests/run_tests.sh` verifies the network claim mechanically
rather than asserting it in prose: it greps every file under `examples/` and
`starter/` for `urlopen`, `requests.`, `socket.`, `http://` and `https://`.

## Why the test image is generated rather than downloaded

This is a security decision as much as a pedagogical one.

A lab that fetches a photograph to work on acquires four problems at once. It
stops working offline. It depends on a URL staying up and serving the same
bytes. It ships an image whose licence somebody has to check. And it hides its
own test data behind a network request, so a reader cannot tell what is in the
file without fetching it.

`pattern.py` builds the picture from arithmetic — a capital F on a 9 by 9 grid
— and every pixel value in it is asserted in the tests. There is nothing to
fetch, nothing to license, and nothing that could differ between your copy and
the authoring machine's.

The harness also asserts that **no image file exists anywhere under the lab**,
so a stray PNG appearing later is caught rather than quietly committed.

## Handling images from elsewhere

The lab does not do this, but you will, so the two real hazards are worth
naming.

**Image parsers are attack surface.** Decoding an untrusted image is running a
complex C parser over bytes you did not write, and image libraries have a long
history of memory-safety bugs. Keep Pillow up to date, and do not decode
attacker-supplied images in a process that holds anything valuable.

**Decompression bombs.** A small file can declare an enormous canvas, and a
naive decoder will try to allocate it. Pillow defends against this by default:
it raises a warning above roughly 89 million pixels and refuses outright above
twice that, controlled by `Image.MAX_IMAGE_PIXELS`. Raising or disabling that
limit — `Image.MAX_IMAGE_PIXELS = None` is a common copy-paste — removes a real
protection, so do it only for files you produced yourself.

Neither hazard arises in this lab, because the only image decoded here is one
the lab wrote nine pixels wide a moment earlier.

## Privacy

Nothing personal is read, written, or transmitted. The lab has no telemetry, no
analytics, and no crash reporting. `pip` contacts PyPI during the install and
nothing else does.

## Supply chain

Three dependencies, all pinned to exact versions in
`requirements/requirements.txt`, all widely used and maintained in the open:

| Package | Version | Licence |
| --- | --- | --- |
| numpy | 2.5.2 | BSD 3-Clause |
| pillow | 12.3.0 | MIT-CMU |
| pytest | 9.1.1 | MIT |

The versions are **checked, not assumed**: section 1 of the harness reads the
installed version of each and compares it against `requirements.txt`, so a
substitution or an accidental upgrade is reported at the top of the run rather
than surfacing later as a confusing difference in output.

Pinning is a trade-off and worth being honest about. It makes runs reproducible
and makes this file's version table true, but it also means you will not pick
up a security fix by rerunning the install. For a lab that decodes only its own
nine-by-nine array that is an acceptable trade; for anything that handles
images from outside, prefer a floor (`pillow>=12.3.0`) and update deliberately.

## Running it as a virtual environment, and why

The install goes into `.venv/` inside the lab rather than into your system
Python. That is not ceremony: it keeps three pinned versions from colliding
with whatever else you have installed, and it means `rm -rf .venv` undoes the
entire install with no trace left.

If you would rather use an environment you already have, the harness will find
`pytest` on your `PATH`, or you can point it at one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness then uses the `python3` beside that binary, and stops with a clear
message if numpy or Pillow is not importable from it — rather than skipping
checks quietly, which would be the dangerous failure mode.

## What the lab deliberately does not do

- It does not download anything at run time.
- It does not write outside its own directory or a temporary directory.
- It does not modify any file it did not create.
- It does not require, read, or store a credential of any kind.
- It does not execute any code supplied at run time — nothing here calls
  `eval`, `exec`, `pickle.load`, or `subprocess` on an unvalidated string.
