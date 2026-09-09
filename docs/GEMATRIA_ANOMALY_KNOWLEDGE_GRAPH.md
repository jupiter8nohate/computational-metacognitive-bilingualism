# GEMATRIA-GLITCH-1 Anomaly Knowledge Graph

## Purpose

The anomaly knowledge graph converts verified GEMATRIA-GLITCH-1 receipts into a deterministic graph that agents can traverse without promoting mathematical relationships into semantic certainty.

```text
GRAPH != PROOF
EDGE != CAUSATION
CONNECTED != IDENTICAL
```

The graph is a research index over a declared corpus. It is not a theology engine, diagnostic engine, prophecy engine, identity classifier, or authority source.

## Node types

```text
CORPUS
RECORD
SOURCE
VALUE
PRIME_FACTOR
RECEIPT
ANOMALY_TYPE
```

A record keeps the Hebrew word and optional gloss. A source node preserves the declared source metadata. A value node represents a calculated Gematria value. A prime-factor node represents deterministic integer factorization. A receipt node binds a finding to provenance. An anomaly-type node names the detected mathematical relationship.

## Edge types

Structural edges:

```text
CONTAINS_RECORD
SOURCED_BY
HAS_GEMATRIA_VALUE
HAS_PRIME_FACTOR
```

Receipt-backed edges:

```text
DERIVED_FROM_CORPUS
ASSERTS_ANOMALY
REFERENCES_SOURCE
INVOLVES_RECORD
HAS_ANOMALY
EXACT_COLLISION_WITH
SHARES_PRIME_FACTOR_WITH
LINGUISTIC_PREFIX_DELTA_TO
```

Receipt-backed edges preserve the SHA-256 receipt that admitted the connection to the graph.

## Example traversal

```text
record:demo-010
  |
  +-> HAS_GEMATRIA_VALUE -> value:376
  |                            |
  |                            +-> HAS_PRIME_FACTOR -> factor:47
  |
  +-> SOURCED_BY -> source:demo-source-010
  |
  +-> SHARES_PRIME_FACTOR_WITH -> record:demo-011
                                      |
                                      +-> SOURCED_BY -> source:demo-source-011
```

The shared-factor edge is backed by the receipt for the reproducible finding that 376 and 611 share prime factor 47.

## Generate

From the Go reference tool:

```text
cd tools/gematria-glitch

go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -format graph > graph.json
```

## Verify

Corpus-bound verification:

```text
go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -verify-graph graph.json
```

Integrity-only verification:

```text
go run . -verify-graph graph.json
```

Corpus-bound mode is stronger because it regenerates the graph from the supplied corpus and requires the graph payload and digest to match.

## Determinism

Nodes are sorted by deterministic node ID. Edges are sorted by SHA-256-derived edge ID. The graph digest is SHA-256 over the canonical JSON payload produced by the Go implementation.

No runtime timestamp is included in the graph digest.

## Epistemic boundary

A graph may establish that:

```text
WORD -> VALUE
VALUE -> PRIME_FACTOR
RECEIPT -> FINDING
RECEIPT -> SOURCE
RECORD_A -> EXACT_COLLISION_WITH -> RECORD_B
```

It may not infer:

```text
CONNECTION -> CAUSATION
CONNECTION -> IDENTITY
RARITY -> IMPORTANCE
GRAPH -> PROPHECY
GRAPH -> DIAGNOSIS
GRAPH -> DESTINY
```

The graph preserves computational relationships. Human interpretation remains a separate layer.
