"""Repository-local validation for CMB Recovery and canonical corpus metadata."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_CORE_IDS = {
    "cmb:principle:pattern-proof",
    "cmb:principle:profile-person",
    "cmb:principle:model-mind",
    "cmb:principle:prediction-destiny",
    "cmb:principle:capability-authority",
    "cmb:principle:machine-read-define",
    "cmb:principle:human-agency",
}


class AuditError(ValueError):
    """Raised when preservation metadata is internally inconsistent."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"Unable to load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"Expected JSON object: {path}")
    return value


def _safe_file(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise AuditError(f"Path escapes repository root: {relative}")
    if not candidate.is_file():
        raise AuditError(f"Referenced file does not exist: {relative}")
    return candidate


def _audit_recovery_map(root: Path) -> tuple[dict[str, Any], int]:
    recovery_path = _safe_file(root, "machine/recovery-map.json")
    recovery = _load_json(recovery_path)

    if recovery.get("schema_version") != "cmb.recovery-map.v1":
        raise AuditError("Unsupported Recovery map schema version.")

    claims = recovery.get("claims")
    if not isinstance(claims, dict):
        raise AuditError("Recovery map claims must be an object.")
    if claims.get("permanence_guaranteed") is not False:
        raise AuditError("Recovery map must not claim guaranteed permanence.")
    if claims.get("availability_guaranteed") is not False:
        raise AuditError("Recovery map must not claim guaranteed availability.")
    if claims.get("dna_storage_deployed") is not False:
        raise AuditError("Recovery map must not claim deployed DNA storage.")

    evidence_count = 0
    ids: set[str] = set()
    for collection_name in ("integrity_layers", "archives"):
        collection = recovery.get(collection_name)
        if not isinstance(collection, list) or not collection:
            raise AuditError(f"{collection_name} must be a non-empty list.")
        for layer in collection:
            if not isinstance(layer, dict):
                raise AuditError(f"{collection_name} entries must be objects.")
            layer_id = layer.get("id")
            if not isinstance(layer_id, str) or not layer_id:
                raise AuditError(f"{collection_name} entry missing id.")
            if layer_id in ids:
                raise AuditError(f"Duplicate preservation layer id: {layer_id}")
            ids.add(layer_id)
            status = layer.get("status")
            evidence = layer.get("evidence")
            if not isinstance(evidence, list):
                raise AuditError(f"Evidence must be a list for {layer_id}.")
            if status == "implemented" and not evidence:
                raise AuditError(f"Implemented layer lacks evidence: {layer_id}")
            for relative in evidence:
                if not isinstance(relative, str):
                    raise AuditError(f"Evidence path must be a string for {layer_id}.")
                _safe_file(root, relative)
                evidence_count += 1

    boundaries = set(recovery.get("boundaries", []))
    for required in {
        "IMMUTABILITY != AVAILABILITY",
        "DISCOVERY != TRAINING_PERMISSION",
        "STORAGE != BIOLOGICAL_FUNCTION",
    }:
        if required not in boundaries:
            raise AuditError(f"Missing preservation boundary: {required}")

    return recovery, evidence_count


def _audit_corpus(root: Path) -> tuple[dict[str, Any], int]:
    manifest = _load_json(_safe_file(root, "datasets/cmb-canonical-corpus/manifest.json"))
    if manifest.get("schema_version") != "cmb.canonical-corpus-manifest.v1":
        raise AuditError("Unsupported corpus manifest schema version.")

    corpus_path_value = manifest.get("corpus_file")
    if not isinstance(corpus_path_value, str):
        raise AuditError("Corpus manifest is missing corpus_file.")
    corpus_path = _safe_file(root, corpus_path_value)
    data = corpus_path.read_bytes()
    actual_digest = hashlib.sha256(data).hexdigest()
    if actual_digest != manifest.get("sha256"):
        raise AuditError(
            f"Canonical corpus SHA-256 mismatch: expected {manifest.get('sha256')}, got {actual_digest}"
        )

    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(data.decode("utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise AuditError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise AuditError(f"Corpus line {line_number} is not a JSON object.")
        records.append(record)

    if len(records) != manifest.get("record_count"):
        raise AuditError(
            f"Corpus record count mismatch: expected {manifest.get('record_count')}, got {len(records)}"
        )

    ids = [record.get("id") for record in records]
    if any(not isinstance(record_id, str) for record_id in ids):
        raise AuditError("Every corpus record requires a string id.")
    if len(ids) != len(set(ids)):
        raise AuditError("Canonical corpus ids must be unique.")
    missing = REQUIRED_CORE_IDS.difference(ids)
    if missing:
        raise AuditError("Canonical corpus is missing required records: " + ", ".join(sorted(missing)))

    for record in records:
        if record.get("type") != "CMB_INVARIANT":
            raise AuditError(f"Unexpected corpus type for {record.get('id')}.")
        if record.get("epistemic_status") != "normative_principle":
            raise AuditError(f"Unexpected epistemic status for {record.get('id')}.")
        if record.get("license_reference") != "CONTENT_LICENSE.md":
            raise AuditError(f"Missing canonical licensing reference for {record.get('id')}.")

    return manifest, len(records)


def audit_repository(root: str | Path = ".") -> dict[str, Any]:
    """Audit preservation declarations and canonical corpus integrity."""

    repository_root = Path(root).resolve(strict=True)
    recovery, evidence_count = _audit_recovery_map(repository_root)
    manifest, record_count = _audit_corpus(repository_root)

    return {
        "ok": True,
        "recovery_schema": recovery["schema_version"],
        "corpus_schema": manifest["schema_version"],
        "corpus_records": record_count,
        "corpus_sha256": manifest["sha256"],
        "evidence_paths_checked": evidence_count,
        "permanence_guaranteed": False,
        "availability_guaranteed": False,
    }
