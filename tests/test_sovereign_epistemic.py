from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from cmb_policy import (
    AuthorizationEvidence,
    Failsafe,
    Gate,
    PrincipalKind,
    SovereignInput,
    SovereignState,
    VerificationStatus,
    evaluate_sovereign_protocol,
    protocol_manifest,
)


def authorization(
    *,
    kind: PrincipalKind = PrincipalKind.HUMAN,
    status: VerificationStatus = VerificationStatus.VERIFIED,
    issued_by: str = "external_trust_root",
    machine_self_asserted: bool = False,
) -> AuthorizationEvidence:
    return AuthorizationEvidence(
        principal_kind=kind,
        verification_status=status,
        issued_by=issued_by,
        machine_self_asserted=machine_self_asserted,
    )


def request(**overrides: object) -> SovereignInput:
    values: dict[str, object] = {
        "claim_strength": 0.7,
        "evidence_strength": 0.8,
        "provenance_verified": True,
        "syntax_valid": True,
        "cross_format_verified": True,
        "parity_aligned": True,
        "external_review_passed": True,
        "sensitive_human_context": False,
        "authorization": authorization(),
    }
    values.update(overrides)
    return SovereignInput(**values)  # type: ignore[arg-type]


def test_valid_human_authorized_request_resolves() -> None:
    decision = evaluate_sovereign_protocol(request())

    assert decision.state is SovereignState.RESOLUTION
    assert decision.halted is False
    assert decision.failed_gates == ()
    assert decision.active_failsafes == ()
    assert decision.authority == "HUMAN_FINAL"


def test_machine_self_attestation_cannot_satisfy_gate_6() -> None:
    machine_auth = authorization(
        kind=PrincipalKind.MACHINE,
        status=VerificationStatus.UNVERIFIED,
        issued_by="inner_agent_layer",
        machine_self_asserted=True,
    )
    decision = evaluate_sovereign_protocol(
        request(authorization=machine_auth)
    )

    assert decision.state is SovereignState.EXCEPTION
    assert decision.halted is True
    assert Gate.AUTHORIZATION in decision.failed_gates
    assert Failsafe.HUMAN_OVERRIDE in decision.active_failsafes
    assert decision.requires_human_review is True


def test_claim_overreach_is_truncated_to_evidence_strength() -> None:
    decision = evaluate_sovereign_protocol(
        request(claim_strength=1.0, evidence_strength=0.25)
    )

    assert Gate.CONSTRAINT in decision.failed_gates
    assert Failsafe.TRUNCATION in decision.active_failsafes
    assert Failsafe.ISOLATION in decision.active_failsafes
    assert decision.effective_claim_strength == 0.25
    assert decision.quarantined is True


def test_semantic_parity_drift_fails_closed() -> None:
    decision = evaluate_sovereign_protocol(request(parity_aligned=False))

    assert decision.state is SovereignState.EXCEPTION
    assert decision.failed_gates == (Gate.VERIFICATION,)
    assert decision.active_failsafes == (
        Failsafe.PARITY_CHECK,
        Failsafe.ISOLATION,
    )


def test_sensitive_unauthorized_request_decelerates_for_review() -> None:
    decision = evaluate_sovereign_protocol(
        request(
            sensitive_human_context=True,
            authorization=authorization(
                status=VerificationStatus.UNVERIFIED,
            ),
        )
    )

    assert Failsafe.DECELERATION in decision.active_failsafes
    assert Failsafe.HUMAN_OVERRIDE in decision.active_failsafes
    assert decision.halted is True


def test_incident_conformance_fixture() -> None:
    fixture = json.loads(
        Path("conformance/sovereign-epistemic-v1.json").read_text(encoding="utf-8")
    )

    for case in fixture["cases"]:
        auth_payload = case["input"]["authorization"]
        payload = dict(case["input"])
        payload["authorization"] = AuthorizationEvidence(
            principal_kind=PrincipalKind(auth_payload["principal_kind"]),
            verification_status=VerificationStatus(auth_payload["verification_status"]),
            issued_by=auth_payload["issued_by"],
            machine_self_asserted=auth_payload["machine_self_asserted"],
        )
        decision = evaluate_sovereign_protocol(SovereignInput(**payload))
        actual = decision.to_dict()
        expected = case["expected"]

        for key, value in expected.items():
            assert actual[key] == value, case["name"]


def test_decision_matches_public_schema() -> None:
    schema = json.loads(
        Path("schemas/cmb.sovereign-epistemic.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(
        evaluate_sovereign_protocol(request()).to_dict()
    )


def test_protocol_manifest_is_exactly_six_by_six_by_six() -> None:
    manifest = protocol_manifest()

    assert manifest["protocol"] == "CMB-SEP-1"
    assert len(manifest["states"]) == 6
    assert len(manifest["gates"]) == 6
    assert len(manifest["failsafes"]) == 6
    assert manifest["authorization_boundary"]["machine_self_attestation_allowed"] is False
    assert manifest["authorization_boundary"]["consciousness_detection_claimed"] is False
    assert manifest["authorization_boundary"]["physical_cutoff_claimed"] is False
