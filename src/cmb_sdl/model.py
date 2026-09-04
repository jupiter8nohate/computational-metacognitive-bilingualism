"""Typed models for CMB Sovereign Delegation Language (CMB-SDL)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping


class SDLValidationError(ValueError):
    """Raised when a CMB-SDL document violates deterministic v1 rules."""


@dataclass(frozen=True, order=True)
class ScopeBinding:
    kind: str
    value: str

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "value": self.value}


@dataclass(frozen=True)
class AuthorityDocument:
    human: str
    agent: str
    allow: tuple[str, ...]
    deny: tuple[str, ...]
    scopes: tuple[ScopeBinding, ...]
    purpose: str
    expires_at: str
    required_evidence: tuple[str, ...]
    event_handlers: tuple[tuple[str, str], ...]
    return_receipt: bool = True
    delegable: bool = False

    def __post_init__(self) -> None:
        if not self.human.strip():
            raise SDLValidationError("HUMAN must not be empty.")
        if not self.agent.strip():
            raise SDLValidationError("AGENT must not be empty.")
        if not self.purpose.strip():
            raise SDLValidationError("PURPOSE must not be empty.")
        if not self.scopes:
            raise SDLValidationError("At least one SCOPE is required.")

        allow = set(self.allow)
        deny = set(self.deny)
        overlap = allow & deny
        if overlap:
            raise SDLValidationError(
                f"Capabilities cannot be both ALLOW and DENY: {sorted(overlap)!r}"
            )
        if not allow:
            raise SDLValidationError("At least one ALLOW capability is required.")

        parsed = parse_timestamp(self.expires_at)
        object.__setattr__(self, "expires_at", format_timestamp(parsed))

    @property
    def handlers(self) -> Mapping[str, str]:
        return dict(self.event_handlers)


def parse_timestamp(value: str) -> datetime:
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SDLValidationError(f"Invalid EXPIRES timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise SDLValidationError("EXPIRES timestamp must include a timezone.")
    return parsed.astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
