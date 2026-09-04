# Project structure and maturity

CMB is easier to evaluate when its layers are separated.

## Stable engineering

These are the parts intended to behave like conventional software infrastructure:

```text
src/cmb_provenance/
schemas/
tests/
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
