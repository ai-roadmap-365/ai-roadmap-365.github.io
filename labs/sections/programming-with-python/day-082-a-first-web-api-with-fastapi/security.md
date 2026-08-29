# Security notes — Day 082 lab

Writing a server is the first thing in this course that, run for real, would
accept input from a stranger. That changes what "careful" means, so this
file is longer than most.

## What this lab does and does not do to your machine

- **Nothing here opens a network connection.** Every request goes through
  `TestClient`, which hands the request object straight to the application in
  the same process. No port is bound, so no firewall prompt appears and no
  other program on your network can reach anything.
- **The reference suite proves that rather than promising it.** An autouse
  fixture in `examples/conftest.py` replaces `socket.socket.connect` and
  `socket.create_connection` with functions that raise. Section 7 of
  `tests/run_tests.sh` writes a throwaway test that deliberately tries to
  connect and asserts that it fails — so the guard is demonstrably armed and
  not decorative.
- **Nothing is written to disk during the tests.** Storage is injected, and
  the tests inject an in-memory dictionary. Section 8 of the harness searches
  the whole lab directory for a `bookmarks.json` afterwards and fails if one
  exists.
- **No credentials, keys or accounts are involved.** No signup, no token, no
  paid service.
- One command in the README does bind a port — `uvicorn ... --host 127.0.0.1`
  — and it is entirely optional. `127.0.0.1` means the loopback interface, so
  even then the server is reachable only from your own machine. Binding
  `0.0.0.0` instead would expose it to your whole network; do not do that
  without meaning to.

## The five security lessons this lab is actually teaching

### 1. Validation is not authorization

Every request in this API is validated, and every request is also completely
unauthenticated. Those are different questions. Validation asks *is this
well-formed?* Authorization asks *is this caller allowed?* A perfectly valid
`DELETE /bookmarks/bm-0001` from a stranger is still a stranger deleting your
bookmark. This lab deliberately stops at validation so the distinction stays
visible; a real API adds an authentication scheme and a permission check per
route, and neither comes free with pydantic.

### 2. Never trust a client-supplied identifier

`BookmarkCreate` has no `id` field, and `extra="forbid"` means sending one is
a 422 rather than a shrug. The id, the creation time and the internal token
are all generated on the server. An API that accepts a client's id lets a
caller overwrite somebody else's record by guessing a number, and an API that
accepts a client's `created_at` lets a caller backdate history.
`examples/test_api.py::test_the_id_is_server_generated_and_a_client_cannot_choose_it`
holds that line.

### 3. Declare what you return, not just what you accept

`StoredBookmark` carries `owner_token`. `BookmarkOut` does not.
`response_model=BookmarkOut` on each handler is what stands between the two,
and it is one line — which is exactly why it is easy to forget. Three tests
assert the field's **absence**, by key and by raw substring, on every route
that returns a bookmark, plus one on the generated schema. Section 6 of the
harness deletes that one line from a copy of the application and demands that
the suite go red, because an assertion that cannot fail is not protecting
anything.

The general shape of this bug is the most common data leak in real APIs: a
handler returns the database row, and the row has a password hash, an
internal note, another user's email, or a flag that reveals your schema.

### 4. A traceback is never a response

`HTTPException` turns a known negative answer into a small JSON body with a
`detail` string. An *unknown* failure — a bug — becomes a 500 whose body is
the five words `Internal Server Error`, while the traceback goes to the
server log. That asymmetry is deliberate. A traceback names your file paths,
your line numbers, your framework versions and the values of your local
variables, and every one of those is a gift to somebody probing your service.
`examples/test_type_demo.py` asserts that a deliberate `ZeroDivisionError`
produces a 500 containing no filename, no exception name and no traceback.

Be careful with `detail` strings too: this lab echoes the requested id back
(`No bookmark with id 'nope'`), which is fine for an id the caller just sent.
Echoing something the caller did *not* send — a filename, a query, an
internal message — is how a helpful error message becomes a disclosure.

### 5. Secrets come from the environment, and CORS is not a security feature

`get_storage` reads its path from `os.environ`, not from a literal in the
source. The same rule Day 078 stated for API tokens applies to every secret a
server holds: a value in source is a value in version control, in every clone
and in every backup.

Cross-Origin Resource Sharing deserves one honest paragraph, because it is
routinely misunderstood. CORS is a browser mechanism: a page loaded from one
origin may not read a response from another origin unless that other origin's
headers permit it. It protects *the user's browser session*, and it does
nothing whatsoever against `curl`, a script, or any non-browser client.
Setting `allow_origins=["*"]` to make a frontend error go away is a decision
about which web pages may read your data, not a decision about security in
general — and if your API relies on cookies, it is a decision with real
consequences. This lab adds no CORS middleware at all, because it has no
browser frontend, and adding middleware you do not need is its own risk.

## Things this lab deliberately does not have

Naming them is more honest than implying the list is complete:

- **No authentication and no authorization.** Anyone who can reach the
  server can do anything.
- **No rate limiting.** A caller can issue as many requests as they like.
- **No request-size limit** beyond what the ASGI server imposes by default.
- **No HTTPS.** `uvicorn` on loopback speaks plain HTTP; a real deployment
  terminates TLS in front of the application.
- **No audit log.** Nothing records who changed what.
- **No concurrency control.** `JsonFileStorage` rewrites the whole file, so
  two simultaneous writes can lose one. Week 13's database work is the answer.

Every one of those is a normal thing to add later, and none of them is
something pydantic, FastAPI or a passing test suite gives you for free.

## Cleanup

The tests leave nothing behind. If you ran the server by hand, stop it with
`Ctrl-C` and delete any `bookmarks.json` it created:

```bash
rm -f bookmarks.json
rm -rf .venv examples/.pytest_cache starter/.pytest_cache
```
