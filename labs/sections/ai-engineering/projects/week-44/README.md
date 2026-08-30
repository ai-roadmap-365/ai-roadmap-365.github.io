# Week 44 Project: Agent-Built Feature

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Project Overview

Ship an end-to-end, reviewed, tested and documented software feature through an autonomous coding-agent pipeline. You build an **Agent Feature Pipeline** in Python that compiles a specification, maps a repository by parsing its AST, applies atomic multi-file patches, runs a self-healing test gate, audits the result for insecure patterns, and emits a walkthrough for human review.

The point of the project is not the agent. It is the **scaffolding around** the agent: the parts that make an automated change reviewable, reversible and safe to merge.

## Learning objectives

- Compile a specification into a bundle of context files, hard constraints and explicit non-goals.
- Extract class and function signatures across a workspace by parsing the AST rather than by regex.
- Apply targeted search-and-replace edits atomically across several files, so a partial application cannot land.
- Parse a test runner's traceback and feed it back as a self-correction signal.
- Audit imports against an allowlist and detect insecure shell execution before a change is proposed.
- Emit a walkthrough artifact a human reviewer can actually read.

## Prerequisites

- Days 302 to 308, the AI Coding Agents week.
- Comfortable with Python's `ast` module and `subprocess`.
- Familiar with `pytest`.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing here is platform-specific.

## Hardware requirements

Any machine that runs Python 3.10 or newer. No GPU. The suite completes in well under a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key and no hosted service is used anywhere in this project — the "agent" is simulated locally so the pipeline's mechanics can be tested deterministically.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/agent_feature_pipeline.py    your work: the pipeline skeleton
examples/agent_feature_pipeline.py   reference implementation
tests/test_agent_feature_pipeline.py four tests, one per stage with real logic
tests/run_tests.sh                   suite entry point
expected-output/                     real captured output and measured values
requirements/                        pinned dependency
```

## How to run

```bash
python3 examples/agent_feature_pipeline.py   # see the pipeline produce a repo map
bash tests/run_tests.sh                      # run the suite
```

## What the commands do

`python3 examples/agent_feature_pipeline.py` constructs the pipeline over this project's own workspace and prints a preview of the AST-derived repository map — the class and the first function signature it finds in the starter file. It is a smoke check that the map builds against real source.

`bash tests/run_tests.sh` runs `pytest` over the four stage tests.

## Expected output

```text
Pipeline ready. Workspace map preview:
 File: starter/agent_feature_pipeline.py
  class AgentFeaturePipeline:
  def __init__(self, workspace
```

The last line is truncated in the preview by design — the map stores the full signature and prints only its head.

The test suite reports:

```text
4 passed in 0.06s
```

`expected-output/measured-values.txt` records the machine and versions those numbers came from.

## Validation steps

1. `bash tests/run_tests.sh` reports `4 passed`.
2. `python3 examples/agent_feature_pipeline.py` prints the four-line preview above and exits 0.
3. Confirm the repo map was built by parsing, not matching: change the indentation of `class AgentFeaturePipeline` in the starter file and re-run. The map must still find it, because `ast` does not care about formatting.

## Tests

Four tests, one per stage that carries real logic:

- `test_generate_repo_map` — signatures are extracted from the AST across workspace files.
- `test_apply_patch_success` — a multi-file patch applies atomically.
- `test_audit_security` — a disallowed import and an insecure shell call are both caught.
- `test_run_tests_and_format_walkthrough` — the test gate parses a result and the walkthrough renders.

Specification compiling and the walkthrough artifact are exercised inside the last test rather than as separate cases.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials, no API key. The security audit stage is itself a defensive exercise — it detects insecure patterns, it does not execute them.

## Extension exercises

1. **Rollback on partial failure.** Make patch application transactional: if the third of four edits fails, the first two must be reverted rather than left applied.
2. **Widen the audit.** Add detection for hardcoded secrets and for `eval` on interpolated strings, with a test for each.
3. **Real self-healing.** Feed a genuine failing traceback back into the pipeline and have it produce a targeted patch, then measure how often that succeeds over a set of seeded bugs. Report the real rate, including if it is low.

## Navigation

- Week 44 — AI Coding Agents (Days 302 to 308)
- Previous: Week 43 project
- Next: Week 45 project
