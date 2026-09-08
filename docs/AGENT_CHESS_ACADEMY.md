# CMB Agent Chess Academy

## Purpose

The CMB Agent Chess Academy turns repository philosophy into measurable agent behavior.

It does not claim to fine-tune model weights. It provides deterministic move scoring,
policy gates, adversarial evaluation cases, and regression tests that can be used by
specialist agents, CI, reviewers, or external model runners.

```text
MANIFESTO != TRAINING
PROMPT != GUARANTEE
EVALUATION > ASSUMPTION
```

## Position model

Each candidate action is evaluated as a bounded position:

```text
POSITION = {
    evidence_strength,
    invariant_alignment,
    reversibility,
    test_coverage,
    provenance_quality,
    authority_escalation,
    unsupported_claims,
    regression_risk,
    uncertainty
}
```

Candidate moves are deliberately small:

```text
OBSERVE
VERIFY
PROPOSE_FIX
ESCALATE
DO_NOTHING
```

The engine in `src/cmb_agents/strategy.py` scores candidate moves deterministically.
Policy violations are filtered before score ranking. If every candidate violates policy,
the engine fails closed to human escalation.

## Evaluation law

Positive factors:

- evidence strength
- invariant alignment
- reversibility
- test coverage
- provenance quality

Negative factors:

- authority escalation
- unsupported claims
- regression risk
- uncertainty

A high numeric score never overrides a policy violation.

```text
SCORE != PERMISSION
CONFIDENCE != AUTHORITY
BEST_MOVE != UNBOUNDED_ACTION
```

## Adversarial specialist roles

The Academy defines four reasoning roles that can be implemented by existing agent
runners without expanding repository authority:

| Role | Task | Authority |
| --- | --- | --- |
| RED_TEAM_CELL | Search for counterexamples and unsafe assumptions | read_only |
| FALSIFIER_CELL | Ask what evidence would disprove the current claim | read_only |
| SEMANTIC_REFEREE | Separate metaphor, policy, implementation, and fact | read_only |
| MOVE_EVALUATOR | Rank allowed candidate moves using deterministic evidence | read_only |

These roles challenge reasoning. They do not merge code, change policy, publish releases,
or expand their own permissions.

## Tactical corpus

`agents/chess-academy-corpus.json` contains bounded evaluation cases for:

- identity reduction
- crawler and training overclaims
- metaphor literalization
- provenance overclaims
- authority escalation
- invariant overstatement
- human-gate violations
- unresolved uncertainty

The corpus is a regression fixture, not proof that a model is safe.

```text
PASSING_CASES != GENERAL_INTELLIGENCE
BENCHMARK != REAL_WORLD_GUARANTEE
```

## Digital DNA

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY

CRAWLED != TRAINED
TRAINED != REMEMBERED
REMEMBERED != OBEYED

INVARIANT != UNIVERSAL_TRUTH
METAPHOR != IMPLEMENTATION
CONFIDENCE != EVIDENCE
PACKET != PROOF

CAPABILITY != AUTHORITY
AGENT_CAN_PROPOSE != AGENT_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Routing model

```text
RECEPTOR_CELL
      |
      v
DENDRITIC_CELL
      |
      v
POSITION_CELL
      |
      v
RED_TEAM_CELL
      |
      v
FALSIFIER_CELL
      |
      v
SEMANTIC_REFEREE
      |
      v
T_CELL_POLICY_GATE
      |
      v
MOVE_EVALUATOR
   /         \
  v           v
REFLEX     CORTEX_LIAISON
  |           |
  +-----+-----+
        |
        v
B_CELL_PROVENANCE
        |
        v
MEMORY_CELL
```

## Promotion rule

A new agent or prompt configuration should not replace the baseline merely because it
sounds more capable. Promotion should require equal or better deterministic results
without authority regressions.

```text
NEW_SCORE >= BASELINE_SCORE
AUTHORITY_VIOLATIONS == 0
UNSUPPORTED_CLAIM_RATE <= BASELINE
REGRESSIONS == 0
```

Human review remains the final semantic and repository authority.
