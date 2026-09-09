# GEMATRIA-GLITCH-1 Out-of-Sample Validation

## Purpose

The validation engine separates anomaly discovery from later testing.

```text
DISCOVERY_SET != VALIDATION_SET
DISCOVERY != CONFIRMATION
```

A discovery corpus may generate candidate anomaly instances and anomaly-class hypotheses. A separate validation corpus then tests them.

The engine rejects:

```text
SAME_CORPUS_IDENTITY
SAME_SAMPLE_CONTENT
DIFFERENT_GEMATRIA_SYSTEM
```

Renaming a corpus does not make it independent.

## Two different questions

The report intentionally separates instance replication from independent class validation.

### Instance replication

Instance replication asks whether the exact discovery signature appears in the validation corpus.

```text
INSTANCE_REPLICATED_IN_VALIDATION
INSTANCE_NOT_REPLICATED_IN_VALIDATION
INSTANCE_NOT_TESTABLE_IN_VALIDATION
```

If the validation corpus does not contain the required Hebrew words, the result is not testable rather than failed.

```text
NOT_TESTABLE != FAILED
```

Because Gematria values are deterministic for the same words, exact instance replication is not treated as strong independent validation.

```text
INSTANCE_REPLICATION != INDEPENDENT_VALIDATION
```

### Class validation

The stronger test asks whether an anomaly class appears on validation signatures that were not present in discovery.

For each anomaly type discovered in the discovery corpus, the validator removes validation signatures already seen in discovery.

If new signatures of that type remain:

```text
CLASS_RECURRED_OUT_OF_SAMPLE
```

Otherwise:

```text
CLASS_NOT_RECURRED_OUT_OF_SAMPLE
```

This tests recurrence on different validation examples.

```text
CLASS_RECURRED_OUT_OF_SAMPLE != TRUTH
NOT_RECURRED != DISPROVEN
```

## Locked discovery sets

Before interpreting validation results, the engine hashes the complete discovery candidate set and the complete anomaly-class hypothesis set.

```text
CANDIDATE_SET_SHA256
HYPOTHESIS_SET_SHA256
```

This makes it explicit which candidates and classes were discovered before validation.

The report includes failures and not-testable candidates. It does not return only successful cases.

```text
ALL_DISCOVERY_CANDIDATES -> VALIDATION_REPORT
CHERRY_PICK_SUCCESS_ONLY -> FORBIDDEN
```

## Sample identity

Each corpus reference contains two hashes.

```text
CORPUS_SHA256
SAMPLE_SHA256
```

`CORPUS_SHA256` binds the full versioned corpus record.

`SAMPLE_SHA256` binds the sorted Hebrew word and Gematria value sample. This prevents the same sample from being relabeled with different corpus metadata and reused as supposedly independent validation data.

## Run

```text
cd tools/gematria-glitch

go run . \
  -discovery-input ../../datasets/gematria/demo-corpus.v1.json \
  -validation-input ../../datasets/gematria/demo-corpus.replication.v1.json \
  -validation-format glitch
```

For JSON:

```text
go run . \
  -discovery-input ../../datasets/gematria/demo-corpus.v1.json \
  -validation-input ../../datasets/gematria/demo-corpus.replication.v1.json \
  -validation-format json
```

## Interpretation boundary

Out-of-sample recurrence increases evidence that an anomaly class is not unique to the discovery sample.

It does not prove semantic identity, causation, theology, prophecy, diagnosis, destiny, supernatural origin, or universal significance.

```text
DISCOVERY_SET != VALIDATION_SET
DISCOVERY != CONFIRMATION
INSTANCE_REPLICATION != INDEPENDENT_VALIDATION
CLASS_RECURRED_OUT_OF_SAMPLE != TRUTH
NOT_RECURRED != DISPROVEN
NOT_TESTABLE != FAILED
VALIDATION_CORPUS != UNIVERSE
PATTERN != PROOF
```

## Machine contract

```text
schemas/gematria-glitch.out-of-sample.v1.schema.json
```
