"""Scoped cryptographic authorization tokens for the CMB sovereignty runtime."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

AUTHORIZATION_SCHEMA = "cmb.authorization.v1"


class AuthorizationError(ValueError):
    """Raised when an authorization token is malformed or fails verification."""


@dataclass(frozen=True, slots=True)
class AuthorizationToken:
    operation: str
    project: str
    policy_digest: str
    subject_digest: str
    authorized_by: str
    issued_at: str
    expires_at: str
    nonce: str
    controls: tuple[str, ...]
    signature: str
    schema: str = AUTHORIZATION_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != AUTHORIZATION_SCHEMA:
            raise AuthorizationError(f"unsupported authorization schema: {self.schema}")
        for name in ("operation", "project", "authorized_by", "nonce"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise AuthorizationError(f"{name} must be non-empty")
        _require_sha256(self.policy_digest, "policy_digest")
        _require_sha256(self.subject_digest, "subject_digest")
        _parse_time(self.issued_at, "issued_at")
        _parse_time(self.expires_at, "expires_at")
        if _parse_time(self.expires_at, "expires_at") <= _parse_time(self.issued_at, "issued_at"):
            raise AuthorizationError("expires_at must be later than issued_at")
        if not isinstance(self.controls, tuple):
            raise AuthorizationError("controls must be a tuple")
        if any(not isinstance(item, str) or not item.strip() for item in self.controls):
            raise AuthorizationError("controls must contain non-empty strings")
        if not isinstance(self.signature, str):
            raise AuthorizationError("signature must be a string")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AuthorizationToken":
        if not isinstance(payload, dict):
            raise TypeError("authorization payload must be a dictionary")
        required = (
            "operation",
            "project",
            "policy_digest",
            "subject_digest",
            "authorized_by",
            "issued_at",
            "expires_at",
            "nonce",
            "controls",
            "signature",
        )
        missing = [name for name in required if name not in payload]
        if missing:
            raise AuthorizationError(f"missing fields: {', '.join(missing)}")
        controls = payload["controls"]
        if isinstance(controls, (str, bytes)) or not isinstance(controls, Iterable):
            raise AuthorizationError("controls must be an array")
        return cls(
            schema=payload.get("schema", AUTHORIZATION_SCHEMA),
            operation=str(payload["operation"]).strip(),
            project=str(payload["project"]).strip(),
            policy_digest=str(payload["policy_digest"]).strip(),
            subject_digest=str(payload["subject_digest"]).strip(),
            authorized_by=str(payload["authorized_by"]).strip(),
            issued_at=str(payload["issued_at"]).strip(),
            expires_at=str(payload["expires_at"]).strip(),
            nonce=str(payload["nonce"]).strip(),
            controls=tuple(sorted({str(item).strip() for item in controls})),
            signature=str(payload["signature"]).strip(),
        )

    def unsigned_payload(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "operation": self.operation,
            "project": self.project,
            "policy_digest": self.policy_digest,
            "subject_digest": self.subject_digest,
            "authorized_by": self.authorized_by,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
            "controls": list(self.controls),
        }

    def signed_bytes(self) -> bytes:
        return canonical_json(self.unsigned_payload())

    def to_dict(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "signature": self.signature}

    @property
    def digest(self) -> str:
        return "sha256:" + hashlib.sha256(canonical_json(self.to_dict())).hexdigest()


def canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def generate_ed25519_keypair() -> tuple[str, str]:
    Ed25519PrivateKey, _, Encoding, PrivateFormat, PublicFormat, NoEncryption = _crypto()
    private_key = Ed25519PrivateKey.generate()
    private_raw = private_key.private_bytes(
        encoding=Encoding.Raw,
        format=PrivateFormat.Raw,
        encryption_algorithm=NoEncryption(),
    )
    public_raw = private_key.public_key().public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )
    return (
        base64.b64encode(private_raw).decode("ascii"),
        base64.b64encode(public_raw).decode("ascii"),
    )


def write_keypair(private_path: Path, public_path: Path) -> None:
    private_key, public_key = generate_ed25519_keypair()
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_text(private_key + "\n", encoding="utf-8")
    public_path.write_text(public_key + "\n", encoding="utf-8")
    try:
        os.chmod(private_path, 0o600)
    except OSError:
        pass


def create_authorization(
    *,
    operation: str,
    project: str,
    policy_digest: str,
    subject_digest: str,
    authorized_by: str,
    controls: Iterable[str],
    private_key_b64: str,
    ttl_seconds: int = 3600,
    now: datetime | None = None,
) -> AuthorizationToken:
    if ttl_seconds <= 0:
        raise AuthorizationError("ttl_seconds must be positive")
    current = _as_utc(now or datetime.now(timezone.utc))
    unsigned = AuthorizationToken(
        operation=operation.strip(),
        project=project.strip(),
        policy_digest=policy_digest,
        subject_digest=subject_digest,
        authorized_by=authorized_by.strip(),
        issued_at=_format_time(current),
        expires_at=_format_time(current + timedelta(seconds=ttl_seconds)),
        nonce=secrets.token_hex(16),
        controls=tuple(sorted({item.strip() for item in controls if item.strip()})),
        signature="",
    )
    private_raw = _decode_key(private_key_b64, 32, "private key")
    Ed25519PrivateKey, _, _, _, _, _ = _crypto()
    signature = Ed25519PrivateKey.from_private_bytes(private_raw).sign(unsigned.signed_bytes())
    return AuthorizationToken(
        **unsigned.unsigned_payload(),
        signature=base64.b64encode(signature).decode("ascii"),
    )


def verify_authorization(
    token: AuthorizationToken,
    *,
    public_key_b64: str,
    operation: str,
    project: str,
    policy_digest: str,
    subject_digest: str,
    required_controls: Iterable[str],
    now: datetime | None = None,
) -> tuple[bool, tuple[str, ...]]:
    failures: list[str] = []
    current = _as_utc(now or datetime.now(timezone.utc))
    issued = _parse_time(token.issued_at, "issued_at")
    expires = _parse_time(token.expires_at, "expires_at")

    if token.operation != operation:
        failures.append("AUTH_OPERATION_MISMATCH")
    if token.project != project:
        failures.append("AUTH_PROJECT_MISMATCH")
    if token.policy_digest != policy_digest:
        failures.append("AUTH_POLICY_DIGEST_MISMATCH")
    if token.subject_digest != subject_digest:
        failures.append("AUTH_SUBJECT_DIGEST_MISMATCH")
    if current < issued - timedelta(minutes=5):
        failures.append("AUTH_NOT_YET_VALID")
    if current >= expires:
        failures.append("AUTH_EXPIRED")

    missing_controls = sorted(set(required_controls) - set(token.controls))
    failures.extend(f"AUTH_CONTROL_MISSING:{name}" for name in missing_controls)

    try:
        public_raw = _decode_key(public_key_b64, 32, "public key")
        signature = base64.b64decode(token.signature, validate=True)
        if len(signature) != 64:
            raise AuthorizationError("signature must decode to 64 bytes")
        _, Ed25519PublicKey, _, _, _, _ = _crypto()
        Ed25519PublicKey.from_public_bytes(public_raw).verify(signature, token.signed_bytes())
    except Exception:
        failures.append("AUTH_SIGNATURE_INVALID")

    ordered = tuple(dict.fromkeys(failures))
    return (not ordered, ordered)


def load_authorization(path: Path) -> AuthorizationToken:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return AuthorizationToken.from_dict(payload)


def _decode_key(value: str, expected_bytes: int, label: str) -> bytes:
    try:
        raw = base64.b64decode(value.strip(), validate=True)
    except Exception as exc:
        raise AuthorizationError(f"{label} is not valid base64") from exc
    if len(raw) != expected_bytes:
        raise AuthorizationError(f"{label} must decode to {expected_bytes} bytes")
    return raw


def _require_sha256(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise AuthorizationError(f"{field} must use sha256:<64 hex> format")
    digest = value[7:]
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.lower()):
        raise AuthorizationError(f"{field} must use sha256:<64 hex> format")


def _parse_time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthorizationError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise AuthorizationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return _as_utc(value).isoformat(timespec="seconds").replace("+00:00", "Z")


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise AuthorizationError("datetime values must be timezone-aware")
    return value.astimezone(timezone.utc)


def _crypto():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
            Ed25519PublicKey,
        )
        from cryptography.hazmat.primitives.serialization import (
            Encoding,
            NoEncryption,
            PrivateFormat,
            PublicFormat,
        )
    except ImportError as exc:
        raise AuthorizationError(
            "Ed25519 support requires the 'sovereignty' extra: "
            "python -m pip install 'cmb-provenance[sovereignty]'"
        ) from exc
    return (
        Ed25519PrivateKey,
        Ed25519PublicKey,
        Encoding,
        PrivateFormat,
        PublicFormat,
        NoEncryption,
    )
