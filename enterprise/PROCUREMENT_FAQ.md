# Enterprise Procurement FAQ

## Is CMB production-certified?

No. The repository has automated testing and signed releases, but it does not currently claim an independent security certification or universal production suitability.

## Does CMB prevent all copying or AI ingestion?

No. CMB provides provenance, policy, authorization, integrity, and enforcement hooks. Preventing access requires actual IAM, storage, network, gateway, DLP, and contractual controls around the data.

## Can the creator access our deployment?

Not by design. The recommended architecture separates creator/project provenance from enterprise operational authority. Enterprise deployment keys belong to the enterprise.

## Is the enterprise dependent on one personal key?

It should not be. Canonical project provenance and enterprise operational keys are separate trust domains. Production Recovery must include organization-controlled rotation and incident procedures.

## Is the software proprietary?

The repository software is Apache-2.0 unless a file states otherwise. Authored literary and artistic material has separate treatment under `CONTENT_LICENSE.md`.

## Can we receive exclusive rights to the Apache-licensed core?

An agreement cannot realistically erase rights already granted to the public under prior Apache-2.0 releases. Commercial exclusivity should therefore concern distinct services, private modules, certification, support, integrations, or future separately licensed assets.

## Does a signature prove authorship?

No. It proves that the corresponding private key signed defined bytes. Identity, authority, authorship, ownership, originality, and legal effect require additional evidence.

## Does CMB satisfy the EU AI Act or another regulation?

CMB may support controls and evidence relevant to governance programs. Compliance is deployment-specific and requires appropriate legal, security, privacy, and organizational assessment.

## What should we test first?

A closed design-partner pilot:

1. seal approved test assets;
2. prove successful verification;
3. prove tamper rejection;
4. test enterprise-key pinning;
5. test expiry and scope rejection;
6. test fail-closed policy behavior;
7. inspect the audit report; and
8. run independent security review before production.

## What is the enterprise value if the protocol is open?

Open inspection can increase trust and interoperability. Commercial value can exist in managed infrastructure, support, integration, certification, policy administration, enterprise connectors, operational reliability, and governance participation.
