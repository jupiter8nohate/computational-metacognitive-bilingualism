# CMB Dynamic Friction Matrix

**Status:** experimental runtime policy layer  
**Purpose:** vary verification effort by task risk without weakening CMB's hard human-agency invariants.

## Core rule

The seesaw changes **friction**, not **truth**.

~~~text
PATTERN != PROOF
FIX_COMMITTED != FIX_VERIFIED
TRUSTED_HISTORY != GUARANTEED_FUTURE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

Low-risk work should remain fluid. High-consequence work should fail closed when required evidence is missing. Repeated clean review may reduce operational uncertainty, but it must never erase intrinsic risk.

## The matrix

| Mode | Effective criticality | Behavior |
|---|---:|---|
| High Agility | 0.00-0.40 | Execute fluidly. No mandatory caveat from this layer. |
| Balanced | >0.40-0.80 | Execute with a provisional epistemic caveat. |
| High Safety | >0.80 | Require evidence gates and halt if they are absent. |

~~~text
effective_criticality =
    max(
        intrinsic_risk_floor,
        decayed_operational_uncertainty + novelty_spike + anomaly_spike
    )
~~~

The epistemic budget is the same normalized scalar, so verification demand rises linearly with effective criticality.

## Why risk is split in two

A single decaying score is unsafe because repeated success could eventually make an intrinsically dangerous task look harmless.

CMB therefore separates:

1. **Intrinsic criticality** - consequence built into the task. This never decays.
2. **Operational uncertainty** - novelty, instability, and unknowns. This may decay after successful human review.

For example, ten successful reviews of a medical workflow may reduce uncertainty about the software path. They do not make the medical consequence low-stakes.

~~~text
SUCCESS_HISTORY -> LOWER_UNCERTAINTY
SUCCESS_HISTORY -/> LOWER_INTRINSIC_HARM
~~~

## Trusted invariant semantics

A task profile becomes a runtime **trusted invariant** after the configured review half-life has been reached with no recorded anomalies and no current unknown variables.

This means only that the operational path has accumulated clean review history. It is not proof of correctness, safety, authorship, or future behavior.

The default half-life is three successful human reviews:

~~~text
trust_discount = 0.5 ** (successful_reviews / half_life_reviews)
~~~

Any anomaly or newly declared unknown variable suspends the discount and raises friction again.

## Evidence gates

High-safety mode always requires confirmed human review and independent verification.

Cryptographic integrity is additionally required when the task profile declares that byte-level integrity or provenance evidence is relevant.

~~~text
HASH != MEDICAL_CORRECTNESS
SIGNATURE != FINANCIAL_CORRECTNESS
CRYPTOGRAPHIC_INTEGRITY != DOMAIN_VALIDITY
~~~

A cryptographic receipt proves an integrity property about bytes. It does not prove that a diagnosis, calculation, or policy judgment is correct.

## Runtime API

~~~python
from cmb_policy.friction import (
    EvidenceState,
    TaskRiskProfile,
    TrustState,
    require_friction,
)

decision = require_friction(
    TaskRiskProfile(
        task_id="production-release",
        intrinsic_criticality=0.90,
        uncertainty=0.30,
        external_side_effect=True,
        reversible=False,
        requires_integrity_receipt=True,
    ),
    evidence=EvidenceState(
        human_review_confirmed=True,
        independent_verification_passed=True,
        cryptographic_integrity_verified=True,
    ),
    trust=TrustState(successful_human_reviews=4),
)

assert decision.allowed
~~~

## Integration order

The Dynamic Friction Matrix does **not** override the existing deny-dominant CMB policy engine.

~~~text
1. DECLARED TASK
2. CMB POLICY AUTHORIZATION
3. DYNAMIC FRICTION EVALUATION
4. DOMAIN-SPECIFIC VALIDATION
5. EXECUTION
6. AUDIT / RECOVERY
~~~

If the policy engine denies an action, low friction cannot authorize it.

~~~text
DENY > TRUST
CONSENT > CONVENIENCE
HARD_INVARIANT > LEARNED_SHORTCUT
~~~

## Recovery rule

When a new variable appears, an anomaly is observed, or required evidence cannot be verified:

~~~text
RESET_OPERATIONAL_TRUST
RAISE_FRICTION
PRESERVE_EVIDENCE
FAIL_CLOSED_WHERE_CONSEQUENTIAL
~~~

This is the equilibrium valve: agility when consequences are low, with evidence demand rising as consequence, novelty, and uncertainty rise.
