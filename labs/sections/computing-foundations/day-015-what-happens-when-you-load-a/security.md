# Security notes — Day 015 lab

- **What the scripts do:** they query the single public host you name (default
  `example.com`) with a DNS lookup (`dig`), two ping packets (`ping`), and one
  HTTPS `GET` request whose body is discarded (`curl -o /dev/null`). They make
  **no other network connections**, write **no files**, and change **no
  settings**.
- **What data leaves your machine:** only what any web request sends — a DNS
  query for the host name and a normal HTTPS GET. **No personal data, no
  credentials, and no payload** beyond a standard request are transmitted. The
  page content is downloaded and immediately thrown away.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`. (In some containers `ping` alone may need extra capability; that is a
  container setting, not a request for elevated privileges by this lab.)
- **Choosing a host:** query hosts you are allowed to probe — your own sites,
  or well-known public ones such as `example.com` or a major encyclopedia.
  Repeated automated probing of a host you do not control can look like abuse;
  this lab sends only a couple of packets and one request, which is normal
  browsing-level traffic.
- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts is a common way to get compromised; the
  course's rule is that every lab script is small enough to read and understand
  before executing.
