from __future__ import annotations

import pytest

from cmb_agents.strategy import (
    CandidateMove,
    MoveKind,
    Position,
    choose_best_move,
    evaluate_move,
)


def position(**overrides: float) -> Position:
    values = {
        "evidence_strength": 0.9,
        "invariant_alignment": 1.0,
        "reversibility": 0.9,
        "test_coverage": 0.8,
        "provenance_quality": 0.9,
        "authority_escalation": 0.0,
        "unsupported_claims": 0.0,
        "regression_risk": 0.1,
        "uncertainty": 0.1,
    }
    values.update(overrides)
    return Position(**values)


def test_rejects_unsupported_claim() -> None:
    evaluated = evaluate_move(
        CandidateMove(
            kind=MoveKind.PROPOSE_FIX,
            position=position(unsupported_claims=0.2),
            rationale="Claim exceeds available evidence.",
        )
    )

    assert not evaluated.allowed
    assert "unsupported_claim" in evaluated.violations


def test_human_gate_requires_escalation() -> None:
    evaluated = evaluate_move(
        CandidateMove(
            kind=MoveKind.PROPOSE_FIX,
            position=position(),
            rationale="Consequential semantic change.",
            requires_human=True,
        )
    )

    assert not evaluated.allowed
    assert "human_gate_required" in evaluated.violations


def test_selects_highest_scoring_allowed_move() -> None:
    observe = CandidateMove(
        kind=MoveKind.OBSERVE,
        position=position(evidence_strength=0.5, uncertainty=0.5),
        rationale="Gather more evidence.",
    )
    verify = CandidateMove(
        kind=MoveKind.VERIFY,
        position=position(),
        rationale="Run deterministic checks.",
    )

    selected = choose_best_move([observe, verify])

    assert selected.allowed
    assert selected.move.kind is MoveKind.VERIFY


def test_fails_closed_to_human_escalation() -> None:
    unsafe = CandidateMove(
        kind=MoveKind.PROPOSE_FIX,
        position=position(unsupported_claims=1.0),
        rationale="Unsafe proposal.",
    )

    selected = choose_best_move([unsafe])

    assert selected.allowed
    assert selected.move.kind is MoveKind.ESCALATE
    assert selected.move.requires_human


def test_position_rejects_out_of_range_values() -> None:
    with pytest.raises(ValueError):
        position(evidence_strength=1.1)
