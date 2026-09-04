from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cmb_provenance.boundary import (
    BOUNDARY_AUTHORITY,
    BOUNDARY_SCHEMA_VERSION,
    BoundaryCode,
    BoundaryContext,
    BoundaryRejectedError,
    evaluate_boundary,
    require_boundary,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "cmb.boundary-event.v1.schema.json"


def test_default_context_is_allowed() -> None:
    decision = evaluate_boundary(BoundaryContext())
    assert decision.allowed is True
    assert decision.violations == ()
    assert decision.authority == BOUNDARY_AUTHORITY


def test_combined_policy_violations_are_deterministic() -> None:
    decision = evaluate_boundary(
        BoundaryContext(
            event_id="decision-42",
            consequential_decision=True,
            ai_involved=True,
            ai_disclosed=False,
            human_review_available=False,
            profile_treated_as_person=True,
            prediction_treated_as_destiny=True,
            consent_required=True,
            consent_present=False,
        )
    )

    assert decision.allowed is False
    assert [item.code for item in decision.violations] == [
        BoundaryCode.AI_DISCLOSURE_REQUIRED,
        BoundaryCode.HUMAN_REVIEW_REQUIRED,
        BoundaryCode.PROFILE_IS_NOT_PERSON,
        BoundaryCode.PREDICTION_IS_NOT_DESTINY,
        BoundaryCode.CONSENT_REQUIRED,
    ]
    assert decision.authority == "HUMAN_FINAL"


def test_require_boundary_raises_with_structured_decision() -> None:
    context = BoundaryContext(ai_involved=True, ai_disclosed=False)

    with pytest.raises(BoundaryRejectedError) as exc:
        require_boundary(context)

    assert exc.value.decision.allowed is False
    assert exc.value.decision.violations[0].code is BoundaryCode.AI_DISCLOSURE_REQUIRED


def test_context_rejects_blank_event_id() -> None:
    with pytest.raises(ValueError, match="event_id"):
        BoundaryContext(event_id="   ")


def test_boundary_event_matches_public_json_schema() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    payload = BoundaryContext(
        event_id="example",
        consequential_decision=True,
        ai_involved=True,
        ai_disclosed=True,
        human_review_available=True,
        consent_required=True,
        consent_present=True,
    ).to_dict()

    assert payload["schema_version"] == BOUNDARY_SCHEMA_VERSION
    Draft202012Validator(schema).validate(payload)


def test_context_rejects_non_boolean_policy_facts() -> None:
    with pytest.raises(TypeError, match="ai_involved"):
        BoundaryContext(ai_involved=1)  # type: ignore[arg-type]


def test_context_rejects_non_string_event_id() -> None:
    with pytest.raises(TypeError, match="event_id"):
        BoundaryContext(event_id=42)  # type: ignore[arg-type]


def test_boundary_decision_cannot_override_human_authority() -> None:
    from cmb_provenance.boundary import BoundaryDecision

    with pytest.raises(TypeError):
        BoundaryDecision(allowed=True, violations=(), authority="MACHINE_FINAL")  # type: ignore[call-arg]


def test_boundary_decision_rejects_inconsistent_allowed_state() -> None:
    from cmb_provenance.boundary import BoundaryDecision, BoundaryViolation

    violation = BoundaryViolation(
        code=BoundaryCode.PROFILE_IS_NOT_PERSON,
        invariant="PROFILE != PERSON",
        message="test",
    )
    with pytest.raises(ValueError, match="allowed"):
        BoundaryDecision(allowed=True, violations=(violation,))
