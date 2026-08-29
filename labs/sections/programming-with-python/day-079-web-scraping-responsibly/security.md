# Security notes — Day 079 lab

- **What this lab does.** It starts an HTTP server bound to `127.0.0.1` on a
  port the operating system assigns, serves the HTML files in
  `examples/fixtures/`, scrapes them, writes a CSV, and stops. It makes **no
  connection to any host but the loopback address**, needs **no privileges**,
  and writes only into the directory you run it from and into temporary
  directories created with `mkdtemp`. Installing the three pinned packages is
  the only step that uses the internet.

- **Bound to loopback on purpose.** `("127.0.0.1", 0)` means the listener is
  reachable only from this machine. Binding `("", 0)` or `("0.0.0.0", 0)`
  instead would expose the fixture site to your whole local network — on a
  café Wi-Fi, to everyone in the café. When you write your own test servers,
  make the interface explicit and make it loopback.

- **The ethics ARE the security model here.** Rate limiting, `robots.txt` and
  an honest `User-Agent` are usually filed under manners. They are also the
  controls that keep a scraper from being indistinguishable from a
  denial-of-service tool. A loop with no delay, no cache and no host guard is
  a stress test that you did not get permission to run, and the operator on
  the other end has no way to tell the difference between that and an attack.
  The cache in this lab is the strongest of those controls: it makes the
  twentieth run of your parser cost the site nothing at all.

- **Never send credentials to a site you are scraping.** Nothing in this lab
  authenticates, and that is deliberate. Logging in to reach content changes
  the legal and contractual picture completely — you have then accepted terms
  of service, and you are acting as an identified user rather than an
  anonymous client. If you ever do need a token for an API, read it from the
  environment as Day 78 showed, never from a literal in the source, and never
  commit it.

- **`robots.txt` is advice a client chooses to honour; it is not access
  control.** The fixture server serves `/private/internal-notes.html` to
  anyone who asks for it. The only reason your scraper never sees it is that
  your scraper asked first and then declined. Read that in both directions: as
  a client, honour it; as someone who will one day run a server, never treat a
  `Disallow:` line as a security boundary. Anything that must not be read
  needs authentication, not a line in a text file.

- **Parsed HTML is untrusted input.** BeautifulSoup builds a tree; it does not
  execute anything, and `html.parser` is pure Python with no external parser
  to exploit. But everything you extract came from someone else's server and
  must be validated before it is used: a price is a string until you convert
  it, a link is a string until you check its host, and a name may contain
  anything at all. This lab converts prices with `float()` inside a guard,
  refuses links whose netloc differs from the start URL, and writes output
  with the `csv` module rather than by joining strings — which is also what
  keeps a comma or a quote inside a product name from corrupting the file.

- **Never interpolate scraped text into a shell command, a SQL query, or a
  file path.** The `csv` module quotes for you; a database driver's parameter
  binding quotes for you. String concatenation does not. A scraped value is
  the textbook case of input you did not write.

- **Formulas in CSV are a real hazard.** A cell beginning with `=`, `+`, `-`
  or `@` is interpreted as a formula by common spreadsheet applications when
  the file is opened. If you will ever open scraped CSV in a spreadsheet,
  prefix such cells or import as text. The fixture data here contains no such
  values; a real site might.

- **A cache directory is a copy of someone else's content on your disk.** It
  inherits every question the original had: how long you may keep it, whether
  it contains personal data, whether it may be shared or committed. This lab's
  cache lives in a temporary directory and is deleted when the run ends. If
  you keep a cache, keep it out of version control, and set yourself an expiry
  rather than accumulating a private archive of a site you do not own.

- **Personal data raises the stakes and this lab deliberately avoids it.** The
  fixture catalogue contains invented products and no people. "Publicly
  visible" is not the same as "free to collect, store, and republish": names,
  photographs, reviews, profiles and posts are personal data in most legal
  regimes, and collecting them at scale is exactly the activity those regimes
  are written about. If your scraping target contains people, stop and get
  advice before you write the loop, not after.

- **Read before you run.** Every file in this lab is short and commented.
  `examples/fixture_server.py`, `examples/catalogue_scraper.py`,
  `examples/demo.py` and `tests/run_tests.sh` are all worth reading first. The
  habit matters more than these particular files: running unread scripts is
  one of the most common ways developers get compromised.

- **This lab is not legal advice, and neither is the lesson.** The legal
  position on scraping varies by jurisdiction, by the terms of the site, by
  what you collect and by what you do with it, and it changes. What the lesson
  and this lab can give you is the engineering discipline that keeps you out
  of the easy trouble, and a clear enough picture of the questions to know
  when you need a real answer from a real lawyer.
