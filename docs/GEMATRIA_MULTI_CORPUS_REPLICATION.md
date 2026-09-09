# GEMATRIA-GLITCH-1 Multi-Corpus Replication

## Purpose

The multi-corpus engine asks a stronger question than a single-corpus anomaly scan:

```text
Does the same reproducible anomaly survive when the corpus changes?
```

It compares two to sixteen provenance-grade corpora using the same declared Gematria system.

```text
REPLICATION != PROOF
RECURRENCE != CAUSATION
REPEATED != UNIVERSAL
CORPUS_DEPENDENCE != FALSEHOOD
ABSENCE != DISPROOF
```

## Two levels of comparison

### Instance replication

Instance replication asks whether the same canonical finding signature appears in multiple corpora.

Example:

```text
CORPUS_A:
נחש = 358
משיח = 358
EXACT_COLLISION

CORPUS_B:
נחש = 358
משיח = 358
EXACT_COLLISION

RESULT:
CORPUS_SUPPORT://2/2
STATUS://REPLICATED_ALL_CORPORA
```

The result establishes repetition across the declared corpus set. It does not establish theological identity, causation, destiny, or universal significance.

### Type recurrence

Type recurrence asks whether the same anomaly class appears in multiple corpora, even when the specific words differ.

Example:

```text
EXACT_COLLISION://2/2
PRIME_VALUE://2/2
PALINDROME://1/2
```

This helps distinguish a recurring mathematical class from a single instance.

## Canonical signatures

Corpus-relative metadata is excluded from the replication signature.

The signature includes:

```text
ANOMALY_TYPE
WORDS
VALUES
```

For symmetric pair relationships such as exact collisions and shared prime factors, the first two word-value pairs are canonicalized before hashing. This prevents corpus record order from creating false non-replication.

The signature ID is:

```text
sig:SHA256(canonical_finding_signature)
```

Rarity score, support count, and support basis are not part of the cross-corpus signature because they depend on corpus composition.

## Run

```text
cd tools/gematria-glitch

go run . \
  -compare-inputs ../../datasets/gematria/demo-corpus.v1.json,../../datasets/gematria/demo-corpus.replication.v1.json \
  -compare-format glitch
```

JSON output:

```text
go run . \
  -compare-inputs ../../datasets/gematria/demo-corpus.v1.json,../../datasets/gematria/demo-corpus.replication.v1.json \
  -compare-format json
```

## Replication status

```text
SINGLE_CORPUS
REPLICATED_SUBSET
REPLICATED_ALL_CORPORA
```

These are descriptive states inside the supplied corpus set.

```text
REPLICATED_ALL_CORPORA != UNIVERSAL_TRUTH
```

A result observed in every supplied corpus may fail in a future corpus.

## Replication rate

```text
REPLICATION_RATE = CORPUS_COUNT / TOTAL_CORPORA
```

This is a transparent frequency measure.

It is not a probability that an interpretation is true.

```text
REPLICATION_RATE != TRUTH_PROBABILITY
```

## Corpus absence

If an instance occurs in one corpus but not another, the correct statement is:

```text
INSTANCE_NOT_REPLICATED_IN_CURRENT_SET
```

Not:

```text
INSTANCE_DISPROVEN
```

A missing anomaly may simply reflect vocabulary differences.

## Machine contract

```text
schemas/gematria-glitch.multicorpus.v1.schema.json
```

## Demonstration corpora

```text
datasets/gematria/demo-corpus.v1.json
datasets/gematria/demo-corpus.replication.v1.json
```

The second corpus intentionally contains partial vocabulary overlap so tests can distinguish replicated and corpus-specific findings.
