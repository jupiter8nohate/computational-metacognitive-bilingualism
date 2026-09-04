# Security Policy

The CMB repository contains provenance and content-authenticity tooling. Security claims are intentionally bounded.

## Supported version

The current supported development line is **cmb-provenance 1.4.x** on Python 3.10–3.13. Version 1.4.0 is the first published signed release in this line; version 1.4.1 is a metadata/release-recovery patch with no intended protocol-semantic changes. Historical standalone scripts and checked-in historical receipts are preserved for provenance, not treated as the preferred implementation.

## Reporting a vulnerability

Do not publish exploit details, private keys, tokens, or sensitive reproduction data in a public issue.

1. If GitHub's **private vulnerability reporting** option is visible under the repository Security tab, use it.
2. If it is not available, open a minimal public issue that says only that you need a private security contact channel. Do not include exploit details.
3. Include the affected commit/version, operating system, Python version, attack preconditions, expected behavior, actual behavior, and a minimal reproduction once a private channel exists.

Security findings are evaluated using:

```text
REPORT
  -> REPRODUCE
  -> CLASSIFY
  -> FIX
  -> REGRESSION_TEST
  -> DISCLOSE
```

## Security boundaries

The project aims to provide integrity and provenance evidence. It does not claim that:

- a hash proves authorship;
- a signature proves originality;
- a timestamp proves legal ownership;
- a valid C2PA credential proves every assertion is true;
- local code can prevent every hostile copier or crawler;
- symbolic CMB policy statements create legal enforcement.

See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Independent review status

The project has automated tests and security automation but has **not yet received an independent security audit**. See [docs/EXTERNAL_REVIEW.md](docs/EXTERNAL_REVIEW.md).

```text
SELF_TEST != INDEPENDENT_AUDIT
SIGNATURE != AUTHORSHIP
PROVENANCE != LEGAL_JUDGMENT
```
