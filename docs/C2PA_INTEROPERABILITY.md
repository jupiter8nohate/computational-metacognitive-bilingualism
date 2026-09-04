# CMB Provenance ↔ C2PA Interoperability Plan

**Status:** Design target; not a claim of current C2PA conformance  
**Component:** `cmb_provenance`  
**Last reviewed:** 2026-09-04

## Position

`cmb_provenance` should be **complementary to C2PA**, not a competing provenance universe.

C2PA already defines a standards-based architecture for assertions, claims, signatures, content binding, manifests, and Content Credentials. CMB's useful role is to provide CMB-specific provenance semantics and explicit artifact receipts that can be mapped into that ecosystem.

```text
CMB RECEIPT
    !=
C2PA MANIFEST

CMB RECEIPT
    -> OPTIONAL C2PA ASSERTION PAYLOAD
    -> C2PA-CONFORMANT TOOLING
    -> SIGNED CONTENT CREDENTIAL
```

C2PA specification:  
https://spec.c2pa.org/

C2PA conformance explorer:  
https://spec.c2pa.org/conformance-explorer/

## What exists today

The CMB tool currently provides:

- explicit-file-set coverage;
- byte-level SHA-256 digests;
- deterministic receipt serialization;
- Git commit metadata and byte-to-commit verification when run in a Git worktree;
- tamper-evident external-evidence references;
- release checksums, Sigstore signing, and GitHub attestations through CI.

These capabilities are useful, but they do **not** make the tool a C2PA implementation.

## What C2PA adds

C2PA provides standardized machinery for:

- asset-bound provenance assertions;
- signed claims;
- claim signatures;
- Content Credentials;
- manifest storage and validation;
- a conformance ecosystem.

C2PA supports entity-specific/custom assertions. That creates a possible bridge for CMB-specific metadata without reimplementing the surrounding provenance standard.

## Non-goals

The CMB project should not:

- invent a replacement for C2PA claim/signature formats;
- implement its own incompatible media container format;
- call a JSON export a "C2PA manifest" unless a conformant C2PA implementation produced it;
- imply that a C2PA credential proves the truth of every assertion;
- include unnecessary personal information in provenance payloads;
- claim C2PA conformance before testing against the relevant conformance process.

## Proposed architecture

```text
┌─────────────────────────────────────┐
│ CMB artifact(s)                     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ cmb_provenance seal                 │
│                                     │
│ exact paths                         │
│ SHA-256                             │
│ sizes                               │
│ schema/tool versions                │
│ Git commit + verification status    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ CMB receipt                         │
│ cmb.seal-receipt.v1                 │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ C2PA assertion adapter              │
│ CMB-specific semantics only         │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ existing C2PA SDK / conformant tool │
│ manifest + signature + binding      │
└──────────────────┬──────────────────┘
                   │
                   ▼
             Content Credential
```

## Proposed assertion payload

The following is an **illustrative internal payload**, not a claim that the label or envelope is already approved by C2PA:

```json
{
  "cmb_schema": "cmb.c2pa-provenance-assertion.v1",
  "framework": "Computational Metacognitive Bilingualism",
  "receipt_schema": "cmb.seal-receipt.v1",
  "manifest_sha256": "<receipt manifest digest>",
  "coverage": {
    "type": "explicit_file_set",
    "excludes_unlisted": true
  },
  "git": {
    "commit": "<full commit sha>",
    "status": "VERIFIED_ARTIFACTS_MATCH_COMMIT"
  },
  "evidence_boundary": {
    "integrity_is_authorship": false,
    "signature_is_originality": false,
    "provenance_is_legal_judgment": false
  }
}
```

The adapter should carry the **minimum necessary provenance facts**. Full unpublished text, private drafts, sensitive identity data, and unnecessary metadata should not be embedded by default.

## Data mapping

| CMB receipt field | C2PA-facing meaning |
|---|---|
| `receipt_schema` | identifies the CMB receipt format |
| `manifest_sha256` | binds the assertion to the CMB artifact-manifest digest |
| `coverage.paths` | optional artifact-set description; avoid embedding private paths |
| `coverage.excludes_unlisted` | clarifies exact scope |
| `manifest.git_commit` | optional hosted-source reference |
| `manifest.git_commit_status` | distinguishes byte-verified Git state from caller-supplied metadata |
| CMB invariants | declared framework metadata, not proof of compliance |
| authorship declaration | assertion by the signer, not independent proof of authorship |

## Implementation phases

### Phase 0 — documentation

- define the interoperability boundary;
- document C2PA as the external standard target;
- prohibit false conformance language.

**Status: implemented by this document.**

### Phase 1 — schema adapter

Add a deterministic function such as:

```python
payload = to_c2pa_assertion_payload(receipt)
```

Requirements:

- deterministic output;
- JSON Schema;
- no private data by default;
- explicit evidence-boundary fields;
- unit tests;
- no claim that the payload alone is a C2PA manifest.

### Phase 2 — SDK integration

Use an established C2PA implementation to embed the custom assertion into test assets.

Acceptance criteria:

- assertion survives round-trip validation;
- manifest remains valid after embedding;
- standard C2PA validators can inspect the resulting credential;
- CMB-specific fields do not break generic consumers.

### Phase 3 — independent validation

Ask an external reviewer with C2PA or content-authenticity experience to verify the integration and identify misuse of C2PA terminology.

### Phase 4 — conformance decision

Only after implementation and testing should the project decide whether formal C2PA conformance is appropriate for the relevant product role.

## Security and epistemic boundary

C2PA itself is a provenance/trust-signal system, not a universal truth oracle. CMB should preserve the same distinction:

```text
ASSERTION != TRUTH
SIGNATURE != AUTHORSHIP
VALID_CREDENTIAL != VALID_WORLD_CLAIM

PROVENANCE_SUPPORTS_JUDGMENT
PROVENANCE_DOES_NOT_REPLACE_JUDGMENT
```

## Recovery rule

If interoperability fails:

```text
DO NOT:
    silently downgrade verification
    rename a custom payload "C2PA"
    preserve a false conformance claim

DO:
    fail closed
    identify the incompatibility
    preserve the original CMB receipt
    record the failed mapping
    fix the adapter
    re-run validation
```
