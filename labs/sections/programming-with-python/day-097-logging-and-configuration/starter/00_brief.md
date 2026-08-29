# The brief — "Say It Where Someone Will Read It"

Read this before you write anything.

## The situation

You have a script. It works. It is full of `print`.

It runs on your laptop while you watch it, and every line it prints is useful
to you, right now, at your desk. `examples/01_prints.py` is that script — run
it once and read what comes out.

Tomorrow it moves to a machine you do not have a terminal on. It runs at
04:00. It runs again at 05:00. Its output lands in a file that also holds
last week's output. Somebody who is not you will read that file, in a hurry,
because something has gone wrong.

Every one of those `print` lines is now useless, and each for a different
reason:

| What the line says | Why it stops working |
| --- | --- |
| `processing record 3` | Which run? There are 168 of them in that file this week |
| `skipping record 2: empty text` | When? There is no timestamp on any line |
| `could not write output` | How bad? Same shape as the line above it, so no alert can tell them apart |
| all of them | How do you turn them down? You edit the source and deploy |
| `using API key sk-live-...` | This one is a security incident, not an inconvenience |

That is the whole day, in one sentence: **`print` is for you, at your desk,
right now; logging is for whoever is awake when it breaks.**

## What you are building

Twelve exercises across two files.

`starter/01_logging.py` — the logging half.

1. A module-level logger, obtained the way every module should obtain one.
2. The `print`-based function converted, with each line given the level it
   deserves.
3. A handler whose level does not silently swallow what the logger accepted —
   the two-level trap, met and fixed.
4. A failure logged with `exception()` rather than `error(str(e))`.
5. A JSON formatter, so the log becomes a table you can query.
6. A redacting filter, so a known secret cannot reach any handler.

`starter/02_config.py` — the configuration half.

7. `to_bool`, which refuses to believe that the string `"false"` is true.
8. The four-layer resolver: default, then file, then environment, then flag.
9. Provenance: every setting reports where its value came from.
10. Missing and empty environment variables, told apart.
11. A startup validator that names the setting and the layer it came from.
12. `safe_dict`, which is the configuration with the secrets removed — the
    only version that may be logged.

## How to work

```bash
# from the lab directory
bash starter/03_check.sh
```

It will say `0 of 12 exercises complete.` and, for each one, what it wanted
and what it got. Work down the two files, re-running it as you go. It exits
non-zero until all twelve pass.

The checker never reads how you wrote something. It runs your code and looks
at the values, so any correct implementation passes.

## The rules of the exercise

- **The standard library only.** `logging`, `logging.config`, `os`,
  `tomllib`, `argparse`, `json`, `pathlib`. Nothing to install.
- **Capture logs with a handler writing to a buffer**, never by scraping
  stdout. `examples/applog.py` has `buffer_handler` if you want to see one.
- **The secret is `sk-live-9f2c4a7b1e63`**, invented for this lab. Exercise 6
  is not complete until that string appears nowhere in the captured output.
- **Read `examples/` after you have tried, not before.** Every exercise has a
  worked reference there, and reading it first costs you the exercise.

## The one thing to carry out of the day

Both halves are the same idea wearing different clothes.

Logging is how a program tells you what it did. Configuration is how you tell
a program what to do. Neither should require editing the source, and both
should be able to answer "why?" without anybody guessing — which is why the
resolver you build in exercise 9 records provenance and the log you build in
exercise 5 records a run id.
