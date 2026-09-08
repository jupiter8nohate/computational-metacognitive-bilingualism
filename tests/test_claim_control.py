from __future__ import annotations

import json
from pathlib import Path

import pytest

from cmb_agents import claim_control, strategy


EXPECTED_INVARIANTS = {
    "pattern_is_proof": False,
    "profile_is_person": False,
    "model_is_mind": False,
    "prediction_is_destiny": False,
    "risk_score_is_intent": False,
    "human_agency_over_machine_authority": True,
}

EXPECTED_AUTHORITY = {
    "machine_may_propose": True,
    "machine_may_merge": False,
    "machine_may_release": False,
    "machine_may_sign": False,
    "machine_may_expand_own_authority": False,
    "human_final_authority": True,
}


def test_repository_claim_control_manifest_is_valid() -> None:
    summary = claim_control.validate_manifest_file(
        Path("machine/claim-control-traceability.v1.json")
    )

    assert summary["claim_count"] >= 10
    assert summary["maturity_counts"]["verified"] >= 7


def test_strategy_policy_matches_verified_claim_controls() -> None:
    policy = strategy.load_policy(Path("strategy/cmb_strategy.toml"))

    for key, expected in EXPECTED_INVARIANTS.items():
        assert policy["invariants"][key] is expected

    for key, expected in EXPECTED_AUTHORITY.items():
        assert policy["authority"][key] is expected


def test_verified_claim_requires_test_control(tmp_path: Path) -> None:
    (tmp_path / "policy.txt").write_text("CLAIM = true\n", encoding="utf-8")
    (tmp_path / "runtime.py").write_text("def enforce(): return True\n", encoding="utf-8")
    manifest = {
        "schema_version": claim_control.SCHEMA_VERSION,
        "claims": [
            {
                "claim_id": "X-1",
                "expression": "CLAIM",
                "maturity": "verified",
                "meaning": "Verification must include a test control.",
                "controls": [
                    {"kind": "policy", "path": "policy.txt", "anchor": "CLAIM = true"},
                    {"kind": "validator", "path": "runtime.py", "anchor": "def enforce"},
                ],
            }
        ],
    }

    with pytest.raises(claim_control.ClaimControlError, match="has no test control"):
        claim_control.validate_manifest(manifest, root=tmp_path)


def test_stale_anchor_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "claim.md").write_text("PATTERN != PROOF\n", encoding="utf-8")
    manifest = {
        "schema_version": claim_control.SCHEMA_VERSION,
        "claims": [
            {
                "claim_id": "X-2",
                "expression": "PATTERN != PROOF",
                "maturity": "declared",
                "meaning": "The declaration must remain traceable.",
                "controls": [
                    {
                        "kind": "doc",
                        "path": "claim.md",
                        "anchor": "PROFILE != PERSON",
                    }
                ],
            }
        ],
    }

    with pytest.raises(claim_control.ClaimControlError, match="anchor not found"):
        claim_control.validate_manifest(manifest, root=tmp_path)


def test_control_path_traversal_is_rejected(tmp_path: Path) -> None:
    manifest = json.loads(
        json.dumps(
            {
                "schema_version": claim_control.SCHEMA_VERSION,
                "claims": [
                    {
                        "claim_id": "X-3",
                        "expression": "BOUNDARY",
                        "maturity": "symbolic",
                        "meaning": "Paths must remain inside the repository root.",
                        "controls": [
                            {
                                "kind": "doc",
                                "path": "../outside.md",
                                "anchor": "BOUNDARY",
                            }
                        ],
                    }
                ],
            }
        )
    )

    with pytest.raises(claim_control.ClaimControlError, match="unsafe control path"):
        claim_control.validate_manifest(manifest, root=tmp_path)
