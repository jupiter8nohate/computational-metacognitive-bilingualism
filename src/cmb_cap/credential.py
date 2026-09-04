"""Signed, portable CMB capability credentials."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from cmb_sdl import compile_text, validate_authority_ir, validate_delegation
from cmb_sdl.model import SDLValidationError, parse_timestamp

CAP_SCHEMA = "cmb.capability-credential.v1"
CAP_PROTOCOL = "CMB-CAP-1"
PROOF_TYPE = "CMBEd25519SignatureV1"
MCP_EXTENSION_ID = "io.cmb.capability/v1"
A2A_EXTENSION_URI = (
    "https://jupiter8nohate.github.io/"
    "computational-metacognitive-bilingualism/extensions/cmb-cap/v1"
)


class CapabilityError(ValueError):
    """Raised when a CMB-CAP credential cannot be issued or parsed."""


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def credential_digest(credential: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(credential)).hexdigest()


def public_key_fingerprint(public_key_b64: str) -> str:
    raw = _decode_key(public_key_b64, 32, "public key")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def issue_from_sdl(
    source: str,
    *,
    private_key_b64: str,
    now: datetime | None = None,
    nonce: str | None = None,
    parent_credential: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return issue_capability(
        compile_text(source),
        private_key_b64=private_key_b64,
        now=now,
        nonce=nonce,
        parent_credential=parent_credential,
    )


def issue_capability(
    authority_ir: Mapping[str, Any],
    *,
    private_key_b64: str,
    now: datetime | None = None,
    nonce: str | None = None,
    parent_credential: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Issue one self-contained Ed25519-signed CMB capability credential."""
    try:
        validate_authority_ir(authority_ir)
    except SDLValidationError as exc:
        raise CapabilityError(str(exc)) from exc

    current = _as_utc(now or datetime.now(timezone.utc))
    expires = parse_timestamp(str(authority_ir["expires_at"]))
    if current >= expires:
        raise CapabilityError("Cannot issue an already-expired authority.")

    private_raw = _decode_key(private_key_b64, 32, "private key")
    Ed25519PrivateKey, _, Encoding, PublicFormat = _crypto()
    private_key = Ed25519PrivateKey.from_private_bytes(private_raw)
    public_raw = private_key.public_key().public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )
    public_b64 = base64.b64encode(public_raw).decode("ascii")
    fingerprint = "sha256:" + hashlib.sha256(public_raw).hexdigest()

    parent_digest: str | None = None
    if parent_credential is not None:
        if parent_credential.get("parent_credential_digest") is not None:
            raise CapabilityError(
                "CMB-CAP-1 supports one delegated hop; verify a full chain "
                "before introducing additional delegation."
            )
        parent_ok, parent_failures = _verify_single(parent_credential, now=current)
        if not parent_ok:
            raise CapabilityError(
                "Parent credential is invalid: " + ", ".join(parent_failures)
            )
        if (
            parent_credential["authority"]["issuer"]["id"]
            != authority_ir["issuer"]["id"]
        ):
            raise CapabilityError("Child and parent must retain the same root human issuer.")
        parent_method = parent_credential["proof"]["verification_method"]
        if parent_method != "cmb:key:" + fingerprint:
            raise CapabilityError(
                "CMB-CAP-1 delegated credentials must be signed by the same "
                "verified root key as the parent credential."
            )
        try:
            validate_delegation(
                parent_credential["authority"],
                authority_ir,
                now=current,
            )
        except SDLValidationError as exc:
            raise CapabilityError(str(exc)) from exc
        parent_digest = credential_digest(parent_credential)

    issued_at = _format_time(current)
    token_nonce = nonce or secrets.token_hex(16)
    if len(token_nonce) < 16:
        raise CapabilityError("nonce must contain at least 16 characters")

    credential_id = _credential_id(
        authority_digest=str(authority_ir["digest"]),
        issued_at=issued_at,
        nonce=token_nonce,
        key_fingerprint=fingerprint,
        parent_credential_digest=parent_digest,
    )

    proof_meta = {
        "type": PROOF_TYPE,
        "created": issued_at,
        "verification_method": "cmb:key:" + fingerprint,
        "public_key_b64": public_b64,
    }
    unsigned: dict[str, Any] = {
        "schema": CAP_SCHEMA,
        "protocol": CAP_PROTOCOL,
        "credential_id": credential_id,
        "issuer": dict(authority_ir["issuer"]),
        "subject": dict(authority_ir["subject"]),
        "authority": dict(authority_ir),
        "issued_at": issued_at,
        "expires_at": authority_ir["expires_at"],
        "nonce": token_nonce,
        "parent_credential_digest": parent_digest,
        "interoperability": {
            "mcp_extension": MCP_EXTENSION_ID,
            "a2a_extension_uri": A2A_EXTENSION_URI,
            "w3c_vc_2_0": "projection_available_not_data_integrity_conformant",
        },
        "proof": proof_meta,
    }
    signature = private_key.sign(canonical_json(unsigned))
    return {
        **unsigned,
        "proof": {
            **proof_meta,
            "signature": base64.b64encode(signature).decode("ascii"),
        },
    }


