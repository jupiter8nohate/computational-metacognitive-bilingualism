"""Deterministic Authority IR compiler and delegation checks for CMB-SDL."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from .model import AuthorityDocument, SDLValidationError, parse_timestamp
from .parser import parse

SCHEMA = "cmb.authority-ir.v1"
PROTOCOL = "CMB-SDL-1"

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
        "invariants": [
            "CAPABILITY != AUTHORITY",
            "DELEGATED_AUTHORITY <= RECEIVED_AUTHORITY",
            "PURPOSE != PERMISSION",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
    }
    return {**core, "digest": _digest_core(core)}


def compile_text(text: str) -> dict[str, Any]:
    return compile_document(parse(text))


def validate_authority_ir(ir: Mapping[str, Any]) -> None:
    """Validate required shape and the deterministic integrity digest."""
    missing = sorted(_REQUIRED_TOP_LEVEL - set(ir))
    if missing:
        raise SDLValidationError(
            f"Authority IR is missing fields: {', '.join(missing)}."
        )
    if ir.get("schema") != SCHEMA:
        raise SDLValidationError(f"Expected schema {SCHEMA!r}.")
    if ir.get("protocol") != PROTOCOL:
        raise SDLValidationError(f"Expected protocol {PROTOCOL!r}.")

    try:
        capabilities = ir["capabilities"]
        allow = capabilities["allow"]
        deny = capabilities["deny"]
        scopes = ir["scopes"]
        handlers = ir["event_handlers"]
        required_evidence = ir["required_evidence"]
    except (KeyError, TypeError) as exc:
        raise SDLValidationError("Malformed Authority IR structure.") from exc

    if not isinstance(allow, list) or not all(
        isinstance(item, str) and item for item in allow
    ):
        raise SDLValidationError("Authority IR allow list is malformed.")
    if not isinstance(deny, list) or not all(
        isinstance(item, str) and item for item in deny
    ):
        raise SDLValidationError("Authority IR deny list is malformed.")
    if set(allow) & set(deny):
        raise SDLValidationError(
            "Authority IR contains conflicting allow/deny capabilities."
        )
    if not isinstance(scopes, list) or not scopes:
        raise SDLValidationError("Authority IR must contain at least one scope.")
    if not isinstance(handlers, dict):
        raise SDLValidationError("Authority IR event_handlers must be an object.")
    if not isinstance(required_evidence, list):
        raise SDLValidationError(
            "Authority IR required_evidence must be an array."
        )

    parse_timestamp(str(ir["expires_at"]))

    core = {key: value for key, value in ir.items() if key != "digest"}
    expected = _digest_core(core)
    if ir.get("digest") != expected:
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

    if not parent.get("delegable", False):
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

    try:
        parent_scopes = {
            (item["kind"], item["value"]) for item in parent["scopes"]
        }
        child_scopes = {
            (item["kind"], item["value"]) for item in child["scopes"]
        }
    except (KeyError, TypeError) as exc:
        raise SDLValidationError(
            "Malformed scope binding in Authority IR."
        ) from exc
    if not child_scopes <= parent_scopes:
        raise SDLValidationError("Child scope exceeds parent scope.")

    if child.get("purpose") != parent.get("purpose"):
        raise SDLValidationError("Child purpose differs from parent purpose.")

    parent_required = set(parent.get("required_evidence", []))
    child_required = set(child.get("required_evidence", []))
    if not parent_required <= child_required:
        raise SDLValidationError(
            "Child weakens parent evidence requirements."
        )

    parent_handlers = dict(parent.get("event_handlers", {}))
    child_handlers = dict(child.get("event_handlers", {}))
    for event, action in parent_handlers.items():
        if child_handlers.get(event) != action:
            raise SDLValidationError(
                f"Child changes or removes required parent handler for {event!r}."
            )

    if parent.get("return_receipt", False) and not child.get(
        "return_receipt", False
    ):
        raise SDLValidationError("Child disables a receipt required by parent.")

    parent_expiry = parse_timestamp(str(parent["expires_at"]))
    child_expiry = parse_timestamp(str(child["expires_at"]))
    if child_expiry > parent_expiry:
        raise SDLValidationError(
            "Child authority expires after parent authority."
        )

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if current >= parent_expiry:
        raise SDLValidationError("Parent authority is expired.")
    if current >= child_expiry:
        raise SDLValidationError("Child authority is expired.")
