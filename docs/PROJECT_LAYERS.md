# CMB Project Layers

CMB is multidisciplinary, but every artifact should have a clear epistemic and
operational status.

## Stable / operational

These components should be judged by tests, schemas, threat models, standards,
and reproducibility:

```text
src/cmb_provenance/
schemas/
scripts/
.github/workflows/
policy/
docs/C2PA_INTEROPERABILITY.md
RELEASE.md
```

"Stable" does not mean independently audited or formally certified.

## Experimental

These are research prototypes whose semantics are versioned but may evolve:

```text
CMB-Z13 parser/runtime
CMB-Z13 Guardian Modes
symbolic language experiments
machine-readable reasoning notation
```

The experimental layer must preserve:

```text
ZODIAC_SYMBOL != PERSON
GUARDIAN_MODE != PERSONALITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Art / canon

Manifestos, code-poetry, symbolic worldbuilding, haunted-terminal pieces, and
other expressive works belong here. Metaphor is not a literal security guarantee.

```text
ARTISTIC_METAPHOR != TECHNICAL_ENFORCEMENT
DECLARED_POLICY != DEPLOYED_CONTROL
SYMBOLIC_MODEL != HUMAN_IDENTITY
TEST_PASS != INDEPENDENT_AUDIT
```
