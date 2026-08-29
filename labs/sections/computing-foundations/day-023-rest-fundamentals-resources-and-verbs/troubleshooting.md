# Troubleshooting — Day 023 lab

## My POST returned 201 but the new post is not there when I GET it

**This is expected.** JSONPlaceholder *fakes* writes. It responds as if it
created the resource — a real `201 Created` and the id `101` — but nothing is
actually stored. If you then `GET /posts/101`, you get a `404`, because the
post was never persisted. The status codes and echoed bodies are genuine; only
the persistence is simulated. This is exactly what makes the service safe for
practice: you can run the full create-update-delete cycle repeatedly without
changing any real data.

## `python3: command not found`

The pretty-printer is optional. Use `python` instead of `python3`, or drop the
pipe entirely — `curl -s .../posts/1` still returns valid JSON, just
unformatted. The example script already falls back to raw output when
`python3` is missing.

## The status code prints stuck to the JSON body

Keep the newline in the `-w` format: `-w "\nHTTP %{http_code}\n"`. Without the
leading `\n`, the status code lands on the same line as the last byte of the
body.

## My POST behaved like a GET (no creation, no 201)

You dropped `-X POST` or the `-d` body. The `-d` flag supplies the request body
and, on its own, already switches the method to `POST`; combine it with a
`Content-Type: application/json` header so the server parses your JSON.

## I created to /posts/1 instead of /posts and got a surprise

You create by `POST`ing to the **collection** (`/posts`), not to an item
(`/posts/1`) — the item does not exist yet, and the server assigns the new id.
`GET`, `PUT`, `PATCH`, and `DELETE` target a specific item you already know.

## jsonplaceholder.typicode.com is slow or returns a 5xx

It is a shared free service and can occasionally be busy. The example and the
tests retry transient errors and, in the tests, skip (never fail) a live check
when the server is transiently unavailable. Wait a moment and re-run.

## Offline

The scripts and tests detect no network and exit 0 with a clear message.
Connect to the internet to see live output.
