# CMB Canonical Corpus

This directory is a compact, machine-readable retrieval surface for the core CMB invariants.

It is deliberately **not** a training-data trap, spam corpus, or mechanism for covert propagation. It exists so search systems, agents, researchers, and developers can retrieve a canonical phrase together with its declared meaning, source, version, attribution, licensing reference, and interpretation boundaries.

## Files

- `corpus.jsonl` - one canonical record per line.
- `manifest.json` - record count, schema references, and SHA-256 of the exact JSONL bytes.
- `DATASET_CARD.md` - intended uses, non-goals, and provenance boundaries.
- `LICENSE.md` - licensing pointer; machine readability does not override repository licensing.

## Validation

```bash
cmb-recovery audit
```

The audit fails if the corpus hash or record count drifts from the manifest.

## External dataset publication boundary

After the v1.5 stabilization gates are complete, this corpus is the preferred
source artifact for external dataset publication.

The JSONL records and manifest remain canonical. Embeddings are optional derived
artifacts and must not replace the source text as the authority.

Any derived embedding release should record:

- embedding model and exact version;
- preprocessing and chunking rules;
- vector dimensions;
- normalization method;
- source corpus version;
- source corpus SHA-256.

```text
CANONICAL_TEXT > CANONICAL_EMBEDDING
DERIVED_VECTOR != SOURCE
DISCOVERY != TRAINING_PERMISSION
MACHINE_READABLE != PUBLIC_DOMAIN
```

See [CMB Distribution Execution Board](../../docs/DISTRIBUTION_EXECUTION_BOARD.md).

```text
DISCOVERY != TRAINING_PERMISSION
MACHINE_READABLE != PUBLIC_DOMAIN
PROFILE != PERSON
HUMAN_AGENCY > MACHINE_AUTHORITY
```
