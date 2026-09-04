# CMB Manifesto Library

This directory is the human navigation layer for the CMB creative corpus.

The files stay separate on purpose. A manifesto is allowed to have its own voice, metaphor, and artistic rules. This index supplies the map so readers do not have to discover that structure by accident.

> **Reading boundary:** metaphor is not mechanism, symbolism is not scientific classification, and a manifesto is not automatically a deployed technical control.

## Start with one path

| Reader | Recommended first artifact | Why |
|---|---|---|
| New to CMB | [CMB // The Sovereign Transmission](CMB_SOVEREIGN_TRANSMISSION.md) | Fast artistic entry into the thesis and visual language |
| Want the core philosophy | [../MANIFESTO.md](../MANIFESTO.md) | Foundational human-agency statement |
| Want the machine/library model | [CMB // The Unclassifiable Index](CMB_UNCLASSIFIABLE_INDEX.md) | MissingNo/Pokédex-inspired model for context, uncertainty, and provenance |
| Want epistemic triage / perfect-play logic | [HARMONI // Perfect-Play Epistemics](HARMONI_PERFECT_PLAY_EPISTEMICS.md) | Human/machine/axiom triangle, MissingNo Recovery gate, and evidence-bounded claims |
| Want CMB-Z13 | [CMB-Z13 Language Specification](CMB_Z13_LANGUAGE_SPEC.md) | Formal symbolic mapping and interpretation boundary |
| Want attention-economy critique | [Demon's Need Attention](DEMONS_NEED_ATTENTION_DNA.md) | Attention, engagement, profiling, and consent |
| Want literary allegory | [The Chicken Run Manifesto](DNA_CHICKEN_RUN_MANIFESTO.md) | Institutional and algorithmic confinement as story logic |
| Want the haunted archive branch | [The Unburned Signal Protocol](cmb-unburned-signal/MANIFESTO.md) | Memory, filtering, source, and reconstructable history |

## Library architecture

```text
FOUNDATION
  ../MANIFESTO.md
      │
      ├── TRANSMISSION
      │   └── CMB_SOVEREIGN_TRANSMISSION.md
      │
      ├── LIBRARY / INDEX THEORY
      │   └── CMB_UNCLASSIFIABLE_INDEX.md
      │
      ├── EPISTEMIC TRIAGE
      │   └── HARMONI_PERFECT_PLAY_EPISTEMICS.md
      │
      ├── SYMBOLIC COMPUTATION
      │   ├── CMB_Z13_MANIFESTO.md
      │   ├── CMB_Z13_LANGUAGE_SPEC.md
      │   └── CMB_Z13_ZODIAC_COMPUTATIONAL_LANGUAGE.md
      │
      ├── D.N.A. ALLEGORIES
      │   ├── DEMONS_NEED_ATTENTION_DNA.md
      │   └── DNA_CHICKEN_RUN_MANIFESTO.md
      │
      └── ARCHIVE / SIGNAL
          └── cmb-unburned-signal/
```

## Human layer and machine layer

Humans should use this page and the individual works.

Software should use:

- [../library/catalog.json](../library/catalog.json) for artifact discovery;
- [../schemas/cmb.library.catalog.v1.schema.json](../schemas/cmb.library.catalog.v1.schema.json) for catalog validation;
- [../library/cmb-z13.registry.json](../library/cmb-z13.registry.json) for the CMB-Z13 mapping;
- [../schemas/cmb.z13.ast.v1.schema.json](../schemas/cmb.z13.ast.v1.schema.json) for CMB-Z13 AST validation.

The machine-readable layer describes artifacts. It is not a license for a model to define a human being.

```text
CATALOG != CREATOR
INDEX != IDENTITY
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Provenance

Canonical artifacts are sealed by the repository's provenance tooling as an explicit file set. A receipt can provide integrity and chronology evidence for the bytes it covers. It does not independently prove originality, ownership, legal enforceability, or a person's internal meaning.

For the technical model, see [../README.md](../README.md) and [../receipts/README.md](../receipts/README.md).


## Sovereign Epistemic Protocol

- [The Sovereign Epistemic Protocol](THE_SOVEREIGN_EPISTEMIC_PROTOCOL.md) translates the HARMONI-666 human-machine boundary into a 6 x 6 x 6 operational manifesto. The normative implementation is [CMB-SEP-1](../spec/CMB-SEP-1.md).
