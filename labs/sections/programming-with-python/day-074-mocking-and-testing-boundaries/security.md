# Security notes — Day 074 lab

- **What the lab does.** It runs Python and pytest against files that ship with
  it. It makes **no network connections at any point** after the one-time
  `pip install`, needs no privileges, and writes nothing into your working
  directory. Every file it creates goes into a directory made with `mktemp -d`
  or pytest's `tmp_path` and is removed when that check finishes. The runner
  passes `-p no:cacheprovider`, so pytest leaves no cache behind either.

- **`sensor_service.py` contacts nothing.** It stands in for a remote service
  by sleeping and returning random numbers. There is no socket, no hostname, no
  certificate, and nothing to intercept. Read it — it is forty lines, and the
  two constants at the top are the whole simulation. A lab about not reaching
  the outside world during a test would be a strange place to reach the outside
  world.

- **A mock-heavy suite is a weak security signal.** This is the day's real
  security point and it is worth stating plainly. A test suite in which most
  dependencies are replaced by doubles proves that your code calls what you
  *believed* it should call. It proves nothing about what the real dependency
  does with those calls. Authentication, authorisation, TLS verification, input
  sanitisation at a real parser, and rate limiting are exactly the things a mock
  will happily pretend to have done. Green mock-heavy tests are not evidence
  that a security control works; a test against the real component, run
  deliberately, is.

- **Never mock away the check you are relying on.** If a test stubs out the
  function that verifies a signature, checks a permission, or validates a
  certificate, the test now asserts that the *rest* of the code behaves
  correctly when verification succeeds — which is the case nobody was worried
  about. Write the failing case too: stub the verifier to *refuse*, and assert
  that your code refuses with it.

- **Patching is run-time mutation of another module's namespace.** `patch`
  reaches into an imported module and rebinds an attribute for the duration of
  a block. That is a large hammer. Two habits keep it safe: always use the
  decorator or `with` form, so the original is restored even when the test
  raises; and never patch anything outside your own test process. A patch that
  escapes its block silently changes the behaviour of every test that follows,
  and the failure surfaces somewhere unrelated.

- **Mocking what you do not own is a correctness *and* a security risk.** When
  you write a double for a third-party client, you encode your beliefs about
  its behaviour — including your beliefs about which inputs it rejects. If the
  real library tightened a check in the version you upgraded to, or loosened
  one, your suite will not notice. The honest fix is a contract test: one set of
  assertions run against both the real client and your fake, with the real case
  run deliberately rather than on every commit. Extension exercise 4 has you
  write one.

- **`autospec` is a small security control.** A double built from the real
  class cannot accept a method that does not exist or a call the real object
  would reject, so a rename or a signature change in a dependency shows up as a
  test failure rather than a production `AttributeError`. Using
  `create_autospec` instead of a bare `Mock()` costs one line and removes a
  whole category of green-but-wrong.

- **`unittest.mock` runs arbitrary code you configure.** `side_effect` accepts a
  callable, and a `Mock` will happily call it. Treat test doubles as code: they
  belong in review, they belong in version control, and you should be as
  suspicious of a fixture file you did not write as of any other file you did
  not write.

- **No secrets are needed or used.** No API key, no token, no credentials, and
  no account of any kind. If you extend this lab toward a real service later,
  keep the key out of the test suite entirely: the whole design here — the
  client as a parameter — exists so that the tests never need one.
