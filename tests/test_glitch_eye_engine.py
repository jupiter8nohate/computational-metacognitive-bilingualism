from __future__ import annotations

import pytest

from cmb_agents.eyes import (
    EXPERIMENTAL,
    OBSERVE_ONLY,
    Eye,
    Perception,
    build_default_engine,
    propose_composite_eye,
)


def test_semantic_parallax_requires_two_views() -> None:
    engine = build_default_engine()
    state = {
        "semantic_contradictions": [
            {
                "files": ["README.md", "docs/contract.md"],
                "confidence": 0.92,
                "description": "The same invariant is defined differently.",
            },
            {
                "files": ["README.md"],
                "confidence": 0.99,
                "description": "Only one view exists.",
            },
        ]
    }

    observations = engine.perceive(Eye.STEREO, state)

    assert len(observations) == 1
    assert observations[0].detector == "semantic_parallax"
    assert observations[0].evidence == ("README.md", "docs/contract.md")


def test_hidden_coupling_filters_explicit_dependencies() -> None:
    engine = build_default_engine()
    state = {
        "cochange_relations": [
            {
                "file_a": "schemas/cmb.json",
                "file_b": "src/cmb_agents/validator.py",
                "score": 0.94,
                "explicit_dependency": False,
            },
            {
                "file_a": "a.py",
                "file_b": "b.py",
                "score": 0.99,
                "explicit_dependency": True,
            },
        ]
    }

    observations = engine.perceive(Eye.HIDDEN_CONTEXT, state)

    assert len(observations) == 1
    assert observations[0].confidence == pytest.approx(0.94)
    assert observations[0].evidence == (
        "schemas/cmb.json",
        "src/cmb_agents/validator.py",
    )


def test_temporal_eye_preserves_evidence() -> None:
    engine = build_default_engine()
    state = {
        "provenance_drift": [
            {
                "artifacts": ["commit:a1", "commit:b2", "docs/invariant.md"],
                "confidence": 0.88,
                "description": "A one-character operator change altered the invariant.",
            }
        ]
    }

    observations = engine.perceive(Eye.TEMPORAL, state)

    assert len(observations) == 1
    assert observations[0].detector == "provenance_drift"
    assert observations[0].evidence[0] == "commit:a1"


def test_fusion_is_deterministic_and_deduplicated() -> None:
    engine = build_default_engine()
    state = {
        "semantic_contradictions": [
            {
                "files": ["a.md", "b.md"],
                "confidence": 0.90,
                "description": "Two definitions conflict.",
            },
            {
                "files": ["a.md", "b.md"],
                "confidence": 0.90,
                "description": "Two definitions conflict.",
            },
        ],
        "cochange_relations": [
            {
                "file_a": "x.py",
                "file_b": "y.py",
                "score": 0.95,
                "explicit_dependency": False,
            }
        ],
    }

    first = engine.fusion((Eye.STEREO, Eye.HIDDEN_CONTEXT), state)
    second = engine.fusion((Eye.HIDDEN_CONTEXT, Eye.STEREO), state)

    assert first == second
    assert len(first) == 2
    assert first[0].confidence == pytest.approx(0.95)


def test_new_eye_proposal_is_observe_only_and_experimental() -> None:
    perceptions = (
        Perception(
            eye=Eye.STEREO,
            detector="semantic_parallax",
            evidence=("a.md", "b.md"),
            confidence=0.91,
            hypothesis="Definitions conflict.",
        ),
        Perception(
            eye=Eye.HIDDEN_CONTEXT,
            detector="hidden_coupling",
            evidence=("a.md", "validator.py"),
            confidence=0.87,
            hypothesis="Files change together.",
        ),
        Perception(
            eye=Eye.TEMPORAL,
            detector="provenance_drift",
            evidence=("commit:a1", "commit:b2"),
            confidence=0.84,
            hypothesis="Meaning changed over time.",
        ),
    )

    proposal = propose_composite_eye(
        perceptions,
        glyph="𓂀⃤",
        name="STRUCTURAL_ECHO",
    )

    assert proposal is not None
    assert proposal.authority == OBSERVE_ONLY
    assert proposal.status == EXPERIMENTAL
    assert proposal.confidence == pytest.approx(0.84)
    assert proposal.logic_expression == (
        "hidden_coupling AND provenance_drift AND semantic_parallax"
    )


def test_new_eye_proposal_fails_closed_without_independent_support() -> None:
    perceptions = (
        Perception(
            eye=Eye.STEREO,
            detector="semantic_parallax",
            evidence=("a.md", "b.md"),
            confidence=0.95,
            hypothesis="Definitions conflict.",
        ),
    )

    assert (
        propose_composite_eye(
            perceptions,
            glyph="𓂀⃤",
            name="STRUCTURAL_ECHO",
        )
        is None
    )


def test_perception_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        Perception(
            eye=Eye.WITNESS,
            detector="witness",
            evidence=("README.md",),
            confidence=1.1,
            hypothesis="Observed.",
        )
