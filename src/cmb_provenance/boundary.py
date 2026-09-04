"""Explicit policy-boundary evaluation for CMB integrations.

The evaluator consumes facts supplied by application code. It does not infer a
person's identity, intent, diagnosis, mental state, or moral status from content.
That distinction is deliberate: policy enforcement should be auditable, while
human meaning remains a human authority boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from .errors import CMBProvenanceError

BOUNDARY_SCHEMA_VERSION: Final = "cmb.boundary-event.v1"
BOUNDARY_AUTHORITY: Final = "HUMAN_FINAL"


class BoundaryCode(str, Enum):
    """Stable machine-readable rejection codes."""

    AI_DISCLOSURE_REQUIRED = "AI_DISCLOSURE_REQUIRED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    PROFILE_IS_NOT_PERSON = "PROFILE_IS_NOT_PERSON"
    PREDICTION_IS_NOT_DESTINY = "PREDICTION_IS_NOT_DESTINY"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"


@dataclass(frozen=True, slots=True)
class BoundaryContext:
    """Explicit facts an application asks the CMB boundary engine to evaluate."""

    event_id: str | None = None
    consequential_decision: bool = False
    ai_involved: bool = False
    ai_disclosed: bool = False
    human_review_available: bool = False
    profile_treated_as_person: bool = False
    prediction_treated_as_destiny: bool = False
    consent_required: bool = False
    consent_present: bool = False

    def __post_init__(self) -> None:
        if self.event_id is not None:
            if not isinstance(self.event_id, str):
                raise TypeError("event_id must be a string or None")
            if not self.event_id.strip():
                raise ValueError("event_id must be non-empty when supplied")

        boolean_fields = (
            "consequential_decision",
            "ai_involved",
            "ai_disclosed",
            "human_review_available",
            "profile_treated_as_person",
            "prediction_treated_as_destiny",
            "consent_required",
            "consent_present",
        )
        for field_name in boolean_fields:
            if type(getattr(self, field_name)) is not bool:
                raise TypeError(f"{field_name} must be bool")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": BOUNDARY_SCHEMA_VERSION,
            "event_id": self.event_id,
            "consequential_decision": self.consequential_decision,
            "ai_involved": self.ai_involved,
            "ai_disclosed": self.ai_disclosed,
            "human_review_available": self.human_review_available,
            "profile_treated_as_person": self.profile_treated_as_person,
            "prediction_treated_as_destiny": self.prediction_treated_as_destiny,
            "consent_required": self.consent_required,
            "consent_present": self.consent_present,
        }


@dataclass(frozen=True, slots=True)
class BoundaryViolation:
    code: BoundaryCode
    invariant: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code.value,
            "invariant": self.invariant,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class BoundaryDecision:
    allowed: bool
    violations: tuple[BoundaryViolation, ...]
    authority: str = field(default=BOUNDARY_AUTHORITY, init=False)

    def __post_init__(self) -> None:
        if type(self.allowed) is not bool:
            raise TypeError("allowed must be bool")
        if not isinstance(self.violations, tuple):
            raise TypeError("violations must be a tuple")
        if self.allowed != (len(self.violations) == 0):
            raise ValueError("allowed must be true exactly when violations is empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "authority": self.authority,
            "violations": [item.to_dict() for item in self.violations],
        }


class BoundaryRejectedError(CMBProvenanceError):
    """Raised when require_boundary() receives a rejected policy context."""

    def __init__(self, decision: BoundaryDecision) -> None:
        self.decision = decision
        codes = ", ".join(item.code.value for item in decision.violations)
        super().__init__(f"CMB boundary rejected event: {codes}")


def evaluate_boundary(context: BoundaryContext) -> BoundaryDecision:
    """Evaluate explicit policy facts without performing behavioral inference."""

    if not isinstance(context, BoundaryContext):
        raise TypeError("context must be a BoundaryContext")

    violations: list[BoundaryViolation] = []

    if context.ai_involved and not context.ai_disclosed:
        violations.append(
            BoundaryViolation(
                code=BoundaryCode.AI_DISCLOSURE_REQUIRED,
                invariant="CAPABILITY != AUTHORITY",
                message="AI involvement must be disclosed when this boundary policy requires transparency.",
            )
        )

    if context.consequential_decision and not context.human_review_available:
        violations.append(
            BoundaryViolation(
                code=BoundaryCode.HUMAN_REVIEW_REQUIRED,
                invariant="HUMAN_AGENCY > MACHINE_AUTHORITY",
                message="Consequential automated decisions require an available human review path.",
            )
        )

    if context.profile_treated_as_person:
        violations.append(
            BoundaryViolation(
                code=BoundaryCode.PROFILE_IS_NOT_PERSON,
                invariant="PROFILE != PERSON",
                message="A profile may inform a workflow but must not be treated as the person itself.",
            )
        )

    if context.prediction_treated_as_destiny:
        violations.append(
            BoundaryViolation(
                code=BoundaryCode.PREDICTION_IS_NOT_DESTINY,
                invariant="PREDICTION != DESTINY",
                message="A prediction must not be treated as an inevitable human outcome.",
            )
        )

    if context.consent_required and not context.consent_present:
        violations.append(
            BoundaryViolation(
                code=BoundaryCode.CONSENT_REQUIRED,
                invariant="ATTENTION != CONSENT",
                message="The declared operation requires consent before it may proceed.",
            )
        )

    frozen = tuple(violations)
    return BoundaryDecision(allowed=not frozen, violations=frozen)


def require_boundary(context: BoundaryContext) -> BoundaryDecision:
    """Return an allowed decision or raise BoundaryRejectedError."""

    decision = evaluate_boundary(context)
    if not decision.allowed:
        raise BoundaryRejectedError(decision)
    return decision
