from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cmb_policy.authorization import (
    AuthorizationError,
    AuthorizationToken,
    create_authorization,
    generate_ed25519_keypair,
    verify_authorization,
    write_keypair,
)
from cmb_policy.runtime import (
    FrictionMode,
    RuntimePolicy,
    RuntimePolicyError,
    VerificationState,
    assess_operation,
    require_transition,
)


POLICY = """
[cmb]
protocol = "cmb.sovereignty-runtime.v1"
default_friction = 0.20
high_friction_threshold = 0.75
critical_threshold = 0.90

[principles]
pattern_is_proof = false
profile_is_person = false
model_is_mind = false
prediction_is_destiny = false
human_agency_over_machine_authority = true

[operations.creative]
criticality = 0.10
reversible = true
controls = []

[operations.deploy]
criticality = 0.95
reversible = false
controls = ["reproducible_build"]
"""


def _policy(tmp_path: Path) -> RuntimePolicy:
    path = tmp_path / "cmb.toml"
    path.write_text(POLICY, encoding="utf-8")
    return RuntimePolicy.load(path)


def test_low_friction_does_not_redefine_proof(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    result = assess_operation(policy, "creative")
    assert result.allowed
    assert result.mode is FrictionMode.LOW_FRICTION
    assert "PATTERN != PROOF" in result.to_dict()["invariants"]


def test_high_friction_fails_closed_without_controls(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    result = assess_operation(policy, "deploy")
    assert not result.allowed
    assert result.mode is FrictionMode.HIGH_FRICTION
    assert "AUTHORIZATION_REQUIRED" in result.failures
    assert "EVIDENCE_REQUIRED:isolated_verification" in result.failures
    assert "EVIDENCE_REQUIRED:reproducible_build" in result.failures
    assert "EVIDENCE_REQUIRED:two_party_review" in result.failures


def test_unknown_operation_fails_closed(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    result = assess_operation(policy, "invented_operation")
    assert not result.allowed
    assert result.criticality == 1.0
    assert result.failures == ("UNKNOWN_OPERATION_FAIL_CLOSED",)


def test_verification_state_cannot_jump() -> None:
    require_transition(VerificationState.FIX_COMMITTED, VerificationState.FIX_TESTED)
    with pytest.raises(RuntimePolicyError):
        require_transition(VerificationState.FIX_COMMITTED, VerificationState.FIX_VERIFIED)


def test_signed_authorization_is_scope_bound(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    private_key, public_key = generate_ed25519_keypair()
    subject_digest = "sha256:" + hashlib.sha256(b"artifact").hexdigest()
    now = datetime(2026, 9, 4, 18, 30, tzinfo=timezone.utc)
    token = create_authorization(
        operation="deploy",
        project="cmb/test",
        policy_digest=policy.digest,
        subject_digest=subject_digest,
        authorized_by="human-reviewer",
        controls=(
            "human_signature",
            "isolated_verification",
            "reproducible_build",
            "two_party_review",
        ),
        private_key_b64=private_key,
        ttl_seconds=3600,
        now=now,
    )
    ok, failures = verify_authorization(
        token,
        public_key_b64=public_key,
        operation="deploy",
        project="cmb/test",
        policy_digest=policy.digest,
        subject_digest=subject_digest,
        required_controls=(
            "human_signature",
            "isolated_verification",
            "reproducible_build",
            "two_party_review",
        ),
        now=now + timedelta(minutes=1),
    )
    assert ok
    assert failures == ()

    wrong, failures = verify_authorization(
        token,
        public_key_b64=public_key,
        operation="modify_permissions",
        project="cmb/test",
        policy_digest=policy.digest,
        subject_digest=subject_digest,
        required_controls=("human_signature",),
        now=now + timedelta(minutes=1),
    )
    assert not wrong
    assert "AUTH_OPERATION_MISMATCH" in failures


def test_expired_authorization_fails(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    private_key, public_key = generate_ed25519_keypair()
    subject_digest = "sha256:" + hashlib.sha256(b"artifact").hexdigest()
    now = datetime(2026, 9, 4, 18, 30, tzinfo=timezone.utc)
    token = create_authorization(
        operation="deploy",
        project="cmb/test",
        policy_digest=policy.digest,
        subject_digest=subject_digest,
        authorized_by="human-reviewer",
        controls=("human_signature",),
        private_key_b64=private_key,
        ttl_seconds=60,
        now=now,
    )
    ok, failures = verify_authorization(
        token,
        public_key_b64=public_key,
        operation="deploy",
        project="cmb/test",
        policy_digest=policy.digest,
        subject_digest=subject_digest,
        required_controls=("human_signature",),
        now=now + timedelta(minutes=2),
    )
    assert not ok
    assert "AUTH_EXPIRED" in failures


def _evidence_digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def test_nonempty_strings_do_not_satisfy_evidence_controls(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    result = assess_operation(
        policy,
        "deploy",
        evidence={
            "isolated_verification": "done",
            "reproducible_build": "yes",
            "two_party_review": "approved",
        },
    )

    assert not result.allowed
    assert "EVIDENCE_REFERENCE_INVALID:isolated_verification" in result.failures
    assert "EVIDENCE_REFERENCE_INVALID:reproducible_build" in result.failures
    assert "EVIDENCE_REFERENCE_INVALID:two_party_review" in result.failures


def test_content_addressed_evidence_and_scoped_authorization_can_pass(
    tmp_path: Path,
) -> None:
    policy = _policy(tmp_path)
    private_key, public_key = generate_ed25519_keypair()
    subject_digest = _evidence_digest("artifact")
    required_controls = (
        "human_signature",
        "isolated_verification",
        "reproducible_build",
        "two_party_review",
    )
    token = create_authorization(
        operation="deploy",
        project="cmb/test",
        policy_digest=policy.digest,
        subject_digest=subject_digest,
        authorized_by="human-reviewer",
        controls=required_controls,
        private_key_b64=private_key,
    )

    result = assess_operation(
        policy,
        "deploy",
        evidence={
            "isolated_verification": _evidence_digest("isolated"),
            "reproducible_build": _evidence_digest("build"),
            "two_party_review": _evidence_digest("review"),
        },
        authorization=token,
        public_key_b64=public_key,
        project="cmb/test",
        subject_digest=subject_digest,
    )

    assert result.allowed
    assert result.failures == ()


def test_keygen_refuses_to_overwrite_existing_key_files(tmp_path: Path) -> None:
    private_path = tmp_path / "human.key"
    public_path = tmp_path / "human.pub"
    write_keypair(private_path, public_path)
    original_private = private_path.read_text(encoding="utf-8")
    original_public = public_path.read_text(encoding="utf-8")

    with pytest.raises(AuthorizationError, match="Refusing to overwrite"):
        write_keypair(private_path, public_path)

    assert private_path.read_text(encoding="utf-8") == original_private
    assert public_path.read_text(encoding="utf-8") == original_public
