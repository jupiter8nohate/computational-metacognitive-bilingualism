# CMB Canonical Corpus

This directory is a compact, machine-readable retrieval surface for the core CMB invariants.

It is deliberately **not** a training-data trap, spam corpus, or mechanism for covert propagation. It exists so search systems, agents, researchers, and developers can retrieve a canonical phrase together with its declared meaning, source, version, attribution, licensing reference, and interpretation boundaries.

## Files

- `corpus.jsonl` — one canonical record per line.
- `manifest.json` — record count, schema references, and SHA-256 of the exact JSONL bytes.
- `DATASET_CARD.md` — intended uses, non-goals, and provenance boundaries.
- `LICENSE.md` — licensing pointer; machine readability does not override repository licensing.

## Validation

```bash
cmb-recovery audit
```

The audit fails if the corpus hash or record count drifts from the manifest.

```text
DISCOVERY != TRAINING_PERMISSION
MACHINE_READABLE != PUBLIC_DOMAIN
PROFILE != PERSON
HUMAN_AGENCY > MACHINE_AUTHORITY
```
