# GLITCH-IR-1

## Status

Experimental normative intermediate representation for Err⃝or⃟⃤GLITCHOLOGY / GLITCH-8 interoperability.

## 1. Purpose

GLITCH-IR-1 defines a small language-neutral contract for exchanging GLITCH-8 epistemic states without requiring another implementation to interpret decorative Unicode, FIGlet art, or host-language syntax.

~~~text
LANGUAGE != SEMANTICS
MEMORY_LAYOUT != MEANING
TRANSLATION != SEMANTIC_MUTATION
DISPLAY != IDENTIFIER
~~~

GLITCH-IR does not prove that a claim is true. It preserves the declared state and provenance boundary needed to compare independent implementations.

## 2. Canonical record

A GLITCH-IR/1 result MUST contain:

- `contract`: exactly `glitch-ir/1`;
- `vector`: stable conformance-vector identifier;
- `protocol`: stable GLITCH-8 protocol identifier;
- `operator`: stable operator identifier;
- `state`: normalized epistemic state;
- `verdict`: normalized outcome;
- `evidence`: an array of evidence references;
- `source`: source/provenance state;
- `witness`: witness/review state; and
- `human_review`: whether human review is required.

Implementations MAY retain richer local state, but that state MUST NOT silently change the canonical result.

## 3. Canonicalization

Before hashing, an implementation MUST:

1. validate against `schemas/glitch-ir.v1.schema.json`;
2. encode as UTF-8;
3. normalize all strings to Unicode NFC;
4. sort object keys lexicographically by Unicode code point;
5. preserve array order;
6. emit no insignificant whitespace;
7. encode booleans as JSON `true` or `false`;
8. reject non-finite numbers; and
9. append no trailing newline to the hashed byte sequence.

The digest is lowercase hexadecimal SHA-256 over those canonical bytes.

~~~text
SAME_CANONICAL_RESULT => SAME_RESULT_DIGEST
DIGEST_MATCH != TRUTH
~~~

A matching digest demonstrates deterministic agreement over the normalized result, not correctness of the underlying real-world claim.

## 4. GLT-8101 — Canonical Synchrony

`GLT-8101` / `GLITCH://CANONICAL_SYNCHRONY` is the composite protocol for comparing independent runtime implementations against the same GLITCH-IR vectors.

A conforming GLT-8101 run MUST:

1. load the same versioned vector;
2. execute the implementation independently;
3. project its result into GLITCH-IR/1;
4. canonicalize and hash the result;
5. compare the result with the vector oracle; and
6. report semantic drift rather than silently coercing a mismatch.

The reference runtime vocabulary is:

| Tag | Runtime |
| --- | --- |
| `PY` | Python |
| `GO` | Go |
| `RS` | Rust |
| `TS` | TypeScript |
| `CL` | Common Lisp |
| `HS` | Haskell |
| `PL` | Prolog |
| `CPP` | C++20 |
| `G8` | GLITCH-8 reference layer |

`C` remains reserved for genuine C implementations and MUST NOT be used as an alias for C++.

## 5. Semantic drift

A mismatch MUST be represented as a conformance failure, not as an alternative truth.

~~~text
GLITCH://SEMANTIC_DRIFT
EXPECTED: 8 / 8
OBSERVED: N / 8

SYNTAX_DIVERGENCE != PERMITTED_SEMANTIC_MUTATION
~~~

Conformance tooling SHOULD identify the runtime, vector, expected canonical result, received canonical result, and both digests.

## 6. Localization

Human-facing labels MAY be localized. Stable protocol IDs, operator IDs, states, verdicts, schema identifiers, and runtime tags MUST NOT be translated.

~~~text
LOCALIZED_LABEL != CANONICAL_IDENTIFIER
~~~

## 7. Authority boundary

GLITCH-IR conformance is an interoperability result. It is not independent certification, legal proof, scientific validation, or machine authority over a person.

~~~text
CONFORMANCE != CERTIFICATION
HASH != TRUTH
PROFILE != PERSON
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## 8. Recovery

When an implementation cannot validate, normalize, or reproduce a vector, it MUST fail closed for that conformance claim and preserve enough diagnostic information to backtrace the divergence.

~~~text
FAILURE != TERMINATION
RETRY != ERASURE
RECOVERY > PROPAGATION
~~~
