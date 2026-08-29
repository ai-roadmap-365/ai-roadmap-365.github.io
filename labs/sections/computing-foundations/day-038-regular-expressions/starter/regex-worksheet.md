# Regex worksheet — Day 038

Fill this in as you work through the lab. Write your patterns in the code spans
and record the counts you get. The sample file is
`../examples/samples/data.txt` (relative to this `starter/` directory).

## 1. Write the pattern for an email address

Write an extended-regex pattern that extracts every email address from the
sample with `grep -E -o`.

- My pattern: `______________________________________________`
- Command I ran: `grep -E -o '______' ../examples/samples/data.txt`
- Number of addresses it found: `____`

> One-sentence note on what your pattern does NOT guarantee (hint: think about
> what "a valid email address" really requires):
>
> _______________________________________________________________

## 2. Write the pattern for a YYYY-MM-DD date

Write a pattern that matches an ISO date such as `2026-07-12`.

- My pattern: `______________________________________________`
- One thing about dates this pattern does NOT verify: `__________________`

## 3. Count how many lines match a pattern of your choice

Pick any pattern (an IP address, a phone number, lines containing `@`, lines
that are comments, …) and use `grep -E -c` to count the matching lines.

- Pattern I chose: `______________________________________________`
- What it is meant to match (in words): `__________________________`
- Command: `grep -E -c '______' ../examples/samples/data.txt`
- Count returned: `____`

## 4. Reflection (2–3 sentences)

Which was harder to get right: describing the shape you wanted, or avoiding
matches you did not want? Give one example from this lab where a pattern was
"too loose" (matched something unintended) or "too tight" (missed something)
and how you fixed it.

_______________________________________________________________________

_______________________________________________________________________
