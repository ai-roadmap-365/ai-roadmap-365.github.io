# Authentication worksheet — Day 025

Fill this in from a real run of the commands (via `bash examples/auth_demo.sh`
or by running each `curl` yourself). Every credential here is fake and
httpbin.org accepts any of them, so you need no account and no real key.

## 1. Basic auth status codes

Run both and record the exact HTTP status code:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -u user:pass       https://httpbin.org/basic-auth/user/pass
curl -s -o /dev/null -w '%{http_code}\n' -u user:wrongpass  https://httpbin.org/basic-auth/user/pass
```

- Status code for CORRECT credentials (`user:pass`): __________
- Status code for WRONG credentials (`user:wrongpass`): __________
- What does each code mean, in one sentence?
  - 200: ______________________________________________________
  - 401: ______________________________________________________

## 2. Bearer token

```bash
curl -s -H "Authorization: Bearer token-example-123" https://httpbin.org/bearer
```

- Did the endpoint accept your token (did the JSON say `"authenticated": true`)?  __________
- What token did it echo back? __________
- Which HTTP header carried the token, and in what exact format? __________

## 3. Key in a header

```bash
curl -s -H "X-API-Key: demo-key" https://httpbin.org/headers
```

- Did your `X-API-Key` header appear in the server's echo of the headers it saw?  __________
- Why is sending a key in a header safer than sending it in the URL query string?
  Name two places a query-string key can leak:
  1. ______________________________________________________
  2. ______________________________________________________

## 4. Storing a real key safely (the important part)

Imagine you will call a paid API tomorrow. Write 4–6 sentences answering:

- What environment variable name would you read the key from?
- Where would the `.env` file live, and why must it be in `.gitignore`?
- Why should you never hard-code the key in your source?
- What would you do the *instant* you discovered the key had been committed to a
  public repository — and why is deleting the commit not enough?

Your answer:

_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
