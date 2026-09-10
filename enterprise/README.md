# CMB Enterprise Readiness

**Status:** design-partner pilot architecture  
**Scope:** enterprise evaluation of CMB provenance, authorization, policy, and audit controls

This directory is the shortest enterprise path through Computational Metacognitive Bilingualism (CMB).

CMB does **not** claim to make accessible data impossible to copy, to prove copyright ownership from a signature, or to automatically satisfy any law. It provides composable controls for artifact integrity, provenance evidence, scoped authorization, machine-readable policy, fail-closed verification, and auditable human authority.

```text
DECLARED_POLICY
!= CRYPTOGRAPHIC_INTEGRITY
!= TECHNICAL_ENFORCEMENT
!= LEGAL_ENFORCEABILITY
```

## Start here

- [Executive brief](EXECUTIVE_BRIEF.md)
- [Trust architecture](TRUST_ARCHITECTURE.md)
- [Pilot specification](PILOT_SPECIFICATION.md)
- [Security model](SECURITY_MODEL.md)
- [IP and licensing matrix](IP_LICENSING_MATRIX.md)
- [Compliance control map](COMPLIANCE_CONTROL_MAP.md)
- [Procurement FAQ](PROCUREMENT_FAQ.md)

## Enterprise thesis

CMB should be evaluated as **creator-originated, cryptographically attributable, policy-aware infrastructure with enterprise-enforceable trust boundaries**.

The open-source core remains independently inspectable. Enterprise operators retain their own deployment keys and access controls. Creator provenance remains a separate evidence layer rather than a hidden administrative backdoor.

```text
AUTHORSHIP_ROOT != OPERATIONAL_ROOT
PROVENANCE != ADMINISTRATOR_ACCESS
SIGNATURE != AUTHORSHIP
HASH != OWNERSHIP
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Reference pilot flow

```text
enterprise asset
    -> cmb-provenance seal
    -> CMB receipt
    -> enterprise authorization / CMB-CAP
    -> verification gateway
    -> ALLOW | DENY | HUMAN_REVIEW
    -> audit report
```

The initial pilot is intentionally narrow: prove the controls on a closed test dataset before discussing production deployment, certification, exclusivity, or foundation governance.
