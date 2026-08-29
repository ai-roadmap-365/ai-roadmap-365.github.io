# Security notes — Day 019 lab

- **What the scripts do:** open a TLS connection to a public HTTPS host and
  read the certificate that server presents to *every* visitor, then print
  its subject, issuer, dates, and the negotiated TLS version. This is
  read-only inspection of public information.
- **What they do not do:** they send no request body, no credentials, and no
  personal data; they log in nowhere; they write no files outside their own
  console output (and the one capture you choose to redirect). There are no
  private keys involved anywhere in this lab — you only ever read the
  server's *public* certificate.
- **Network:** the lab requires an outbound HTTPS connection (port 443) to
  the host you inspect. It makes no other connections. On an offline machine
  the scripts detect the lack of network and exit cleanly.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`; if any tutorial ever tells you to `sudo` a script you have not
  read, stop and read it first.
- **Choosing a host:** inspecting a public site's certificate is a normal,
  unremarkable act — it is the same data your browser reads on every visit.
  Prefer well-known public sites; avoid probing hosts you do not have
  permission to interact with, as a courtesy and to keep your intent clear.
- **A real caution the lesson teaches:** never disable certificate
  verification (for example `curl -k` / `--insecure`) to "make an error go
  away." That silently reopens the man-in-the-middle hole TLS exists to
  close. This lab never uses those flags, and neither should your real code.
