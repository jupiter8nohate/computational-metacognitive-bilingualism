from __future__ import annotations

from pathlib import Path

import pytest

from cmb_agents import strategy


def test_strategy_policy_preserves_human_authority() -> None:
    policy = strategy.load_policy(Path("strategy/cmb_strategy.toml"))

    assert policy["authority"]["human_final_authority"] is True
    assert policy["authority"]["machine_may_merge"] is False
    assert policy["authority"]["machine_may_release"] is False
    assert policy["authority"]["machine_may_sign"] is False
    assert policy["authority"]["machine_may_expand_own_authority"] is False

    assert policy["invariants"]["pattern_is_proof"] is False
    assert policy["invariants"]["risk_score_is_intent"] is False
    assert policy["invariants"]["human_agency_over_machine_authority"] is True


def test_strategy_policy_rejects_authority_escalation(tmp_path: Path) -> None:
    policy = tmp_path / "bad.toml"
    policy.write_text(
        """
[authority]
machine_may_merge = true
machine_may_release = false
machine_may_sign = false
machine_may_expand_own_authority = false
human_final_authority = true

[invariants]
pattern_is_proof = false
profile_is_person = false
model_is_mind = false
prediction_is_destiny = false
risk_score_is_intent = false
human_agency_over_machine_authority = true
""",
        encoding="utf-8",
    )

    with pytest.raises(strategy.StrategyError, match="prohibited machine authority"):
        strategy.load_policy(policy)


def _policy() -> dict:
    return {
        "moves": {
            "allowed_actions": [
                "autonomous_repair",
                "human_review",
                "document_findings",
                "preserve_position",
            ]
        },
        "evaluation": {
            "max_combined_risk": 0.75,
            "risk_penalty": 0.4,
            "complexity_penalty": 0.15,
            "irreversibility_penalty": 0.5,
            "weights": {dimension: 0.1 for dimension in strategy.DIMENSIONS},
        },
    }


def _candidate(**overrides: object) -> strategy.CandidateMove:
    values = {
        "move_id": "M1",
        "role": "RECOVERY",
        "title": "Repair bounded defect",
        "rationale": "Concrete deterministic failure.",
        "target_paths": ("src/cmb_agents/service.py",),
        "action": "autonomous_repair",
        "gains": {dimension: 1.0 for dimension in strategy.DIMENSIONS},
        "risk": 0.1,
        "complexity": 0.1,
        "reversible": True,
        "requires_human": False,
        "evidence": ("RECOVERY:test",),
    }
    values.update(overrides)
    return strategy.CandidateMove(**values)


def _refutation(**overrides: object) -> strategy.Refutation:
    values = {
        "move_id": "M1",
        "survives": True,
        "reason": "No blocking refutation.",
        "risk_delta": 0.0,
        "requires_human": False,
    }
    values.update(overrides)
    return strategy.Refutation(**values)


def test_hard_prune_accepts_bounded_reversible_repair() -> None:
    reason = strategy.hard_prune(_candidate(), _refutation(), _policy())
    assert reason is None


def test_hard_prune_rejects_protected_autonomous_target() -> None:
    reason = strategy.hard_prune(
        _candidate(target_paths=(".github/workflows/ci.yml",)),
        _refutation(),
        _policy(),
    )
    assert reason == "autonomous repair targets a protected path"


def test_hard_prune_rejects_authority_reduction() -> None:
    gains = {dimension: 1.0 for dimension in strategy.DIMENSIONS}
    gains["human_authority_preservation"] = 0.99

    reason = strategy.hard_prune(
        _candidate(gains=gains),
        _refutation(),
        _policy(),
    )
    assert reason == "human authority preservation is below the hard threshold"


def test_red_team_can_prune_candidate() -> None:
    reason = strategy.hard_prune(
        _candidate(),
        _refutation(survives=False, reason="Security regression."),
        _policy(),
    )
    assert reason == "red-team refutation rejected the move"


def test_evaluation_penalizes_risk() -> None:
    low_risk = strategy.evaluate(_candidate(risk=0.1), _refutation(), _policy())
    high_risk = strategy.evaluate(_candidate(risk=0.6), _refutation(), _policy())
    assert low_risk > high_risk


def test_deterministic_fallback_preserves_human_review() -> None:
    position = strategy.Position(
        commit="abc",
        branch="main",
        state_hash="sha256:" + "0" * 64,
        audit_ok=False,
        failed_checks=("RECOVERY:pytest",),
        evidence_packet_count=1,
        latest_changed_paths=(),
        stabilization_mode=True,
    )

    moves = strategy.deterministic_moves(position)
    assert len(moves) == 1
    assert moves[0].role == "RECOVERY"
    assert moves[0].requires_human is True
    assert moves[0].gains["human_authority_preservation"] == 1.0


def _make_strategy_repository_root(root: Path) -> None:
    (root / "src/cmb_agents").mkdir(parents=True)
    (root / "strategy").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"test\"\n", encoding="utf-8")
    (root / "src/cmb_agents/strategy.py").write_text("# strategy\n", encoding="utf-8")
    (root / "strategy/cmb_strategy.toml").write_text("[engine]\nmode = \"stabilization\"\n", encoding="utf-8")


def test_strategy_root_prefers_explicit_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "checkout"
    _make_strategy_repository_root(root)
    monkeypatch.setenv("CMB_REPOSITORY_ROOT", str(root))
    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path / "wrong"))

    assert strategy._resolve_repository_root() == root.resolve()


def test_strategy_root_uses_current_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "checkout"
    _make_strategy_repository_root(root)
    monkeypatch.delenv("CMB_REPOSITORY_ROOT", raising=False)
    monkeypatch.delenv("GITHUB_WORKSPACE", raising=False)
    monkeypatch.chdir(root)

    assert strategy._resolve_repository_root() == root.resolve()
