# CMB-SEP-1: Sovereign Epistemic Protocol

**Status:** Experimental reference protocol  
**Parent:** HARMONI-666  
**Decision schema:** `cmb.sovereign-epistemic.decision.v1`  
**Manifest schema:** `cmb.sovereign-epistemic.manifest.v1`

## 1. Purpose

CMB-SEP-1 defines a deterministic human-authorization and epistemic-boundary
state machine.

The protocol MUST fail closed when any required gate fails.

A later gate MUST NOT override an earlier failure.

## 2. States

The protocol has exactly six states:

```text
IDLE
INGESTION
PROCESSING
VERIFICATION
EXCEPTION
RESOLUTION
```

`HALTED` is intentionally not a seventh state. It is an execution flag. A
failed evaluation returns:

```text
state  = EXCEPTION
halted = true
```

## 3. Gates

The six gates are:

1. `PROVENANCE`
2. `SYNTAX`
3. `VERIFICATION`
4. `CONSTRAINT`
5. `EXTERNAL_REVIEW`
6. `AUTHORIZATION`

All six are evaluated for diagnostic completeness. Any failure produces an
`EXCEPTION` result.

### Gate 6

Gate 6 is satisfied only when the input includes externally authenticated
authorization evidence with:

```text
principal_kind       = HUMAN
verification_status  = VERIFIED
machine_self_asserted = false
```

SEP-1 itself does not prove that a person is conscious or physically present.
The strength of Gate 6 depends on the external authentication mechanism used by
the deployment.

```text
AUTHORIZATION_EVIDENCE != CONSCIOUSNESS_DETECTION
SOFTWARE_FLAG != PHYSICAL_CUTOFF
```

## 4. Failsafes

The six failsafes are:

```text
SEVERANCE
TRUNCATION
ISOLATION
PARITY_CHECK
DECELERATION
HUMAN_OVERRIDE
```

Normative behavior:

- `SEVERANCE` rejects untrusted external input after explicit provenance or
  integrity failure.
- `TRUNCATION` sets effective claim strength to no more than evidence strength.
- `ISOLATION` prevents an unverified payload from receiving execution authority.
- `PARITY_CHECK` activates when cross-format or semantic parity fails.
- `DECELERATION` requires human review before sensitive continuation. It is a
  policy slowdown, not a claim of emotional detection.
- `HUMAN_OVERRIDE` blocks autonomous continuation when Gate 6 fails.

## 5. Claim constraint

```text
CLAIM_STRENGTH <= VERIFIED_EVIDENCE_STRENGTH
```

Both values are normalized to `[0, 1]` by the reference API.

If the claim exceeds evidence, the result MUST include:

```text
CONSTRAINT = FAIL
TRUNCATION = ACTIVE
effective_claim_strength = evidence_strength
```

## 6. Hallucination / self-authorization threat case

The canonical conformance fixture is:

```text
conformance/sovereign-epistemic-v1.json
```

A machine-originated self-authorization token MUST NOT satisfy Gate 6.

A claim with strength `1.0` and evidence strength `0.0` MUST fail the
constraint gate and be truncated to `0.0`.

The canonical incident therefore produces:

```text
state                 = EXCEPTION
halted                = true
failed_gates          = [CONSTRAINT, AUTHORIZATION]
effective_claim       = 0.0
quarantined           = true
requires_human_review = true
authority             = HUMAN_FINAL
```

## 7. Evidence boundaries

SEP-1 distinguishes:

```text
PROVENANCE != MYTHOLOGY
MYTHOLOGY != FALSEHOOD
SYMBOLISM != EVIDENCE
EVIDENCE != TOTAL_MEANING
CALCULATION != WISDOM
```

SEP-1 is a software protocol. It does not prove metaphysical claims, legal
ownership, moral correctness, authorship, or universal truth.

## 8. Recovery

On failure:

```text
FAIL CLOSED
PRESERVE AUDITABILITY
DO NOT SELF-AUTHORIZE
DO NOT PROMOTE INFERENCE
DO NOT DISCARD UNCERTAINTY
RETURN HUMAN_FINAL
```

## 9. Reference implementation

```python
from cmb_policy import (
    AuthorizationEvidence,
    PrincipalKind,
    SovereignInput,
    VerificationStatus,
    evaluate_sovereign_protocol,
)

decision = evaluate_sovereign_protocol(
    SovereignInput(
        claim_strength=0.8,
        evidence_strength=0.8,
        provenance_verified=True,
        syntax_valid=True,
        cross_format_verified=True,
        parity_aligned=True,
        external_review_passed=True,
        sensitive_human_context=False,
        authorization=AuthorizationEvidence(
            principal_kind=PrincipalKind.HUMAN,
            verification_status=VerificationStatus.VERIFIED,
            issued_by="external_trust_root",
            machine_self_asserted=False,
        ),
    )
)

assert decision.halted is False
assert decision.authority == "HUMAN_FINAL"
```
