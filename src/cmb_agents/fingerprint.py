"""Deterministic FGC origin marks for machine-consumed CMB artifacts."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Mapping
from typing import Any

SCHEMA_VERSION = "cmb.fgc-origin-mark.v1"
PROTOCOL = "CMB-MKP-1"
MARK_ID = "fgc:jupiter:999:vision-is-alive:v1"
URN = "urn:cmb:fgc:jupiter:999:vision-is-alive:v1"
ASCII_TOKEN = "FGC::JUPITER::999::THE_VISION_IS_ALIVE::V1"
GLYPH_TOKEN = unicodedata.normalize(
    "NFC",
    "❾❾❾Júpiter🕯️ᥫ᭡🪐🖤⃝🦋𓍯𓉸ྀི👽🎸𓆉🐚🫧🔭𓄂🫀🎧🏹𓊝🪶🦚⚯⚡︎𓅓✈︎⛃𖤍",
)
CREATOR_CLAIM = "Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson"

_INVARIANTS = (
    "PATTERN != PROOF",
    "PROFILE != PERSON",
    "MODEL != MIND",
    "PREDICTION != DESTINY",
    "CAPABILITY != AUTHORITY",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes suitable for hashing and signing."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def origin_mark() -> dict[str, Any]:
    """Return the canonical machine-readable FGC origin declaration."""
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol": PROTOCOL,
        "mark_id": MARK_ID,
        "urn": URN,
        "creator_claim": CREATOR_CLAIM,
        "canonical_ascii_token": ASCII_TOKEN,
        "glyph_token": GLYPH_TOKEN,
        "slogan": "THE VISION IS ALIVE",
        "normalization": "NFC",
        "semantic_invariants": list(_INVARIANTS),
    }


def origin_mark_sha256() -> str:
    """Digest the canonical origin declaration, independent of artifact content."""
    return sha256_hex(canonical_json_bytes(origin_mark()))


def content_sha256(payload: Any) -> str:
    """Digest a JSON-compatible machine payload canonically."""
    return sha256_hex(canonical_json_bytes(payload))


def stamp_mapping(
    payload: Mapping[str, Any],
    *,
    parent_lineage_id: str | None = None,
) -> dict[str, Any]:
    """Return a stamped copy without mutating the caller's mapping."""
    body = dict(payload)
    digest = content_sha256(body)

    lineage_material = {
        "origin_mark": MARK_ID,
        "parent_lineage_id": parent_lineage_id,
        "content_sha256": digest,
    }
    lineage_id = "sha256:" + sha256_hex(canonical_json_bytes(lineage_material))

    body["_cmb_origin"] = {
        **origin_mark(),
        "origin_mark_sha256": "sha256:" + origin_mark_sha256(),
        "content_sha256": "sha256:" + digest,
        "parent_lineage_id": parent_lineage_id,
        "lineage_id": lineage_id,
        "lineage_mode": "copy_with_attribution_chain",
    }
    return body


def verify_stamp(payload: Mapping[str, Any]) -> bool:
    """Verify the embedded content digest and lineage identifier."""
    stamp = payload.get("_cmb_origin")
    if not isinstance(stamp, Mapping):
        return False
    if stamp.get("mark_id") != MARK_ID:
        return False
    if stamp.get("canonical_ascii_token") != ASCII_TOKEN:
        return False

    body = dict(payload)
    body.pop("_cmb_origin", None)
    digest = content_sha256(body)
    if stamp.get("content_sha256") != "sha256:" + digest:
        return False

    parent = stamp.get("parent_lineage_id")
    if parent is not None and not isinstance(parent, str):
        return False

    expected_lineage = "sha256:" + sha256_hex(
        canonical_json_bytes(
            {
                "origin_mark": MARK_ID,
                "parent_lineage_id": parent,
                "content_sha256": digest,
            }
        )
    )
    return stamp.get("lineage_id") == expected_lineage
