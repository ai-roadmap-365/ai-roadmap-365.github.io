# Troubleshooting — Day 362

## The good README reports its own examples as unknown commands

Your extractor accepts untagged fenced blocks. Only ```` ```bash ````, ```` ```sh ```` and ```` ```console ```` blocks are instructions; a bare ```` ``` ```` block is **output**.

This lab had exactly that bug. The checker read `listening on 127.0.0.1:8080` back as a command and reported that the project did not provide it — a checker failing on its own correct documentation, which is a particularly convincing way to get a gate ignored.

Check with:

```bash
python3 -c "
import sys; sys.path.insert(0,'examples')
from doccheck import commands_in
print(commands_in('\`\`\`bash\nmake run\n\`\`\`\n\nmake run ->\n\n\`\`\`\nlistening\n\`\`\`\n'))"
```

It must print `['make run']` and nothing else.

## Every claimed output reports "no captured output to compare"

Your output pattern uses `re.S` for the command group. A dot then matches newlines, and the group swallows everything from the top of the document to the first fenced block — so the "command" is the whole README and matches nothing.

Use `[^\n]+?` for the command and reserve `re.S` for the block body.

## Prompts or comments appear as commands

Strip a leading `$` and skip lines beginning with `#`. Both are conventions readers expect in a shell block, and neither is part of the command.

## An undocumented command fails the review

It should warn. Only `FAIL` findings make `DocReport.ok` false. Blocking on incompleteness makes the gate annoying enough that someone removes it, at which point it catches nothing.

## `test_recording_no_limitations_warns` fails

An empty `known_limitations` tuple is a claim — that the system has no limitations — and it is usually false. Warn rather than passing silently.

## `test_a_known_limitation_left_unstated_fails` fails

The comparison must be case-insensitive: lower both the README body and the limitation before checking membership. A README saying "english only" still states the limitation.

## The section check fails on a heading you can see

`sections_in` matches `#`, `##` and `###` headings and compares the title exactly. `## Limitations` matches `Limitations`; `## Known limitations` does not. Either match the required list exactly or relax the comparison deliberately.

## `NotImplementedError` on nearly every test

Expected. The starter stubs five functions — see `expected-output/starter-run.txt`, which also names the one test that passes without them.
