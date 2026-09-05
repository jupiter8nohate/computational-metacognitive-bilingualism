"""GLITCH://402 payment-requirement and provenance-receipt primitives.

This module intentionally does not hold keys, submit transactions, or verify a
blockchain. It creates x402-compatible payment requirements and validates the
integrity of documentary receipts built from settlements that were verified by
an external facilitator or chain verifier.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Final, Mapping
from urllib.parse import urlparse

GLITCH402_PROTOCOL: Final[str] = "GLITCH://402/1"
GLITCH402_RECEIPT_SCHEMA: Final[str] = "glitch402.payment-receipt.v1"
GLITCH402_LANGUAGE: Final[str] = "Err ⃝or⃟⃤ GLITCHOLOGY"
GLITCH402_PROJECT: Final[str] = "CMB-G8 / GLITCH-8"
GLITCH402_DEPLOYMENT_STATUS: Final[str] = "incubation-no-production-settlement"

X402_VERSION: Final[int] = 2
BASE_MAINNET_CAIP2: Final[str] = "eip155:8453"
BASE_USDC_MAINNET: Final[str] = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

_HEX_64_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_EVM_ADDRESS_RE: Final[re.Pattern[str]] = re.compile(r"^0x[0-9a-fA-F]{40}$")
_EVM_TX_RE: Final[re.Pattern[str]] = re.compile(r"^0x[0-9a-fA-F]{64}$")
_CAIP2_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9]+:[A-Za-z0-9_-]+$")


class Glitch402Error(ValueError):
    """Raised when GLITCH://402 data fails validation."""


def _require_nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Glitch402Error(f"{field} must be a non-empty string.")
    return value.strip()


def _require_uri(value: str, field: str) -> str:
    candidate = _require_nonempty(value, field)
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise Glitch402Error(f"{field} must be an absolute http(s) URL.")
    return candidate


def _require_atomic_amount(value: str) -> str:
    candidate = _require_nonempty(value, "amount_atomic")
    if not candidate.isdigit() or int(candidate) <= 0:
        raise Glitch402Error("amount_atomic must be a positive integer string.")
    return candidate


def _require_caip2(network: str) -> str:
    candidate = _require_nonempty(network, "network")
    if _CAIP2_RE.fullmatch(candidate) is None:
        raise Glitch402Error("network must use CAIP-2 form such as eip155:8453.")
    return candidate


def _require_evm_address(value: str, field: str) -> str:
    candidate = _require_nonempty(value, field)
    if _EVM_ADDRESS_RE.fullmatch(candidate) is None:
        raise Glitch402Error(f"{field} must be a 20-byte EVM address.")
    return candidate


def _require_tx_hash(value: str) -> str:
    candidate = _require_nonempty(value, "transaction_hash")
    if _EVM_TX_RE.fullmatch(candidate) is None:
        raise Glitch402Error("transaction_hash must be a 32-byte EVM transaction hash.")
    return candidate


