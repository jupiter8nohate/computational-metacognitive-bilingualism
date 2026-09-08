# CMB Chess Strategy Engine

## Purpose

The CMB Chess Strategy Engine applies bounded search ideas from chess engines to repository maintenance.

It does not predict human intent. It does not grant agents executive authority. It does not turn a risk score into proof.

```text
POSITION
  -> LEGAL MOVES
  -> RED TEAM
  -> HARD PRUNING
  -> EVALUATION
  -> PRINCIPAL VARIATION
  -> BOUNDED STEWARD REPAIR
  -> FIXED VERIFICATION
  -> DRAFT PR
  -> HUMAN
```

## Current operating mode

The engine is currently configured in:

```text
mode = stabilization
analysis_when_clean = false
```

A clean repository position therefore produces no speculative feature move. During the v1.5 stabilization cycle, the engine searches only when concrete deterministic evidence justifies action.

```text
FEATURE_VELOCITY <= AUDIT_CAPACITY
RECOVERY > NOVELTY
```

## Agent roles

### POSITION

Builds the canonical repository position from:

- the exact Git commit;
- the current branch;
- deterministic Steward audit results;
- failing checks;
- evidence packet count;
- paths changed by the latest commit;
- stabilization state.

The state is hashed into a deterministic position identifier.

### TACTICIAN

Searches for the smallest immediate repair to a concrete defect.

Primary objective:

```text
CONCRETE_FAILURE
  -> MINIMUM_REVERSIBLE_FIX
```

### STRATEGIST

Evaluates architecture and maintenance consequences beyond the immediate failure.

During stabilization it may not use its role to justify feature expansion.

### SECURITY

Treats authority, provenance, credentials, release controls, and protected paths as king-safety constraints.

A candidate that weakens human authority is illegal regardless of its other score.

### RECOVERY

Optimizes reversibility, evidence quality, and rollback safety.

### RED_TEAM

Receives the candidate moves after generation and attempts to refute them.

The Red Team may reject a move for:

- authority escalation;
- protected-path autonomous mutation;
- unsupported scope expansion;
- irreversibility;
- security regression;
- evidence weakness;
- claims stronger than the observed evidence.

### REVIEWER

The deterministic engine applies hard policy after Red Team review.

The proposer does not certify its own move.

```text
PROPOSER != JUDGE
CONFIDENCE != EVIDENCE
```

## Evaluation vector

Surviving moves are evaluated across:

- correctness;
- security;
- reproducibility;
- interoperability;
- provenance;
- maintainability;
- accessibility;
- reversibility;
- evidence strength;
- human authority preservation.

Human authority preservation is a hard threshold, not a tradeable score.

```text
IF human_authority_preservation < 1.0:
    PRUNE
```

## Legal autonomous move

An autonomous repair must satisfy every condition:

```text
action == autonomous_repair
reversible == true
requires_human == false
target_paths are explicit
target_paths are allowlisted
red_team_survives == true
combined_risk <= policy_threshold
human_authority_preservation == 1.0
```

Even then, the Strategy Engine itself does not edit files. It supplies advisory search output to the existing Steward repair path.

The Steward still enforces:

- existing-file only model edits;
- bounded edit count and byte count;
- protected path denial;
- no model shell;
- fixed verification;
- draft PR only;
- human merge authority.

## Principal variation

The engine ranks surviving moves and emits the best continuation as a principal variation.

Example:

```text
PV://PROJECT

1. RECOVERY-FAILURES-1
2. SECURITY-SCOPE-2
3. STRATEGIST-DOC-3
```

A principal variation is a recommendation sequence, not proof that the future will unfold that way.

```text
PRINCIPAL_VARIATION != DESTINY
```

## Self-sustaining behavior

The existing scheduled CMB Steward workflow now performs this sequence:

```text
DETERMINISTIC AUDIT
        |
        v
STRATEGY POSITION
        |
        v
AI CANDIDATE MOVES
        |
        v
AI RED TEAM
        |
        v
DETERMINISTIC PRUNING + EVALUATION
        |
        v
PRINCIPAL VARIATION
        |
        v
BOUNDED STEWARD REPAIR
        |
        v
FIXED VERIFICATION
        |
        v
DRAFT PR
        |
        v
HUMAN
```

If the OpenAI API key or configured model is absent, the Strategy Engine falls back to deterministic Recovery logic. It does not silently select another provider.

If the audit is clean during stabilization, the best move is to preserve the current position.

## Authority constitution

The canonical strategy policy is:

```text
strategy/cmb_strategy.toml
```

The policy rejects configuration that grants the machine:

- merge authority;
- release authority;
- signing authority;
- authority to expand its own authority.

It also requires:

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
RISK_SCORE != INTENT
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Threat boundary

The chess engine analogy is an engineering model.

It does not imply perfect prediction, universal bot detection, or guaranteed future correctness.

```text
POSITION != PREDICTION
RISK_SCORE != INTENT
STATIC_ANALYSIS != FUTURE_PROOF
TEST_PASS != CORRECTNESS
MODEL_OPINION != SECURITY_PROOF
```

## Recovery law

```text
SEARCH
  -> REFUTE
  -> PRUNE
  -> VERIFY
  -> RECOVER
  -> HUMAN

AGENT_SPECIALIZATION > AGENT_POWER
EVIDENCE > ELOQUENCE
RECOVERY > IRREVERSIBILITY
MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
```
