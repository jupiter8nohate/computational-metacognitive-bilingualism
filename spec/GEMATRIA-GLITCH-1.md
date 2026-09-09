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

## Corpus-aware rarity

GGL-1 may annotate a finding with corpus-relative support and rarity.

```text
SUPPORT://<COUNT>/<BASIS>
RARITY_SCORE://<0_TO_1>
RARITY != SIGNIFICANCE
```

The score answers only this question:

> How uncommon is this deterministic structure within the declared input corpus under the scanner's stated support basis?

For single-entry properties, the support basis is the number of corpus entries. For linguistic prefix-delta relationships, the support basis is the number of possible unordered entry pairs. Exact collisions and digital-root families use the number of corpus entries sharing the same calculated signature.

A higher rarity score MUST NOT be interpreted as stronger evidence, greater truth, theological importance, scientific importance, diagnostic meaning, or destiny.

```text
RARE != IMPORTANT
RARE != TRUE
RARE != SACRED
RARE != DESTINY
```

The canonical machine-readable finding shape is defined by:

```text
schemas/gematria-glitch.finding.v1.schema.json
```

## Provenance receipts

A provenance-grade GGL-1 corpus uses:

```text
schema_version
corpus_id
version
gematria_system
records[]
records[].id
records[].word
records[].source.id
records[].source.kind
records[].source.reference
```

The canonical corpus schema is:

```text
schemas/gematria-glitch.corpus.v1.schema.json
```

The canonical receipt schema is:

```text
schemas/gematria-glitch.receipt.v1.schema.json
```

Receipt generation follows:

```text
CORPUS
  -> NORMALIZE
  -> SHA256(CORPUS)
  -> FINDING
  -> SOURCE_RECORD_IDS
  -> RECEIPT_PAYLOAD
  -> SHA256(RECEIPT_PAYLOAD)
  -> RECEIPT
```

No current clock value is included in the deterministic receipt hash. The same normalized corpus and finding produce the same receipt digest.

A receipt MUST preserve:

```text
PATTERN != PROOF
RARITY != SIGNIFICANCE
RECEIPT != TRUTH
```

A receipt proves payload integrity under the implemented hash procedure. It does not prove external truth, authorship, originality, prophecy, causation, diagnosis, identity, or destiny.

## Receipt-backed anomaly graph

GGL-1 may project a verified corpus and its deterministic receipts into a typed anomaly knowledge graph.

Canonical schema:

```text
schemas/gematria-glitch.graph.v1.schema.json
```

Canonical documentation:

```text
docs/GEMATRIA_ANOMALY_KNOWLEDGE_GRAPH.md
```

Graph projection follows:

```text
CORPUS
  -> RECORD
  -> VALUE
  -> PRIME_FACTOR

FINDING
  -> RECEIPT
  -> ANOMALY_TYPE
  -> TYPED_EDGE
  -> SOURCE_TRACE
```

Receipt-backed relationships include exact collisions, shared prime factors, linguistic prefix deltas, anomaly membership, source references, and corpus derivation.

Every graph MUST preserve:

```text
GRAPH != PROOF
EDGE != CAUSATION
CONNECTED != IDENTICAL
```

A graph edge describes a reproducible relationship encoded by the implementation. It does not establish semantic identity, causation, prophecy, diagnosis, destiny, or human worth.

## Bounded graph path discovery

GGL-1 may query its verified anomaly graph for simple paths between exact graph node IDs or exact Hebrew record words.

Canonical result schema:

```text
schemas/gematria-glitch.path-query.v1.schema.json
```

Canonical documentation:

```text
docs/GEMATRIA_GRAPH_PATH_DISCOVERY.md
```

The query engine may traverse a stored edge in either direction for navigation while preserving the original relation and recording `FORWARD` or `REVERSE` traversal.

Path ranking MUST use the declared evidence ordering, not symbolic appeal:

```text
EVIDENCE_FLOOR descending
HOP_COUNT ascending
PATH_ID lexical ascending
```

Every result MUST preserve:

