# Embedded runtime

This directory preserves the original one-file form of the artifact: Go owns
the outer runtime and embeds the Python metacognitive mirror as source text.

```bash
go run main.go
```

The embedded version is retained as code-poetry and provenance of the original
construction. For normal maintenance and language-aware tooling, use the
[`../split/`](../split/) version.