def _timestamp(value: datetime | str) -> str:
    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            raise Glitch402Error("timestamp must be non-empty.")
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError as exc:
            raise Glitch402Error("timestamp must be ISO-8601.") from exc
    elif isinstance(value, datetime):
        parsed = value
    else:
        raise Glitch402Error("timestamp must be datetime or ISO-8601 string.")

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise Glitch402Error("timestamp must include a timezone.")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def canonical_receipt_body(receipt: Mapping[str, Any]) -> bytes:
    """Return deterministic bytes for the receipt body.

    receipt_id and integrity are excluded to avoid a circular digest.
    This is a CMB-specific canonical form, not RFC 8785 JCS.
    """

    body = {key: value for key, value in receipt.items() if key not in {"receipt_id", "integrity"}}
    try:
        encoded = json.dumps(
            body,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise Glitch402Error(f"receipt body is not canonicalizable JSON: {exc}") from exc
    return encoded.encode("utf-8")


def receipt_sha256(receipt: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_receipt_body(receipt)).hexdigest()


def build_payment_required(
    *,
    resource_url: str,
    description: str,
    amount_atomic: str,
    asset: str,
    pay_to: str,
    network: str = BASE_MAINNET_CAIP2,
    mime_type: str = "application/json",
    service_name: str = "GLITCH-8 Official Service",
    max_timeout_seconds: int = 60,
) -> dict[str, Any]:
    """Build an x402 v2 PaymentRequired object with GLITCH://402 metadata.

    No default payee exists by design. Callers must explicitly supply pay_to.
    """

    resource = _require_uri(resource_url, "resource_url")
    description_value = _require_nonempty(description, "description")
    network_value = _require_caip2(network)
    amount_value = _require_atomic_amount(amount_atomic)
    asset_value = _require_nonempty(asset, "asset")
    payee_value = _require_nonempty(pay_to, "pay_to")
    mime_value = _require_nonempty(mime_type, "mime_type")
    service_value = _require_nonempty(service_name, "service_name")

    if max_timeout_seconds <= 0:
        raise Glitch402Error("max_timeout_seconds must be positive.")

    if network_value.startswith("eip155:"):
        _require_evm_address(asset_value, "asset")
        _require_evm_address(payee_value, "pay_to")

    return {
        "x402Version": X402_VERSION,
        "resource": {
            "url": resource,
            "description": description_value,
            "mimeType": mime_value,
            "serviceName": service_value,
            "tags": ["glitchology", "glitch8", "cmb"],
        },
        "accepts": [
            {
                "scheme": "exact",
                "network": network_value,
                "amount": amount_value,
                "asset": asset_value,
                "payTo": payee_value,
                "maxTimeoutSeconds": max_timeout_seconds,
                "extra": {"name": "USDC", "version": "2"},
            }
        ],
        "extensions": {
            "glitch402": {
                "info": {
                    "protocol": GLITCH402_PROTOCOL,
                    "language": GLITCH402_LANGUAGE,
                    "project": GLITCH402_PROJECT,
                    "boundary": "PAYMENT != OWNERSHIP",
                    "deployment_status": GLITCH402_DEPLOYMENT_STATUS,
                },
                "schema": {
                    "type": "object",
                    "required": ["protocol", "language", "project", "boundary", "deployment_status"],
                    "additionalProperties": True,
                },
            }
        },
    }


def create_verified_settlement_receipt(
    *,
    operation: str,
    resource_uri: str,
    artifact_sha256: str,
    creator_name: str,
    creator_attribution_uri: str,
    network: str,
    asset: str,
    amount_atomic: str,
    decimals: int,
    payer: str,
    payee: str,
    transaction_hash: str,
    verification_source: str,
    verification_evidence: str,
    verified_at: datetime | str,
    provider: str = "external",
) -> dict[str, Any]:
    """Create a tamper-evident receipt from an already verified settlement.

    This function does not verify the chain transaction itself. The caller must
    obtain verification from a facilitator or chain verifier first.
    """

    if verification_source not in {"facilitator", "chain"}:
        raise Glitch402Error("verification_source must be 'facilitator' or 'chain'.")
    if not isinstance(decimals, int) or isinstance(decimals, bool) or not 0 <= decimals <= 36:
        raise Glitch402Error("decimals must be an integer from 0 through 36.")

    network_value = _require_caip2(network)
    if not _HEX_64_RE.fullmatch(artifact_sha256):
        raise Glitch402Error("artifact_sha256 must be 64 lowercase hexadecimal characters.")

    payer_value = _require_nonempty(payer, "payer")
    payee_value = _require_nonempty(payee, "payee")
    asset_value = _require_nonempty(asset, "asset")
    tx_value = _require_nonempty(transaction_hash, "transaction_hash")

    if network_value.startswith("eip155:"):
        payer_value = _require_evm_address(payer_value, "payer")
        payee_value = _require_evm_address(payee_value, "payee")
        asset_value = _require_evm_address(asset_value, "asset")
        tx_value = _require_tx_hash(tx_value)

    receipt: dict[str, Any] = {
        "schema_version": GLITCH402_RECEIPT_SCHEMA,
        "protocol": GLITCH402_PROTOCOL,
        "operation": _require_nonempty(operation, "operation"),
        "created_at": _timestamp(verified_at),
        "resource_uri": _require_uri(resource_uri, "resource_uri"),
        "artifact_sha256": artifact_sha256,
        "creator": {
            "name": _require_nonempty(creator_name, "creator_name"),
            "project": GLITCH402_PROJECT,
            "attribution_uri": _require_uri(creator_attribution_uri, "creator_attribution_uri"),
        },
        "settlement": {
            "status": "settled",
            "provider": _require_nonempty(provider, "provider"),
            "scheme": "x402-exact",
            "x402_version": X402_VERSION,
            "network": network_value,
            "asset": asset_value,
            "amount_atomic": _require_atomic_amount(amount_atomic),
            "decimals": decimals,
            "payer": payer_value,
            "payee": payee_value,
            "transaction_hash": tx_value,
        },
        "verification": {
            "source": verification_source,
            "verified_at": _timestamp(verified_at),
            "evidence": _require_nonempty(verification_evidence, "verification_evidence"),
            "scope": "settlement_observed_external_to_cmb",
        },
        "boundaries": [
            "PAYMENT != OWNERSHIP",
            "PAYMENT_RECEIPT != AUTHORSHIP_PROOF",
            "HASH != COPYRIGHT",
            "INCUBATION != FUNDRAISING",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
    }

    digest = receipt_sha256(receipt)
    receipt["receipt_id"] = f"g402_{digest}"
    receipt["integrity"] = {
        "canonicalization": "cmb-json-v1",
        "sha256": digest,
        "scope": "all receipt fields except receipt_id and integrity",
    }
    return receipt


def validate_receipt_integrity(receipt: Mapping[str, Any]) -> None:
    """Validate receipt structure and CMB-level digest integrity.

    Successful validation means the receipt has not been modified relative to
    its embedded digest. It does not independently prove that a blockchain
    transaction occurred.
    """

    if receipt.get("schema_version") != GLITCH402_RECEIPT_SCHEMA:
        raise Glitch402Error("unsupported receipt schema_version.")
    if receipt.get("protocol") != GLITCH402_PROTOCOL:
        raise Glitch402Error("unsupported GLITCH://402 protocol.")

    integrity = receipt.get("integrity")
    if not isinstance(integrity, Mapping):
        raise Glitch402Error("integrity must be an object.")
    expected = integrity.get("sha256")
    if not isinstance(expected, str) or _HEX_64_RE.fullmatch(expected) is None:
        raise Glitch402Error("integrity.sha256 is invalid.")

    receipt_id = receipt.get("receipt_id")
    if receipt_id != f"g402_{expected}":
        raise Glitch402Error("receipt_id does not match integrity.sha256.")

    actual = receipt_sha256(receipt)
    if actual != expected:
        raise Glitch402Error("receipt digest mismatch; receipt content was modified.")

    settlement = receipt.get("settlement")
    if not isinstance(settlement, Mapping) or settlement.get("status") != "settled":
        raise Glitch402Error("receipt must describe a settled payment.")
    if settlement.get("x402_version") != X402_VERSION:
        raise Glitch402Error("receipt must use x402 version 2.")

    verification = receipt.get("verification")
    if not isinstance(verification, Mapping):
        raise Glitch402Error("verification must be an object.")
    if verification.get("source") not in {"facilitator", "chain"}:
        raise Glitch402Error("verification source must be facilitator or chain.")
