"""Typed policy models for the CMB sovereignty policy engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Iterable

POLICY_SCHEMA_VERSION = "cmb.policy-envelope.v1"
POLICY_VERSION = "1.0"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class DecisionReason(str, Enum):
    EXPLICIT_PROHIBITION = "explicit_prohibition"
    POLICY_REVOKED = "policy_revoked"
    UNKNOWN_ACTION = "unknown_action"
    NOT_TASK_NECESSARY = "not_task_necessary"
    EXPLICIT_PERMISSION_REQUIRED = "explicit_permission_required"
    EXPLICIT_PERMISSION = "explicit_permission"
    TASK_NECESSARY = "task_necessary"


class Scope(str, Enum):
    THIS_REQUEST = "THIS_REQUEST"
    THIS_SESSION = "THIS_SESSION"
    THIS_ARTIFACT = "THIS_ARTIFACT"
    THIS_PROJECT = "THIS_PROJECT"
    UNTIL_REVOKED = "UNTIL_REVOKED"


class Sensitivity(IntEnum):
    ORDINARY_TRANSFORMATION = 0
    CONTEXTUAL_INTERPRETATION = 1
    PERSONAL_INFERENCE = 2
    SENSITIVE_INFERENCE = 3
    PERSISTENT_PROFILING = 4
    HIGH_STAKES_DECISION = 5


@dataclass(frozen=True, slots=True)
class ActionDefinition:
    name: str
    sensitivity: Sensitivity
    description: str

    def __post_init__(self) -> None:
        if not self.name or self.name != self.name.strip().upper():
            raise ValueError("action name must be non-empty uppercase text")
        if not isinstance(self.sensitivity, Sensitivity):
            raise TypeError("sensitivity must be a Sensitivity")
        if not self.description.strip():
            raise ValueError("description must be non-empty")

    @property
    def explicit_permission_required(self) -> bool:
        return self.sensitivity >= Sensitivity.PERSONAL_INFERENCE


@dataclass(frozen=True, slots=True)
class PolicyEnvelope:
    """A deny-dominant policy envelope for one declared task scope."""

    policy_id: str
    task_actions: frozenset[str]
    allow: frozenset[str] = frozenset()
    deny: frozenset[str] = frozenset()
    scope: Scope = Scope.THIS_REQUEST
    revoked: bool = False
    version: str = POLICY_VERSION
    schema: str = POLICY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id.strip():
            raise ValueError("policy_id must be a non-empty string")
        if self.schema != POLICY_SCHEMA_VERSION:
            raise ValueError(f"unsupported policy schema: {self.schema}")
        if self.version != POLICY_VERSION:
            raise ValueError(f"unsupported policy version: {self.version}")
        if not isinstance(self.scope, Scope):
            raise TypeError("scope must be a Scope")
        if type(self.revoked) is not bool:
            raise TypeError("revoked must be bool")
        for field_name in ("task_actions", "allow", "deny"):
            value = getattr(self, field_name)
            if not isinstance(value, frozenset):
                raise TypeError(f"{field_name} must be a frozenset")
            for action in value:
                if not isinstance(action, str) or not action.strip():
                    raise ValueError(f"{field_name} contains an invalid action")
                if action != action.strip().upper():
                    raise ValueError(f"{field_name} actions must be uppercase")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PolicyEnvelope":
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")
        try:
            return cls(
                policy_id=payload["policy_id"],
                task_actions=_to_action_set(payload["task_actions"]),
                allow=_to_action_set(payload.get("allow", [])),
                deny=_to_action_set(payload.get("deny", [])),
                scope=Scope(payload.get("scope", Scope.THIS_REQUEST.value)),
                revoked=payload.get("revoked", False),
                version=payload.get("version", POLICY_VERSION),
                schema=payload.get("schema", POLICY_SCHEMA_VERSION),
            )
        except KeyError as exc:
            raise ValueError(f"missing required field: {exc.args[0]}") from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "policy_id": self.policy_id,
            "version": self.version,
            "scope": self.scope.value,
            "task_actions": sorted(self.task_actions),
            "allow": sorted(self.allow),
            "deny": sorted(self.deny),
            "revoked": self.revoked,
        }


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    action: str
    decision: Decision
    reason: DecisionReason
    sensitivity: Sensitivity | None
    policy_id: str
    policy_version: str
    scope: Scope

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "decision": self.decision.value,
            "allowed": self.allowed,
            "reason": self.reason.value,
            "sensitivity": (
                int(self.sensitivity) if self.sensitivity is not None else None
            ),
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "scope": self.scope.value,
        }


def _to_action_set(values: Iterable[object]) -> frozenset[str]:
    if isinstance(values, (str, bytes)):
        raise TypeError("action collections must not be strings")
    normalized: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("actions must be non-empty strings")
        normalized.add(value.strip().upper())
    return frozenset(normalized)
