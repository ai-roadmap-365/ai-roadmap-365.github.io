# Troubleshooting — Day 024 lab

## `python3: command not found`

Your system may expose Python 3 as `python`. Check with `python --version`;
if it reports 3.x, substitute `python` for `python3` in every command. On
Windows, run the lab inside WSL, or install Python 3 from python.org.

## `bash examples/json_tools.sh` stops immediately with a JSON error

If it fails on `config.json`, that file has probably been edited by accident.
Restore it from version control (`git checkout -- examples/samples/config.json`)
and re-run. The script is designed so that only `broken.json` should fail.

## The broken-file error wording is different from the README

That is expected. Python 3.13 and newer say `Illegal trailing comma before
end of object`; older versions say `Expecting property name enclosed in
double quotes`. Both report the same trailing-comma mistake and both exit
non-zero, which is all the test checks. See `expected-output/FIELDS.md`.

## `KeyError` when extracting a field

You asked for a key that is not in the file, or spelled one wrong. Keys are
case-sensitive: use `lat`, not `Lat`, and `coordinates`, not `Coordinates`.
Pretty-print the file first (`python3 -m json.tool examples/samples/config.json`)
to see the exact key names.

## The Python one-liner errors about quotes

Keep the outer double quotes around the `-c` program and single quotes for the
filename inside, exactly as shown:
`python3 -c "import json; print(json.load(open('examples/samples/config.json'))['coordinates']['lat'])"`.
Mixing them up makes the shell mangle the program before Python sees it.

## `jq: command not found`

`jq` is optional. Every required step uses `python3`; the `jq` lines in the
scripts are comments for comparison only. Install `jq` (`brew install jq` or
`apt install jq`) only if you want to try them.

## `Permission denied` when running a script

Run it through bash explicitly: `bash starter/json_tools.sh`. You do not need
to mark the file executable.
