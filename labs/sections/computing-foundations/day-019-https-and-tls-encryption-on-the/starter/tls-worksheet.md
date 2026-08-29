# TLS certificate worksheet

Fill this in for **two** different public HTTPS sites of your choice, using
the commands from the Day 19 lab and lesson. Replace the bracketed blanks.

## Commands you will use

```bash
# Subject, issuer, and validity dates:
openssl s_client -connect HOST:443 -servername HOST </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# Negotiated TLS version (read the "SSL connection using ..." line):
curl -vI https://HOST 2>&1 | grep -Ei "SSL connection|verify"
```

## Site 1

- Host (domain): `[ e.g. example.com ]`
- Certificate **subject** (the domain the cert is for): `[ ______ ]`
- Certificate **issuer** (the CA that signed it): `[ ______ ]`
- **notBefore** date: `[ ______ ]`
- **notAfter** (expiry) date: `[ ______ ]`
- Currently valid? (is today between the two dates?): `[ yes / no ]`
- Negotiated **TLS version** (from curl): `[ e.g. TLSv1.3 ]`
- Certificate verification result: `[ SSL certificate verify ok / error ]`

## Site 2

- Host (domain): `[ ______ ]`
- Certificate **subject**: `[ ______ ]`
- Certificate **issuer**: `[ ______ ]`
- **notBefore** date: `[ ______ ]`
- **notAfter** (expiry) date: `[ ______ ]`
- Currently valid?: `[ yes / no ]`
- Negotiated **TLS version**: `[ ______ ]`
- Certificate verification result: `[ ______ ]`

## Short written answer (4–6 sentences)

Pick one of your two sites. Explain what would happen to a visitor if that
certificate's `notAfter` date passed with no renewal:

- Which of TLS's three protections (confidentiality, integrity,
  authentication) would still technically function, and which trust decision
  breaks?
- What warning would the visitor see, and why does the browser refuse to
  proceed silently?
- Why is "just click through the warning" dangerous advice — what real attack
  does that warning exist to catch?

`[ Write your paragraph here. ]`
