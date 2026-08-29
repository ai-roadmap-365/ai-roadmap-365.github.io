# HTTP worksheet — Day 018

Fill this in by running `curl` yourself. Every answer comes from a command you
run in the terminal; copy the real values you see.

## 1. Status code of a normal GET

Command:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://example.com
```

- Status code returned: `__________`  (expected: a 2xx success)
- Which status class is that, and what does the class mean? `__________`

## 2. The Content-Type header of a page

Run the verbose request and find the `content-type` line in the **response**
headers (the lines starting with `<`):

```bash
curl -v https://example.com 2>&1 | grep -i "^< content-type"
```

- `Content-Type` reported: `__________`  (expected: `text/html`)
- In one sentence, what does `Content-Type` tell the client to do? `__________`

## 3. What httpbin.org/post echoes back for your POST body

Send a JSON body of your choosing (change the values if you like) and read the
`json` field of the response:

```bash
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"hello":"world"}' https://httpbin.org/post
```

(If httpbin.org returns 503, retry once or use `https://httpbingo.org/post`.)

- The body you sent: `__________`
- What the `"json"` field of the response contained: `__________`
- Did the `headers` section of the response show the `Content-Type` you sent?
  `__________`

## 4. Short answer: 401 vs 429

In 4–6 sentences, explain why a `401` and a `429` require **completely
different** responses from your code. Name whose fault each is (client or
server), and say what you should do for each — for example, why retrying a
`401` unchanged can never succeed, while a `429` calls for slowing down.

```
____________________________________________________________________________
____________________________________________________________________________
____________________________________________________________________________
____________________________________________________________________________
```
