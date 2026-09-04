"""Strict schema validation without optional runtime dependencies."""

from __future__ import annotations

import json
import re
from pathlib import PurePosixPath
from typing import Any, Mapping

from .canonical import canonical_json_bytes, sha256_bytes
from .constants import (
    ANCHOR_SCHEMA_VERSION,
    ANCHOR_TYPES,
    GIT_COMMIT_STATUSES,
    HASH_ALGORITHM,
    MANIFEST_SCHEMA_VERSION,
    RECEIPT_SCHEMA_VERSION,
    UNVERIFIED_REFERENCE_STATUS,
)
from .errors import SchemaValidationError
from .timeutil import normalize_timestamp

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")

_ARTIFACT_KEYS = {"path", "sha256", "size_bytes"}
_MANIFEST_KEYS = {
    "schema_version",
    "tool_version",
    "hash_algorithm",
    "git_commit",
    "git_commit_status",
    "artifacts",
}
_COVERAGE_KEYS = {"type", "paths", "excludes_unlisted"}
_RECEIPT_KEYS = {
    "schema_version",
    "tool_version",
    "created_at_utc",
    "coverage",
    "manifest",
    "manifest_sha256",
}
_ANCHOR_KEYS = {
    "schema_version",
    "sequence",
    "anchor_type",
    "description",
    "location",
    "manifest_sha256",
    "local_recorded_at_utc",
    "claimed_external_time_utc",
    "external_time_basis",
    "verification_status",
    "previous_record_sha256",
    "record_sha256",
}


def load_json_strict(value: str) -> Any:
    """Decode JSON while rejecting duplicate object keys."""

    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise SchemaValidationError(f"Duplicate JSON object key: {key!r}.")
            result[key] = item
        return result

    try:
        return json.loads(value, object_pairs_hook=object_pairs)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"Malformed JSON: {exc}") from exc


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SchemaValidationError(f"{label} must be a JSON object.")
    if not all(isinstance(key, str) for key in value):
        raise SchemaValidationError(f"{label} keys must be strings.")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing or unknown:
        details: list[str] = []
        if missing:
            details.append(f"missing={missing}")
        if unknown:
            details.append(f"unknown={unknown}")
        raise SchemaValidationError(
            f"{label} fields are invalid ({', '.join(details)})."
        )


def _nonempty_string(value: Any, label: str, *, maximum: int = 4096) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaValidationError(f"{label} must be a non-empty string.")
    if value != value.strip():
        raise SchemaValidationError(f"{label} must not have surrounding whitespace.")
    if len(value) > maximum:
        raise SchemaValidationError(f"{label} exceeds {maximum} characters.")
    return value


def validate_sha256(value: Any, label: str = "SHA-256") -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise SchemaValidationError(
            f"{label} must be 64 lowercase hexadecimal characters."
        )
    return value


def validate_git_commit(value: Any) -> str:
    if not isinstance(value, str) or not _GIT_COMMIT_RE.fullmatch(value):
        raise SchemaValidationError(
            "git_commit must be a full lowercase Git object ID."
        )
    return value


def validate_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise SchemaValidationError(
            "Artifact path must be a non-empty normalized POSIX path."
        )
    path = PurePosixPath(value)
    if path.is_absolute() or value in {".", ".."} or ".." in path.parts:
        raise SchemaValidationError(
            f"Artifact path escapes the sealing root: {value!r}."
        )
    if str(path) != value or any(part in {"", "."} for part in path.parts):
        raise SchemaValidationError(f"Artifact path is not normalized: {value!r}.")
    return value


def validate_manifest(value: Any) -> Mapping[str, Any]:
    manifest = _mapping(value, "manifest")
    _exact_keys(manifest, _MANIFEST_KEYS, "manifest")
    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise SchemaValidationError(
            f"Unsupported manifest schema: {manifest['schema_version']!r}."
        )
    if not isinstance(manifest["tool_version"], str) or not _SEMVER_RE.fullmatch(
        manifest["tool_version"]
    ):
        raise SchemaValidationError(
            "manifest.tool_version must be semantic version syntax."
        )
    if manifest["hash_algorithm"] != HASH_ALGORITHM:
        raise SchemaValidationError(
            f"manifest.hash_algorithm must be {HASH_ALGORITHM!r}."
        )
    validate_git_commit(manifest["git_commit"])
    if manifest["git_commit_status"] not in GIT_COMMIT_STATUSES:
        raise SchemaValidationError(
            f"manifest.git_commit_status must be one of {GIT_COMMIT_STATUSES}."
        )

    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise SchemaValidationError(
            "manifest.artifacts must be a non-empty JSON array."
        )
    paths: list[str] = []
    for index, raw in enumerate(artifacts):
        artifact = _mapping(raw, f"manifest.artifacts[{index}]")
        _exact_keys(artifact, _ARTIFACT_KEYS, f"manifest.artifacts[{index}]")
        paths.append(validate_relative_path(artifact["path"]))
        validate_sha256(artifact["sha256"], f"manifest.artifacts[{index}].sha256")
        if type(artifact["size_bytes"]) is not int or artifact["size_bytes"] < 0:
            raise SchemaValidationError(
                f"manifest.artifacts[{index}].size_bytes must be a non-negative integer."
            )
    if paths != sorted(paths):
        raise SchemaValidationError("manifest.artifacts must be sorted by path.")
    if len(paths) != len(set(paths)):
        raise SchemaValidationError("manifest.artifacts contains duplicate paths.")
    return manifest


