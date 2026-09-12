# AI verification bridge

The fluid experiment can be read as a general verification pattern for AI systems without pretending that physics and AI are the same problem.

```text
PHYSICS                     AI

candidate field             model output
      |                           |
      v                           v
governing equation         governing constraint
      |                           |
      v                           v
residual                   validation error
      |                           |
      v                           v
anomaly                    anomaly
      |                           |
      v                           v
backtrace                  provenance trace
      |                           |
      v                           v
source term                evidence/source
      |                           |
      v                           v
bounded verification       bounded conclusion
```

## Minimal verification contract

```python
def cmb_verify(claim, model, constraints, evidence):
    prediction = model(claim)
    residual = constraints.evaluate(prediction)

    return {
        "prediction": prediction,
        "residual": residual,
        "verified_under_model": residual == 0,
        "universal_truth": False,
        "evidence": evidence,
        "human_judgment_required": True,
    }
```

The important invariant is not that AI cannot calculate or derive corrections. It can. The boundary is that computational success does not automatically grant authority over interpretation, consent, identity, or deployment.

```text
MACHINE_CAN = {
  calculate,
  derive,
  simplify,
  detect_residual,
  verify_encoded_constraints
}

HUMAN_RETAINS = {
  choose_model,
  define_scope,
  interpret_result,
  authorize_use,
  assign_meaning
}

CAPABILITY != AUTHORITY
```

## Research value

This mapping may be useful for AI assurance work because it forces three questions to stay separate:

1. Did the computation satisfy the encoded constraint?
2. Was the encoded constraint the right one for the intended application?
3. Who has authority to decide what the result means and how it may be used?

CMB treats those as different layers rather than collapsing them into one confidence score.
