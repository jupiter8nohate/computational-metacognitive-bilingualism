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
