# Project structure and maturity

CMB is easier to evaluate when its layers are separated.

## Stable engineering

These are the parts intended to behave like conventional software infrastructure:

```text
src/cmb_provenance/
schemas/
tests/
conformance/
adapters/
scripts/
.github/workflows/
RELEASE.md
SECURITY.md
```

The stable engineering contract is correctness, reproducibility, bounded claims, Recovery behavior, and tests.

## Experimental research

These are implemented but still exploratory:

```text
cmb-z13 reference parser
CMB-Z13 notation
Guardian Modes teaching layer
cmb-edu parser, CLI, child-facing curriculum, and privacy-first context envelope
C2PA entity-specific assertion integration beyond the test round-trip
```

Experimental does not mean meaningless; it means compatibility and semantics may still evolve with versioned changes and evidence.

## Art / canon / policy

These are authored cultural, philosophical, educational, and policy materials:

```text
manifestos/
policy/
library/
```

A canonical artifact may be important to CMB's authored history without being a stable software API.

## Boundary rule

```text
METAPHOR != SECURITY_CONTROL
POLICY != ENFORCEMENT
TEST != LEGAL_PROOF
ARTIFACT_STATUS != HUMAN_IDENTITY
```

Moving a claim between maturity layers requires an explicit change, evidence, and versioning.


## Platform layer additions

- `src/cmb_provenance/boundary.py` - explicit policy-boundary evaluator with deterministic machine-readable rejection codes.
- `schemas/cmb.boundary-event.v1.schema.json` - cross-language event contract for boundary adapters.
- `schemas/cmb.library.catalog.v1.schema.json` - strict validation contract for the digital-library catalog.
- `docs/playground/index.html` - zero-dependency interactive browser front door.
- `manifestos/README.md` - human-readable map of the manifesto corpus.
- `examples/06_fastapi_boundary` - reference integration using server-supplied policy facts.

These components intentionally separate symbolic meaning from executable enforcement.

## CMB-EDU educational layer

- `src/cmb_edu/` - experimental parser and installed `cmb-edu` CLI.
- `schemas/cmb.edu.v1.schema.json` - strict Metacognitive Context Envelope contract.
- `docs/CMB_EDU_KIDS.md` - child-facing Flamingoglyph computational-literacy curriculum.
- `examples/07_cmb_edu` - minimal parse/validate example.
- `tests/test_cmb_edu*.py` - parser, privacy, schema, and CLI regression tests.

CMB-EDU stores the epistemic source of context explicitly: `human_declared`
does not become `machine_inferred`. Its privacy fields are declarations that
integrating applications must actually enforce.


## Polyglot boundary layer

- `conformance/boundary.v1.cases.json` - language-neutral semantic fixtures.
- `adapters/typescript-express` - strict TypeScript parser, evaluator, and Express endpoint.
- `adapters/rust-actix` - strict Rust evaluator, Serde input contract, and Actix endpoint.
- `.github/workflows/polyglot-conformance.yml` - hosted TypeScript and Rust build/conformance gate.

The Python implementation remains the reference engine. The adapters are compatible only insofar as they keep passing the shared fixtures.
