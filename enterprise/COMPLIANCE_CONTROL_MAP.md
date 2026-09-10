# Compliance Control Map

**Status:** engineering crosswalk only.  
**Not:** legal advice, certification, conformity assessment, or a representation that CMB satisfies any law.

CMB can help produce technical evidence relevant to governance and assurance programs. Applicability depends on the organization, system, jurisdiction, role, risk class, and deployment.

## Control-oriented mapping

| CMB capability | Evidence it can produce | Governance theme |
|---|---|---|
| artifact receipts | byte integrity, exact scope, digest | traceability / change control |
| signed releases | release identity and tamper evidence | software supply chain |
| scoped authorization | operation, subject, policy, expiry | access governance / human authority |
| fail-closed runtime | explicit deny reasons | risk controls |
| audit ledger | ordered integrity evidence | logging / accountability |
| C2PA-facing adapter | provenance payload interoperability | content provenance |
| human-review state | escalation rather than silent automation | human oversight |
| evidence-boundary rules | avoids treating prediction as proof | transparency / accountable inference |

## EU AI Act

Where the EU AI Act applies, organizations may face obligations involving risk management, technical documentation, logging, transparency, human oversight, cybersecurity, quality management, or other controls depending on the system and actor role.

CMB may support evidence collection for some of those control themes. It does not determine whether a system is in scope, what risk category applies, who bears a legal duty, or whether the implementation conforms.

Official starting point:

- https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai

## NIST AI RMF

The NIST AI Risk Management Framework organizes AI risk work around GOVERN, MAP, MEASURE, and MANAGE.

CMB's strongest overlap is evidence preservation, authority boundaries, traceable policy decisions, documented limitations, and Recovery.

Official source:

- https://www.nist.gov/itl/ai-risk-management-framework

## C2PA

CMB's C2PA work is an interoperability bridge. It does not claim that a CMB receipt itself is a C2PA manifest or Content Credential.

Official specification:

- https://spec.c2pa.org/

## Procurement rule

No sales, procurement, or technical document should say:

- "CMB guarantees EU AI Act compliance";
- "CMB is C2PA certified";
- "cryptography proves ownership"; or
- "CMB prevents all AI ingestion."

Use:

> CMB provides auditable technical controls and evidence that may support an organization's broader governance, provenance, security, and compliance program.
