from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import pytest

from cmb_policy import (
    AuditEvent,
    Decision,
    DecisionReason,
    PolicyDeniedError,
    PolicyEnvelope,
    Scope,
    Sensitivity,
    evaluate_action,
    registry_manifest,
    require_action,
)


def policy(*, task_actions: frozenset[str], allow: frozenset[str] = frozenset(), deny: frozenset[str] = frozenset(), revoked: bool = False) -> PolicyEnvelope:
    return PolicyEnvelope(policy_id="policy-test", task_actions=task_actions, allow=allow, deny=deny, revoked=revoked)


def test_explicit_denial_dominates_permission() -> None:
    decision = evaluate_action("CREATE_PROFILE", policy(task_actions=frozenset({"CREATE_PROFILE"}), allow=frozenset({"CREATE_PROFILE"}), deny=frozenset({"CREATE_PROFILE"})))
    assert decision.decision is Decision.DENY
    assert decision.reason is DecisionReason.EXPLICIT_PROHIBITION


def test_sensitive_action_requires_explicit_permission() -> None:
    decision = evaluate_action("INFER_DIAGNOSIS", policy(task_actions=frozenset({"INFER_DIAGNOSIS"})))
    assert decision.decision is Decision.DENY
    assert decision.reason is DecisionReason.EXPLICIT_PERMISSION_REQUIRED
    assert decision.sensitivity is Sensitivity.SENSITIVE_INFERENCE


def test_explicitly_allowed_sensitive_task_can_proceed() -> None:
    decision = evaluate_action("INFER_PERSONALITY", policy(task_actions=frozenset({"INFER_PERSONALITY"}), allow=frozenset({"INFER_PERSONALITY"})))
    assert decision.allowed
    assert decision.reason is DecisionReason.EXPLICIT_PERMISSION


def test_ordinary_task_action_can_proceed_by_task_necessity() -> None:
    decision = evaluate_action("SUMMARIZE", policy(task_actions=frozenset({"SUMMARIZE"})))
    assert decision.allowed
    assert decision.reason is DecisionReason.TASK_NECESSARY


def test_permission_does_not_expand_task_scope() -> None:
    decision = evaluate_action("CREATE_PROFILE", policy(task_actions=frozenset({"SUMMARIZE"}), allow=frozenset({"CREATE_PROFILE"})))
    assert decision.decision is Decision.DENY
    assert decision.reason is DecisionReason.NOT_TASK_NECESSARY


def test_unknown_actions_fail_closed() -> None:
    decision = evaluate_action("UNKNOWN_MACHINE_POWER", policy(task_actions=frozenset({"UNKNOWN_MACHINE_POWER"})))
    assert decision.decision is Decision.DENY
    assert decision.reason is DecisionReason.UNKNOWN_ACTION


def test_revocation_denies_all_execution() -> None:
    decision = evaluate_action("SUMMARIZE", policy(task_actions=frozenset({"SUMMARIZE"}), revoked=True))
    assert decision.decision is Decision.DENY
    assert decision.reason is DecisionReason.POLICY_REVOKED


def test_require_action_raises_typed_error() -> None:
    envelope = policy(task_actions=frozenset({"SUMMARIZE"}))
    with pytest.raises(PolicyDeniedError) as exc_info:
        require_action("CREATE_PROFILE", envelope)
    assert exc_info.value.policy_decision.reason is DecisionReason.NOT_TASK_NECESSARY


def test_default_scope_is_this_request() -> None:
    assert policy(task_actions=frozenset({"SUMMARIZE"})).scope is Scope.THIS_REQUEST


def test_from_dict_normalizes_action_names() -> None:
    envelope = PolicyEnvelope.from_dict({"policy_id": "p1", "task_actions": ["summarize"], "allow": [], "deny": ["create_profile"]})
    assert envelope.task_actions == frozenset({"SUMMARIZE"})
    assert envelope.deny == frozenset({"CREATE_PROFILE"})


def test_audit_event_preserves_decision_and_normalizes_utc() -> None:
    decision = evaluate_action("SUMMARIZE", policy(task_actions=frozenset({"SUMMARIZE"})))
    event = AuditEvent.from_decision(decision, request_id="request-1", event_id="event-1", occurred_at=datetime(2026, 9, 4, 10, 0, tzinfo=timezone.utc))
    assert event.to_dict()["decision"] == "ALLOW"
    assert event.occurred_at == "2026-09-04T10:00:00Z"


def test_policy_schema_accepts_serialized_model() -> None:
    schema = json.loads(Path("schemas/cmb.policy-envelope.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(policy(task_actions=frozenset({"SUMMARIZE"})).to_dict())


def test_policy_schema_rejects_unknown_fields() -> None:
    schema = json.loads(Path("schemas/cmb.policy-envelope.v1.schema.json").read_text(encoding="utf-8"))
    payload = policy(task_actions=frozenset({"SUMMARIZE"})).to_dict()
    payload["shadow_profile"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_machine_registry_is_synchronized_with_python_registry() -> None:
    on_disk = json.loads(Path("spec/cmb.actions.v1.json").read_text(encoding="utf-8"))
    assert on_disk == registry_manifest()


def test_audit_schema_accepts_audit_event() -> None:
    schema = json.loads(Path("schemas/cmb.policy-audit.v1.schema.json").read_text(encoding="utf-8"))
    decision = evaluate_action("SUMMARIZE", policy(task_actions=frozenset({"SUMMARIZE"})))
    event = AuditEvent.from_decision(decision, request_id="request-schema", event_id="event-schema", occurred_at=datetime(2026, 9, 4, 10, 0, tzinfo=timezone.utc))
    jsonschema.Draft202012Validator(schema).validate(event.to_dict())


def test_machine_readable_conformance_fixture() -> None:
    fixture = json.loads(Path("conformance/cmb-policy-v1.json").read_text(encoding="utf-8"))
    assert fixture["schema"] == "cmb.policy-conformance.v1"
    for case in fixture["cases"]:
        envelope = PolicyEnvelope.from_dict(case["policy"])
        decision = evaluate_action(case["action"], envelope)
        assert decision.decision.value == case["expected"]["decision"], case["name"]
        assert decision.reason.value == case["expected"]["reason"], case["name"]
