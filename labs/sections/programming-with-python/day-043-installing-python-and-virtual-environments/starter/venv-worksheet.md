# Virtual environment worksheet — Day 043

Fill this in for **your** machine as you work through the exercises. The goal is
to see, with your own eyes, that activating a virtual environment changes which
Python you are using.

## 1. Your Python

Run `python3 --version` and record the output:

- My Python version: `____________________`

## 2. `which python` before activation

Before activating any environment, run `which python` (or `command -v python`)
and record the full path:

- Before activation, `which python` prints: `____________________`

## 3. Create and activate

Run these from a scratch folder:

```bash
mkdir venv-demo && cd venv-demo
python3 -m venv .venv
source .venv/bin/activate
```

- Did your prompt gain a `(.venv)` marker? (yes / no): `______`

## 4. `which python` after activation

With the environment active, run `which python` again:

- After activation, `which python` prints: `____________________`
- Is this path different from step 2? (yes / no): `______`

## 5. Prove isolation with `sys.prefix`

Run:

```bash
python -c "import sys; print(sys.prefix)"
```

- `sys.prefix` prints: `____________________`
- Does this path end in `.venv`? (yes / no): `______`

## 6. Explain it (4–6 sentences)

In your own words, what did activation change, and why does `sys.prefix`
pointing inside `.venv` prove your project's packages are isolated from the
global Python?

```
____________________________________________________________________

____________________________________________________________________

____________________________________________________________________
```

## 7. Clean up

```bash
deactivate
cd .. && rm -rf venv-demo
```

- After `deactivate`, `which python` prints: `____________________`
  (it should match step 2 again).
