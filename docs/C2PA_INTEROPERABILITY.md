# CMB Provenance ↔ C2PA Interoperability Plan

**Status:** Phase 2 test round-trip implemented; not a claim of C2PA conformance  
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

These capabilities are useful, but they do **not** make the tool a C2PA implementation. The repository now also contains a deterministic Phase 1 adapter that exports a privacy-minimized payload body for eventual use inside an entity-specific C2PA assertion.

## What C2PA adds

C2PA provides standardized machinery for:

- asset-bound provenance assertions;
- signed claims;
- claim signatures;
- Content Credentials;
- manifest storage and validation;
- a conformance ecosystem.

C2PA supports entity-specific/custom assertions. That creates a possible bridge for CMB-specific metadata without reimplementing the surrounding provenance standard. C2PA entity-specific assertion labels are namespaced by an Internet domain controlled by the asserting entity; this project therefore does **not** invent or reserve a C2PA assertion label before such a namespace is established.

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

## Implemented Phase 1 payload

The repository now exposes:

```python
from cmb_provenance import to_c2pa_assertion_payload

payload = to_c2pa_assertion_payload(receipt)
```

and:

```bash
cmb-provenance export-c2pa-payload \
  --receipt cmb-source.cmb-receipt.json \
  --output cmb-c2pa-payload.json
```

The payload uses schema `cmb.c2pa-assertion-payload.v1`. By default, artifact paths are omitted and only the artifact count, exact-coverage semantics, manifest digest, Git commit metadata, and evidence-boundary fields are exported. Paths require explicit `--include-paths` opt-in.

The JSON Schema is:

```text
schemas/cmb.c2pa-assertion-payload.v1.schema.json
```

The adapter deliberately does **not** output a C2PA assertion label. C2PA entity-specific labels require a namespace based on a domain controlled by the asserting entity; inventing one would be false interoperability.

The adapter also hard-codes the following boundary:

```text
payload_is_c2pa_manifest = false
payload_is_content_credential = false
project_claims_c2pa_conformance = false
requires_external_c2pa_tooling = true
```

Full unpublished text, private drafts, sensitive identity data, and unnecessary metadata are not embedded by default.

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

### Phase 0 ✦ documentation

- define the interoperability boundary;
- document C2PA as the external standard target;
- prohibit false conformance language.

**Status: implemented by this document.**

### Phase 1 ✦ schema adapter

**Status: implemented.**

Implemented controls:

- deterministic canonical JSON output;
- public JSON Schema;
- artifact paths omitted by default;
- explicit evidence-boundary fields;
- deterministic fixtures and unit tests;
- CLI export;
- no invented entity-specific C2PA namespace;
- no claim that the payload is a C2PA manifest or Content Credential.

### Phase 2 ✦ SDK integration

**Status: implemented as a CI integration test.**

The repository pins the external CAI/C2PA `c2patool` binary, verifies its published SHA-256 digest before installation, generates a deterministic PNG test asset, builds a manifest definition around the CMB payload, signs and binds that manifest with c2patool's development signer, reads the resulting asset back with generic c2patool, and verifies that the exact CMB payload survived the round trip.

The integration uses the reserved documentation namespace `com.example.cmb_provenance` **only in tests**. Production manifest generation rejects example.com/.net/.org namespaces by default and requires the caller to provide an entity-specific reverse-domain label.

Acceptance criteria now enforced in CI:

- the external C2PA tool can build and bind the manifest;
- the signed test asset can be read back by generic c2patool;
- the assertion label is visible to the generic reader;
- the exact deterministic CMB payload survives the round trip;
- CMB-specific fields do not require a CMB reader to be exposed;
- the development test credential is not represented as trusted production identity or formal C2PA conformance.

### Phase 2 limitations

The CI round trip is an interoperability test, not a production trust claim. It uses c2patool's development signer and a reserved example namespace. A production deployment still needs:

- a domain-controlled assertion namespace;
- an appropriate production signer and certificate strategy;
- a trust-list/conformance decision appropriate to the deployment;
- external review of the integration and terminology.

### Phase 3 ✦ independent validation

Ask an external reviewer with C2PA or content-authenticity experience to verify the integration and identify misuse of C2PA terminology.

### Phase 4 ✦ conformance decision

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
