# GLITCH-IR-1

## Status

Experimental normative interoperability contract for Err⃝or⃟⃤GLITCHOLOGY / GLITCH-8.

## 1. Purpose

GLITCH-IR-1 defines a language-neutral semantic representation beneath the human-facing
GLITCHOLOGY visual layer. Its purpose is to let independent implementations preserve the
same meaning without requiring identical syntax, binaries, memory layouts, compilers, or
runtime behavior.

~~~text
ART != PROTOCOL
GLYPH != IDENTIFIER
LANGUAGE != MEANING
MEMORY_LAYOUT != SEMANTIC_STATE
TRANSLATION != SEMANTIC_MUTATION
~~~

The FIGlet 3D Diagonal presentation is a human-facing rendering layer. Machine-facing
identifiers and exchange objects remain plain UTF-8 text.

## 2. Canonical synchrony

GLT-8101 // GLITCH://CANONICAL_SYNCHRONY is the conformance state in which independent
language implementations evaluate the same canonical semantic vector and produce the same
canonical semantic result.

~~~text
8 IMPLEMENTATIONS
        ↓
1 CANONICAL CONTRACT
        ↓
8 INDEPENDENT VERDICTS
        ↓
1 CANONICAL RESULT
        ↓
1 RESULT DIGEST
~~~

Canonical synchrony does not require identical memory addresses, compiler output, process
state, instruction sequences, or binary representations.

## 3. Required semantic fields

A GLITCH-IR v1 vector MUST identify:

- schema version;
- protocol and protocol version;
- vector identifier;
- GLITCH-8 registry identifier;
- canonical protocol name;
- claim verification-label state;
- evidence state;
- source state;
- human-review state;
- expected verdict, operator, and semantic state;
- applicable invariants.

Unknown fields MUST be rejected by strict schema validators unless a later protocol version
explicitly defines an extension mechanism.

## 4. GLT-8101 reference rule

For the canonical GLT-8101-V001 vector:

~~~text
verification_label = PRESENT
evidence           = ABSENT
source             = UNKNOWN
human_review       = REQUIRED
~~~

A conforming semantic engine MUST return:

~~~text
verdict  = BACKTRACE
operator = GLT-0036
state    = CONTESTED
~~~

This rule operationalizes:

~~~text
VERIFIED_LABEL != VERIFIED_TRUTH
LABEL != EVIDENCE
SIGNAL != SOURCE
PATTERN != PROOF
~~~

## 5. Canonical result serialization

The v1 conformance result is serialized as exactly five UTF-8 fields joined by ASCII `|`
with one trailing LF:

~~~text
VECTOR_ID|PROTOCOL_VERSION|VERDICT|OPERATOR|STATE\n
~~~

For GLT-8101-V001:

~~~text
GLT-8101-V001|1.0.0|BACKTRACE|GLT-0036|CONTESTED
~~~

Implementations MUST emit no additional stdout when running the conformance vector.
Diagnostic information MAY be emitted to stderr.

The SHA-256 digest used by the conformance harness is computed over the exact UTF-8 bytes
of this canonical result including the trailing LF.

~~~text
SAME_CANONICAL_RESULT => SAME_RESULT_DIGEST
SAME_RESULT_DIGEST != PROOF_OF_REAL_WORLD_TRUTH
~~~

A matching digest proves equality of the canonical result bytes only.

## 6. Canonical input projection

The normative machine envelope is JSON and MUST validate against
`schemas/glitch-ir.v1.schema.json`.

The eight-language test bench also consumes a deterministic UTF-8 key/value projection
stored beside the JSON fixture. The projection exists to keep the semantic engines free of
third-party JSON dependencies. Tests MUST verify that the projection matches the normative
JSON fixture before comparing language verdicts.

~~~text
TRANSPORT_PARSER != SEMANTIC_ENGINE
PROJECTION != SECOND_SOURCE_OF_TRUTH
JSON_FIXTURE = NORMATIVE_INPUT
~~~

## 7. Runtime tags

The canonical GLT-8101 language set is:

~~~text
PY   Python
GO   Go
RS   Rust
TS   TypeScript
CL   Common Lisp
HS   Haskell
PL   Prolog
CPP  C++20
~~~

`G8` remains the GLITCH-8 semantic layer. Existing runtime tags remain valid where
defined by GLITCH-8.

## 8. Unicode and localization

Protocol identifiers MUST remain untranslated. Human descriptions MAY be localized.

Implementations MUST preserve UTF-8. Human-facing decorated strings SHOULD provide a plain
identifier or semantic key. GLITCH-IR does not require a model to infer meaning from
decorative Unicode.

~~~text
DISPLAY != IDENTIFIER
DECORATION != SEMANTIC_MUTATION
LOCALIZATION != IDENTIFIER_MUTATION
~~~

## 9. Conformance

A GLITCH-IR-1 implementation claiming GLT-8101 conformance MUST:

1. identify protocol version 1.0.0;
2. consume the canonical vector;
3. evaluate it independently;
4. emit the canonical result format;
5. match the expected semantic result;
6. match the canonical result bytes produced by every other conforming engine in the test;
7. avoid claiming external or independent certification unless such certification exists.

A CI pass demonstrates repository conformance for the tested code and fixtures. It does not
establish universal interoperability with every AI system, legal enforceability, AGI/ASI
behavior, or correctness of claims outside the protocol.

## 10. Recovery

If one implementation diverges, the harness MUST fail and identify the runtime that drifted.

~~~text
GLITCH://SEMANTIC_DRIFT

EXPECTED: 8 / 8
OBSERVED: N / 8

DIVERGENCE != COLLAPSE
FAILURE != TERMINATION
BACKTRACE -> REPAIR -> RETEST
~~~
