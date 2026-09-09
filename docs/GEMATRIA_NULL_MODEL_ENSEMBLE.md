# GEMATRIA-GLITCH-1 Null-Model Ensemble

## Purpose

The ensemble tests whether an observed anomaly remains uncommon under more than one reasonable randomization assumption.

It currently runs two deterministic Monte Carlo baselines:

```text
1. value_permutation
2. word_length_stratified_value_permutation
```

The first shuffles the complete observed Gematria value multiset across all words.

The second shuffles values only among words with the same Unicode rune length. This controls for the possibility that some apparent rarity is explained by word length.

```text
ONE_NULL_MODEL != ALL_REASONABLE_NULL_MODELS
NULL_MODEL_ENSEMBLE != REALITY
```

## Why this matters

A finding can look unusual under unrestricted value permutation but ordinary once word length is controlled.

That is evidence of assumption sensitivity.

```text
ASSUMPTION_SENSITIVITY != FALSEHOOD
MODEL_AGREEMENT != CAUSATION
```

## Run

```text
cd tools/gematria-glitch

go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -null-ensemble \
  -null-simulations 10000 \
  -null-seed 369 \
  -null-q-threshold 0.05 \
  -null-format glitch
```

JSON output uses `-null-format json`.

## Per-model statistics

Each model reports:

```text
NULL_HITS
EMPIRICAL_P_VALUE
BH_ADJUSTED_Q_VALUE
SURPRISE_BITS
FREQUENCY_CLASS
```

Benjamini-Hochberg correction is applied separately inside each model across the complete observed finding family.

## Robustness states

Using the declared adjusted q-value threshold:

```text
NOT_UNCOMMON_UNDER_ENSEMBLE
UNCOMMON_IN_MODEL_SUBSET
UNCOMMON_ACROSS_ALL_MODELS
```

The report also stores:

```text
UNCOMMON_MODELS
TOTAL_MODELS
WORST_CASE_Q_VALUE
```

The worst-case q-value is the largest adjusted q-value across models and is therefore a conservative summary of cross-model sensitivity.

```text
ROBUST_ACROSS_MODELS != TRUTH
Q_THRESHOLD != SEMANTIC_THRESHOLD
```

## Length-stratified model

For each Hebrew token:

```text
STRATUM = Unicode rune length
```

Values are permuted only inside the same stratum.

If a length stratum contains one record, that value is fixed under this baseline. This is deliberate and exposes findings that depend strongly on structural constraints of the corpus.

The model preserves:

```text
CORPUS_SIZE
WORD_SET
GEMATRIA_SYSTEM
WORD_LENGTH_PER_RECORD
VALUE_MULTISET_WITHIN_EACH_LENGTH_STRATUM
```

## Boundaries

```text
NULL_MODEL_ENSEMBLE != REALITY
ROBUST_ACROSS_MODELS != TRUTH
MODEL_AGREEMENT != CAUSATION
Q_THRESHOLD != SEMANTIC_THRESHOLD
ASSUMPTION_SENSITIVITY != FALSEHOOD
EMPIRICAL_P_VALUE != TRUTH_PROBABILITY
BH_Q_VALUE != TRUTH_PROBABILITY
PATTERN != PROOF
```

A finding that remains uncommon under both models has survived two declared baselines. It has not become a semantic, theological, causal, diagnostic, prophetic, or supernatural fact.

## Machine contract

```text
schemas/gematria-glitch.null-ensemble.v1.schema.json
```
