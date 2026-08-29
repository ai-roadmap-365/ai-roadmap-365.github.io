# Debug worksheet — Day 021

Run the commands (from the examples or your completed starter) and record what
YOUR machine and network returned. Values vary — that is expected.

## 1. A redirect you followed
- Command: `curl -IL https://httpbin.org/redirect/1`
- First response status: `____`  (should be a 3xx)
- Final status after `-L` follows it: `____`  (should be 200)

## 2. A timing breakdown
- Command: `curl -o /dev/null -s -w 'dns:%{time_namelookup} connect:%{time_connect} tls:%{time_appconnect} total:%{time_total}\n' https://example.com`
- DNS: `____`  connect: `____`  TLS: `____`  total: `____`
- Which stage took the longest? `____`

## 3. A status code you read deliberately
- Command: `curl -o /dev/null -s -w '%{http_code}\n' https://httpbin.org/status/503`
- Status returned: `____`  — which class is it, and what does it mean? `____`

## 4. One sentence
Using the decision tree (DNS → connect → TLS → status), describe how you would
diagnose a request that "just fails."

> _your answer here_
