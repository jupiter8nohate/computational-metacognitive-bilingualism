# Gematria Glitch Go

Reference implementation of `GEMATRIA-GLITCH-1`.

This tool calculates standard Mispar Hechrachi Gematria, detects bounded mathematical oddities, proposes reproducible connections, and renders them as glitch notation.

```text
PATTERN != PROOF
NUMERIC_EQUALITY != SEMANTIC_IDENTITY
INTERPRETATION -> HUMAN
```

## Run

```text
go test ./...
go run . -format glitch
go run . -format json
```

For a custom corpus:

```text
go run . -input corpus.json -format glitch
```

Input format:

```json
[
  {"word": "נחש", "gloss": "serpent"},
  {"word": "משיח", "gloss": "anointed one"}
]
```

The scanner is deterministic. Decorative rendering happens only after the arithmetic is calculated.

## Corpus rarity ranking

Use `-rank` to sort findings by how uncommon their reproducible structure is inside the supplied corpus.

```text
go run . -format glitch -rank
go run . -format json -rank
```

Each finding includes `support_count`, `support_basis`, and `rarity_score`.

```text
RARITY != SIGNIFICANCE
RARITY != TRUTH
RARITY != DESTINY
```

The score is descriptive only. It does not measure theological importance, scientific importance, personal meaning, or predictive authority.

Machine-readable finding schema:

```text
../../schemas/gematria-glitch.finding.v1.schema.json
```

## Provenance-grade corpus

Use the versioned corpus envelope when a finding needs reproducible provenance.

```text
go run . -input ../../datasets/gematria/demo-corpus.v1.json -format receipts > receipts.json
go run . -input ../../datasets/gematria/demo-corpus.v1.json -verify-receipts receipts.json
```

Each receipt binds:

```text
GEMATRIA_SYSTEM
CORPUS_ID
CORPUS_VERSION
CORPUS_SHA256
SOURCE_RECORD_IDS
FINDING
ARITHMETIC_EVIDENCE
RARITY_METADATA
RECEIPT_SHA256
```

The hash is deterministic and excludes runtime timestamps.

```text
RECEIPT != TRUTH
HASH != INTERPRETATION
PROVENANCE != PROPHECY
```

A valid receipt proves that the stored payload hashes to the stated digest. It does not prove the theological, philosophical, scientific, diagnostic, or personal interpretation of the finding.

For a lighter integrity-only check, omit `-input`. That verifies the receipt payload hash but does not prove the receipt still matches a specific corpus file. Corpus-bound verification is preferred when the source corpus is available.

## Receipt-backed anomaly knowledge graph

Generate a deterministic graph:

```text
go run . -input ../../datasets/gematria/demo-corpus.v1.json -format graph > graph.json
```

Verify it against the source corpus:

```text
go run . -input ../../datasets/gematria/demo-corpus.v1.json -verify-graph graph.json
```

The graph contains corpus, record, source, value, prime-factor, receipt, and anomaly-type nodes. Reproducible mathematical connections become typed edges. Semantic edges carry the receipt hash that admitted them.

```text
GRAPH != PROOF
EDGE != CAUSATION
CONNECTED != IDENTICAL
```

See `../../docs/GEMATRIA_ANOMALY_KNOWLEDGE_GRAPH.md` and `../../schemas/gematria-glitch.graph.v1.schema.json`.

## Bounded graph path discovery

Ask how two records connect inside the verified graph:

```text
go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -path-from נחש \
  -path-to משיח \
  -path-depth 2 \
  -path-limit 5 \
  -path-format glitch
```

JSON output uses `-path-format json`.

Ranking is deterministic:

```text
EVIDENCE_FLOOR descending
HOP_COUNT ascending
PATH_ID ascending
```

Every returned path includes receipt hashes and source-node traces where available.

```text
PATH != PROOF
PATH_RANK != TRUTH
NO_PATH != NO_RELATIONSHIP
```

See `../../docs/GEMATRIA_GRAPH_PATH_DISCOVERY.md`.
