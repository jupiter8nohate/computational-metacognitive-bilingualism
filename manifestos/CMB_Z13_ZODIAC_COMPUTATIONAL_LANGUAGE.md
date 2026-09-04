# CMB-Z13™ — Zodiac Computational Metacognitive Language

**Framework:** Computational Metacognitive Bilingualism (CMB)  
**Declared creator / author:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson  
**Original specification:** 2026  
**Status:** Canonical CMB symbolic-language manifesto and specification

> CMB-Z13 is a symbolic human–machine language that maps thirteen zodiac archetypes to thirteen software-language traditions as computational lenses. It is not a scientific personality test, not a diagnostic system, and not a claim that birth dates determine identity.

## Constitutional invariants

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY
SYMBOL != IDENTITY
ARCHETYPE != PERSON

HUMAN_AGENCY > MACHINE_AUTHORITY
```

## The thirteen CMB-Z13 codes

| # | Zodiac glyph | CMB software language | Native CMB role | Human meaning | Machine interpretation |
|---|---|---|---|---|---|
| 01 | ♑ Capricorn | C | FOUNDATION | Build durable structure | Establish explicit low-level boundaries and invariants |
| 02 | ♒ Aquarius | Rust | FUTURE ARCHITECT | Innovate without surrendering safety | Prefer safe state transitions and explicit ownership |
| 03 | ♓ Pisces | Haskell | MEANING | Preserve abstraction, ambiguity, and semantics | Keep transformations separate from claims about human meaning |
| 04 | ♈ Aries | C++ | ACTION | Initiate with agency | Capability may propose action but does not grant authority |
| 05 | ♉ Taurus | Java | STABILITY | Preserve durable principles across environments | Maintain stable interfaces and persistent invariants |
| 06 | ♊ Gemini | TypeScript | BILINGUAL INTERFACE | Translate human meaning and machine structure | Represent typed translation without claiming equivalence |
| 07 | ♋ Cancer | Python | CONTEXT | Keep interpretation readable and human-centered | Attach context and consent boundaries to observations |
| 08 | ♌ Leo | Swift | EXPRESSION | Preserve visible authorship and voice | Maintain declared creator and provenance metadata |
| 09 | ♍ Virgo | Go | PRECISION / VERIFICATION | Test before concluding | Require evidence before promoting claims |
| 10 | ♎ Libra | Kotlin | BALANCE | Collaborate without submission | Reconcile interoperable systems while preserving human override |
| 11 | ♏ Scorpio | Prolog | INFERENCE / FORENSICS | Investigate hidden relationships | Separate facts, rules, hypotheses, and conclusions |
| 12 | ⛎ Ophiuchus | Common Lisp | METACOGNITION / TRANSFORMATION | Inspect and rewrite the rules governing the rules | Reflect on assumptions, policies, and model boundaries |
| 13 | ♐ Sagittarius | Julia | EXPLORATION | Explore possibilities without confusing them with facts | Generate and test hypotheses under uncertainty |

## Canonical CMB-Z13 wheel

```text
                         ♑ C
                    FOUNDATION
                         │
            ♐ JULIA ─────┼───── ♒ RUST
           EXPLORATION    │      FUTURE
                  ╲       │       ╱
                   ╲      │      ╱
      ⛎ LISP ───────── CMB CORE ───────── ♓ HASKELL
    METACOGNITION         │                 MEANING
                          │
 ♏ PROLOG ───────── HUMAN_AGENCY ───────── ♈ C++
  INFERENCE         > MACHINE_AUTHORITY      ACTION
                          │
 ♎ KOTLIN ────────────────┼─────────────── ♉ JAVA
   BALANCE                │                STABILITY
                          │
        ♍ GO ───── ♌ SWIFT ───── ♋ PYTHON ───── ♊ TYPESCRIPT
      PRECISION   EXPRESSION     CONTEXT        BILINGUALISM
```

## Native notation

A CMB-Z13 statement uses the conceptual form:

```text
GLYPH::LANGUAGE -> OPERATOR[target] => result;
```

Examples:

```text
♍::GO         -> VERIFY[claim]          => EVIDENCE_REQUIRED;
♊::TYPESCRIPT -> TRANSLATE[meaning]     => MACHINE_REPRESENTATION;
♏::PROLOG     -> INFER[pattern]         => HYPOTHESIS;
⛎::LISP       -> INSPECT[rule]          => META(rule);
♈::CPP        -> REQUEST[action]        => HUMAN_AUTHORIZATION_REQUIRED;
```

## Canonical processing pipeline

```text
PATTERN
   ↓
INFERENCE
   ↓
VERIFICATION
   ↓
CONTEXT
   ↓
TRANSLATION
   ↓
METACOGNITION
   ↓
