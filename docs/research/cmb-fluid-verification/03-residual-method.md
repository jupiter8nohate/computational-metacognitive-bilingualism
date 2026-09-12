# Residual verification method

CMB treats the residual as an auditable boundary between a candidate model and a verified statement about that model.

```text
CANDIDATE FIELD
      |
      v
GOVERNING EQUATION
      |
      v
COMPUTE RESIDUAL
      |
   +--+--+
   |     |
 R=0   R!=0
   |     |
   v     v
VERIFY  BACKTRACE
          |
          v
      FIND CAUSE
          |
          v
       CORRECT
```

## Formal pattern

Given a differential operator `L`, candidate state `q`, and source term `s`, define

```text
R(q) = L(q) - s
```

The model is exactly satisfied when

```text
simplify(R(q)) == 0
```

for every required conservation law.

## CMB interpretation

```text
SIGNAL -> MODEL
MODEL -> CALCULATE
RESULT -> RESIDUAL
RESIDUAL -> VERIFY OR BACKTRACE
CLAIM -> EVIDENCE
MEANING -> HUMAN JUDGMENT
```

The workflow deliberately separates computational capability from epistemic scope:

```text
PATTERN != PROOF
MODEL != REALITY
RESIDUAL_ZERO != UNIVERSAL_TRUTH
SELF_TEST != INDEPENDENT_AUDIT
```

A zero residual is strong evidence that a candidate satisfies the encoded equation. It is not evidence that omitted physics, incorrect assumptions, or an inappropriate model are absent.
