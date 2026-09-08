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
| `𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃` | Temporal Eye | Detect provenance or meaning drift across repository history. |

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

## Data contract

The current engine accepts normalized repository-state records.

```python
state = {
    "semantic_contradictions": [
        {
            "files": ["README.md", "docs/contract.md"],
            "confidence": 0.92,
            "description": "The same invariant is defined differently.",
        }
    ],
    "cochange_relations": [
        {
            "file_a": "schemas/cmb.json",
            "file_b": "src/cmb_agents/validator.py",
            "score": 0.94,
            "explicit_dependency": False,
        }
    ],
    "provenance_drift": [
        {
            "artifacts": ["commit:a1", "commit:b2"],
            "confidence": 0.88,
            "description": "A small textual change altered the semantic invariant.",
        }
    ],
}
```

The next integration layer should build these normalized records from deterministic Git history, dependency graphs, schema analysis, and repository audits before any model-based interpretation occurs.

## Recovery rule

If evidence is absent, malformed, contradictory, or below threshold, the Eye emits nothing.

Silence is preferable to invented certainty.
