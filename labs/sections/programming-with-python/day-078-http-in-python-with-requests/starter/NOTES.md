# Your notes — exercise 8

Fill this in after the code works. Sentences, not single words: the writing
is the exercise. Numbers come from your own runs, not from the lesson.

## 1. The status codes you met

Run each of these against the local test server and record what came back.
`pt` is your pytest; use `python3 -c` or the demo, whichever you prefer.

| Endpoint | Status | Retryable? | What your client did |
| --- | --- | --- | --- |
| `/api/readings?station=ALPHA` |  |  |  |
| `/api/readings?station=NOWHERE` |  |  |  |
| `/api/broken` |  |  |  |
| `/old/readings` |  |  |  |
| `/api/flaky` (first call after reset) |  |  |  |

## 2. The timeout

Run the slow endpoint three ways and record the wall-clock time each took:

| Call | Seconds elapsed | What happened |
| --- | --- | --- |
| `timeout=(3.05, 0.4)` against `/api/slow?seconds=3` |  |  |
| `timeout=(3.05, 10.0)` against `/api/slow?seconds=3` |  |  |
| no `timeout=` at all against `/api/slow?seconds=3` |  |  |

Now answer in two or three sentences: what would the third row have done if
the server had accepted the connection and then never sent a single byte?

## 3. Connection reuse

Fill in from your own run of the exercise-5 test:

- five requests through one `Session`: ______ TCP connection(s)
- five calls to `requests.get`: ______ TCP connection(s)

In one sentence: why does this matter more over HTTPS than over plain HTTP?

## 4. Retry

- Your schedule with `jitter=lambda: 1.0` and `attempts=6`: ______
- The same with `jitter=lambda: 0.0`: ______
- Wall-clock time of `test_retry_recovers_from_two_429s_on_the_third_attempt`:
  ______ seconds.

In two or three sentences: why is the jitter there? Describe what happens to
a server that has just come back up when a thousand clients all retry on an
identical, un-jittered schedule.

Then: name one status code you were tempted to retry and should not, and say
what retrying it would actually accomplish.

## 5. Streaming

- Bytes written by exercise 6: ______
- Chunks read: ______
- The most memory your process held at any one moment, approximately: ______

In one sentence: what would have happened if the body had been 4 GB and you
had called `response.content`?

## 6. The boundary — the point of the day

Count these yourself:

| | `test_client.py` (against the server) | your exercise-7 tests (fake session) |
| --- | --- | --- |
| tests |  |  |
| wall-clock seconds |  |  |
| sockets opened |  |  |
| failures they can produce on demand |  |  |

Now the three questions worth writing down properly:

1. What can the server-backed tests prove that the fake-backed ones cannot?
2. What can the fake-backed tests prove that the server-backed ones cannot,
   or can only prove awkwardly?
3. Rewrite `fetch_readings` in your head so it calls `requests.get` directly
   instead of taking `session`. Exactly which of your tests would still be
   possible, and what would you have had to do instead? Answer in sentences,
   and name the Day 74 idea this is an instance of.

## 7. One sentence for a code review

Write the single sentence you would leave on a pull request that adds a call
to a third-party API with no `timeout=` argument.
