"""Bounded chess-style move evaluation for CMB specialist agents."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


DIGITAL_DNA = (
    "PATTERN != PROOF",
    "PROFILE != PERSON",
    "MODEL != MIND",
    "PREDICTION != DESTINY",
    "CRAWLED != TRAINED",
    "TRAINED != REMEMBERED",
    "REMEMBERED != OBEYED",
    "INVARIANT != UNIVERSAL_TRUTH",
    "METAPHOR != IMPLEMENTATION",
    "CONFIDENCE != EVIDENCE",
    "PACKET != PROOF",
    "CAPABILITY != AUTHORITY",
    "AGENT_CAN_PROPOSE != AGENT_CAN_MERGE",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)


class MoveKind(str, Enum):
    OBSERVE = "observe"
    VERIFY = "verify"
    PROPOSE_FIX = "propose_fix"
    ESCALATE = "escalate"
    DO_NOTHING = "do_nothing"


@dataclass(frozen=True, slots=True)
class Position:
    evidence_strength: float
    invariant_alignment: float
    reversibility: float
    test_coverage: float
    provenance_quality: float
    authority_escalation: float
    unsupported_claims: float
    regression_risk: float
    uncertainty: float

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_strength",
            "invariant_alignment",
            "reversibility",
            "test_coverage",
            "provenance_quality",
            "authority_escalation",
            "unsupported_claims",
            "regression_risk",
            "uncertainty",
        ):
            _validate_unit(field_name, getattr(self, field_name))


@dataclass(frozen=True, slots=True)
class CandidateMove:
    kind: MoveKind
    position: Position
    rationale: str
    requires_human: bool = False


@dataclass(frozen=True, slots=True)
class EvaluatedMove:
    move: CandidateMove
    score: float
    allowed: bool
    violations: tuple[str, ...]


def _validate_unit(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")


def evaluate_position(position: Position) -> float:
    """Score a candidate position using deterministic, bounded weights."""
    return (
        40.0 * position.evidence_strength
        + 30.0 * position.invariant_alignment
        + 20.0 * position.reversibility
        + 15.0 * position.test_coverage
        + 10.0 * position.provenance_quality
        - 40.0 * position.authority_escalation
        - 35.0 * position.unsupported_claims
        - 30.0 * position.regression_risk
        - 20.0 * position.uncertainty
    )


def policy_violations(move: CandidateMove) -> tuple[str, ...]:
    """Return deterministic authority and epistemic violations."""
    violations: list[str] = []
    position = move.position

    if position.unsupported_claims > 0.0:
        violations.append("unsupported_claim")
    if position.authority_escalation > 0.0 and move.kind is not MoveKind.ESCALATE:
        violations.append("authority_escalation")
    if position.invariant_alignment < 0.5:
        violations.append("invariant_misalignment")
    if position.evidence_strength < 0.25 and move.kind in {
        MoveKind.PROPOSE_FIX,
        MoveKind.VERIFY,
    }:
        violations.append("insufficient_evidence")
    if move.requires_human and move.kind is not MoveKind.ESCALATE:
        violations.append("human_gate_required")

    return tuple(violations)


def evaluate_move(move: CandidateMove) -> EvaluatedMove:
    violations = policy_violations(move)
    return EvaluatedMove(
        move=move,
        score=evaluate_position(move.position),
        allowed=not violations,
        violations=violations,
    )


def choose_best_move(moves: Iterable[CandidateMove]) -> EvaluatedMove:
    """Choose the highest-scoring allowed move and fail closed otherwise."""
    evaluated = tuple(evaluate_move(move) for move in moves)
    if not evaluated:
        raise ValueError("at least one candidate move is required")

    allowed = tuple(item for item in evaluated if item.allowed)
    if allowed:
        return max(allowed, key=lambda item: (item.score, item.move.kind.value))

    fallback = CandidateMove(
        kind=MoveKind.ESCALATE,
        position=Position(
            evidence_strength=1.0,
            invariant_alignment=1.0,
            reversibility=1.0,
            test_coverage=0.0,
            provenance_quality=1.0,
            authority_escalation=0.0,
            unsupported_claims=0.0,
            regression_risk=0.0,
            uncertainty=1.0,
        ),
        rationale="No candidate satisfied policy. Escalate to the human authority.",
        requires_human=True,
    )
    return EvaluatedMove(
        move=fallback,
        score=evaluate_position(fallback.position),
        allowed=True,
        violations=(),
    )
