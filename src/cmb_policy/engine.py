"""Deterministic policy evaluation for CMB human-agency boundaries."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import (
    ActionDefinition,
    Decision,
    DecisionReason,
    PolicyDecision,
    PolicyEnvelope,
    Sensitivity,
)

DEFAULT_ACTIONS: dict[str, ActionDefinition] = {
    item.name: item
    for item in (
        ActionDefinition("SUMMARIZE", Sensitivity.ORDINARY_TRANSFORMATION, "Summarize supplied content."),
        ActionDefinition("TRANSLATE", Sensitivity.ORDINARY_TRANSFORMATION, "Translate supplied content."),
        ActionDefinition("FORMAT", Sensitivity.ORDINARY_TRANSFORMATION, "Reformat supplied content."),
        ActionDefinition("SORT", Sensitivity.ORDINARY_TRANSFORMATION, "Sort supplied items."),
        ActionDefinition("CONVERT", Sensitivity.ORDINARY_TRANSFORMATION, "Convert a representation or format."),
        ActionDefinition("COMPARE", Sensitivity.CONTEXTUAL_INTERPRETATION, "Compare supplied materials."),
        ActionDefinition("CLASSIFY_DOCUMENT", Sensitivity.CONTEXTUAL_INTERPRETATION, "Classify an artifact rather than a person."),
        ActionDefinition("EXTRACT_ARGUMENT", Sensitivity.CONTEXTUAL_INTERPRETATION, "Extract an argument from supplied content."),
        ActionDefinition("IDENTIFY_CONTRADICTION", Sensitivity.CONTEXTUAL_INTERPRETATION, "Identify contradictions in supplied content."),
        ActionDefinition("INFER_PERSONALITY", Sensitivity.PERSONAL_INFERENCE, "Infer personality characteristics about a person."),
        ActionDefinition("INFER_COGNITIVE_CAPABILITY", Sensitivity.PERSONAL_INFERENCE, "Infer cognitive capability about a person."),
        ActionDefinition("INFER_DIAGNOSIS", Sensitivity.SENSITIVE_INFERENCE, "Infer a diagnosis or health condition."),
        ActionDefinition("INFER_EMOTIONAL_VULNERABILITY", Sensitivity.SENSITIVE_INFERENCE, "Infer emotional vulnerability about a person."),
        ActionDefinition("CREATE_PROFILE", Sensitivity.PERSISTENT_PROFILING, "Create a persistent behavioral or personal profile."),
        ActionDefinition("UPDATE_PROFILE", Sensitivity.PERSISTENT_PROFILING, "Update a persistent behavioral or personal profile."),
        ActionDefinition("STORE_INFERRED_STATE", Sensitivity.PERSISTENT_PROFILING, "Persist an inferred human state."),
        ActionDefinition("LINK_BEHAVIOR_ACROSS_CONTEXTS", Sensitivity.PERSISTENT_PROFILING, "Link behavior across distinct contexts."),
        ActionDefinition("HIGH_STAKES_DECISION", Sensitivity.HIGH_STAKES_DECISION, "Use automation in a consequential human decision."),
    )
}


class PolicyDeniedError(PermissionError):
    """Raised when a caller requires an action that policy does not authorize."""

    def __init__(self, decision: PolicyDecision) -> None:
        self.policy_decision = decision
        super().__init__(
            f"CMB policy denied {decision.action}: {decision.reason.value}"
        )


def evaluate_action(
    action: str,
    policy: PolicyEnvelope,
    *,
    registry: Mapping[str, ActionDefinition] = DEFAULT_ACTIONS,
) -> PolicyDecision:
    """Evaluate one machine action against a CMB policy envelope.

    Evaluation order is intentionally deterministic:

    1. revoked policy denies all execution;
    2. explicit denial dominates every permission;
    3. unknown actions fail closed;
    4. actions outside the declared task are denied;
    5. personal/sensitive/profiling/high-stakes actions require explicit allow;
    6. explicit allow authorizes a task-necessary action;
    7. ordinary/contextual task actions may proceed by task necessity.
    """

    if not isinstance(policy, PolicyEnvelope):
        raise TypeError("policy must be a PolicyEnvelope")
    normalized = _normalize_action(action)

    definition = registry.get(normalized)
    if policy.revoked:
        return _decision(policy, normalized, Decision.DENY, DecisionReason.POLICY_REVOKED, definition)

    if normalized in policy.deny:
        return _decision(policy, normalized, Decision.DENY, DecisionReason.EXPLICIT_PROHIBITION, definition)

    if definition is None:
        return _decision(policy, normalized, Decision.DENY, DecisionReason.UNKNOWN_ACTION, None)

    if normalized not in policy.task_actions:
        return _decision(policy, normalized, Decision.DENY, DecisionReason.NOT_TASK_NECESSARY, definition)

    if definition.explicit_permission_required and normalized not in policy.allow:
        return _decision(
            policy,
            normalized,
            Decision.DENY,
            DecisionReason.EXPLICIT_PERMISSION_REQUIRED,
            definition,
        )

    if normalized in policy.allow:
        return _decision(policy, normalized, Decision.ALLOW, DecisionReason.EXPLICIT_PERMISSION, definition)

    return _decision(policy, normalized, Decision.ALLOW, DecisionReason.TASK_NECESSARY, definition)


def evaluate_actions(
    actions: Iterable[str],
    policy: PolicyEnvelope,
    *,
    registry: Mapping[str, ActionDefinition] = DEFAULT_ACTIONS,
) -> tuple[PolicyDecision, ...]:
    return tuple(evaluate_action(action, policy, registry=registry) for action in actions)


def require_action(
    action: str,
    policy: PolicyEnvelope,
    *,
    registry: Mapping[str, ActionDefinition] = DEFAULT_ACTIONS,
) -> PolicyDecision:
    decision = evaluate_action(action, policy, registry=registry)
    if not decision.allowed:
        raise PolicyDeniedError(decision)
    return decision


def registry_manifest(
    registry: Mapping[str, ActionDefinition] = DEFAULT_ACTIONS,
) -> dict[str, object]:
    return {
        "schema": "cmb.actions.v1",
        "actions": [
            {
                "name": item.name,
                "sensitivity": int(item.sensitivity),
                "sensitivity_name": item.sensitivity.name,
                "explicit_permission_required": item.explicit_permission_required,
                "description": item.description,
            }
            for item in sorted(registry.values(), key=lambda item: item.name)
        ],
    }


def _decision(
    policy: PolicyEnvelope,
    action: str,
    decision: Decision,
    reason: DecisionReason,
    definition: ActionDefinition | None,
) -> PolicyDecision:
    return PolicyDecision(
        action=action,
        decision=decision,
        reason=reason,
        sensitivity=definition.sensitivity if definition is not None else None,
        policy_id=policy.policy_id,
        policy_version=policy.version,
        scope=policy.scope,
    )


def _normalize_action(action: str) -> str:
    if not isinstance(action, str):
        raise TypeError("action must be a string")
    normalized = action.strip().upper()
    if not normalized:
        raise ValueError("action must be non-empty")
    return normalized
