"""Deterministic Authority IR compiler and delegation checks for CMB-SDL."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from .model import AuthorityDocument, SDLValidationError, parse_timestamp
from .parser import parse

SCHEMA = "cmb.authority-ir.v1"
PROTOCOL = "CMB-SDL-1"

_CANONICAL_INVARIANTS = (
    "CAPABILITY != AUTHORITY",
    "DELEGATED_AUTHORITY <= RECEIVED_AUTHORITY",
    "PURPOSE != PERMISSION",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)
_REQUIRED_TOP_LEVEL = frozenset(
    {
        "schema",
        "protocol",
        "issuer",
        "subject",
        "capabilities",
        "scopes",
        "purpose",
        "expires_at",
        "required_evidence",
        "event_handlers",
        "return_receipt",
        "delegable",
        "invariants",
        "digest",
    }
)
_KNOWN_EVENTS = frozenset({"uncertainty", "scope_violation", "expiry"})
_KNOWN_HANDLER_ACTIONS = frozenset({"ASK_HUMAN", "HALT", "REVOKE"})


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest_core(core: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(core)).hexdigest()


def compile_document(document: AuthorityDocument) -> dict[str, Any]:
    core: dict[str, Any] = {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "issuer": {"type": "human", "id": document.human},
        "subject": {"type": "agent", "id": document.agent},
        "capabilities": {
            "allow": list(document.allow),
            "deny": list(document.deny),
        },
        "scopes": [scope.as_dict() for scope in document.scopes],
        "purpose": document.purpose,
        "expires_at": document.expires_at,
        "required_evidence": list(document.required_evidence),
        "event_handlers": dict(document.event_handlers),
        "return_receipt": document.return_receipt,
        "delegable": document.delegable,
        "invariants": list(_CANONICAL_INVARIANTS),
    }
    return {**core, "digest": _digest_core(core)}


def compile_text(text: str) -> dict[str, Any]:
    return compile_document(parse(text))


def validate_authority_ir(ir: Mapping[str, Any]) -> None:
    """Strictly validate canonical Authority IR before trusting its digest."""
    if not isinstance(ir, Mapping):
        raise SDLValidationError("Authority IR must be an object.")

    _require_exact_keys(ir, _REQUIRED_TOP_LEVEL, "Authority IR")

    if ir.get("schema") != SCHEMA:
        raise SDLValidationError(f"Expected schema {SCHEMA!r}.")
    if ir.get("protocol") != PROTOCOL:
        raise SDLValidationError(f"Expected protocol {PROTOCOL!r}.")

    issuer = _require_object(ir["issuer"], {"type", "id"}, "issuer")
    subject = _require_object(ir["subject"], {"type", "id"}, "subject")
    if issuer["type"] != "human":
        raise SDLValidationError("Authority IR issuer.type must be 'human'.")
    if subject["type"] != "agent":
        raise SDLValidationError("Authority IR subject.type must be 'agent'.")
    _require_nonempty_string(issuer["id"], "issuer.id")
    _require_nonempty_string(subject["id"], "subject.id")

    capabilities = _require_object(
        ir["capabilities"], {"allow", "deny"}, "capabilities"
    )
    allow = _require_canonical_string_list(
        capabilities["allow"], "capabilities.allow", require_nonempty=True
    )
    deny = _require_canonical_string_list(
        capabilities["deny"], "capabilities.deny"
    )
    if set(allow) & set(deny):
        raise SDLValidationError(
            "Authority IR contains conflicting allow/deny capabilities."
        )

    _validate_scopes(ir["scopes"])
    _require_nonempty_string(ir["purpose"], "purpose")
    if not isinstance(ir["expires_at"], str):
        raise SDLValidationError("expires_at must be a string.")
    parse_timestamp(ir["expires_at"])

    _require_canonical_string_list(
        ir["required_evidence"], "required_evidence"
    )
    _validate_handlers(ir["event_handlers"])

    if type(ir["return_receipt"]) is not bool:
        raise SDLValidationError("return_receipt must be a boolean.")
    if type(ir["delegable"]) is not bool:
        raise SDLValidationError("delegable must be a boolean.")

    invariants = ir["invariants"]
    if not isinstance(invariants, list) or invariants != list(_CANONICAL_INVARIANTS):
        raise SDLValidationError(
            "Authority IR invariants must exactly match the canonical CMB-SDL-1 set."
        )

    digest = ir["digest"]
    if not isinstance(digest, str):
        raise SDLValidationError("digest must be a string.")
    core = {key: value for key, value in ir.items() if key != "digest"}
    expected = _digest_core(core)
    if digest != expected:
        raise SDLValidationError("Authority IR digest mismatch.")


def validate_delegation(
    parent: Mapping[str, Any],
    child: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> None:
    """Fail closed unless child authority is monotonically narrower than parent."""
    validate_authority_ir(parent)
    validate_authority_ir(child)

    if not parent["delegable"]:
        raise SDLValidationError("Parent authority is not delegable.")

    parent_allow = set(parent["capabilities"]["allow"])
    child_allow = set(child["capabilities"]["allow"])
    parent_deny = set(parent["capabilities"]["deny"])
    child_deny = set(child["capabilities"]["deny"])

    if not child_allow <= parent_allow:
        raise SDLValidationError(
            "Child grants capabilities absent from parent authority."
        )
    if child_allow & parent_deny:
        raise SDLValidationError(
            "Child grants a capability explicitly denied by parent."
        )
    if not parent_deny <= child_deny:
        raise SDLValidationError("Child weakens an explicit parent denial.")

    parent_scopes = {
        (item["kind"], item["value"]) for item in parent["scopes"]
    }
    child_scopes = {
        (item["kind"], item["value"]) for item in child["scopes"]
    }
    if not child_scopes <= parent_scopes:
        raise SDLValidationError("Child scope exceeds parent scope.")

    if child["purpose"] != parent["purpose"]:
        raise SDLValidationError("Child purpose differs from parent purpose.")

    parent_required = set(parent["required_evidence"])
    child_required = set(child["required_evidence"])
    if not parent_required <= child_required:
        raise SDLValidationError(
            "Child weakens parent evidence requirements."
        )

    parent_handlers = dict(parent["event_handlers"])
    child_handlers = dict(child["event_handlers"])
    for event, action in parent_handlers.items():
        if child_handlers.get(event) != action:
            raise SDLValidationError(
                f"Child changes or removes required parent handler for {event!r}."
            )

    if parent["return_receipt"] and not child["return_receipt"]:
        raise SDLValidationError("Child disables a receipt required by parent.")

    parent_expiry = parse_timestamp(parent["expires_at"])
    child_expiry = parse_timestamp(child["expires_at"])
    if child_expiry > parent_expiry:
        raise SDLValidationError(
            "Child authority expires after parent authority."
        )

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if current >= parent_expiry:
        raise SDLValidationError("Parent authority is expired.")
    if current >= child_expiry:
        raise SDLValidationError("Child authority is expired.")


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: set[str] | frozenset[str],
    label: str,
) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        raise SDLValidationError(
            f"{label} is missing fields: {', '.join(missing)}."
        )
    if extra:
        raise SDLValidationError(
            f"{label} contains unknown fields: {', '.join(extra)}."
        )


def _require_object(
    value: Any,
    expected: set[str],
    label: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SDLValidationError(f"{label} must be an object.")
    _require_exact_keys(value, expected, label)
    return value


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SDLValidationError(f"{label} must be a non-empty string.")
    return value


def _require_canonical_string_list(
    value: Any,
    label: str,
    *,
    require_nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        raise SDLValidationError(f"{label} must be an array.")
    if require_nonempty and not value:
        raise SDLValidationError(f"{label} must not be empty.")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise SDLValidationError(f"{label} must contain non-empty strings.")
    if len(set(value)) != len(value):
        raise SDLValidationError(f"{label} must not contain duplicates.")
    if value != sorted(value):
        raise SDLValidationError(f"{label} must use canonical sorted order.")
    return value


def _validate_scopes(value: Any) -> None:
    if not isinstance(value, list) or not value:
        raise SDLValidationError("scopes must be a non-empty array.")

    normalized: list[tuple[str, str]] = []
    for index, item in enumerate(value):
        scope = _require_object(item, {"kind", "value"}, f"scopes[{index}]")
        kind = _require_nonempty_string(scope["kind"], f"scopes[{index}].kind")
        scope_value = _require_nonempty_string(
            scope["value"], f"scopes[{index}].value"
        )
        normalized.append((kind, scope_value))

    if len(set(normalized)) != len(normalized):
        raise SDLValidationError("scopes must not contain duplicates.")
    if normalized != sorted(normalized):
        raise SDLValidationError("scopes must use canonical sorted order.")


def _validate_handlers(value: Any) -> None:
    if not isinstance(value, Mapping):
        raise SDLValidationError("event_handlers must be an object.")
    unknown = sorted(set(value) - _KNOWN_EVENTS)
    if unknown:
        raise SDLValidationError(
            f"event_handlers contains unknown events: {', '.join(unknown)}."
        )
    for event, action in value.items():
        if action not in _KNOWN_HANDLER_ACTIONS:
            raise SDLValidationError(
                f"event_handlers.{event} has unsupported action {action!r}."
            )
