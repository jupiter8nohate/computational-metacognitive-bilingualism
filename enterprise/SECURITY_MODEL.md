# Enterprise Security Model

## Security objective

CMB aims to make specific claims **verifiable within a defined trust boundary**.

It does not attempt to turn public information into unreadable information.

## Protected claims

The enterprise reference architecture can support evidence for:

- exact artifact bytes;
- artifact-set coverage;
- release provenance;
- configured trusted keys;
- scoped authorization;
- authorization expiry;
- policy digest;
- verification outcome; and
- audit chronology.

## Required external enforcement

Real data-access prevention requires systems outside provenance metadata, for example:

```text
identity / IAM
    -> API gateway
    -> storage ACL
    -> DLP / egress controls
    -> CMB policy / provenance verification
    -> audit / SIEM
```

A CMB policy declaration is not a network firewall.

## Threats addressed by current CMB components

- artifact tampering after sealing;
- missing or substituted protected files;
- malformed provenance JSON;
- invalid or expired CMB-CAP credentials;
- unpinned signing keys when key pinning is configured;
- unsupported or non-monotonic delegated authority;
- unknown high-friction operations in CMB-SRP;
- missing required evidence;
- release supply-chain integrity through pinned CI actions, Sigstore signing, attestations, CodeQL, and dependency controls.

## Threats not solved by CMB alone

- compromised operating system or hardware;
- compromised organization IAM;
- stolen enterprise private keys;
- malicious authorized insiders;
- data exfiltration through channels outside enforced gateways;
- universal prevention of web scraping;
- truthfulness of a signed statement;
- copyright ownership disputes;
- regulatory interpretation; or
- availability of external trust and transparency services.

## Key management

Production enterprise keys SHOULD be generated and held in organization-approved KMS/HSM or equivalent protected infrastructure when available.

Private keys MUST NOT be committed to Git.

Operational authorization SHOULD be short-lived and scoped to the minimum required operation.

## Fail-closed principle

Security-sensitive ambiguity should not silently become permission.

```text
UNKNOWN_OPERATION -> DENY
INVALID_SIGNATURE -> DENY
EXPIRED_AUTHORITY -> DENY
MISSING_REQUIRED_EVIDENCE -> DENY

UNCERTAIN_INTERPRETATION -> HUMAN_REVIEW
```