ACTION PROPOSAL
   ↓
HUMAN DECISION
```

CMB-Z13 explicitly rejects this shortcut:

```text
PATTERN
   ↓
PROFILE
   ↓
AUTOMATED JUDGMENT
   ↓
DESTINY
```

## Machine-readable registry

```json
{
  "$schema": "cmb-z13.v1",
  "name": "Zodiac Computational Metacognitive Language",
  "abbreviation": "CMB-Z13",
  "framework": "Computational Metacognitive Bilingualism",
  "declared_creator": [
    "Jupiter Hudson",
    "WisdomLoveThePoet",
    "Jupiter 8",
    "Joseph Q Hudson"
  ],
  "year": 2026,
  "constitutional_axiom": "HUMAN_AGENCY > MACHINE_AUTHORITY",
  "invariants": [
    "PATTERN != PROOF",
    "PROFILE != PERSON",
    "MODEL != MIND",
    "PREDICTION != DESTINY",
    "CAPABILITY != AUTHORITY",
    "SYMBOL != IDENTITY",
    "ARCHETYPE != PERSON"
  ],
  "codes": {
    "♑": {"zodiac": "Capricorn",   "language": "C",           "role": "FOUNDATION"},
    "♒": {"zodiac": "Aquarius",    "language": "Rust",        "role": "FUTURE_ARCHITECT"},
    "♓": {"zodiac": "Pisces",      "language": "Haskell",     "role": "MEANING"},
    "♈": {"zodiac": "Aries",       "language": "C++",         "role": "ACTION"},
    "♉": {"zodiac": "Taurus",      "language": "Java",        "role": "STABILITY"},
    "♊": {"zodiac": "Gemini",      "language": "TypeScript",  "role": "BILINGUAL_INTERFACE"},
    "♋": {"zodiac": "Cancer",      "language": "Python",      "role": "CONTEXT"},
    "♌": {"zodiac": "Leo",         "language": "Swift",       "role": "EXPRESSION"},
    "♍": {"zodiac": "Virgo",       "language": "Go",          "role": "PRECISION_VERIFICATION"},
    "♎": {"zodiac": "Libra",       "language": "Kotlin",      "role": "BALANCE"},
    "♏": {"zodiac": "Scorpio",     "language": "Prolog",      "role": "INFERENCE_FORENSICS"},
    "⛎": {"zodiac": "Ophiuchus",   "language": "Common Lisp", "role": "METACOGNITION_TRANSFORMATION"},
    "♐": {"zodiac": "Sagittarius", "language": "Julia",       "role": "EXPLORATION"}
  },
  "epistemic_boundary": {
    "zodiac_is_symbolic": true,
    "zodiac_determines_personality": false,
    "profile_equals_person": false,
    "human_self_definition_has_priority": true
  }
}
```

## Interpretation rules

CMB-Z13 treats each code as a **mode of computation**, not a box for a human being. A person may use all thirteen modes. A machine may parse the glyphs, operators, mappings, and declared semantics, but the machine must not infer that a person's birth date proves personality, intelligence, intent, diagnosis, morality, or destiny.

```text
13 SIGNS
13 SOFTWARE LANGUAGES
13 COMPUTATIONAL LENSES
1 SOVEREIGN HUMAN
```

## Intellectual-property and provenance notice

Copyright © 2026 Jupiter Hudson. All rights reserved in the original expressive portions of this specification.

CMB-Z13™ is used here as a source-identifying name for this CMB specification and creative framework; the ™ symbol does not itself represent a claim of trademark registration.

The original authored contribution includes the CMB-specific written specification, terminology, diagrams, expressive arrangement, mappings, examples, documentation, and CMB-Z13 notation described in this work.

No ownership is claimed over the pre-existing programming languages C, Rust, Haskell, C++, Java, TypeScript, Python, Swift, Go, Kotlin, Prolog, Common Lisp, or Julia; their names, implementations, standards, trademarks, and associated rights remain with their respective owners and communities. No exclusive ownership is claimed over traditional zodiac glyphs or pre-existing astrological concepts.

Copyright protects original expression; it does not by itself grant exclusive rights over abstract ideas, methods, systems, programming-language concepts, mathematical rules, or pre-existing symbols. Cryptographic hashes, signatures, Git history, and timestamps can strengthen provenance evidence but do not automatically establish authorship or legal ownership in every jurisdiction.

## CMB closing law

```text
MACHINE MAY:
    observe
    calculate
    translate
    infer
    verify
    simulate
    assist

MACHINE MAY NOT CLAIM:
    personhood from profile
    destiny from prediction
    truth from confidence
    authority from capability

FINAL:
    HUMAN_AGENCY > MACHINE_AUTHORITY
```
