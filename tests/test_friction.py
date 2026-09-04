from __future__ import annotations

import pytest

from cmb_policy.friction import (
    EvidenceKind,
    EvidenceState,
    ExecutionDisposition,
    FrictionMode,
    FrictionRejectedError,
    TaskRiskProfile,
    TrustState,
    evaluate_friction,
    require_friction,
)


def test_low_risk_creative_task_stays_fluid() -> None:
    decision = evaluate_friction(
        TaskRiskProfile(
            task_id="creative-draft",
            intrinsic_criticality=0.10,
            uncertainty=0.20,
        )
    )
    assert decision.mode is FrictionMode.HIGH_AGILITY
    assert decision.disposition is ExecutionDisposition.EXECUTE_FLUID
    assert decision.allowed is True
    assert decision.caveats == ()


def test_balanced_mode_preserves_pattern_not_proof() -> None:
    decision = evaluate_friction(
        TaskRiskProfile(
            task_id="contextual-analysis",
            intrinsic_criticality=0.30,
            uncertainty=0.60,
        )
    )
    assert decision.mode is FrictionMode.BALANCED
    assert decision.disposition is ExecutionDisposition.EXECUTE_WITH_CAVEAT
    assert "PATTERN != PROOF" in decision.caveats


def test_high_safety_fails_closed_without_evidence() -> None:
    decision = evaluate_friction(
        TaskRiskProfile(
            task_id="production-release",
            intrinsic_criticality=0.90,
            external_side_effect=True,
            reversible=False,
            requires_integrity_receipt=True,
        )
    )
    assert decision.mode is FrictionMode.HIGH_SAFETY
    assert decision.disposition is ExecutionDisposition.HALT
    assert decision.missing_evidence == (
        EvidenceKind.HUMAN_REVIEW,
        EvidenceKind.INDEPENDENT_VERIFICATION,
        EvidenceKind.CRYPTOGRAPHIC_INTEGRITY,
    )


def test_high_safety_executes_when_all_required_evidence_passes() -> None:
    decision = evaluate_friction(
        TaskRiskProfile(
            task_id="production-release",
            intrinsic_criticality=0.90,
            requires_integrity_receipt=True,
        ),
        evidence=EvidenceState(
            human_review_confirmed=True,
            independent_verification_passed=True,
            cryptographic_integrity_verified=True,
        ),
    )
    assert decision.disposition is ExecutionDisposition.EXECUTE_VERIFIED
    assert decision.missing_evidence == ()


def test_trust_decays_uncertainty_but_not_intrinsic_risk() -> None:
    profile = TaskRiskProfile(
        task_id="stable-high-stakes-task",
        intrinsic_criticality=0.90,
        uncertainty=0.80,
    )
    decision = evaluate_friction(
        profile,
        trust=TrustState(successful_human_reviews=12),
        half_life_reviews=3,
    )
    assert decision.trusted_invariant is True
    assert decision.operational_criticality == pytest.approx(0.05)
    assert decision.effective_criticality == pytest.approx(0.90)
    assert decision.mode is FrictionMode.HIGH_SAFETY


def test_clean_reviews_can_return_low_intrinsic_task_to_agility() -> None:
    profile = TaskRiskProfile(
        task_id="repeat-formatting",
        intrinsic_criticality=0.10,
        uncertainty=0.80,
    )
    initial = evaluate_friction(profile)
    trusted = evaluate_friction(
        profile,
        trust=TrustState(successful_human_reviews=6),
        half_life_reviews=3,
    )
    assert initial.mode is FrictionMode.BALANCED
    assert trusted.operational_criticality == pytest.approx(0.20)
    assert trusted.mode is FrictionMode.HIGH_AGILITY
    assert trusted.trusted_invariant is True


def test_unknown_variable_resets_discount_and_spikes_friction() -> None:
    profile = TaskRiskProfile(
        task_id="repeat-formatting",
        intrinsic_criticality=0.10,
        uncertainty=0.35,
        unknown_variables=("new-parser-version", "new-output-target"),
    )
    decision = evaluate_friction(
        profile,
        trust=TrustState(successful_human_reviews=9),
    )
    assert decision.trust_discount == 1.0
    assert decision.trusted_invariant is False
    assert decision.operational_criticality == pytest.approx(0.75)
    assert decision.mode is FrictionMode.BALANCED


def test_anomaly_suspends_trust_discount() -> None:
    profile = TaskRiskProfile(
        task_id="repeat-transform",
        intrinsic_criticality=0.10,
        uncertainty=0.25,
    )
    decision = evaluate_friction(
        profile,
        trust=TrustState(successful_human_reviews=9, anomaly_count=1),
    )
    assert decision.trust_discount == 1.0
    assert decision.trusted_invariant is False
    assert decision.operational_criticality == pytest.approx(0.50)


def test_required_evidence_forces_high_safety_floor() -> None:
    decision = evaluate_friction(
        TaskRiskProfile(
            task_id="signed-artifact",
            intrinsic_criticality=0.10,
            requires_integrity_receipt=True,
        )
    )
    assert decision.intrinsic_floor == pytest.approx(0.81)
    assert decision.mode is FrictionMode.HIGH_SAFETY


def test_require_friction_raises_on_halt() -> None:
    with pytest.raises(FrictionRejectedError):
        require_friction(
            TaskRiskProfile(
                task_id="high-risk",
                intrinsic_criticality=1.0,
            )
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("intrinsic_criticality", -0.01),
        ("intrinsic_criticality", 1.01),
        ("uncertainty", float("nan")),
    ],
)
def test_profile_rejects_invalid_scalar_inputs(field: str, value: float) -> None:
    kwargs = {
        "task_id": "invalid",
        "intrinsic_criticality": 0.5,
        "uncertainty": 0.5,
    }
    kwargs[field] = value
    with pytest.raises(ValueError):
        TaskRiskProfile(**kwargs)


def test_decision_is_machine_readable() -> None:
    payload = evaluate_friction(
        TaskRiskProfile(
            task_id="machine-contract",
            intrinsic_criticality=0.1,
        )
    ).to_dict()
    assert payload["schema"] == "cmb.friction-decision.v1"
    assert payload["mode"] == "HIGH_AGILITY"
    assert payload["allowed"] is True
