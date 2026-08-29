# Text-pipelines worksheet — Day 010

Run your completed `starter/analyze_log.sh` against the sample log and record
the answers below. Each answer comes from one of the four pipelines you built.

## Your findings

| Question | Your answer | The pipeline you used |
| --- | --- | --- |
| 1. Total requests in the log | _____ | `wc -l < …` |
| 2. Top IP address (most requests) | _____ | `awk '{print $1}' … \| sort \| uniq -c \| sort -rn \| head` |
| 3. That top IP's request count | _____ | (same pipeline as row 2 — read the first column) |
| 4. Number of 404 responses | _____ | `awk '$9 == 404' … \| wc -l` |
| 5. Count of unique paths requested | _____ | `awk '{print $7}' … \| sort -u \| wc -l` |

## One thing you noticed

Write one or two sentences about a pattern in the log. For example: which
paths returned 404, whether one client dominated the traffic, or how many
responses were successful (status 200) versus errors.

_Your notes:_

## Check yourself

- Did every pipeline read the file without changing it? (Re-run
  `wc -l < examples/samples/access.log` — it should still report the same
  number of lines.)
- Could you rebuild each pipeline from memory, naming what every stage does?
