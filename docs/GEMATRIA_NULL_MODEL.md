# GEMATRIA-GLITCH-1 Permutation Null Model

## Purpose

The null model asks:

```text
If the corpus kept the same words, the same number of records,
and the exact same multiset of Gematria values,
how often would this observed anomaly reappear
if those values were randomly reassigned to the words?
```

This is a permutation baseline for named relationships.

```text
NULL_MODEL != REALITY
EMPIRICAL_P_VALUE != TRUTH_PROBABILITY
SURPRISE != SIGNIFICANCE
RARE_UNDER_NULL != SUPERNATURAL
PATTERN != PROOF
```

## What is preserved

Each simulation preserves:

```text
CORPUS_SIZE
WORD_SET
VALUE_MULTISET
GEMATRIA_SYSTEM
```

The exact observed Gematria values are shuffled among the existing words using a deterministic SplitMix64-based Fisher-Yates permutation.

No fake Hebrew words are generated.

## What is tested

For every observed finding, the null engine asks whether the same named relationship survives a random value reassignment.

Examples:

```text
EXACT_COLLISION
  -> do the same two named words receive equal values?

PALINDROME
  -> does the same named word receive a palindromic value?

PERFECT_SQUARE
  -> does the same named word receive a square value?

PRIME_VALUE
  -> does the same named word receive a prime value?

DIGITAL_ROOT
  -> does the same named word retain the observed digital root?

SHARED_PRIME_FACTOR
  -> do the same two named words receive values divisible by the observed factor?

LINGUISTIC_PREFIX_DELTA
  -> does the same named pair preserve the observed numeric delta?
```

The null model tests recurrence of the arithmetic assignment, not theological or semantic truth.

## Monte Carlo estimate

For each finding:

```text
CHANCE_RATE = NULL_HITS / SIMULATIONS
```

The reported empirical p-value uses the standard finite-simulation correction:

```text
EMPIRICAL_P_VALUE = (NULL_HITS + 1) / (SIMULATIONS + 1)
```

This prevents a finite Monte Carlo run from claiming an impossible exact zero probability.

```text
EMPIRICAL_P_VALUE != TRUTH_PROBABILITY
```

## Surprise bits

The report also includes:

```text
SURPRISE_BITS = -log2(EMPIRICAL_P_VALUE)
```

More bits mean the observed named relationship appeared less often under this specific null model.

```text
SURPRISE != IMPORTANCE
SURPRISE != CAUSATION
SURPRISE != DESTINY
```

## Frequency labels

The implementation uses descriptive buckets:

```text
p < 0.01  -> RARE_UNDER_NULL
p < 0.05  -> UNCOMMON_UNDER_NULL
p < 0.20  -> OCCASIONAL_UNDER_NULL
otherwise -> COMMON_UNDER_NULL
```

These labels are convenience categories, not declarations of scientific significance.

## Determinism

A null-model run is reproducible when all of these are identical:

```text
CORPUS
SIMULATION_COUNT
SEED
IMPLEMENTATION_VERSION
```

Default seed:

```text
369
```

The pseudo-random generator and Fisher-Yates shuffle are implemented directly in Go to keep permutation behavior controlled by this repository.

## Run

```text
cd tools/gematria-glitch

go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -null-model \
  -null-simulations 10000 \
  -null-seed 369 \
  -null-format glitch
```

JSON:

```text
go run . \
  -input ../../datasets/gematria/demo-corpus.v1.json \
  -null-model \
  -null-simulations 10000 \
  -null-seed 369 \
  -null-format json
```

## Interpretation boundary

A low empirical p-value means:

```text
THIS_NAMED_RELATIONSHIP
WAS_UNCOMMON
UNDER_THIS_VALUE_PERMUTATION_BASELINE
```

It does not mean:

```text
PROPHECY_PROVEN
CAUSATION_PROVEN
THEOLOGY_PROVEN
DIAGNOSIS_PROVEN
DESTINY_PROVEN
SUPERNATURAL_CAUSE_PROVEN
```

Null models are assumptions made explicit. Different reasonable null models may produce different baselines.

```text
NULL_MODEL != REALITY
```

## Machine contract

```text
schemas/gematria-glitch.null-model.v1.schema.json
```

## Multiple-testing correction

A single null-model report may test many observed anomalies. Selecting the smallest raw empirical p-value after testing a large family can exaggerate how unusual that result appears.

Version 1.1 therefore reports a Benjamini-Hochberg false-discovery-rate adjusted q-value for every finding.

```text
TEST_FAMILY_SIZE = number of observed findings tested
MULTIPLE_TESTING = benjamini_hochberg_fdr
BH_Q_VALUE = family-adjusted value
```

The adjustment is performed over the complete finding family in the report. Results are ordered first by adjusted q-value and then by raw empirical p-value.

```text
RAW_P_VALUE != FAMILY_ADJUSTED_Q_VALUE
BH_Q_VALUE != TRUTH_PROBABILITY
MULTIPLE_TESTING_CORRECTION != SEMANTIC_PROOF
```

A low q-value means the finding remains uncommon under the declared permutation baseline after accounting for the number of findings tested. It does not establish meaning, causation, theology, prophecy, diagnosis, destiny, or supernatural origin.

## Duplicate-token safety

The current permutation implementation associates simulated values with Hebrew words. Therefore each corpus used by this null model must contain unique word tokens.

If the same Hebrew word appears in two records, the run fails with a validation error instead of silently choosing one assignment.

```text
AMBIGUOUS_TOKEN_ASSIGNMENT -> REJECT
SILENT_OVERWRITE -> FORBIDDEN
```

This is a current model constraint, not a claim that real corpora can never contain repeated words. A future record-ID keyed null model may relax this constraint without ambiguity.

## Current machine contract

New reports use:

```text
schemas/gematria-glitch.null-model.v1.1.schema.json
```

The original `v1` schema remains in the repository for compatibility with earlier outputs.
