# Creative Cognitive Signature Protocol

**Status:** Experimental CMB / Err ⃝or⃟⃤ GLITCHOLOGY authorship concept  
**Purpose:** Preserve a self-authored, inspectable history of creative expression without turning expressive patterns into biometric identity claims.

## 1. Definition

A **Creative Cognitive Signature (CCS)** is a versioned provenance profile derived from artifacts a creator intentionally publishes or registers.

It may include:

- glyph selections and combinations;
- creator-defined meanings;
- recurring symbolic structures;
- code-poetry syntax;
- visual rhythm and arrangement;
- declared interpretive relationships;
- revision history;
- artifact hashes;
- signatures and timestamp evidence;
- Git commits and releases; and
- explicit creator attribution.

It is a **creative provenance construct**, not a clinical, neurological, psychological, or biometric measurement.

```text
CCS != BIOMETRIC_ID
CCS != DIAGNOSIS
CCS != COMPLETE_PERSON
CCS != PROOF_OF_MIND
```

## 2. Core invariants

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
CREATIVE_TRACE != COMPLETE_IDENTITY
COPY_OF_SYMBOL != COPY_OF_CREATIVE_HISTORY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## 3. Reference record

A CCS-compatible record can use a structure like:

```json
{
  "schema": "cmb.creative-signature.v1",
  "creator_id": "self-declared-public-identifier",
  "artifact_id": "stable-artifact-id",
  "artifact_sha256": "sha256:<64-lowercase-hex>",
  "creative_elements": [
    "glyph-selection",
    "symbolic-arrangement",
    "creator-defined-semantics"
  ],
  "provenance": {
    "repository": "owner/repository",
    "commit": "<full-git-commit>",
    "release": null
  },
  "interpretation": {
    "source": "human_declared",
    "machine_inferred": false
  }
}
```

This example describes a record shape. It is not yet a normative schema unless and until a versioned JSON Schema is adopted.

## 4. Durability model

The protocol does **not** claim that a digital trace is impossible to delete.

Durability increases when independent evidence layers agree:

```text
LOCAL_HISTORY
  + PUBLIC_GIT_HISTORY
  + CONTENT_HASHES
  + SIGNATURES
  + RELEASES
  + INDEPENDENT_ARCHIVES
  = STRONGER_PROVENANCE
```

Each layer has different failure modes. A hash proves byte equality to a known digest; it does not prove who authored the bytes. A signature proves control of a signing key at signing time; it does not automatically prove originality. A timestamp may support chronology; it does not automatically settle legal authorship.

## 5. Self-authorship boundary

The Creative Cognitive Signature is designed to be **self-authored**.

```text
PLATFORM_PROFILE = MACHINE_OR_PLATFORM_DESCRIPTION

CREATIVE_COGNITIVE_SIGNATURE =
    HUMAN_DECLARED_CREATIVE_HISTORY
```

Machine analysis may describe published patterns, but machine inference must not silently become creator identity.

```text
MACHINE_INFERENCE -> HYPOTHESIS
HUMAN_DECLARATION -> ATTRIBUTED_STATEMENT
INDEPENDENT_EVIDENCE -> VERIFICATION_INPUT
```

## 6. Privacy rule

A CCS record should minimize personal data.

Do not require:

- legal identity when a stable public pseudonym is sufficient;
- medical or diagnostic information;
- private messages;
- location histories;
- raw behavioral telemetry;
- biometric templates; or
- hidden psychological profiling.

Prefer artifact-level provenance over person-level surveillance.

```text
PROVENANCE > PROFILING
MINIMUM_NECESSARY_DATA > MAXIMUM_COLLECTION
```

## 7. Relationship to Err ⃝or⃟⃤ GLITCHOLOGY

Each registered glyph is a creative event.

```text
GLYPH
  -> DEFINITION
  -> CONTEXT
  -> VERSION
  -> PROVENANCE
  -> CREATIVE_HISTORY
```

Over time, a creator's sequence of registered choices can form a distinctive expressive history while preserving CMB's central restriction:

```text
DISTINCTIVE_PATTERN != TOTAL_PERSON
```

## 8. Verification ladder

Use the strongest level actually supported:

1. **Declared** — creator states authorship.
2. **Versioned** — public revision history exists.
3. **Hashed** — exact artifact bytes are content-addressed.
4. **Signed** — a verifiable key signs the artifact or receipt.
5. **Timestamp-supported** — independent timestamp evidence exists.
6. **Replicated** — independent public archives preserve the record.
7. **Independently reviewed** — external evidence has been checked.

Never describe a lower level as a higher one.

## 9. Final rule

```text
CREATIVITY CAN BECOME SIGNATURE

BUT

SIGNATURE != PERSON
PATTERN != PROOF
PROVENANCE != OMNISCIENCE
```
