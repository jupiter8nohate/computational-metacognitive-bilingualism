# GEMATRIA-GLITCH-1 Graph Path Discovery

## Purpose

The path engine answers bounded questions such as:

```text
What connects נחש to משיח within two verified edges?
What connects שלום to תורה within four verified edges?
```

It searches the deterministic anomaly knowledge graph without inventing missing edges.

```text
PATH != PROOF
PATH_RANK != TRUTH
EDGE != CAUSATION
CONNECTED != IDENTICAL
NO_PATH != NO_RELATIONSHIP
```

## Query

Selectors may be an exact graph node ID or an exact Hebrew record word.

```text
cd tools/gematria-glitch

go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -path-from נחש \
  -path-to משיח \
  -path-depth 2 \
  -path-limit 5 \
  -path-format glitch
```

For JSON:

```text
go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -path-from שלום \
  -path-to תורה \
  -path-depth 4 \
  -path-limit 10 \
  -path-format json
```

## Traversal

The stored graph remains directed. Path discovery may traverse a stored edge in either direction for research navigation.

The default search surface intentionally excludes high-degree metadata hubs such as corpus membership, receipt plumbing, and anomaly-type membership. Those remain available as trace metadata but are not used as shortcuts between otherwise unrelated records.

Queryable discovery relations are:

```text
SOURCED_BY
HAS_GEMATRIA_VALUE
HAS_PRIME_FACTOR
EXACT_COLLISION_WITH
SHARES_PRIME_FACTOR_WITH
LINGUISTIC_PREFIX_DELTA_TO
```

This pruning prevents paths such as `record -> corpus -> unrelated_record` from masquerading as meaningful connections.

Each step records:

```text
EDGE_ID
FROM
RELATION
TO
TRAVERSAL://FORWARD | REVERSE
EVIDENCE_TIER
RECEIPT_SHA256
EVIDENCE
```

Reverse traversal does not reverse the meaning of the stored predicate. It means only that the query engine navigated from the predicate object back to its subject.

## Evidence tiers

The current bounded ranking uses evidence tiers, not a mystical score.

```text
4 = DIRECT_STRUCTURAL
    CONTAINS_RECORD
    SOURCED_BY
    HAS_GEMATRIA_VALUE
    HAS_PRIME_FACTOR

3 = RECEIPT_BACKED
    deterministic anomaly and provenance edges backed by a verified receipt

1 = LOWER_ASSURANCE
    reserved fallback for unsupported or future relations
```

The path evidence floor is the minimum tier across its steps.

Paths sort by:

```text
1. EVIDENCE_FLOOR descending
2. HOP_COUNT ascending
3. PATH_ID lexical ascending
```

Therefore a two-hop direct arithmetic path may rank above a one-hop receipt-backed anomaly edge.

```text
MECHANISM > DRAMA
PATH_RANK != TRUTH
```

## Receipt and source trail

Every returned path includes:

```text
receipt_sha256s[]
source_node_ids[]
```

Source traces include sources attached to records on the path plus sources referenced by receipts used by the path.

## Example

For `נחש` and `משיח`, both standard values are 358.

A high-evidence structural route is:

```text
record:demo-001
  -> HAS_GEMATRIA_VALUE
value:358
  <- HAS_GEMATRIA_VALUE
record:demo-002
```

A second route may be:

```text
record:demo-001
  -> EXACT_COLLISION_WITH
record:demo-002
```

The direct collision edge is shorter but receipt-backed. The value route has a stronger evidence floor because each step is direct arithmetic structure.

Neither route proves the two concepts are semantically identical.

## Search bounds

To keep discovery deterministic and computationally bounded:

```text
1 <= path-depth <= 8
1 <= path-limit <= 50
candidate expansions <= 10000
```

The engine searches simple paths only. A node is not revisited inside the same candidate path.

If no path appears within the requested depth:

```text
NO_PATH_FOUND != NO_RELATIONSHIP
```

The result means only that the current graph and current search boundary did not produce a path.

## Machine contract

```text
schemas/gematria-glitch.path-query.v1.schema.json
```
