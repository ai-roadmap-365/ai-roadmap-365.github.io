# Security notes — Day 107 lab

## What this lab touches

| Resource | Used? | Detail |
| --- | --- | --- |
| Network | **Once**, to install | `pip install -r requirements/requirements.txt` fetches numpy and pytest from the Python Package Index. Nothing else in the lab opens a socket, reads a URL or contacts a service. |
| Filesystem | Inside the lab only | The lab reads its own source and writes nothing at all except `.venv/` if you create it. There is no temporary file, no cache and no output artefact. |
| Credentials | **None** | No API key, no token, no account, no login. `requires_api_key` is `false` in `metadata.yml`. |
| Elevated privileges | **None** | Nothing here needs `sudo` or an administrator prompt. If something asks, stop and read the command. |
| Ports | **None** | Nothing binds, listens or connects. |
| Environment variables | Two, both optional | `PYTEST` points the harness at a specific pytest binary; `D107_SELF_TEST` is set by the harness on itself in section 6 and is not for you to set. |

Section 7 of `tests/run_tests.sh` verifies the network claim mechanically
rather than asserting it in prose: it greps every file under `examples/` and
`starter/` for `urlopen`, `requests.`, `socket.`, `http://` and `https://`.

## Why every dataset is written out in the source

This is a security decision as much as a pedagogical one.

A lab that downloads its data acquires four problems at once. It stops working
offline. It depends on a URL staying up and serving the same bytes. It ships
data whose licence and provenance somebody has to check. And it hides its own
inputs behind a network request, so a reader cannot tell what is in the file
without fetching it.

`catalogue.py` contains every number this lab uses: four term counts, four
part dimensions, six categorical fields, two ingredient lists, eight sensor
readings and six bearings. All of it is visible, all of it is small enough to
verify by hand, and every derived value is asserted. The harness also checks
that **no data file exists anywhere under the lab** — no CSV, JSON, `.npy`,
Parquet or SQLite — so a stray download appearing later is caught rather than
quietly committed.

## The security-shaped hazard this lab is actually about

The day's subject has a direct security consequence that is worth stating
plainly, because it is not obvious.

**A distance function is an access-control decision in disguise whenever it is
used for matching.** Face matching, fingerprint matching, deduplication,
fraud-ring detection, "is this login from a familiar device" — all of them are
a threshold on a distance, and all of them inherit whatever that measure
ignores.

Three specific failures follow from the material in this lab:

1. **Cosine similarity cannot tell a document from the same document
   repeated.** `cosine_distance((1, 0), (2, 0))` is 0, which the lab asserts.
   A deduplication or plagiarism check built on cosine over raw counts will
   score a doubled document as identical to the original — sometimes what you
   want, and sometimes a way to slip content past a filter.

2. **An unscaled feature is a silent thumb on the scale.** The bearing example
   in `06_scaling_changes_the_answer.py` shows one column contributing
   0.0036 per cent of every distance in the table. If an attacker knows which
   feature dominates your measure, they know exactly which field to manipulate
   and which ones they can leave alone. Normalising is not only a quality
   improvement; it removes a cheap attack.

3. **Mahalanobis distance depends on an estimate of your data, and estimates
   can be poisoned.** The covariance matrix is computed from the data you have
   seen. An adversary who can inject rows can widen the variance in the
   direction they intend to attack along, and afterwards their anomaly scores
   drop. Any anomaly detector that re-fits its covariance on live traffic
   without provenance controls has this property.

None of these is a bug in the mathematics. Each one is a consequence of what
the measure was asked to ignore, which is why the day insists that the choice
be made deliberately.

## Handling data from elsewhere

The lab does not do this, but you will.

`numpy.load` executes pickled Python by default when the file contains object
arrays. `.npy` and `.npz` files from an untrusted source are therefore
executable content, not data. Pass `allow_pickle=False`, which has been the
default since NumPy 1.16.2, and do not turn it back on to make a file load.

Nothing in this lab loads a file of any kind, so the hazard does not arise
here.

## Privacy

Nothing personal is read, written, or transmitted. The lab has no telemetry, no
analytics, and no crash reporting. `pip` contacts PyPI during the install and
nothing else does.

## Supply chain

Two dependencies, both pinned to exact versions in
`requirements/requirements.txt`, both widely used and maintained in the open:

| Package | Version | Licence |
| --- | --- | --- |
| numpy | 2.5.2 | BSD 3-Clause |
| pytest | 9.1.1 | MIT |

The versions are **checked, not assumed**: section 1 of the harness reads the
installed version of each and compares it against `requirements.txt`, so a
substitution or an accidental upgrade is reported at the top of the run rather
than surfacing later as a confusing difference in output.

Pinning is a trade-off and worth being honest about. It makes runs reproducible
and makes this file's version table true, but it also means you will not pick
up a security fix by rerunning the install. For a lab that reads no external
input at all that is an acceptable trade; for anything that parses data from
outside, prefer a floor (`numpy>=2.5.2`) and update deliberately.

## Running it in a virtual environment, and why

The install goes into `.venv/` inside the lab rather than into your system
Python. That is not ceremony: it keeps two pinned versions from colliding with
whatever else you have installed, and `rm -rf .venv` undoes the entire install
with no trace left.

If you would rather use an environment you already have, the harness will find
`pytest` on your `PATH`, or you can point it at one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness then uses the `python3` beside that binary, and stops with a clear
message if numpy is not importable from it — rather than skipping checks
quietly, which would be the dangerous failure mode.

## What the lab deliberately does not do

- It does not download anything at run time.
- It does not write outside its own directory. It writes nothing at all.
- It does not modify any file it did not create.
- It does not require, read, or store a credential of any kind.
- It does not execute any code supplied at run time — nothing here calls
  `eval`, `exec`, `pickle.load`, or `subprocess` on an unvalidated string.
