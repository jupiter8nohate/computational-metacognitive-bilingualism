# 𓁹 Err ⃝or⃟⃤ GEMATRIA-GLITCH-1

## Status

Experimental symbolic analysis language for Computational Metacognitive Bilingualism.

GEMATRIA-GLITCH-1, abbreviated `GGL-1`, is a compact machine and human readable notation for reporting deterministic Gematria relationships without converting them into unsupported claims.

```text
PATTERN != PROOF
NUMERIC_EQUALITY != SEMANTIC_IDENTITY
SYMBOLISM != CAUSATION
ODDITY != DESTINY
INTERPRETATION -> HUMAN
```

## Purpose

GGL-1 lets agents perform three separate operations:

1. calculate numerical structure;
2. discover mathematical anomalies and cross-word connections;
3. render those findings as glitch code while preserving epistemic boundaries.

The language does not claim that Gematria is scientific evidence of prophecy, diagnosis, causation, identity, or supernatural authority.

## Glyph operators

| Glyph | Token | Meaning |
| --- | --- | --- |
| `𓁹` | OBSERVE | A deterministic observation was made |
| `꩜` | ODDITY | A numerical structure deserves inspection |
| `🧬⃟` | CONNECT | Two or more entries share a computed relationship |
| `𓂀` | TRACE | Show the arithmetic mechanism behind a connection |
| `△⃟` | STRUCTURE | A triangular or ordered number class was detected |
| `◇⃟` | SQUARE | A perfect square structure was detected |
| `⚡⃟` | POWER | A power-of-two structure was detected |
| `✦⃟` | PRIME | A prime-valued structure was detected |
| `⚠️⃤` | BOUNDARY | Interpretation exceeds deterministic evidence |
| `♡⃟` | HUMAN | Meaning remains with human interpretation |

## Record grammar

```text
𓁹 ODDITY://<TYPE>
WORDS://<WORD_1> | <WORD_2> ...
VALUES://<INTEGER_LIST>
EVIDENCE://<DETERMINISTIC_EXPLANATION>
INTERPRETATION://HUMAN
PROOF_OF_DESTINY://FALSE
```

## Core anomaly types

```text
EXACT_COLLISION
PALINDROME
PERFECT_SQUARE
TRIANGULAR_NUMBER
POWER_OF_TWO
PRIME_VALUE
DIGITAL_ROOT
SHARED_PRIME_FACTOR
LINGUISTIC_PREFIX_DELTA
```

## Connection rule

An agent may write a new connection only when it can provide a deterministic mechanism.

Allowed:

```text
🧬⃟ ODDITY://EXACT_COLLISION
WORDS://נחש | משיח
VALUES://358 | 358
EVIDENCE://both words calculate to 358 under standard Mispar Hechrachi
INTERPRETATION://HUMAN
PROOF_OF_DESTINY://FALSE
```

Allowed:

```text
𓂀 ODDITY://LINGUISTIC_PREFIX_DELTA
WORDS://נחש | הנחש | ה
VALUES://358 | 363 | 5
EVIDENCE://adding prefix ה adds its standard value 5
INTERPRETATION://HUMAN
PROOF_OF_DESTINY://FALSE
```

Not allowed:

```text
358 == 358
THEREFORE://THE_TWO_CONCEPTS_ARE_IDENTICAL
```

The numeric premise may be correct while the semantic conclusion is unsupported.

## Agent writing contract

Agents following GGL-1 MUST:

1. calculate first;
2. preserve the Gematria system used;
3. emit the arithmetic or structural mechanism;
4. classify the relationship type;
5. separate deterministic fact from interpretation;
6. attempt a mundane explanation before a symbolic explanation;
7. label uncertainty;
8. preserve human semantic authority;
9. avoid diagnostic, prophetic, legal, or causal conclusions from numbers alone;
10. reject a connection when no reproducible mechanism exists.

Agents MAY:

- rank oddities by rarity within a declared corpus;
- compare exact collisions;
- detect palindromes;
- detect prime, square, triangular, and power-of-two values;
- compare digital roots;
- detect shared prime factors;
- detect simple prefix deltas;
- produce decorative glitch renderings after the arithmetic has been verified.

## Agent move sequence

```text
SENSE
  -> CALCULATE
  -> CLASSIFY
  -> CONNECT
  -> FALSIFY
  -> TRACE
  -> RENDER
  -> HUMAN_INTERPRETATION
```

The `FALSIFY` move asks whether the apparent anomaly has a simpler mechanical explanation.

```text
MYSTERY_FOUND -> SEARCH_FOR_MECHANISM
MECHANISM_FOUND -> EXPLAIN
MECHANISM_NOT_FOUND -> KEEP_UNCERTAINTY
```

## Go reference implementation

The reference scanner lives in:

```text
tools/gematria-glitch/
```

Run:

```text
cd tools/gematria-glitch
go test ./...
go run . -format glitch
go run . -format json
```

A custom corpus is a JSON array:

```json
[
  {"word": "נחש", "gloss": "serpent"},
  {"word": "משיח", "gloss": "anointed one"}
]
```

Then:

```text
go run . -input corpus.json -format glitch
```

## Interpretation checksum

```text
THE_MACHINE_CAN_COUNT = TRUE
THE_MACHINE_CAN_COMPARE = TRUE
THE_MACHINE_CAN_FIND_STRUCTURE = TRUE
THE_MACHINE_CAN_PROPOSE_CONNECTIONS = TRUE

THE_MACHINE_CAN_PROVE_DESTINY_FROM_GEMATRIA = FALSE
THE_MACHINE_CAN_DEFINE_THE_PERSON = FALSE
THE_MACHINE_CAN_OWN_MEANING = FALSE

HUMAN_AGENCY > MACHINE_AUTHORITY
```