def verify_capability(
    credential: Mapping[str, Any],
    *,
    now: datetime | None = None,
    expected_key_fingerprint: str | None = None,
    parent_credential: Mapping[str, Any] | None = None,
) -> tuple[bool, tuple[str, ...]]:
    """Verify signature, authority integrity, expiry, optional key pin, and lineage."""
    current = _as_utc(now or datetime.now(timezone.utc))
    ok, failures = _verify_single(
        credential,
        now=current,
        expected_key_fingerprint=expected_key_fingerprint,
    )
    result = list(failures)

    if ok:
        parent_digest = credential.get("parent_credential_digest")
        if parent_digest:
            if parent_credential is None:
                result.append("CAP_PARENT_REQUIRED")
            else:
                if parent_credential.get("parent_credential_digest") is not None:
                    result.append("CAP_PARENT_CHAIN_UNSUPPORTED")
                    parent_ok = False
                    parent_failures = ()
                else:
                    parent_ok, parent_failures = _verify_single(
                        parent_credential,
                        now=current,
                    )
                if not parent_ok:
                    result.extend(
                        f"CAP_PARENT_INVALID:{item}" for item in parent_failures
                    )
                elif credential_digest(parent_credential) != parent_digest:
                    result.append("CAP_PARENT_DIGEST_MISMATCH")
                else:
                    try:
                        if (
                            parent_credential["proof"]["verification_method"]
                            != credential["proof"]["verification_method"]
                        ):
                            result.append("CAP_DELEGATION_SIGNER_MISMATCH")
                        if (
                            parent_credential["authority"]["issuer"]["id"]
                            != credential["authority"]["issuer"]["id"]
                        ):
                            result.append("CAP_ROOT_ISSUER_MISMATCH")
                        validate_delegation(
                            parent_credential["authority"],
                            credential["authority"],
                            now=current,
                        )
                    except (KeyError, TypeError, SDLValidationError):
                        result.append("CAP_DELEGATION_INVALID")

    ordered = tuple(dict.fromkeys(result))
    return (not ordered, ordered)


def _verify_single(
    credential: Mapping[str, Any],
    *,
    now: datetime,
    expected_key_fingerprint: str | None = None,
) -> tuple[bool, tuple[str, ...]]:
    failures: list[str] = []
    try:
        if credential.get("schema") != CAP_SCHEMA:
            failures.append("CAP_SCHEMA_INVALID")
        if credential.get("protocol") != CAP_PROTOCOL:
            failures.append("CAP_PROTOCOL_INVALID")

        authority = credential["authority"]
        validate_authority_ir(authority)

        if credential["issuer"] != authority["issuer"]:
            failures.append("CAP_ISSUER_AUTHORITY_MISMATCH")
        if credential["subject"] != authority["subject"]:
            failures.append("CAP_SUBJECT_AUTHORITY_MISMATCH")
        if credential["expires_at"] != authority["expires_at"]:
            failures.append("CAP_EXPIRY_AUTHORITY_MISMATCH")

        issued = _parse_time(str(credential["issued_at"]), "issued_at")
        expires = _parse_time(str(credential["expires_at"]), "expires_at")
        if now < issued - timedelta(minutes=5):
            failures.append("CAP_NOT_YET_VALID")
        if now >= expires:
            failures.append("CAP_EXPIRED")

        proof = credential["proof"]
        if proof.get("type") != PROOF_TYPE:
            failures.append("CAP_PROOF_TYPE_INVALID")
        if proof.get("created") != credential["issued_at"]:
            failures.append("CAP_PROOF_TIME_MISMATCH")

        public_b64 = str(proof["public_key_b64"])
        fingerprint = public_key_fingerprint(public_b64)
        if proof.get("verification_method") != "cmb:key:" + fingerprint:
            failures.append("CAP_KEY_FINGERPRINT_MISMATCH")
        if (
            expected_key_fingerprint is not None
            and fingerprint != expected_key_fingerprint
        ):
            failures.append("CAP_EXPECTED_KEY_MISMATCH")

        expected_id = _credential_id(
            authority_digest=str(authority["digest"]),
            issued_at=str(credential["issued_at"]),
            nonce=str(credential["nonce"]),
            key_fingerprint=fingerprint,
            parent_credential_digest=credential.get("parent_credential_digest"),
        )
        if credential.get("credential_id") != expected_id:
            failures.append("CAP_CREDENTIAL_ID_MISMATCH")

        unsigned = dict(credential)
        unsigned["proof"] = {
            key: value
            for key, value in proof.items()
            if key != "signature"
        }
        public_raw = _decode_key(public_b64, 32, "public key")
        signature = base64.b64decode(str(proof["signature"]), validate=True)
        if len(signature) != 64:
            failures.append("CAP_SIGNATURE_INVALID")
        else:
            _, Ed25519PublicKey, _, _ = _crypto()
            Ed25519PublicKey.from_public_bytes(public_raw).verify(
                signature,
                canonical_json(unsigned),
            )
    except SDLValidationError:
        failures.append("CAP_AUTHORITY_INVALID")
    except (KeyError, TypeError, ValueError, CapabilityError):
        failures.append("CAP_MALFORMED")
    except Exception:
        failures.append("CAP_SIGNATURE_INVALID")

    ordered = tuple(dict.fromkeys(failures))
    return (not ordered, ordered)


