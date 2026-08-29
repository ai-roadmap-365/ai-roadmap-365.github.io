# Security notes — Day 080 lab

A command-line tool is a program that takes input from strangers. Sometimes
the stranger is you in six months; sometimes it is a shell script running as a
scheduled job with arguments assembled from somewhere else. The interface is a
trust boundary, and argparse is the first place you can defend it.

## What this lab does, and does not do

- **No network.** Nothing here opens a socket, resolves a name, or downloads
  anything. The only install is pytest, and that is optional if you already
  have it.
- **No credentials, no keys, no accounts.** The tool stores plain notes in a
  plain JSON file.
- **Writes only where you point it.** The store path comes from `--store`,
  then `$NOTES_STORE`, then `./notes.json` in the current directory. The test
  suite writes exclusively inside a `mktemp -d` directory and removes it in a
  `trap`, so a failed run leaves nothing behind.

## Validation at the boundary is a security control

Every `type=` function in this tool is a gate. `iso_date` means no code past
the parser has to wonder whether `args.on` is a date — it is a
`datetime.date` or the program already exited 2. `positive_int` means no
handler receives a negative note id. `choices=["table", "json"]` means the
format selector can never hold a third value.

This matters more than it looks. The classic command-line vulnerability is a
value that is accepted at the edge, carried untouched through three layers,
and finally interpolated somewhere dangerous. Converting and validating at the
parser — the moment the value enters — means the dangerous shape never exists
inside the program at all. It is the same argument Day 70 made for validating
in `__post_init__`, moved out to the process boundary.

## Never build a shell command out of user input

This tool does not run subprocesses, but the day you write one that does, the
rule is absolute:

```python
subprocess.run(["grep", pattern, path])          # a list: safe
subprocess.run(f"grep {pattern} {path}", shell=True)   # never do this
```

With `shell=True` a pattern of `x; rm -rf ~` is not a pattern, it is two
commands. Passing a list means the operating system hands your arguments to
the program directly and no shell ever sees them. Day 81 uses `subprocess`
properly; this is the habit to bring to it.

## Path arguments deserve suspicion

`--store` takes a path, and a path from a stranger can point anywhere:
`../../.ssh/config`, a symbolic link, a device file. This lab's tool is a
personal note keeper, so it does what a personal tool should — writes where
you say. A tool that accepts a path from a less trusted source should
additionally:

- resolve it with `Path(value).resolve()` and confirm it is inside an expected
  directory before opening it;
- refuse symbolic links where they are not wanted (`Path.is_symlink()`);
- open with the narrowest mode that works, and set restrictive permissions on
  files it creates.

## `--dry-run` is a safety feature, not a convenience

Any command that deletes, overwrites, sends, or spends should have one, and it
should be exercised in tests the way this lab's is — by hashing the target
before and after. A `--dry-run` that has never been checked is a claim, not a
guarantee, and it is the kind of claim people trust right up until the moment
it turns out to be false.

Consider also a confirmation prompt for genuinely destructive operations, with
a `--yes`/`--force` flag to skip it in scripts. The pattern is: interactive
users get a chance to stop; automation opts out explicitly and on the record.

## Secrets do not belong on the command line

A password or API key passed as `--token abc123` is visible to every user on
the machine through the process list, and lands in your shell history file in
plain text. The conventions that avoid this:

- read the secret from an environment variable (`os.environ["API_TOKEN"]`);
- read it from a file whose path is the argument, not the secret itself
  (`--token-file`);
- read it from standard input, which is exactly the `-` convention this lab
  implements for note text.

The `add -` exercise is therefore not only about pipelines. It is the same
mechanism you use to keep a secret off the command line.

## JSON, not pickle

The store is read with `json.loads`, which builds only lists, dicts, strings,
numbers, booleans and null — it cannot execute anything. `pickle` can and does
execute arbitrary code while loading, so a pickle file is as dangerous as a
program. A malformed store here produces `notes: ... is not valid JSON` and
exit 1; a malicious pickle would produce whatever its author wanted.

The tool also checks the *shape* of what it loaded, not just that it parsed,
and refuses a file that is valid JSON but not a notes store. Parsing and
validating are two different steps.

## Errors on standard error, always

Sending diagnostics to standard error is a correctness rule, but it has a
security edge: a pipeline like `notes export --format json | some-importer`
must never have an error message injected into the middle of its data. Keeping
the two streams separate means a downstream program sees either good data or
no data, and never a plausible-looking mixture of the two.

## Personal data

Notes are personal data. This store is a plain file in your working directory
with no encryption; treat it accordingly, and keep it out of version control.
A `.gitignore` entry for `notes.json` costs nothing.
