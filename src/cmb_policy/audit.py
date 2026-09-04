"""Audit-event helpers for CMB policy decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .models import PolicyDecision

AUDIT_SCHEMA_VERSION = "cmb.policy-audit.v1"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    request_id: str
    action: str
    decision: str
    reason: str
    policy_id: str
    policy_version: str
    scope: str
    occurred_at: str
    schema: str = AUDIT_SCHEMA_VERSION

    @classmethod
    def from_decision(
        cls,
        decision: PolicyDecision,
        *,
        request_id: str,
        event_id: str | None = None,
        occurred_at: datetime | None = None,
    ) -> "AuditEvent":
        if not isinstance(decision, PolicyDecision):
            raise TypeError("decision must be a PolicyDecision")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        timestamp = occurred_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        normalized = timestamp.astimezone(timezone.utc)
        return cls(
            event_id=event_id or f"cmb-audit-{uuid4()}",
            request_id=request_id,
            action=decision.action,
            decision=decision.decision.value,
            reason=decision.reason.value,
            policy_id=decision.policy_id,
            policy_version=decision.policy_version,
            scope=decision.scope.value,
            occurred_at=normalized.isoformat().replace("+00:00", "Z"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "event_id": self.event_id,
            "request_id": self.request_id,
            "action": self.action,
            "decision": self.decision,
            "reason": self.reason,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "scope": self.scope,
            "occurred_at": self.occurred_at,
        }