def load_credential(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CapabilityError(f"Could not load credential: {path}") from exc
    if not isinstance(payload, dict):
        raise CapabilityError("Credential must be a JSON object.")
    return payload


def mcp_extension_payload(credential: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "extension": MCP_EXTENSION_ID,
        "protocol": CAP_PROTOCOL,
        "credential_digest": credential_digest(credential),
        "credential": dict(credential),
    }


def a2a_extension_declaration(*, required: bool = False) -> dict[str, Any]:
    return {
        "uri": A2A_EXTENSION_URI,
        "description": (
            "Carries CMB-CAP signed human-to-agent authority credentials. "
            "CMB-CAP is experimental and is not an official A2A extension."
        ),
        "required": required,
        "params": {
            "protocol": CAP_PROTOCOL,
            "schema": CAP_SCHEMA,
        },
    }


def a2a_extension_payload(credential: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "extension_uri": A2A_EXTENSION_URI,
        "protocol": CAP_PROTOCOL,
        "credential_digest": credential_digest(credential),
        "credential": dict(credential),
    }


def vc_projection(credential: Mapping[str, Any]) -> dict[str, Any]:
    """Return a VC Data Model 2.0-shaped projection without claiming DI proof conformance."""
    issuer_id = str(credential["issuer"]["id"])
    subject_id = str(credential["subject"]["id"])
    return {
        "@context": [
            "https://www.w3.org/ns/credentials/v2",
            {
                "cmb": (
                    "https://jupiter8nohate.github.io/"
                    "computational-metacognitive-bilingualism/ns#"
                )
            },
        ],
        "id": credential["credential_id"],
        "type": ["VerifiableCredential", "cmb:CapabilityCredential"],
        "issuer": "urn:cmb:issuer:" + _text_hash(issuer_id),
        "validFrom": credential["issued_at"],
        "validUntil": credential["expires_at"],
        "credentialSubject": {
            "id": "urn:cmb:agent:" + _text_hash(subject_id),
            "cmb:issuerLabel": issuer_id,
            "cmb:subjectLabel": subject_id,
            "cmb:authority": credential["authority"],
            "cmb:credentialDigest": credential_digest(credential),
        },
        "cmb:standardsStatus": (
            "VC_2_0_projection_only_not_W3C_Data_Integrity_proof"
        ),
    }


def _credential_id(
    *,
    authority_digest: str,
    issued_at: str,
    nonce: str,
    key_fingerprint: str,
    parent_credential_digest: str | None,
) -> str:
    seed = {
        "authority_digest": authority_digest,
        "issued_at": issued_at,
        "nonce": nonce,
        "key_fingerprint": key_fingerprint,
        "parent_credential_digest": parent_credential_digest,
    }
    return "urn:cmb:cap:" + hashlib.sha256(canonical_json(seed)).hexdigest()


def _text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _decode_key(value: str, expected_bytes: int, label: str) -> bytes:
    try:
        raw = base64.b64decode(value.strip(), validate=True)
    except Exception as exc:
        raise CapabilityError(f"{label} is not valid base64") from exc
    if len(raw) != expected_bytes:
        raise CapabilityError(f"{label} must decode to {expected_bytes} bytes")
    return raw


def _parse_time(value: str, label: str) -> datetime:
    try:
        return parse_timestamp(value)
    except SDLValidationError as exc:
        raise CapabilityError(f"Invalid {label}") from exc


def _format_time(value: datetime) -> str:
    return _as_utc(value).isoformat(timespec="seconds").replace("+00:00", "Z")


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise CapabilityError("datetime values must include a timezone")
    return value.astimezone(timezone.utc)


def _crypto() -> tuple[Any, Any, Any, Any]:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
            Ed25519PublicKey,
        )
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    except ImportError as exc:
        raise CapabilityError(
            'CMB-CAP signing requires the "sovereignty" extra: '
            'python -m pip install -e ".[sovereignty]"'
        ) from exc
    return Ed25519PrivateKey, Ed25519PublicKey, Encoding, PublicFormat
