# Numerical Anomaly Verifier

**Status:** bounded read-only verification extension during v1.5 stabilization.

The numerical anomaly verifier gives CMB Steward research a deterministic way to
inspect Gematria-style string coincidences without converting those
coincidences into claims about identity, causation, theology, destiny, or
social truth.

It lives inside the existing `cmb_agents` package and adds no installed CLI,
top-level package, protocol family, merge authority, or release authority.

```text
PATTERN != PROOF
NUMERIC_MATCH != SEMANTIC_IDENTITY
COINCIDENCE != CAUSATION
RARITY_CLAIM_REQUIRES_CORPUS
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Numeric vector

Each term is normalized to ASCII letters and receives three deterministic
coordinates:

```text
VECTOR(term) = (
    ENGLISH_ORDINAL,
    REVERSE_ORDINAL,
    CYCLIC_REDUCTION_1_TO_9,
)
```

Example:

```text
FOLLOWER = (106, 110, 43)
IDENTITY = (106, 110, 43)
```

This is a triple-vector collision. It means the two normalized strings occupy
the same coordinates under these three transforms. It does not mean the words
have the same meaning.

## Detected structures

### RECIPROCAL_MIRROR

Two terms swap ordinal and reverse values.

```text
JUPITER = (99, 90, 36)
CONSENT = (90, 99, 27)

ORDINAL(JUPITER) == REVERSE(CONSENT)
REVERSE(JUPITER) == ORDINAL(CONSENT)
```

### TRIPLE_VECTOR_COLLISION

Two terms match on all three coordinates.

```text
FOLLOWER = (106, 110, 43)
IDENTITY = (106, 110, 43)
```

### PARTIAL_VECTOR_TWIN

Two terms match on exactly two coordinates but differ on the third.

```text
HASHTAG   = (64, 125, 28)
BACKTRACE = (64, 179, 28)
```

### BICIPHER_LATTICE

Two collision groups on different axes overlap through at least two bridge
terms.

```text
ORDINAL 62:
SIGNAL
AUDIENCE
VIRAL

REDUCTION 26:
SIGNAL
VIRAL
REACH

BRIDGE:
SIGNAL
VIRAL
```

### CIPHER_RECTANGLE

Four terms share one coordinate while the other two coordinates form every
combination of two values.

```text
PATTERN  = (94,  95, 31)
PRIVACY  = (94,  95, 40)
CATEGORY = (94, 122, 40)
JUDGMENT = (94, 122, 31)
```

The shared ordinal is 94. The reverse coordinates are 95 and 122. The
reduction coordinates are 31 and 40. All four combinations exist.

## Rarity rule

The verifier deliberately does not label a discovered pattern rare.

```text
COMPLEX = MEASURABLE_FROM_STRUCTURE
RARE = REQUIRES_REFERENCE_CORPUS
```

`benchmark_pair_kind()` can count an anomaly type across a caller-supplied
corpus. Below the configured corpus threshold, rarity remains `UNMEASURED`.
At or above the threshold, the tool reports only empirical frequency in that
corpus.

A low observed frequency still does not prove meaning or universal rarity.

## Agent role

This module is suitable for a read-only specialist agent:

```text
DISCOVER
-> CLASSIFY
-> COUNT
-> BENCHMARK
-> RECORD
-> HUMAN_REVIEW
```

It must not:

```text
DECLARE_PROPHECY
INFER_IDENTITY
INFER_INTENT
INFER_MENTAL_STATE
DECLARE_CAUSATION
DECLARE_UNIVERSAL_RARITY_FROM_SMALL_SAMPLES
```

## Python surface

```python
from cmb_agents.numeric_anomaly import analyze

report = analyze(
    [
        "FOLLOWER",
        "IDENTITY",
        "JUPITER",
        "CONSENT",
        "PATTERN",
        "PRIVACY",
        "CATEGORY",
        "JUDGMENT",
    ]
)
```

The returned object is deterministic and JSON-ready. It contains vectors,
pair anomalies, same-axis collision groups, cipher rectangles, bicipher
lattices, and the epistemic boundaries attached to the report.

## Stabilization boundary

This verifier remains intentionally narrow for v1.5:

```text
READ_ONLY_ANALYSIS = TRUE
NEW_CLI = FALSE
NEW_TOP_LEVEL_PACKAGE = FALSE
NEW_AGENT_AUTHORITY = FALSE
AUTONOMOUS_MEANING_ASSIGNMENT = FALSE
MERGE_AUTHORITY = FALSE
```

Future corpus ingestion, repository-wide vocabulary extraction, graph
visualization, additional historical Gematria systems, or public APIs should be
considered only after stabilization and independent review.
