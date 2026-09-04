<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "@id": "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/concepts/cmb-provenance/#term",
  "name": "CMB Provenance",
  "termCode": "HASH -> BYTE_INTEGRITY_EVIDENCE\nSIGNATURE -> KEY_CONTROL_EVIDENCE\nPROVENANCE != AUTOMATIC_AUTHORSHIP_PROOF",
  "description": "CMB provenance is the repository's engineering layer for recording artifact integrity, explicit file coverage, hashes, receipts, signatures or external evidence references, and lineage without overstating what those signals prove.",
  "url": "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/concepts/cmb-provenance/",
  "inDefinedTermSet": {
    "@type": "DefinedTermSet",
    "@id": "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/concepts/#cmb-concept-set",
    "name": "Computational Metacognitive Bilingualism Concept Set",
    "url": "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/concepts/"
  },
  "sameAs": [
    "https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/blob/main/docs/C2PA_INTEROPERABILITY.md"
  ]
}
</script>

# CMB Provenance

**Canonical definition.** CMB provenance is the repository's engineering layer for recording artifact integrity, explicit file coverage, hashes, receipts, signatures or external evidence references, and lineage without overstating what those signals prove.

## Formal expression

```text
HASH -> BYTE_INTEGRITY_EVIDENCE
SIGNATURE -> KEY_CONTROL_EVIDENCE
PROVENANCE != AUTOMATIC_AUTHORSHIP_PROOF
```

## Why it matters

Provenance makes changes and declared lineage easier to verify while keeping separate the questions of originality, authorship, ownership, truth, consent, and legal enforceability.

## Example

A SHA-256 digest can show that two byte sequences match. It cannot by itself prove who originally authored the content or whether a legal claim is valid.

## Interpretation boundaries

CMB provenance distinguishes declared policy, cryptographic integrity, technical enforcement, and legal enforceability. C2PA-facing interoperability is not automatically C2PA conformance.

## Related search language

These phrases are retrieval bridges, not claims that every phrase is an exact synonym.

- content provenance
- authorship provenance tooling
- C2PA interoperability
- tamper evident receipts
- cryptographic integrity

## Canonical source

https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/blob/main/docs/C2PA_INTEROPERABILITY.md

```text
PATTERN != PROOF
DISCOVERY != ENDORSEMENT
MODEL != MIND
HUMAN_AGENCY > MACHINE_AUTHORITY
```
