"""Versioned protocol constants."""

from typing import Final

TOOL_VERSION: Final[str] = "1.5.0-rc.1"
MANIFEST_SCHEMA_VERSION: Final[str] = "cmb.artifact-manifest.v1"
RECEIPT_SCHEMA_VERSION: Final[str] = "cmb.seal-receipt.v1"
ANCHOR_SCHEMA_VERSION: Final[str] = "cmb.anchor.v2"
C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION: Final[str] = "cmb.c2pa-assertion-payload.v1"
HASH_ALGORITHM: Final[str] = "SHA-256"
DEFAULT_LEDGER_NAME: Final[str] = "cmb_anchors.jsonl"
UNVERIFIED_REFERENCE_STATUS: Final[str] = "UNVERIFIED_EXTERNAL_REFERENCE"
GIT_COMMIT_VERIFIED: Final[str] = "VERIFIED_ARTIFACTS_MATCH_COMMIT"
GIT_COMMIT_CALLER_SUPPLIED: Final[str] = "CALLER_SUPPLIED_UNVERIFIED"
GIT_COMMIT_STATUSES: Final[tuple[str, ...]] = (
    GIT_COMMIT_VERIFIED,
    GIT_COMMIT_CALLER_SUPPLIED,
)
ANCHOR_TYPES: Final[tuple[str, ...]] = (
    "public_post",
    "hosted_git_reference",
    "rfc3161_timestamp",
    "public_ledger",
    "other",
)
