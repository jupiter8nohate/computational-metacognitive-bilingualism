# Security Policy

## Supported software

The supported provenance implementation is the installable `cmb-provenance`
package on the default branch and its tagged releases.

Historical standalone scripts and artistic/code-poetry artifacts are preserved
for provenance and research, but they are not treated as supported security
software unless a document explicitly says otherwise.

## Reporting a vulnerability

Please do **not** publish exploit details in a public issue.

1. Use GitHub private vulnerability reporting / Security Advisories if available.
2. If private reporting is unavailable, open a minimal public issue requesting a
   private contact channel. Do not include exploit details, secrets, or private data.

Useful reports include the affected version/commit, impacted component,
reproducible behavior, expected boundary, minimal non-destructive reproduction,
likely impact, and suggested mitigation if known.

## Security boundaries

```text
DECLARED_POLICY
!= CRYPTOGRAPHIC_INTEGRITY
!= TECHNICAL_ENFORCEMENT
!= LEGAL_ENFORCEABILITY
```

A hash can support byte-integrity evidence. A signature can identify a signing
workflow or key. A timestamp can support chronology. None alone proves authorship,
originality, copyright ownership, truth, or legal priority.

C2PA test integration is interoperability evidence, not formal C2PA conformance
and not a production trust identity.

## Disclosure process

```text
REPORT -> REPRODUCE -> CLASSIFY -> FIX -> TEST -> RELEASE -> DISCLOSE
SELF_TEST != INDEPENDENT_AUDIT
```
