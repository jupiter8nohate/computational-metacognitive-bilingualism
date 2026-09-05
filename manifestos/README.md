# CMB Manifesto Library

This directory is the human navigation layer for the CMB creative corpus.

The files stay separate on purpose. A manifesto is allowed to have its own voice, metaphor, and artistic rules. This index supplies the map so readers do not have to discover that structure by accident.

> **Reading boundary:** metaphor is not mechanism, symbolism is not scientific classification, and a manifesto is not automatically a deployed technical control.

> **Featured prophecy boundary:** *The Prophecy of the Question Mark* is deliberate 2030 speculative worldbuilding, not a claim that its events are guaranteed to occur.

## Start with one path

| Reader | Recommended first artifact | Why |
|---|---|---|
| New to CMB | [CMB // The Sovereign Transmission](CMB_SOVEREIGN_TRANSMISSION.md) | Fast artistic entry into the thesis and visual language |
| Want the core philosophy | [../MANIFESTO.md](../MANIFESTO.md) | Foundational human-agency statement |
| Want the motto and mission in code-poetry | [Reclaiming the Pen](RECLAIMING_THE_PEN_EIGHT_LANGUAGES.md) | Eight-language manifesto for authorship, meaning, consent, and cognitive sovereignty |
| Want the machine/library model | [CMB // The Unclassifiable Index](CMB_UNCLASSIFIABLE_INDEX.md) | MissingNo/Pokédex-inspired model for context, uncertainty, and provenance |
| Want epistemic triage / perfect-play logic | [HARMONI // Perfect-Play Epistemics](HARMONI_PERFECT_PLAY_EPISTEMICS.md) | Human/machine/axiom triangle, MissingNo Recovery gate, and evidence-bounded claims |
| Want CMB-Z13 | [CMB-Z13 Language Specification](CMB_Z13_LANGUAGE_SPEC.md) | Formal symbolic mapping and interpretation boundary |
| Want attention-economy critique | [Demon's Need Attention](DEMONS_NEED_ATTENTION_DNA.md) | Attention, engagement, profiling, and consent |
| Want the featured haunting prophecy | [The Prophecy of the Question Mark // 2030](DNA_PROPHECY_QUESTION_MARK_2030.md) | Scroll 666: speculative AI authority, uncertainty, recursive attention, accountability, and human sovereignty |
| Want literary allegory | [The Chicken Run Manifesto](DNA_CHICKEN_RUN_MANIFESTO.md) | Institutional and algorithmic confinement as story logic |
| Want the haunted archive branch | [The Unburned Signal Protocol](cmb-unburned-signal/MANIFESTO.md) | Memory, filtering, source, and reconstructable history |

## Library architecture

```text
FOUNDATION
  ../MANIFESTO.md
      │
      ├── RECLAIMING THE PEN
      │   └── RECLAIMING_THE_PEN_EIGHT_LANGUAGES.md
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
      ├── D.N.A. ALLEGORIES / PROPHECY
      │   ├── DEMONS_NEED_ATTENTION_DNA.md
      │   ├── DNA_PROPHECY_QUESTION_MARK_2030.md  ← FEATURED HAUNTING
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
