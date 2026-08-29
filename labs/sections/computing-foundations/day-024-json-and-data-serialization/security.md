# Security notes — Day 024 lab

- **What the scripts do:** read two small local JSON files
  (`examples/samples/config.json` and `examples/samples/broken.json`) and
  print or validate them with `python3`. They make **no network
  connections**, write **no files** outside their own console output, and
  change **no settings**.
- **Never `eval` untrusted JSON.** Because JSON's syntax overlaps with
  JavaScript's, it is tempting to turn a JSON string into values by running
  it as code — this is dangerous: a malicious payload could then execute
  arbitrary instructions. Always use a real parser (`python3 -m json.tool`,
  Python's `json.load`, or `jq`), which treats the input strictly as data and
  can only ever produce the six JSON value types, never executable behavior.
- **This lab only reads local sample files** that ship with it, so there is
  no untrusted input here — but the habit matters for every real service you
  will call later, where the JSON comes from outside and must be parsed, not
  evaluated, and then validated before you trust its fields.
- **Privileges:** everything runs as your normal user. Nothing needs `sudo`.
- **Reading before running:** the scripts are short and commented — read them
  first. Running unread scripts is one of the most common ways developers get
  compromised.
