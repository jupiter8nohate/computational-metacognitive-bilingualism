# Independent Review Requested

**Project:** Computational Metacognitive Bilingualism (CMB)  
**Primary review target:** `cmb_provenance`  
**Status:** Open review request

## Current validation status

The repository has automated tests, CI across supported Python versions, canonical-receipt verification, build checks, release checksums, Sigstore-oriented release automation, and GitHub artifact-attestation support.

As of 2026-09-04, the project does **not** claim:

- an independent security audit;
- formal C2PA conformance;
- certification by a digital-rights organization;
- independent verification of historical priority or legal authorship.

```text
SELF_TEST != INDEPENDENT_AUDIT
SELF_ATTESTATION != EXTERNAL_VALIDATION
```

The goal is to obtain **one serious external review before seeking broad validation**.

## Requested reviewer profile

A useful first reviewer could be one of:

- a security engineer familiar with Python supply-chain or cryptographic tooling;
- a provenance/content-authenticity engineer familiar with C2PA;
- a privacy or digital-rights researcher;
- an independent open-source maintainer.

No endorsement is required. Critical findings are useful.

## Technical audit scope

Priority files:

```text
src/cmb_provenance/
scripts/seal_canonical_artifacts.py
scripts/build_checksums.py
.github/workflows/ci.yml
.github/workflows/release.yml
tests/
RELEASE.md
docs/C2PA_INTEROPERABILITY.md
```

Questions:

1. Are artifact hashes computed correctly and over the intended bytes?
2. Is deterministic serialization actually deterministic?
3. Are symlink, file-replacement, race, and concurrent-ledger cases handled safely?
4. Does Git verification prove only what the documentation says it proves?
5. Are receipt schemas strict enough to reject ambiguous or malformed data?
6. Could an attacker make the tool report stronger provenance than it has?
7. Are release signing and attestation claims described accurately?
8. Does the C2PA interoperability plan misuse C2PA concepts or terminology?
9. Is private or unnecessary data exposed in receipts?
10. What should be fixed before the tool is recommended to others?

## Policy review scope

For a policy reviewer:

1. Which CMB principles already exist in law or established scholarship?
2. Where does the Charter overstate novelty?
3. Which proposals are too broad to be operational?
4. Which terms need legal precision?
5. Which claims need citations?
6. What would make the one-page policy summary useful to a legislator, journalist, researcher, or civil-society organization?

## Desired review format

A short public review is enough:

```text
REVIEWER:
DATE:
SCOPE:
COMMIT:
MAJOR_FINDINGS:
MINOR_FINDINGS:
LIMITATIONS:
RECOMMENDATION:
```

The reviewer should state what they did **not** examine.

## Project response rule

External criticism should not be converted into branding language.

For every finding:

```text
FINDING
    ↓
REPRODUCE
    ↓
CLASSIFY
    ↓
FIX OR DISPUTE WITH EVIDENCE
    ↓
TEST
    ↓
DOCUMENT
```

## Independence boundary

A reviewer is independent only if the project accurately discloses relevant relationships and does not misrepresent ordinary feedback as certification.

```text
COMMENT != AUDIT
LIKE != ENDORSEMENT
REVIEW != CERTIFICATION
CERTIFICATION != TRUTH
```
