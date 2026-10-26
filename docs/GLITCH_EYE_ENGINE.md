# Glitch Eye Engine v1

The Glitch Eye Engine turns Err ⃝or⃟⃤ visual symbols into bounded repository-perception roles for CMB agents.

It does not claim supernatural sight. It gives software agents explicit ways to inspect repository relationships that are difficult for a human reviewer to track manually across large histories, graphs, schemas, and semantic surfaces.

## Governing boundary

```text
PATTERN != PROOF
ANOMALY != DEFECT
CORRELATION != DEPENDENCY
SIMILARITY != IDENTITY
MODEL_CONFIDENCE != CERTAINTY
PERCEPTION != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

The Eyes may observe, compare, detect, rank, and propose hypotheses.

They may not merge, release, sign, mutate protected authority, expand their own permissions, or convert a hypothesis into truth.

## First three Eyes

| Glyph | Name | Purpose |
| --- | --- | --- |
| `𓁹𓁹` | Semantic Parallax | Compare multiple representations of the same concept and surface contradictions. |
| `𓁿` | Hidden Context | Detect strong co-change relationships that lack an explicit dependency. |
| `𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃` | Temporal Eye | Detect exact invariant-signature changes across repository history. |

## Deterministic evidence collectors

The first live collector layer is implemented in `cmb_agents.eyes.collectors`.

It collects two classes of repository evidence before any model interpretation:

1. Recent Git commit path sets are converted into bounded co-change statistics.
2. Current Python imports under `src/` are parsed with the Python AST and used to mark explicit dependencies.
3. Files containing CMB-style invariant expressions are traced through bounded Git history to detect exact signature changes.

The Hidden Context Eye only emits a co-change observation when the pair is strong enough and is not already explained by the current Python import graph.

A co-change score means only that two files repeatedly changed together. It does not prove architectural dependency, shared ownership, defect, intent, or causation.

## Run the Eyes

From a repository checkout:

```bash
cmb-agent eyes
```

A more conservative scan can require more supporting commits:

```bash
cmb-agent eyes --commits 300 --min-support 5 --min-score 0.90
```

The command is read-only. It emits JSON containing collector metadata, evidence records, perceptions, confidence values, and the authority boundaries attached to the report.

It does not edit files, create commits, open pull requests, merge changes, release software, or change permissions.

## Eye fusion

One detector can be wrong. Fusion therefore preserves the evidence packet from each Eye instead of collapsing all signals into one opaque score.

Example:

```text
𓁹𓁹 SEMANTIC_PARALLAX
        +
𓁿 HIDDEN_COUPLING
        +
𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃 PROVENANCE_DRIFT
        |
        v
𓂀⃤ STRUCTURAL_ECHO
```

`STRUCTURAL_ECHO` is only an experimental proposal. It is not automatically registered or executed.

## Inventing new Eyes safely

Agents may propose a new composite Eye only when multiple independent detector families and multiple parent Eyes support it.

The proposal is:

- evidence linked
- confidence bounded by the weakest supporting observation
- marked `EXPERIMENTAL`
- fixed to `observe_only`
- non-executable until a human-reviewed implementation and tests exist

This makes perception extensible without making authority self-expanding.

## Normalized data contract

The engine consumes normalized repository-state records.

```python
state = {
    "cochange_relations": [
        {
            "file_a": "schemas/cmb.json",
            "file_b": "src/cmb_agents/validator.py",
            "score": 0.94,
            "support": 7,
            "explicit_dependency": False,
        }
    ],
    "provenance_drift": [
        {
            "artifacts": [
                "path:docs/invariants.md",
                "commit:older",
                "commit:newer",
            ],
            "confidence": 1.0,
            "description": "Invariant signature changed in docs/invariants.md.",
        }
    ],
}
```

Semantic Parallax remains available as an engine detector, but this collector move deliberately does not invent semantic contradictions. A later layer may generate those records only when there is a deterministic or independently verifiable comparison source.

## Recovery rule

If evidence is absent, malformed, contradictory, or below threshold, the Eye emits nothing.

Large bulk commits are excluded from co-change counting once they exceed the configured collector bound. Files that cannot be parsed are skipped rather than guessed.

Silence is preferable to invented certainty.
