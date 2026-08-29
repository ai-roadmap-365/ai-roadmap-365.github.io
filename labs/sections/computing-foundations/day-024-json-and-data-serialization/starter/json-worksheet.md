# JSON worksheet — Day 024

Fill this in from your own runs of `starter/json_tools.sh` and the commands
in the lesson's hands-on section. Keep it — Week 4's project (a weather
command-line dashboard) parses live JSON and builds on this groundwork.

## The sample file (`examples/samples/config.json`)

| Question | Your answer | Command you used |
| --- | --- | --- |
| How many top-level keys does it have? |  |  |
| One nested value, and the path to it |  |  |
| What value type is `active`? |  | (read it — no command needed) |
| What value type is `sensors`? |  |  |
| What value type is `notes`? |  |  |

Hint for the key count: `python3 -c "import json; print(len(json.load(open('examples/samples/config.json'))))"`

Hint for a nested value: `python3 -c "import json; print(json.load(open('examples/samples/config.json'))['coordinates']['lat'])"`

## The broken file (`examples/samples/broken.json`)

Run `python3 -m json.tool examples/samples/broken.json` and record the exact
error message it prints:

```text
(paste the error line here)
```

**Which single character makes the document invalid?**

(one sentence)

**Why does that one character make the whole document invalid?**

(two or three sentences, in your own words)

## The six JSON value types

List all six value types JSON allows, and next to each write which key in
`config.json` is an example of it (some types appear more than once).

1. object —
2. array —
3. string —
4. number —
5. boolean —
6. null —