```text
PATH != PROOF
PATH_RANK != TRUTH
EDGE != CAUSATION
CONNECTED != IDENTICAL
NO_PATH != NO_RELATIONSHIP
```

A returned path shows graph connectivity under the current corpus and search bounds. It does not prove semantic identity, causation, prophecy, diagnosis, destiny, or significance.

## Multi-corpus replication

GGL-1 may compare two to sixteen provenance-grade corpora that use the same declared Gematria system.

Canonical result schema:

```text
schemas/gematria-glitch.multicorpus.v1.schema.json
```

Canonical documentation:

```text
docs/GEMATRIA_MULTI_CORPUS_REPLICATION.md
```

The engine reports two distinct layers:

```text
INSTANCE_REPLICATION
TYPE_RECURRENCE
```

Instance replication asks whether the same canonical anomaly signature appears in multiple corpora. Type recurrence asks whether the same anomaly class appears across corpora, even when the specific words differ.

Cross-corpus signatures exclude corpus-relative rarity and support metadata.

Every comparison MUST preserve:

```text
REPLICATION != PROOF
RECURRENCE != CAUSATION
REPEATED != UNIVERSAL
CORPUS_DEPENDENCE != FALSEHOOD
ABSENCE != DISPROOF
```

A repeated structure is stronger evidence that the arithmetic pattern is not unique to one corpus. It is not proof of interpretation, causation, prophecy, diagnosis, destiny, or universal significance.

## Permutation null model

GGL-1 may test observed findings against a deterministic value-permutation null model.

Canonical result schema:

```text
schemas/gematria-glitch.null-model.v1.schema.json
```

Canonical documentation:

```text
docs/GEMATRIA_NULL_MODEL.md
```

The model preserves:

```text
CORPUS_SIZE
WORD_SET
VALUE_MULTISET
GEMATRIA_SYSTEM
```

It randomly reassigns the exact observed values among the existing words using a deterministic seeded Fisher-Yates permutation.

For each observed finding:

```text
CHANCE_RATE = NULL_HITS / SIMULATIONS
EMPIRICAL_P_VALUE = (NULL_HITS + 1) / (SIMULATIONS + 1)
SURPRISE_BITS = -log2(EMPIRICAL_P_VALUE)
```

The empirical p-value describes recurrence under this declared null model. It is not the probability that an interpretation is true.

Every null-model report MUST preserve:

```text
NULL_MODEL != REALITY
EMPIRICAL_P_VALUE != TRUTH_PROBABILITY
SURPRISE != SIGNIFICANCE
RARE_UNDER_NULL != SUPERNATURAL
REPLICATION != PROOF
PATTERN != PROOF
```

A finding that is uncommon under the permutation baseline may justify further investigation. It does not establish causation, prophecy, diagnosis, destiny, supernatural origin, or universal significance.

## Null-model statistical hardening

Null-model report version `gematria-glitch.null-model.v1.1` extends the original permutation report with family-aware multiple-testing correction.

Canonical schema:

```text
schemas/gematria-glitch.null-model.v1.1.schema.json
```

Each finding reports:

```text
EMPIRICAL_P_VALUE
BH_ADJUSTED_Q_VALUE
```

The report also records:

```text
TEST_FAMILY_SIZE
MULTIPLE_TESTING://benjamini_hochberg_fdr
```

The Benjamini-Hochberg adjustment is computed across all observed findings tested in the report. It reduces the risk of treating the smallest raw p-value from a large anomaly family as uniquely compelling.

The current value-permutation model is word-keyed and therefore requires unique Hebrew word tokens inside a corpus. Duplicate tokens MUST fail validation rather than overwrite one another.

Every v1.1 report MUST preserve:

```text
EMPIRICAL_P_VALUE != TRUTH_PROBABILITY
BH_Q_VALUE != TRUTH_PROBABILITY
MULTIPLE_TESTING_CORRECTION != SEMANTIC_PROOF
NULL_MODEL != REALITY
PATTERN != PROOF
```
