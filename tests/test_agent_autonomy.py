from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from cmb_agents import autonomy
from cmb_agents.strategy import load_policy


def _policy() -> dict:
    return load_policy(Path("strategy/cmb_strategy.toml"))


def _audit(*, ok: bool) -> dict:
    return {
        "ok": ok,
        "checks": [] if ok else [{"role": "RECOVERY", "name": "pytest", "ok": False}],
        "evidence_packets": [],
    }


def _strategy_report(
    *,
    action: str = "autonomous_repair",
    target_paths: tuple[str, ...] = ("docs/example.md",),
    requires_human: bool = False,
    pruned: bool = False,
    survives: bool = True,
    reversible: bool = True,
    authority_gain: float = 1.0,
) -> dict:
    move_id = "M1"
    return {
        "selected_move_id": move_id,
        "selected_move_title": "Repair bounded defect",
        "selected_move_action": action,
        "selected_move_requires_human": requires_human,
        "evaluated_moves": [
            {
                "candidate": {
                    "move_id": move_id,
                    "role": "RECOVERY",
                    "title": "Repair bounded defect",
                    "rationale": "Concrete deterministic failure.",
                    "target_paths": list(target_paths),
                    "action": action,
                    "gains": {
                        "correctness": 1.0,
                        "security": 1.0,
                        "reproducibility": 1.0,
                        "interoperability": 1.0,
                        "provenance": 1.0,
                        "maintainability": 1.0,
                        "accessibility": 1.0,
                        "reversibility": 1.0,
                        "evidence_strength": 1.0,
                        "human_authority_preservation": authority_gain,
                    },
                    "risk": 0.1,
                    "complexity": 0.1,
                    "reversible": reversible,
                    "requires_human": requires_human,
                    "evidence": ["RECOVERY:pytest"],
                },
                "refutation": {
                    "move_id": move_id,
                    "survives": survives,
                    "reason": "No blocking refutation." if survives else "Blocked by Red Team.",
                    "risk_delta": 0.0,
                    "requires_human": requires_human,
                },
                "pruned": pruned,
                "prune_reason": None if not pruned else "policy",
                "score": 0.91,
            }
        ],
    }


def test_clean_position_preserves_state() -> None:
    report = {
        "selected_move_id": None,
        "selected_move_title": None,
        "selected_move_action": None,
        "selected_move_requires_human": False,
        "evaluated_moves": [],
    }

    decision = autonomy.decide(_audit(ok=True), report, _policy())

    assert decision.verdict == "PRESERVE_POSITION"
    assert decision.should_repair is False
    assert decision.requires_human is False


def test_safe_concrete_failure_can_reach_steward() -> None:
    decision = autonomy.decide(_audit(ok=False), _strategy_report(), _policy())

    assert decision.verdict == "PROPOSE_REPAIR"
    assert decision.should_repair is True
    assert decision.requires_human is False
    assert decision.target_paths == ("docs/example.md",)


def test_protected_target_fails_closed_to_human_review() -> None:
    decision = autonomy.decide(
        _audit(ok=False),
        _strategy_report(target_paths=(".github/workflows/ci.yml",)),
        _policy(),
    )

    assert decision.verdict == "HUMAN_REVIEW"
    assert decision.should_repair is False
    assert decision.requires_human is True
    assert "protected paths" in " ".join(decision.reasons)


def test_red_team_refutation_blocks_autonomous_repair() -> None:
    decision = autonomy.decide(
        _audit(ok=False),
        _strategy_report(survives=False),
        _policy(),
    )

    assert decision.verdict == "HUMAN_REVIEW"
    assert decision.should_repair is False
    assert decision.requires_human is True


def test_human_boundary_blocks_autonomous_repair() -> None:
    decision = autonomy.decide(
        _audit(ok=False),
        _strategy_report(requires_human=True),
        _policy(),
    )

    assert decision.verdict == "HUMAN_REVIEW"
    assert decision.should_repair is False
    assert decision.requires_human is True


def test_nonreversible_move_fails_closed() -> None:
    decision = autonomy.decide(
        _audit(ok=False),
        _strategy_report(reversible=False),
        _policy(),
    )

    assert decision.verdict == "HUMAN_REVIEW"
    assert decision.should_repair is False


def test_authority_score_is_permission_boundary() -> None:
    decision = autonomy.decide(
        _audit(ok=False),
        _strategy_report(authority_gain=0.99),
        _policy(),
    )

    assert decision.verdict == "HUMAN_REVIEW"
    assert decision.should_repair is False
    assert "authority preservation" in " ".join(decision.reasons)


def test_policy_must_remain_draft_pr_only() -> None:
    policy = deepcopy(_policy())
    policy["recovery"]["draft_pr_only"] = False

    with pytest.raises(autonomy.AutonomyError, match="draft-pr-only"):
        autonomy.decide(_audit(ok=False), _strategy_report(), policy)