def validate_receipt(value: Any) -> Mapping[str, Any]:
    receipt = _mapping(value, "receipt")
    _exact_keys(receipt, _RECEIPT_KEYS, "receipt")
    if receipt["schema_version"] != RECEIPT_SCHEMA_VERSION:
        raise SchemaValidationError(
            f"Unsupported receipt schema: {receipt['schema_version']!r}."
        )
    if not isinstance(receipt["tool_version"], str) or not _SEMVER_RE.fullmatch(
        receipt["tool_version"]
    ):
        raise SchemaValidationError(
            "receipt.tool_version must be semantic version syntax."
        )
    normalized_time = normalize_timestamp(receipt["created_at_utc"])
    if normalized_time != receipt["created_at_utc"]:
        raise SchemaValidationError(
            "receipt.created_at_utc must already be normalized to UTC."
        )

    manifest = validate_manifest(receipt["manifest"])
    manifest_sha256 = validate_sha256(
        receipt["manifest_sha256"], "receipt.manifest_sha256"
    )
    expected_digest = sha256_bytes(canonical_json_bytes(manifest))
    if manifest_sha256 != expected_digest:
        raise SchemaValidationError(
            "receipt.manifest_sha256 does not match the canonical manifest."
        )

    coverage = _mapping(receipt["coverage"], "receipt.coverage")
    _exact_keys(coverage, _COVERAGE_KEYS, "receipt.coverage")
    if coverage["type"] != "explicit_file_set":
        raise SchemaValidationError(
            "receipt.coverage.type must be 'explicit_file_set'."
        )
    if coverage["excludes_unlisted"] is not True:
        raise SchemaValidationError("receipt.coverage.excludes_unlisted must be true.")
    if not isinstance(coverage["paths"], list):
        raise SchemaValidationError("receipt.coverage.paths must be a JSON array.")
    coverage_paths = [validate_relative_path(path) for path in coverage["paths"]]
    artifact_paths = [item["path"] for item in manifest["artifacts"]]
    if coverage_paths != artifact_paths:
        raise SchemaValidationError(
            "receipt.coverage.paths must exactly match manifest artifact paths."
        )
    if receipt["tool_version"] != manifest["tool_version"]:
        raise SchemaValidationError("Receipt and manifest tool versions do not match.")
    return receipt


def validate_anchor_record(value: Any) -> Mapping[str, Any]:
    record = _mapping(value, "anchor record")
    _exact_keys(record, _ANCHOR_KEYS, "anchor record")
    if record["schema_version"] != ANCHOR_SCHEMA_VERSION:
        raise SchemaValidationError(
            f"Unsupported anchor schema: {record['schema_version']!r}."
        )
    if type(record["sequence"]) is not int or record["sequence"] < 1:
        raise SchemaValidationError("anchor.sequence must be an integer >= 1.")
    if record["anchor_type"] not in ANCHOR_TYPES:
        raise SchemaValidationError(
            f"anchor.anchor_type must be one of {ANCHOR_TYPES}."
        )
    _nonempty_string(record["description"], "anchor.description")
    _nonempty_string(record["location"], "anchor.location")
    validate_sha256(record["manifest_sha256"], "anchor.manifest_sha256")

    local_time = normalize_timestamp(record["local_recorded_at_utc"])
    if local_time != record["local_recorded_at_utc"]:
        raise SchemaValidationError(
            "anchor.local_recorded_at_utc must be normalized to UTC."
        )

    claimed = record["claimed_external_time_utc"]
    basis = record["external_time_basis"]
    if (claimed is None) != (basis is None):
        raise SchemaValidationError(
            "claimed_external_time_utc and external_time_basis must both be set or both be null."
        )
    if claimed is not None:
        claimed_normalized = normalize_timestamp(claimed)
        if claimed_normalized != claimed:
            raise SchemaValidationError(
                "anchor.claimed_external_time_utc must be normalized to UTC."
            )
        _nonempty_string(basis, "anchor.external_time_basis")
    if record["verification_status"] != UNVERIFIED_REFERENCE_STATUS:
        raise SchemaValidationError(
            f"anchor.verification_status must be {UNVERIFIED_REFERENCE_STATUS!r}."
        )
    previous = record["previous_record_sha256"]
    if previous is not None:
        validate_sha256(previous, "anchor.previous_record_sha256")
    validate_sha256(record["record_sha256"], "anchor.record_sha256")
    return record
